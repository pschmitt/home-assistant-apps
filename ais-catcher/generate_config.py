#!/usr/bin/env python3
"""Translate Home Assistant app options into an AIS-catcher JSON config."""

from __future__ import annotations

import argparse
import copy
import json
import os
import pathlib
import re
import sys
import tempfile
from typing import Any


DEFAULTS: dict[str, Any] = {
    "hardware_required": True,
    "receiver": {
        "device": "auto",
        "gain": "auto",
        "ppm": 0,
        "rtlagc": False,
        "sample_rate": 1536000,
        "bandwidth": 192000,
        "channel": "AB",
    },
    "web": {"enabled": True},
    "udp_outputs": [],
    "tcp_outputs": [],
    "aishub": {"enabled": False, "host": "", "port": 0},
    "aiscatcher_share": {"enabled": False, "key": ""},
    "log_level": "info",
}

TOP_LEVEL_KEYS = set(DEFAULTS)
RECEIVER_KEYS = set(DEFAULTS["receiver"])
WEB_KEYS = set(DEFAULTS["web"])
AISHUB_KEYS = set(DEFAULTS["aishub"])
SHARE_KEYS = set(DEFAULTS["aiscatcher_share"])
LOG_LEVELS = {"debug", "info", "warning", "error", "critical"}
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


class ConfigurationError(ValueError):
    """An invalid Home Assistant option."""


def fail(message: str) -> ConfigurationError:
    return ConfigurationError(f"invalid configuration: {message}")


def require_type(value: Any, expected: type, name: str) -> Any:
    if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
        raise fail(f"{name} must be {expected.__name__}")
    return value


def require_keys(value: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise fail(f"unknown option(s) in {name}: {', '.join(unknown)}")


def merged_options(options: Any) -> dict[str, Any]:
    require_type(options, dict, "top-level options")
    require_keys(options, TOP_LEVEL_KEYS, "top-level options")
    result = copy.deepcopy(DEFAULTS)
    for key, value in options.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key].update(value)
        else:
            result[key] = value
    return result


def validate_options(options: dict[str, Any]) -> None:
    require_type(options["hardware_required"], bool, "hardware_required")

    receiver = require_type(options["receiver"], dict, "receiver")
    require_keys(receiver, RECEIVER_KEYS, "receiver")
    device = require_type(receiver["device"], str, "receiver.device")
    if not device.strip():
        raise fail("receiver.device must not be empty")
    gain = require_type(receiver["gain"], str, "receiver.gain")
    if gain.lower() != "auto":
        try:
            gain_value = float(gain)
        except ValueError as error:
            raise fail("receiver.gain must be auto or a number from 0 to 50") from error
        if not 0 <= gain_value <= 50:
            raise fail("receiver.gain must be auto or a number from 0 to 50")
    ppm = require_type(receiver["ppm"], int, "receiver.ppm")
    if not -150 <= ppm <= 150:
        raise fail("receiver.ppm must be between -150 and 150")
    require_type(receiver["rtlagc"], bool, "receiver.rtlagc")
    sample_rate = require_type(receiver["sample_rate"], int, "receiver.sample_rate")
    if not 12500 <= sample_rate <= 12288000:
        raise fail("receiver.sample_rate must be between 12500 and 12288000")
    bandwidth = require_type(receiver["bandwidth"], int, "receiver.bandwidth")
    if not 0 <= bandwidth <= 1000000:
        raise fail("receiver.bandwidth must be between 0 and 1000000")
    channel = require_type(receiver["channel"], str, "receiver.channel")
    if channel not in {"AB", "CD"}:
        raise fail("receiver.channel must be AB or CD")

    web = require_type(options["web"], dict, "web")
    require_keys(web, WEB_KEYS, "web")
    require_type(web["enabled"], bool, "web.enabled")

    validate_outputs(options["udp_outputs"], "udp_outputs")
    validate_outputs(options["tcp_outputs"], "tcp_outputs")

    aishub = require_type(options["aishub"], dict, "aishub")
    require_keys(aishub, AISHUB_KEYS, "aishub")
    require_type(aishub["enabled"], bool, "aishub.enabled")
    require_type(aishub["host"], str, "aishub.host")
    port = require_type(aishub["port"], int, "aishub.port")
    if not 0 <= port <= 65535:
        raise fail("aishub.port must be between 0 and 65535")
    if aishub["enabled"] and (not aishub["host"].strip() or port == 0):
        raise fail("aishub.host and aishub.port are required when AISHub is enabled")

    sharing = require_type(options["aiscatcher_share"], dict, "aiscatcher_share")
    require_keys(sharing, SHARE_KEYS, "aiscatcher_share")
    require_type(sharing["enabled"], bool, "aiscatcher_share.enabled")
    require_type(sharing["key"], str, "aiscatcher_share.key")
    if sharing["enabled"] and not sharing["key"].strip():
        raise fail("aiscatcher_share.key is required when sharing is enabled")
    if sharing["key"] and not UUID_PATTERN.fullmatch(sharing["key"]):
        raise fail("aiscatcher_share.key must be a UUID supplied by aiscatcher.org")
    log_level = require_type(options["log_level"], str, "log_level")
    if log_level not in LOG_LEVELS:
        raise fail(f"log_level must be one of: {', '.join(sorted(LOG_LEVELS))}")


def validate_outputs(outputs: Any, name: str) -> None:
    require_type(outputs, list, name)
    for index, output in enumerate(outputs):
        output_name = f"{name}[{index}]"
        output = require_type(output, dict, output_name)
        require_keys(output, {"host", "port"}, output_name)
        host = require_type(output.get("host"), str, f"{output_name}.host")
        if not host.strip():
            raise fail(f"{output_name}.host must not be empty")
        port = require_type(output.get("port"), int, f"{output_name}.port")
        if not 1 <= port <= 65535:
            raise fail(f"{output_name}.port must be between 1 and 65535")


def build_config(options: dict[str, Any]) -> dict[str, Any]:
    receiver_options = options["receiver"]
    if options["hardware_required"]:
        receiver: dict[str, Any] = {
            "input": "rtlsdr",
            "channel": receiver_options["channel"],
            "rtlsdr": {
                "tuner": (
                    receiver_options["gain"].lower()
                    if receiver_options["gain"].lower() == "auto"
                    else receiver_options["gain"]
                ),
                "rtlagc": receiver_options["rtlagc"],
                "freqoffset": receiver_options["ppm"],
                "sample_rate": receiver_options["sample_rate"],
                "bandwidth": receiver_options["bandwidth"],
            },
        }
        if receiver_options["device"].lower() != "auto":
            receiver["serial"] = receiver_options["device"]
        mode = "hardware"
    else:
        # This is a real AIS-catcher UDP NMEA input, not an SDR simulator. It
        # keeps the native web viewer available while waiting for hardware.
        receiver = {
            "input": "udpserver",
            "udpserver": {"server": "127.0.0.1", "port": 10110},
        }
        mode = "no-hardware"

    config: dict[str, Any] = {
        "config": "aiscatcher",
        "version": 1,
        "screen": 0,
        "receiver": [receiver],
        "udp": [
            {"active": True, "host": output["host"], "port": output["port"]}
            for output in options["udp_outputs"]
        ],
        "tcp": [
            {"active": True, "host": output["host"], "port": output["port"]}
            for output in options["tcp_outputs"]
        ],
    }
    if options["aishub"]["enabled"]:
        config["udp"].append(
            {
                "active": True,
                "host": options["aishub"]["host"],
                "port": options["aishub"]["port"],
            }
        )
    if options["web"]["enabled"]:
        config["server"] = [{"active": True, "port": 8100}]
    else:
        config["server"] = []
    config["sharing"] = options["aiscatcher_share"]["enabled"]
    if options["aiscatcher_share"]["enabled"]:
        config["sharing_key"] = options["aiscatcher_share"]["key"]
    return {"mode": mode, "log_level": options["log_level"], "config": config}


def redact(config: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(config)
    if "sharing_key" in result:
        result["sharing_key"] = "<redacted>"
    return result


def load_options(path: pathlib.Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as options_file:
            return merged_options(json.load(options_file))
    except FileNotFoundError as error:
        raise fail(f"options file does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise fail(f"options file is not valid JSON: {error}") from error


def write_config(path: pathlib.Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, indent=2)
            config_file.write("\n")
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, path)
    except BaseException:
        os.unlink(temporary_name)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--options", type=pathlib.Path, default=pathlib.Path("/data/options.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("/data/aiscatcher.json"))
    parser.add_argument("--print-redacted", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        options = load_options(args.options)
        validate_options(options)
        result = build_config(options)
        write_config(args.output, result["config"])
    except (ConfigurationError, OSError) as error:
        print(error, file=sys.stderr)
        return 2

    if args.print_redacted:
        print(json.dumps(redact(result["config"]), indent=2))
    else:
        print(f"{result['mode']}|{result['log_level']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

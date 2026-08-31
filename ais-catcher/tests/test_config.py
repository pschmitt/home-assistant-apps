#!/usr/bin/env python3
"""Tests for the options-to-AIS-catcher configuration boundary."""

from __future__ import annotations

import json
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "generate_config.py"
OPTIONS = ROOT / "tests" / "options"
sys.path.insert(0, str(ROOT))
import generate_config  # noqa: E402


class ConfigGenerationTests(unittest.TestCase):
    def run_generator(self, fixture: str, *extra: str) -> tuple[subprocess.CompletedProcess[str], pathlib.Path]:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        output = pathlib.Path(temporary_directory.name) / "aiscatcher.json"
        process = subprocess.run(
            [
                "python3",
                str(GENERATOR),
                "--options",
                str(OPTIONS / fixture),
                "--output",
                str(output),
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return process, output

    def test_minimal_configuration_uses_auto_rtl_sdr_and_ingress_server(self) -> None:
        process, output = self.run_generator("minimal.json")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "hardware|info")
        config = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(config["receiver"][0]["input"], "rtlsdr")
        self.assertNotIn("serial", config["receiver"][0])
        self.assertEqual(config["receiver"][0]["rtlsdr"]["tuner"], "auto")
        self.assertEqual(config["receiver"][0]["rtlsdr"]["freqoffset"], 0)
        self.assertEqual(config["server"], [{"active": True, "port": 8100}])
        self.assertEqual(config["udp"], [])
        self.assertEqual(config["tcp"], [])

    def test_full_configuration_maps_outputs_and_sharing(self) -> None:
        process, output = self.run_generator("full.json")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "hardware|debug")
        config = json.loads(output.read_text(encoding="utf-8"))
        receiver = config["receiver"][0]
        self.assertEqual(receiver["serial"], "NESDR-TEST-SERIAL")
        self.assertEqual(receiver["rtlsdr"]["tuner"], "32.8")
        self.assertEqual(receiver["rtlsdr"]["freqoffset"], -3)
        self.assertEqual(config["udp"], [
            {"active": True, "host": "192.0.2.10", "port": 10110},
            {"active": True, "host": "aishub.example", "port": 12345},
        ])
        self.assertEqual(config["tcp"], [{
            "active": True,
            "host": "ais-consumer.example",
            "port": 4001,
        }])
        self.assertTrue(config["sharing"])
        self.assertEqual(config["sharing_key"], "123e4567-e89b-12d3-a456-426614174000")

    def test_selected_usb_device_resolves_to_ais_catcher_serial(self) -> None:
        options = json.loads((OPTIONS / "selected-usb.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary_directory:
            sysfs_root = pathlib.Path(temporary_directory)
            usb_device = sysfs_root / "1-8"
            usb_device.mkdir()
            (usb_device / "busnum").write_text("001\n", encoding="utf-8")
            (usb_device / "devnum").write_text("008\n", encoding="utf-8")
            (usb_device / "serial").write_text("28567980\n", encoding="utf-8")
            merged = generate_config.merged_options(options)
            generate_config.validate_options(merged)
            config = generate_config.build_config(merged, sysfs_root)["config"]
        self.assertEqual(config["receiver"][0]["serial"], "28567980")

    def test_redacted_output_does_not_contain_sharing_key(self) -> None:
        process, output = self.run_generator("full.json", "--print-redacted")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertNotIn("123e4567-e89b-12d3-a456-426614174000", process.stdout)
        self.assertIn('"sharing_key": "<redacted>"', process.stdout)
        self.assertIn("123e4567-e89b-12d3-a456-426614174000", output.read_text(encoding="utf-8"))
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_no_hardware_mode_is_native_idle_udp_input(self) -> None:
        process, output = self.run_generator("no-hardware.json")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "no-hardware|info")
        config = json.loads(output.read_text(encoding="utf-8"))
        receiver = config["receiver"][0]
        self.assertEqual(receiver["input"], "udpserver")
        self.assertEqual(receiver["udpserver"], {"server": "127.0.0.1", "port": 10110})
        self.assertNotIn("rtlsdr", json.dumps(config))

    def test_invalid_options_fail_before_writing_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            options = pathlib.Path(temporary_directory) / "options.json"
            output = pathlib.Path(temporary_directory) / "config.json"
            base = json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
            base["receiver"]["ppm"] = 151
            options.write_text(json.dumps(base), encoding="utf-8")
            process = subprocess.run(
                [
                    "python3",
                    str(GENERATOR),
                    "--options",
                    str(options),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            output_exists = output.exists()
        self.assertEqual(process.returncode, 2)
        self.assertIn("receiver.ppm", process.stderr)
        self.assertFalse(output_exists)

    def test_enabled_aishub_requires_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            options = pathlib.Path(temporary_directory) / "options.json"
            output = pathlib.Path(temporary_directory) / "config.json"
            base = json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
            base["aishub"]["enabled"] = True
            options.write_text(json.dumps(base), encoding="utf-8")
            process = subprocess.run(
                [
                    "python3",
                    str(GENERATOR),
                    "--options",
                    str(options),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            output_exists = output.exists()
        self.assertEqual(process.returncode, 2)
        self.assertIn("AISHub", process.stderr)
        self.assertFalse(output_exists)

    def test_invalid_community_key_fails_before_writing_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            options = pathlib.Path(temporary_directory) / "options.json"
            output = pathlib.Path(temporary_directory) / "config.json"
            base = json.loads((OPTIONS / "full.json").read_text(encoding="utf-8"))
            base["aiscatcher_share"]["key"] = "not-a-community-uuid"
            options.write_text(json.dumps(base), encoding="utf-8")
            process = subprocess.run(
                [
                    "python3",
                    str(GENERATOR),
                    "--options",
                    str(options),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            output_exists = output.exists()
        self.assertEqual(process.returncode, 2)
        self.assertIn("must be a UUID", process.stderr)
        self.assertFalse(output_exists)

    def test_non_string_channel_fails_as_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            options = pathlib.Path(temporary_directory) / "options.json"
            output = pathlib.Path(temporary_directory) / "config.json"
            base = json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
            base["receiver"]["channel"] = []
            options.write_text(json.dumps(base), encoding="utf-8")
            process = subprocess.run(
                [
                    "python3",
                    str(GENERATOR),
                    "--options",
                    str(options),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            output_exists = output.exists()
        self.assertEqual(process.returncode, 2)
        self.assertIn("receiver.channel", process.stderr)
        self.assertFalse(output_exists)


if __name__ == "__main__":
    unittest.main()

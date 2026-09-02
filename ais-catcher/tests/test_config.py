#!/usr/bin/env python3
"""Tests for the options-to-AIS-catcher configuration boundary."""

from __future__ import annotations

import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


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
        self.assertEqual(process.stdout.strip(), "hardware|info|false|0.0|0.0")
        config = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(config["receiver"][0]["input"], "rtlsdr")
        self.assertNotIn("serial", config["receiver"][0])
        self.assertEqual(config["receiver"][0]["rtlsdr"]["tuner"], "auto")
        self.assertEqual(config["receiver"][0]["rtlsdr"]["freqoffset"], 0)
        self.assertEqual(config["server"], [{
            "active": True,
            "port": 8100,
            "file": generate_config.WEB_VIEWER_BACKUP_FILE,
            "backup": generate_config.WEB_VIEWER_BACKUP_INTERVAL_MINUTES,
        }])
        self.assertEqual(config["udp"], [])
        self.assertEqual(config["tcp"], [])

    def test_full_configuration_maps_outputs_and_sharing(self) -> None:
        process, output = self.run_generator("full.json")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "hardware|debug|true|52.520008|13.404954")
        config = json.loads(output.read_text(encoding="utf-8"))
        receiver = config["receiver"][0]
        self.assertNotIn("serial", receiver)
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
        self.assertEqual(config["server"], [{
            "active": True,
            "port": 8100,
            "file": generate_config.WEB_VIEWER_BACKUP_FILE,
            "backup": generate_config.WEB_VIEWER_BACKUP_INTERVAL_MINUTES,
            "lat": 52.520008,
            "lon": 13.404954,
            "share_loc": True,
            "use_gps": False,
        }])
        self.assertTrue(config["sharing"])
        self.assertEqual(config["sharing_key"], "123e4567-e89b-12d3-a456-426614174000")

    def test_enabled_antenna_location_is_exported_to_web_server(self) -> None:
        process, output = self.run_generator("full.json")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(
            process.stdout.strip(), "hardware|debug|true|52.520008|13.404954"
        )
        config = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(config["server"][0]["lat"], 52.520008)
        self.assertEqual(config["server"][0]["lon"], 13.404954)
        self.assertTrue(config["server"][0]["share_loc"])
        self.assertFalse(config["server"][0]["use_gps"])

    def test_default_log_level_maps_to_ais_catcher_info(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            options = pathlib.Path(temporary_directory) / "options.json"
            output = pathlib.Path(temporary_directory) / "config.json"
            base = json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
            base["log_level"] = "default"
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
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "hardware|info|false|0.0|0.0")

    def test_invalid_antenna_latitude_fails_before_writing_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            options = pathlib.Path(temporary_directory) / "options.json"
            output = pathlib.Path(temporary_directory) / "config.json"
            base = json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
            base["antenna"]["latitude"] = 90.1
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
        self.assertIn("antenna.latitude", process.stderr)
        self.assertFalse(output_exists)

    def test_redacted_output_does_not_contain_sharing_key(self) -> None:
        process, output = self.run_generator("full.json", "--print-redacted")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertNotIn("123e4567-e89b-12d3-a456-426614174000", process.stdout)
        self.assertIn('"sharing_key": "<redacted>"', process.stdout)
        self.assertIn("123e4567-e89b-12d3-a456-426614174000", output.read_text(encoding="utf-8"))
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_no_hardware_mode_is_native_idle_udp_input(self) -> None:
        process, output = self.run_generator("no-hardware.json", "--no-hardware")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "no-hardware|info|false|0.0|0.0")
        config = json.loads(output.read_text(encoding="utf-8"))
        receiver = config["receiver"][0]
        self.assertEqual(receiver["input"], "udpserver")
        self.assertEqual(receiver["udpserver"], {"server": "127.0.0.1", "port": 10110})
        self.assertNotIn("rtlsdr", json.dumps(config))

    def test_legacy_options_are_migrated_without_exposing_old_fields(self) -> None:
        options = json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        options["device"] = "/dev/bus/usb/001/008"
        options["hardware_required"] = True
        options["udp_outputs"] = [{"host": "192.0.2.10", "port": 10110}]
        options["tcp_outputs"] = [{"host": "ais-consumer.example", "port": 4001}]
        del options["nmea"]

        merged = generate_config.merged_options(options)
        generate_config.validate_options(merged)
        config = generate_config.build_config(merged)["config"]

        self.assertEqual(merged["nmea"]["udp_outputs"], options["udp_outputs"])
        self.assertEqual(merged["nmea"]["tcp_outputs"], options["tcp_outputs"])
        self.assertNotIn("device", merged)
        self.assertNotIn("serial", config["receiver"][0])

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

    def test_mqtt_output_uses_discovered_service_and_redacts_password(self) -> None:
        options = generate_config.merged_options(
            json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        )
        options["mqtt"].update(
            {
                "enabled": True,
                "topic": "ais-catcher/%mmsi%",
                "msgformat": "JSON_FULL",
                "qos": 1,
                "client_id": "ais-catcher-test",
            }
        )
        service = {
            "host": "core-mosquitto",
            "port": 1883,
            "username": "mqtt-user",
            "password": "mqtt-secret",
            "ssl": False,
        }

        generate_config.validate_options(options)
        config = generate_config.build_config(options, mqtt_service=service)["config"]
        mqtt = config["mqtt"][0]

        self.assertEqual(mqtt["host"], "core-mosquitto")
        self.assertEqual(mqtt["port"], 1883)
        self.assertEqual(mqtt["topic"], "ais-catcher/%mmsi%")
        self.assertEqual(mqtt["msgformat"], "JSON_FULL")
        self.assertEqual(mqtt["qos"], 1)
        self.assertEqual(mqtt["protocol"], "MQTT")
        self.assertEqual(mqtt["password"], "mqtt-secret")
        self.assertNotIn("mqtt-secret", json.dumps(generate_config.redact(config)))
        self.assertIn('"password": "<redacted>"', json.dumps(generate_config.redact(config)))

    def test_mqtt_output_requires_the_discovered_service(self) -> None:
        options = generate_config.merged_options(
            json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        )
        options["mqtt"]["enabled"] = True

        generate_config.validate_options(options)
        with self.assertRaisesRegex(
            generate_config.ConfigurationError, "MQTT.*service.*unavailable"
        ):
            generate_config.build_config(options)

    def test_mqtt_tls_uses_service_ssl_setting(self) -> None:
        options = generate_config.merged_options(
            json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        )
        options["mqtt"]["enabled"] = True
        generate_config.validate_options(options)
        config = generate_config.build_config(
            options,
            mqtt_service={
                "host": "mqtt.example",
                "port": 8883,
                "username": "user",
                "password": "secret",
                "ssl": True,
            },
        )["config"]

        self.assertEqual(config["mqtt"][0]["protocol"], "MQTTS")

    def test_mqtt_wildcard_topic_is_rejected(self) -> None:
        options = generate_config.merged_options(
            json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        )
        options["mqtt"].update({"enabled": True, "topic": "ais/#"})

        with self.assertRaisesRegex(generate_config.ConfigurationError, "mqtt.topic"):
            generate_config.validate_options(options)

    def test_mqtt_custom_host_requires_host_and_port(self) -> None:
        options = generate_config.merged_options(
            json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        )
        options["mqtt"].update({"enabled": True, "use_ha_service": False})

        with self.assertRaisesRegex(
            generate_config.ConfigurationError, "mqtt.host.*mqtt.port"
        ):
            generate_config.validate_options(options)

    def test_mqtt_custom_host_is_accepted_without_the_discovered_service(self) -> None:
        options = generate_config.merged_options(
            json.loads((OPTIONS / "minimal.json").read_text(encoding="utf-8"))
        )
        options["mqtt"].update(
            {
                "enabled": True,
                "use_ha_service": False,
                "host": "mqtt.example.com",
                "port": 1883,
                "username": "ais-catcher",
                "password": "custom-secret",
            }
        )

        generate_config.validate_options(options)
        config = generate_config.build_config(
            options,
            mqtt_service={
                "host": "mqtt.example.com",
                "port": 1883,
                "username": "ais-catcher",
                "password": "custom-secret",
                "ssl": False,
            },
        )["config"]
        mqtt = config["mqtt"][0]

        self.assertEqual(mqtt["host"], "mqtt.example.com")
        self.assertEqual(mqtt["username"], "ais-catcher")
        self.assertEqual(mqtt["password"], "custom-secret")

    def test_load_mqtt_service_from_environment_reads_custom_host_details(self) -> None:
        environment = {
            "AIS_MQTT_HOST": "mqtt.example.com",
            "AIS_MQTT_PORT": "8883",
            "AIS_MQTT_USERNAME": "ais-catcher",
            "AIS_MQTT_PASSWORD": "custom-secret",
            "AIS_MQTT_SSL": "true",
        }
        with mock.patch.dict(os.environ, environment, clear=False):
            service = generate_config.load_mqtt_service_from_environment()

        self.assertEqual(
            service,
            {
                "host": "mqtt.example.com",
                "port": 8883,
                "username": "ais-catcher",
                "password": "custom-secret",
                "ssl": True,
            },
        )

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

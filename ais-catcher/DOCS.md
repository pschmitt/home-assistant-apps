# AIS-catcher Home Assistant app

## Installation

In Home Assistant, open **Settings → Add-ons → Add-on Store**, select the
three-dot menu, choose **Repositories**, and add:

```text
https://github.com/pschmitt/home-assistant-apps
```

Install **AIS-catcher**. The app is built for `amd64` and `aarch64`, and its
multi-architecture images are published to GHCR for Supervisor to pull. This
includes generic x86-64 systems and 64-bit Raspberry Pi Home Assistant OS
installations. The add-on has no public port mapping; its web viewer is
available through Home Assistant ingress.

## Basic configuration

The default options are suitable as a starting point:

```yaml
receiver:
  gain: auto
  ppm: 0
  rtlagc: true
  sample_rate: 1536000
  bandwidth: 192000
  channel: AB
antenna:
  enabled: false
  latitude: 0.0
  longitude: 0.0
web:
  enabled: true
nmea:
  udp_outputs: []
  tcp_outputs: []
mqtt:
  enabled: false
  use_ha_service: true
  host: ""
  port: 1883
  tls: false
  username: ""
  password: ""
  topic: ais-catcher/ais
  msgformat: JSON_FULL
  qos: 0
  client_id: ais-catcher
aishub:
  enabled: false
  host: ""
  port: 0
aiscatcher_share:
  enabled: false
  key: ""
log_level: info
```

AIS-catcher automatically selects a compatible RTL-SDR. This add-on intentionally
does not expose USB bus paths in its configuration because those paths are
transient and can change after a replug. The intended setup has one RTL-SDR
receiver attached to the Home Assistant OS host. `gain` is either
`auto` or a tuner gain in dB from 0 to 50. Start with `auto` and adjust only
after looking at the signal-level and message statistics in the web viewer.
`ppm` accepts -150 through 150. `channel: AB` covers AIS1 and AIS2 with one
RTL-SDR; `CD` is available for the alternate channel pair supported by
AIS-catcher.

`antenna.enabled` passes `antenna.latitude` and `antenna.longitude` to
AIS-catcher's native receiver-location option and to the web server's station
location. The web server's `share_loc` setting is enabled at the same time so
the viewer can calculate station range and distances. Coordinates are decimal
degrees. The option is disabled by default; enabling it exposes the receiver
position to the AIS-catcher viewer and sharing services, so consider the
privacy implications.

`log_level` is a dropdown with AIS-catcher's `debug`, `info`, `warning`,
`error`, and `critical` levels. The additional `default` choice is an explicit
add-on alias for `info`; it keeps the five actual AIS-catcher levels in a
dropdown in the current Home Assistant frontend.

The app enables AIS-catcher's native statistics output every 60 seconds. The
statistics include decoded message counts and help distinguish a quiet radio
channel from a receiver, USB, or output failure. Zero decoded messages are
expected when no vessel is transmitting within reception range; the app does
not restart the receiver merely because the count is zero.

### Community station marked as lagging

The community map can mark a station as lagging when it has not received a
recent useful AIS update from that station. In practice, a position-bearing
message is the meaningful update for the map. This is a data-age indicator,
not proof that the add-on, USB connection, or community TCP session has
failed. A quiet channel can produce this state, especially when there are no
vessels within radio range. AIS-catcher must not send fabricated messages to
keep a station looking active.

Use the following signals together when diagnosing this state:

* increasing `received` bytes and a running receiver show that RTL-SDR samples
  are still arriving;
* `total.count` and `last_minute.count` show whether AIS messages were decoded;
* `outputs[].stats.connected` and `outputs[].stats.dropped` show the state of
  the community and MQTT outputs;
* an AIS message such as type 12 may be valid traffic but has no vessel
  position, so it does not necessarily create a vessel on the map.

The first real position-bearing message from a vessel should normally clear
the inactivity symptom upstream. A single `RTLSDR: timeout.` line is an
internal sample-FIFO wait timeout and is not, by itself, evidence of a USB
failure. If `received` stops increasing, AIS-catcher reports `lost device` or
`buffer overrun`, the process restarts, or an output reports reconnects or
drops, investigate the corresponding hardware, antenna, network, or service
problem instead.

The `nmea` section contains UDP and TCP NMEA destinations, for example:

```yaml
nmea:
  udp_outputs:
    - host: 192.0.2.10
      port: 10110
  tcp_outputs:
    - host: ais-consumer.example
      port: 4001
```

These are AIS-catcher TCP clients, not TCP listeners. AISHub is also a native
AIS-catcher UDP NMEA output. Enter the host and port supplied by AISHub; the
app never fetches AISstream or any other public AIS API.

## MQTT output

The app can publish the locally decoded AIS stream over MQTT. Enable MQTT
output in the app configuration:

```yaml
mqtt:
  enabled: true
  use_ha_service: true
  topic: ais-catcher/ais
  msgformat: JSON_FULL
  qos: 0
  client_id: ais-catcher
```

By default (`use_ha_service: true`) the app declares `mqtt:want` and obtains
the broker host, port, TLS setting, username, and password from Supervisor's
MQTT service discovery. Do not enter broker credentials in the AIS-catcher
options in this mode. If no MQTT broker is available, the app continues to
work while MQTT is disabled; enabling it without a discoverable broker is a
startup error after a bounded 60-second discovery wait.

To publish to a different broker instead of the one Home Assistant
discovers — for example an external Mosquitto instance, a cloud MQTT
broker, or a second local broker — set `use_ha_service: false` and provide
the broker directly:

```yaml
mqtt:
  enabled: true
  use_ha_service: false
  host: mqtt.example.com
  port: 1883
  tls: false
  username: ais-catcher
  password: "correct-horse-battery-staple"
  topic: ais-catcher/ais
  msgformat: JSON_FULL
  qos: 0
  client_id: ais-catcher
```

`host` and `port` are required when `use_ha_service` is disabled; `username`
and `password` may be left empty for a broker that allows anonymous
connections. `tls` selects `MQTTS` instead of `MQTT` for the connection. The
`username`/`password` fields are only used in this mode — they are ignored
(and the discovered service's own credentials are used instead) when
`use_ha_service: true`.

`JSON_FULL` is the recommended format because it includes decoded fields such
as MMSI, message type, latitude, longitude, speed, and the original NMEA
sentence. `JSON_NMEA` contains common metadata and the NMEA payload, while
`NMEA` publishes the raw AIS sentence. AIS-catcher topic templates are
supported, for example `ais-catcher/vessels/%mmsi%`. MQTT wildcards (`+` and
`#`) are not valid publish topics.

This publishes only data received and decoded by the local RTL-SDR. It does
not consume AISstream or another public AIS API. Publishing MQTT messages does
not automatically create Home Assistant entities; use MQTT triggers, sensors,
or a dedicated integration if you want to model vessel data in Home Assistant.

The `aiscatcher_share` option enables the upstream `sharing` / `sharing_key`
configuration. Register the station at [aiscatcher.org](https://www.aiscatcher.org/)
to obtain a sharing key. Sharing is disabled by default.

The key field uses Home Assistant's `password` schema type and is not printed
by the startup script. It is still present in Supervisor's `/data/options.json`
and in the generated `/data/aiscatcher.json` (mode `0600`), so this is not a
replacement for a separate secrets vault. Do not paste it into bug reports or
share generated configuration files.

## Upstream and Home Assistant compatibility

This app currently builds AIS-catcher [v0.70](https://github.com/jvde-github/AIS-catcher/releases/tag/v0.70)
from a pinned commit and source archive checksum. The generator uses the
upstream version-1 JSON configuration format: `receiver` selects `rtlsdr`,
`udp` and `tcp` carry NMEA outputs, `server` enables the viewer, and `sharing`
with `sharing_key` enables the upstream community feed. The image compiles
only the RTL-SDR, web viewer, OpenSSL, and zlib integrations to keep the image
focused. It also applies one small security patch to the upstream network
startup messages so a configured community UUID is logged as `[redacted]`.
The sharing protocol and wire format remain upstream AIS-catcher behavior.

The add-on metadata is in the current `config.yaml` format. `build.yaml` is
retained as an empty compatibility file for this repository; the pinned base
images and build settings are intentionally declared in the Dockerfile. The
published image is `ghcr.io/pschmitt/{arch}-home-assistant-app-ais-catcher`.

## Connecting and checking the NESDR Smart v5

Connect the NESDR directly to the Home Assistant OS host, or use a powered USB
hub if the host cannot provide stable power. The app sets `usb: true`, which
maps Home Assistant OS's raw `/dev/bus/usb` tree into the container and allows
plug-and-play enumeration. No vendor/product ID or bus path is hardcoded;
AIS-catcher automatically selects a compatible RTL-SDR. The add-on is intended
to have one RTL-SDR receiver attached to the host.

After connecting the receiver:

1. Check host hardware from the Home Assistant CLI or Terminal/SSH app with
   `ha hardware info` where supported. For a diagnostic host shell, `lsusb`
   and `dmesg`/`journalctl -k` can confirm USB enumeration.
2. Restart the app and inspect its log. Hardware mode runs
   `AIS-catcher -l JSON on` first, then prints AIS-catcher's device initialization
   messages.
3. A successful startup identifies an RTL-SDR and continues into the receiver
   loop. `cannot find device`, `no devices available`, `cannot open device`,
   or `access denied` indicate a host/USB/driver problem, not a reception
   result.
   The periodic statistics line is the useful next check: increasing raw
   sample input with zero decoded messages indicates that the receiver is
   running but has not found valid AIS traffic; increasing message counts
   confirm decoder activity.
4. Open the app from the Home Assistant sidebar and check the receiver,
   signal, and message statistics. A map with no vessels is not by itself
   proof that the radio is broken; continue with the antenna and frequency
   checks below.

App logs can be viewed in the UI or with the Home Assistant CLI:

```sh
ha addons logs ais-catcher
ha addons info ais-catcher
```

For a repository-installed copy whose Supervisor slug is prefixed with
`local_`, use `ha addons logs local_ais-catcher` instead. The exact slug is
shown by `ha addons list` or in the add-on information page.

## Antenna and reception

AIS is received in the maritime VHF band. Use a vertically polarized antenna
designed for approximately 162 MHz, installed as high and unobstructed as is
practical, with a short, good-quality 50-ohm coax run. A marine VHF antenna
with an appropriate splitter can work, but the splitter must protect the
receiver from transmitter power. Do not connect a transmitting radio directly
to the NESDR.

Once the receiver is initialized, verify both AIS channels:

* AIS1: **161.975 MHz**
* AIS2: **162.025 MHz**

AIS-catcher's `AB` mode is intended to receive both channels around 162 MHz.
Use the web viewer's signal/drift information to tune PPM and gain. Excessive
gain can overload the tuner just as readily as too little gain can hide weak
signals.

## Web UI and ingress

The built-in AIS-catcher web viewer listens on container port 8100 when
`web.enabled` is true. Home Assistant ingress proxies that port and handles
Home Assistant authentication. No host port is published by this app.

Setting `web.enabled` to `false` deliberately disables the viewer; the
sidebar ingress entry will then be unavailable until it is enabled again.

Ingress has only been validated structurally in this repository. Its behavior
through a particular Supervisor/Frontend version should be checked on the
target Home Assistant OS system.

## Development without an SDR

The `/run.sh --no-hardware` argument is specifically for development and
configuration checks. It is not part of the Home Assistant configuration and
is never used by the production app. In this mode, the generated configuration
has an AIS-catcher `udpserver` receiver bound to `127.0.0.1:10110`. It waits
for NMEA input but does not create a radio source and does not invent traffic.

Build and run it on an amd64 development machine:

```sh
docker build --build-arg BUILD_ARCH=amd64 -t local/ais-catcher:dev ais-catcher
docker run --rm --name ais-catcher-dev \
  --publish 8100:8100 \
  --volume "$PWD/ais-catcher/tests/options/no-hardware.json:/data/options.json:ro" \
  local/ais-catcher:dev /run.sh --no-hardware
```

Open `http://127.0.0.1:8100`. The interface should load and show that no
receiver messages are arriving. This tests the image, options parsing, config
generation, and web process without claiming SDR or AIS success.

To inspect a generated configuration without Docker:

```sh
python3 ais-catcher/generate_config.py \
  --options ais-catcher/tests/options/full.json \
  --output /tmp/aiscatcher.json \
  --print-redacted
```

Production always uses the real RTL-SDR input. Without the physical device,
AIS-catcher reports that no compatible device is available and exits; this is
intentional and makes a missing receiver visible instead of creating fake
reception.

## AISHub and community sharing

For AISHub, obtain the station endpoint from AISHub and set `aishub.enabled`,
`aishub.host`, and `aishub.port`. AIS-catcher sends the locally decoded raw
NMEA output directly to that UDP endpoint. With no SDR, no AISHub packets are
generated by this app.

For the community feed, register at aiscatcher.org, put the supplied key in
`aiscatcher_share.key`, and set `aiscatcher_share.enabled` to `true`. The
upstream AIS-catcher community mechanism is used; this app does not implement
or proxy that protocol.

## Troubleshooting

### No RTL-SDR detected

Check `ha hardware info`, then inspect kernel USB logs. Restart the app after
plugging in the dongle. In the app log, AIS-catcher's `-l JSON on` output should
include the RTL-SDR. If several RTL-SDR devices are present, AIS-catcher's
automatic selection may not choose the intended one; use a single attached
RTL-SDR for this add-on.

### Permission or access failure

Confirm that the app is using the image from this repository and that its
protection setting has not been changed in a way that removes normal app
device mapping. The app requires the USB mapping supplied by `usb: true`; it
does not require full privileged mode. Replug the device and restart the app.

### MQTT output unavailable

With `mqtt.use_ha_service: true` (the default), confirm that the Mosquitto
broker app is installed and running, and that the Home Assistant MQTT
integration is configured. The app obtains the broker details through
Supervisor service discovery. If the broker cannot be discovered, the app
reports that condition and exits rather than silently dropping messages. Keep
MQTT disabled until the broker is available.

With `mqtt.use_ha_service: false`, confirm `mqtt.host` and `mqtt.port` point
at a reachable broker and that `mqtt.username`/`mqtt.password`/`mqtt.tls`
match its configuration; the app validates that `host` is non-empty and
`port` is set before starting.

The generated configuration contains the broker password. Inspect it only
with redaction enabled:

```sh
python3 /usr/bin/generate_config.py --print-redacted
```

### The kernel DVB driver claimed the RTL2832 device

On a diagnostic HAOS host shell, check `lsmod` and kernel logs for
`dvb_usb_rtl28xxu`, `rtl2832`, or related modules. Temporarily unload the
modules only when the host permits it, for example with `modprobe -r` after
stopping any service using the tuner. If the module must be blocked across
reboots, use the HAOS-supported `CONFIG/modprobe` configuration mechanism and
follow the current HAOS documentation; do not edit the container.

### No AIS packets received

First confirm device initialization, then verify the antenna is connected and
vertical, the coax and connectors are sound, and there are vessels within
radio line of sight. Try `gain: auto`, then modest fixed gain values. Verify
that PPM is reasonable and that `channel: AB` is selected. Use AIS-catcher's
web statistics and signal/drift plots; an empty map without nearby AIS traffic
is not conclusive.

### Bad gain

Overload may appear as a high noise floor and fewer valid messages. Weak gain
can produce sporadic or distant-only reception. Start with `auto` and change
one setting at a time while watching valid message counts and signal levels.

### Bad antenna or reception

Raise and clear the antenna, keep coax short, remove unnecessary splitters,
and compare reception at different times. AIS coverage is strongly dependent
on local terrain, buildings, antenna height, and nearby vessel traffic.

### Web UI unavailable

Ensure `web.enabled: true`, restart the app, and check that AIS-catcher logged
the web viewer startup on port 8100. Use the add-on page's **Open Web UI** or
sidebar ingress link; do not expect a host port because none is published.
For local Docker testing, publish `8100:8100` as shown above.

## Hardware validation checklist

The first three checks below were completed on 2026-08-31 against the physical
NESDR Smart v5 connected to the HAOS VM on `fnuc`. The remaining checks require
actual AIS traffic and are still open:

- [x] Verify USB enumeration on the Home Assistant OS host.
- [x] Verify AIS-catcher detects the RTL-SDR.
- [x] Verify AIS-catcher initializes and opens the device.
- [ ] Determine an appropriate tuner gain.
- [ ] Verify reception on AIS1, 161.975 MHz.
- [ ] Verify reception on AIS2, 162.025 MHz.
- [ ] Confirm vessels appear in AIS-catcher.
- [ ] Confirm raw NMEA output through a configured UDP or TCP destination.
- [ ] Confirm AISHub receives the station feed, if enabled.
- [ ] Confirm ingress remains functional during active reception.
- [ ] Observe CPU and memory usage on Home Assistant OS during reception.

# Changelog

## 0.1.17

- Persist the web viewer's ship and statistics state across restarts and
  updates by backing it up to the add-on's own persistent volume every 10
  minutes. Previously a restart silently discarded all runtime history;
  add-on configuration (`options.json`) is unaffected.

## 0.1.16

- Wait up to 60 seconds for Supervisor MQTT service discovery while retaining a
  clear startup failure when MQTT remains unavailable.

## 0.1.15

- Explicitly disable GPS lookup when a fixed antenna location is configured,
  keeping the station location available to the web viewer and range tools.

## 0.1.14

- Emit AIS-catcher decoder statistics every 60 seconds so quiet RF conditions
  are distinguishable from a stalled receiver or output feed.

## 0.1.13

- Enable RTL-SDR AGC by default, matching AIS-catcher's documented RTL-SDR
  starting configuration.

## 0.1.12

- Import the Supervisor-provided container environment in the s6 service so
  Bashio can authenticate MQTT service discovery.

## 0.1.11

- Use bashio's Supervisor token handling for MQTT service discovery while
  keeping transient discovery errors out of normal app logs.

## 0.1.10

- Avoid noisy Supervisor API errors while waiting for MQTT service discovery.

## 0.1.9

- Correctly handle the MQTT service's boolean SSL value during startup.

## 0.1.8

- Avoid noisy Supervisor API errors while waiting for MQTT service discovery.
- Fetch the MQTT service details in one redacted-in-memory request per retry.

## 0.1.7

- Wait for Supervisor MQTT service discovery to become available during app startup.
- Read the local MQTT enable flag directly from the Supervisor-provided options file.

## 0.1.6

- Add optional native AIS-catcher MQTT output using Home Assistant's discovered
  MQTT service.
- Publish raw NMEA or decoded JSON to a configurable topic without exposing
  broker credentials in the app configuration UI.

## 0.1.5

- Publish the configured antenna coordinates to the AIS-catcher web viewer so
  station range and distance calculations are available.

## 0.1.4

- Group UDP and TCP NMEA destinations under one `nmea` configuration section.
- Remove the transient USB device selector; AIS-catcher now auto-selects the
  attached RTL-SDR.
- Keep no-hardware execution as an explicit development-only environment
  override rather than a production add-on option.

## 0.1.3

- Add an optional antenna latitude/longitude setting using AIS-catcher's native
  receiver-location option.
- Add an optional HAOS udev rule that provides a persistent, human-readable
  `by-id` path for NESDR Smart v5 devices.
- Render the log-level choices as a dropdown by adding an explicit `default`
  alias for AIS-catcher's INFO level.

## 0.1.2

- Use Home Assistant's dynamic USB device selector for the RTL-SDR.
- Resolve the selected USB device path to its AIS-catcher serial number.
- Preserve compatibility with the pre-0.1.2 manually configured serial option.

## 0.1.1

- Use the published GHCR image instead of building the app on the Home
  Assistant host.
- Disable Supervisor's default Docker init because the base image provides
  s6-overlay.
- Add translated configuration labels and descriptions.
- Add the upstream AIS-catcher icon and logo assets.

## 0.1.0

- Initial experimental Home Assistant OS app.
- Build AIS-catcher v0.70 from a pinned upstream source commit.
- Add native RTL-SDR input, web ingress, UDP/TCP NMEA output, AISHub output,
  and optional aiscatcher.org community sharing.
- Add an explicit no-hardware development mode that does not simulate radio
  reception.

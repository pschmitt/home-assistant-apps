# Changelog

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

# Changelog

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

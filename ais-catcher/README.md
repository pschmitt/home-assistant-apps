# AIS-catcher

Receive Automatic Identification System (AIS) traffic with a USB RTL-SDR and
[AIS-catcher](https://github.com/jvde-github/AIS-catcher). The app targets
Home Assistant OS and provides the AIS-catcher web viewer through Home
Assistant ingress.

This app is currently experimental. USB device initialization has been tested
with a Nooelec NESDR Smart v5, but reception quality depends on the antenna,
location, and local AIS traffic.

See [DOCS.md](DOCS.md) for installation, configuration, troubleshooting, and
the hardware validation checklist.

The published image builds AIS-catcher v0.70 from its upstream source commit.
Only the RTL-SDR driver and built-in web viewer are enabled in the image. UDP
and TCP outputs, MQTT, AISHub, and the optional aiscatcher.org community feed
all use AIS-catcher's native output mechanisms. MQTT credentials are obtained
from Home Assistant's discovered Mosquitto service when MQTT output is enabled.

## Quick start

1. Add this repository to Home Assistant's add-on repository list:
   `https://github.com/pschmitt/home-assistant-apps`.
2. Install **AIS-catcher** from the add-on store.
3. Connect the NESDR Smart v5, attach a suitable VHF antenna, and start the
   app with the default configuration.
4. Open **AIS-catcher** from the Home Assistant sidebar.

For development without an SDR, start the image with `/run.sh --no-hardware`.
This starts the real AIS-catcher web server with an idle UDP NMEA input; it
does not emulate an RTL-SDR or generate AIS messages.

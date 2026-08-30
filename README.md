# home-assistant-apps

[![Build](https://github.com/pschmitt/home-assistant-apps/workflows/Build/badge.svg)](https://github.com/pschmitt/home-assistant-apps/actions?query=workflow%3ABuild)

Home Assistant apps by Philipp Schmitt

## AIS-catcher

The [`ais-catcher/`](ais-catcher/) app receives AIS traffic with an RTL-SDR
and the upstream AIS-catcher decoder. It supports Home Assistant ingress,
native NMEA outputs, AISHub, and optional AIS-catcher community sharing. An
explicit no-hardware development mode is available for validation before an
SDR is installed.

Add to Home Assistant using the repository url:
https://github.com/pschmitt/home-assistant-apps

[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fpschmitt%2Fhome-assistant-apps)

> [!WARNING]
> **This repository was renamed from `home-assistant-addons` to `home-assistant-apps`.**
> If you already have the old repository added to Home Assistant, please update it:
> 1. Go to [**Settings → Add-ons → Repositories**](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fpschmitt%2Fhome-assistant-apps) and remove `https://github.com/pschmitt/home-assistant-addons`
> 2. Add the new URL: `https://github.com/pschmitt/home-assistant-apps`
>    (or use the badge above)

## flicd

React to flic button presses on the Raspberry Pi.

### Installation

The flicd server needs a bluetooth controller. If you are running [Hass.io based on HassOS](https://www.home-assistant.io/blog/2018/07/11/hassio-images/), you can use the built-in controller. If you are running the older [Hass.io based on ResinOS](https://www.home-assistant.io/blog/2018/07/11/hassio-images/), you'll need to install the [Bluetooth BCM43xx](https://www.home-assistant.io/addons/bluetooth_bcm43xx/) add-on.

```text
Available HCI devices found:
hci0
Trying hci0
hci0 is busy, shutting down and retrying...
Successfully bound HCI socket
Flic server is now up and running!
Initialization of Bluetooth controller done!
```

By default, flicd is going to use `hci0` bluetooth controller. If you have multiple bluetooth controllers you can configure flicd to use another controller by specifying it in `hci_dev` configuration setting of the app.

```json
{
  "hci_dev": "hci1"
}
```

After starting the flicd app, you might need to restart Home Assistant.
Your flic buttons should be detected automatically if you keep pressing the button.

For more information, check the Home Assistant Forum at https://community.home-assistant.io/search?q=flicd or check the other community support channels at https://www.home-assistant.io/help/

### Usage

Check the [flic component page at home-assistant.io](https://www.home-assistant.io/components/binary_sensor.flic/).

## avahi-reflector

avahi-reflector to bridge mDNS.

## keepalived

[osixia/docker-keepalived](https://github.com/osixia/docker-keepalived) packaged
as a Home Assistant app.

## picamera

Expose your raspicam.

## pilight

**⚠️ DEPRECATED** Please use [another addon](https://github.com/philipp-luettecke/hassio-addons/) (or fork)

## Tailscale

[Tailscale](https://tailscale.com) VPN service. This app was originally published [here](https://github.com/tsujamin/hass-addons/tree/main/tailscale).

## Zabbix Agent

Uses zabbix-agent package from current alpine version.

## Zabbix Agent 2

Uses zabbix-agent2 package from current alpine version, also includes PostgreSQL and MongoDB plug-ins.

To access docker api it is necessary to disable protection mode.

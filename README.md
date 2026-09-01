# home-assistant-apps

[![Build](https://github.com/pschmitt/home-assistant-apps/workflows/Build/badge.svg)](https://github.com/pschmitt/home-assistant-apps/actions?query=workflow%3ABuild)

Home Assistant apps by Philipp Schmitt

Add to Home Assistant using the repository url:
https://github.com/pschmitt/home-assistant-apps

[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fpschmitt%2Fhome-assistant-apps)

> [!WARNING]
> **This repository was renamed from `home-assistant-addons` to `home-assistant-apps`.**
> If you already have the old repository added to Home Assistant, please update it:
> 1. Go to [**Settings → Add-ons → Repositories**](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fpschmitt%2Fhome-assistant-apps) and remove `https://github.com/pschmitt/home-assistant-addons`
> 2. Add the new URL: `https://github.com/pschmitt/home-assistant-apps`
>    (or use the badge above)

## [<img src="ais-catcher/icon.png" alt="" width="32" height="32" style="vertical-align: middle;">](ais-catcher/) AIS-catcher

The [`ais-catcher/`](ais-catcher/) app receives AIS traffic with an RTL-SDR
and the upstream AIS-catcher decoder. It supports Home Assistant ingress,
native NMEA outputs, AISHub, and optional AIS-catcher community sharing. An
explicit no-hardware development mode is available for validation before an
SDR is installed.

## [<img src="avahi-reflector/icon.png" alt="" width="32" height="32">](avahi-reflector/) avahi-reflector

avahi-reflector to bridge mDNS.

## [<picture><source media="(prefers-color-scheme: dark)" srcset="https://brands.home-assistant.io/flic/dark_icon.png"><img src="https://brands.home-assistant.io/flic/icon.png" alt="" width="32" height="32" style="vertical-align: middle;"></picture>](flicd/) flicd

React to Flic button presses on the Raspberry Pi. See the
[flicd documentation](flicd/README.md) for installation, configuration, and
usage instructions.

## [<img src="keepalived/icon.png" alt="" width="32" height="32">](keepalived/) keepalived

[osixia/docker-keepalived](https://github.com/osixia/docker-keepalived) packaged
as a Home Assistant app.

## picamera

Expose your raspicam.

## [<img src="https://brands.home-assistant.io/pilight/icon.png" alt="" width="32" height="32" style="vertical-align: middle;">](pilight/) pilight

**⚠️ DEPRECATED** Please use [another addon](https://github.com/philipp-luettecke/hassio-addons/) (or fork)

## [<img src="tailscale/icon.png" alt="" width="32" height="32">](tailscale/) Tailscale

[Tailscale](https://tailscale.com) VPN service. This app was originally published [here](https://github.com/tsujamin/hass-addons/tree/main/tailscale).

## [<img src="zabbix-agent/icon.png" alt="" width="32" height="32">](zabbix-agent/) Zabbix Agent

Uses zabbix-agent package from current alpine version.

## [<img src="zabbix-agent2/icon.png" alt="" width="32" height="32">](zabbix-agent2/) Zabbix Agent 2

Uses zabbix-agent2 package from current alpine version, also includes PostgreSQL and MongoDB plug-ins.

To access docker api it is necessary to disable protection mode.

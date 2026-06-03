# Home Assistant Add-on: Tailscale

## OG Source: https://github.com/tsujamin/hass-addons

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

This Add-on installs Tailscale, a zero-config VPN, enabling you to remotely 
access your Home Assistant system away from your home network.

For more information, see the Add-on documentation and
[Tailscale's website](https://tailscale.com)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

# Usage w/o Home Assistant OS (Standalone)

All the configuration options can be overridden by passing env var values.
The env var names are the same as the config options, except that they need to 
be capitalized and `-` chars are replaced with `_`.

## Example

```shell
docker run -it --rm \
  --name tailscale \
  --hostname docker-test \
  --net=host \
  --cap-add=NET_ADMIN \
  --device /dev/net/tun \
  -v $PWD/data:/data:rw \
  -e AUTHKEY=tskey-XXXXXXXX \
  -e ADVERTISE_ROUTES=192.168.1.0/24 \
  ghcr.io/pschmitt/amd64-home-assistant-app-tailscale
```

If you prefer to not use env args you can use the following form:

```shell
docker run -it --rm \
  --name tailscale \
  --hostname docker-test \
  --net=host \
  --cap-add=NET_ADMIN \
  --device /dev/net/tun \
  -v $PWD/data:/data:rw \
  ghcr.io/pschmitt/amd64-home-assistant-app-tailscale \
    --authkey=tskey-XXXXXXXX \
    --advertise-routes=192.168.1.0/24
```

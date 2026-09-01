# flicd

React to Flic button presses on the Raspberry Pi.

## Installation

The flicd server needs a Bluetooth controller. If you are running [Home
Assistant OS](https://www.home-assistant.io/installation/), you can use the
built-in controller. If you are running Home Assistant on another operating
system, make sure a compatible Bluetooth controller is available to the host
and exposed to the app.

After installing and starting the app, you might need to restart Home
Assistant. Your Flic buttons should be detected automatically if you keep
pressing the button.

## Configuration

By default, flicd uses the `hci0` Bluetooth controller. If you have multiple
Bluetooth controllers, configure another controller in the app's `hci_dev`
setting:

```json
{
  "hci_dev": "hci1"
}
```

Typical startup output looks like this:

```text
Available HCI devices found:
hci0
Trying hci0
hci0 is busy, shutting down and retrying...
Successfully bound HCI socket
Flic server is now up and running!
Initialization of Bluetooth controller done!
```

## Usage

See the [Flic integration documentation on Home Assistant](https://www.home-assistant.io/integrations/flic/).

For community support, see the [Home Assistant Community search for
flicd](https://community.home-assistant.io/search?q=flicd) or the other
[Home Assistant support channels](https://www.home-assistant.io/help/).

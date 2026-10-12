#!/usr/bin/env bash

CONFIG_PATH=/data/options.json
AVAHI_CONFIG_PATH=/etc/avahi/avahi-daemon.conf

ALLOW_INTERFACES="$(jq --raw-output '(.allow_interfaces // []) | if type == "array" then map(select(length > 0)) | join(",") elif type == "string" then . else "" end' \
                    "$CONFIG_PATH")"

# Edit avahi config
# Enable reflector, disable DBUS
sed -i -E \
  -e 's/^#?enable-reflector=.*/enable-reflector=yes/' \
  -e 's/^#?enable-dbus=.*/enable-dbus=no/' \
  "$AVAHI_CONFIG_PATH"

# Set allow-interfaces
if [[ -n "$ALLOW_INTERFACES" ]]
then
  echo "Setting allow-interfaces to $ALLOW_INTERFACES" >&2
  # Escape sed replacement metacharacters: backslash, delimiter (/), and &
  ESCAPED_INTERFACES="${ALLOW_INTERFACES//\\/\\\\}"
  ESCAPED_INTERFACES="${ESCAPED_INTERFACES//\//\\/}"
  ESCAPED_INTERFACES="${ESCAPED_INTERFACES//&/\\&}"

  sed -i -E \
    -e 's/^#?allow-interfaces=.*/allow-interfaces='"${ESCAPED_INTERFACES}"'/' \
    "$AVAHI_CONFIG_PATH"
else
  echo "No allow-interfaces specified, allowing all interfaces" >&2
  sed -i -E \
    -e 's/^allow-interfaces=/#allow-interfaces=/' \
    "$AVAHI_CONFIG_PATH"
fi

{
  echo "$ grep -v '^#' $AVAHI_CONFIG_PATH"
  grep -v '^#' "$AVAHI_CONFIG_PATH" | grep -v '^$' || true
} >&2

exec avahi-daemon

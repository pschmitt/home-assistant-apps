#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
APP_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
readonly APP_DIR

main() {
  python3 "${SCRIPT_DIR}/test_config.py"
  python3 -m json.tool "${SCRIPT_DIR}/options/minimal.json" >/dev/null
  python3 -m json.tool "${SCRIPT_DIR}/options/full.json" >/dev/null
  python3 -m json.tool "${SCRIPT_DIR}/options/no-hardware.json" >/dev/null
  python3 -m json.tool "${SCRIPT_DIR}/options/no-hardware-sharing.json" >/dev/null
  python3 -m json.tool "${SCRIPT_DIR}/options/mqtt.json" >/dev/null
  yq '.' "${APP_DIR}/config.yaml" >/dev/null
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
  main "$@"
fi

# vim: set ft=sh et ts=2 sw=2 :

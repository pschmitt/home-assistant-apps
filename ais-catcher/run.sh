#!/usr/bin/env bash

set -Eeuo pipefail

readonly OPTIONS_PATH=/data/options.json
readonly CONFIG_PATH=/data/aiscatcher.json

usage() {
  cat <<EOF
Usage: $(basename "$0") [--no-hardware]

Run AIS-catcher with the Home Assistant options in ${OPTIONS_PATH}.
The --no-hardware mode is for local development only.
EOF
}

main() {
  local summary mode log_level antenna_enabled antenna_latitude antenna_longitude
  local no_hardware
  local -a ais_args generator_args

  while [[ -n "${1:-}" ]]
  do
    case "$1" in
      -h|--help)
        usage
        return 0
        ;;
      --no-hardware)
        no_hardware=1
        shift
        ;;
      *)
        printf 'AIS-catcher: unknown option: %s\n' "$1" >&2
        usage >&2
        return 2
        ;;
    esac
  done

  if [[ ! -r "${OPTIONS_PATH}" ]]
  then
    printf 'AIS-catcher: %s is missing or unreadable.\n' "${OPTIONS_PATH}" >&2
    return 2
  fi

  generator_args=(
    --options "${OPTIONS_PATH}"
    --output "${CONFIG_PATH}"
  )
  if [[ -n "${no_hardware:-}" ]]
  then
    generator_args+=(--no-hardware)
  fi
  summary="$(python3 /usr/bin/generate_config.py "${generator_args[@]}")"
  IFS='|' read -r mode log_level antenna_enabled antenna_latitude antenna_longitude <<< "${summary}"

  printf 'AIS-catcher: generated configuration (%s mode, log level %s).\n' \
    "${mode}" "${log_level}"

  if [[ "${mode}" == "hardware" ]]
  then
    printf 'AIS-catcher: RTL-SDR access is required; no SDR data is simulated.\n'
    printf 'AIS-catcher: enumerating devices before starting the receiver:\n'
    if ! /usr/bin/AIS-catcher -l JSON on
    then
      printf 'AIS-catcher: device enumeration command failed; receiver startup will show the cause.\n' >&2
    fi
  else
    printf 'AIS-catcher: no-hardware mode uses an idle UDP NMEA input on 127.0.0.1:10110.\n'
    printf 'AIS-catcher: no radio reception or fabricated AIS data will be produced.\n'
  fi

  ais_args=(
    -G LEVEL "${log_level^^}"
    -C "${CONFIG_PATH}"
  )
  if [[ "${antenna_enabled}" == true ]]
  then
    printf 'AIS-catcher: receiver antenna location is %s, %s.\n' \
      "${antenna_latitude}" "${antenna_longitude}"
    ais_args+=(
      -Z "${antenna_latitude}" "${antenna_longitude}"
    )
  fi
  exec /usr/bin/AIS-catcher "${ais_args[@]}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
  main "$@"
fi

# vim: set ft=sh et ts=2 sw=2 :

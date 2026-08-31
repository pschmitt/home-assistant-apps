#!/usr/bin/env bash

set -Eeuo pipefail

readonly OPTIONS_PATH=/data/options.json
readonly CONFIG_PATH=/data/aiscatcher.json

main() {
  local summary mode log_level
  local -a ais_args

  if [[ ! -r "${OPTIONS_PATH}" ]]
  then
    printf 'AIS-catcher: %s is missing or unreadable.\n' "${OPTIONS_PATH}" >&2
    return 2
  fi

  summary="$(python3 /usr/bin/generate_config.py \
    --options "${OPTIONS_PATH}" \
    --output "${CONFIG_PATH}")"
  IFS='|' read -r mode log_level <<< "${summary}"

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
  exec /usr/bin/AIS-catcher "${ais_args[@]}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
  main "$@"
fi

# vim: set ft=sh et ts=2 sw=2 :

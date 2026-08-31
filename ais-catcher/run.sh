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
  local mqtt_enabled mqtt_host mqtt_port mqtt_username mqtt_password mqtt_ssl
  local mqtt_service_ready
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

  # shellcheck disable=SC1091
  if ! source /usr/lib/bashio/bashio.sh
  then
    printf 'AIS-catcher: cannot load Home Assistant service helpers.\n' >&2
    return 2
  fi

  if ! mqtt_enabled="$(jq --raw-output '.mqtt.enabled // false' "${OPTIONS_PATH}")"
  then
    printf 'AIS-catcher: cannot read mqtt.enabled from %s.\n' "${OPTIONS_PATH}" >&2
    return 2
  fi
  if [[ "${mqtt_enabled}" == true ]]
  then
    mqtt_service_ready=false
    for attempt in {1..30}
    do
      if bashio::services.available mqtt
      then
        mqtt_service_ready=true
        break
      fi
      if (( attempt < 30 ))
      then
        sleep 1
      fi
    done
    if [[ "${mqtt_service_ready}" != true ]] \
      || ! mqtt_host="$(bashio::services mqtt 'host')" \
      || ! mqtt_port="$(bashio::services mqtt 'port')" \
      || ! mqtt_username="$(bashio::services mqtt 'username')" \
      || ! mqtt_password="$(bashio::services mqtt 'password')" \
      || ! mqtt_ssl="$(bashio::services mqtt 'ssl')"
    then
      printf 'AIS-catcher: MQTT is enabled, but the Home Assistant MQTT service is unavailable after waiting 30 seconds.\n' >&2
      printf 'AIS-catcher: install/start the Mosquitto broker or disable mqtt.enabled.\n' >&2
      return 2
    fi
    export AIS_MQTT_HOST="${mqtt_host}"
    export AIS_MQTT_PORT="${mqtt_port}"
    export AIS_MQTT_USERNAME="${mqtt_username}"
    export AIS_MQTT_PASSWORD="${mqtt_password}"
    export AIS_MQTT_SSL="${mqtt_ssl}"
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

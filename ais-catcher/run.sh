#!/usr/bin/with-contenv bash
# shellcheck shell=bash

set -Eeuo pipefail

readonly OPTIONS_PATH=/data/options.json
readonly CONFIG_PATH=/data/aiscatcher.json
readonly MQTT_SERVICE_ATTEMPTS=60

usage() {
  cat <<EOF
Usage: $(basename "$0") [--no-hardware]

Run AIS-catcher with the Home Assistant options in ${OPTIONS_PATH}.
The --no-hardware mode is for local development only.
EOF
}

get_mqtt_service()
{
  local quiet_log_fd result

  # bashio owns the Supervisor token and API endpoint.  Keep its retry errors
  # out of the normal app log while the Supervisor is still becoming ready.
  exec {quiet_log_fd}>/dev/null
  # shellcheck disable=SC2034 # LOG_FD is consumed by the sourced bashio library.
  LOG_FD="${quiet_log_fd}"
  if bashio::services mqtt
  then
    result=0
  else
    result=$?
  fi
  exec {quiet_log_fd}>&-
  return "${result}"
}

main() {
  local summary mode log_level antenna_enabled antenna_latitude antenna_longitude
  local mqtt_enabled mqtt_use_ha_service mqtt_host mqtt_port mqtt_username
  local mqtt_password mqtt_ssl
  local mqtt_service mqtt_service_ready
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
    if ! mqtt_use_ha_service="$(jq --raw-output '.mqtt.use_ha_service // true' "${OPTIONS_PATH}")"
    then
      printf 'AIS-catcher: cannot read mqtt.use_ha_service from %s.\n' "${OPTIONS_PATH}" >&2
      return 2
    fi
    if [[ "${mqtt_use_ha_service}" == true ]]
    then
      mqtt_service_ready=false
      for ((attempt = 1; attempt <= MQTT_SERVICE_ATTEMPTS; attempt++))
      do
        if mqtt_service="$(get_mqtt_service 2>/dev/null)" \
          && mqtt_host="$(jq --raw-output --exit-status '.host // empty' <<< "${mqtt_service}")" \
          && mqtt_port="$(jq --raw-output --exit-status '.port // empty' <<< "${mqtt_service}")" \
          && mqtt_username="$(jq --raw-output '.username // empty' <<< "${mqtt_service}")" \
          && mqtt_password="$(jq --raw-output '.password // empty' <<< "${mqtt_service}")" \
          && mqtt_ssl="$(jq --raw-output '.ssl | tostring' <<< "${mqtt_service}")" \
          && [[ "${mqtt_ssl}" == true || "${mqtt_ssl}" == false ]]
        then
          mqtt_service_ready=true
          break
        fi
        if (( attempt < MQTT_SERVICE_ATTEMPTS ))
        then
          sleep 1
        fi
      done
      if [[ "${mqtt_service_ready}" != true ]]
      then
        printf 'AIS-catcher: MQTT is enabled, but the Home Assistant MQTT service is unavailable after waiting %s seconds.\n' \
          "${MQTT_SERVICE_ATTEMPTS}" >&2
        printf 'AIS-catcher: install/start the Mosquitto broker, disable mqtt.enabled, or configure a custom MQTT host.\n' >&2
        return 2
      fi
    else
      if ! mqtt_host="$(jq --raw-output '.mqtt.host // empty' "${OPTIONS_PATH}")"
      then
        printf 'AIS-catcher: cannot read mqtt.host from %s.\n' "${OPTIONS_PATH}" >&2
        return 2
      fi
      if [[ -z "${mqtt_host}" ]]
      then
        printf 'AIS-catcher: mqtt.enabled is set with mqtt.use_ha_service disabled, but mqtt.host is empty.\n' >&2
        return 2
      fi
      mqtt_port="$(jq --raw-output '.mqtt.port // 1883' "${OPTIONS_PATH}")"
      mqtt_username="$(jq --raw-output '.mqtt.username // empty' "${OPTIONS_PATH}")"
      mqtt_password="$(jq --raw-output '.mqtt.password // empty' "${OPTIONS_PATH}")"
      mqtt_ssl="$(jq --raw-output '.mqtt.tls // false | tostring' "${OPTIONS_PATH}")"
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
    -v 60
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

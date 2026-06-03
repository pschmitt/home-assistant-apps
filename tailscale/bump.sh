#!/usr/bin/env bash

usage() {
  echo "Usage: $(basename "$0") [--check] [VERSION]"
}

current_version() {
  jq -er .version ./config.json
}

latest_version() {
  curl -fsSL "https://api.github.com/repos/tailscale/tailscale/releases/latest" | \
    jq -er '.tag_name | sub("^v"; "")'
}

static_binary_available() {
  local version="$1"
  curl -fsI "https://pkgs.tailscale.com/stable/tailscale_${version}_amd64.tgz" > /dev/null 2>&1
}

new_version_available() {
  local current_version
  local latest_version

  current_version="$(current_version)"
  latest_version="$(latest_version)"

  if [[ "$current_version" == "$latest_version" ]]; then
    return 1
  fi

  if ! static_binary_available "$latest_version"; then
    echo "Static binary for $latest_version not yet available, skipping" >&2
    return 1
  fi

  return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
  set -eo pipefail

  cd "$(cd "$(dirname "$0")" >/dev/null 2>&1; pwd -P)" || exit 9

  case "$1" in
    help|h|-h|--help)
      usage
      exit 0
      ;;
    --check)
      CHECK_ONLY=1
      shift
      ;;
  esac

  # Handle --check flag
  if [[ -n "$CHECK_ONLY" ]]
  then
    if new_version_available
    then
      echo "New version is available"
      exit 1
    fi

    echo "Already on latest version: $(current_version)"
    exit 0
  fi

  VERSION="${1:-$(latest_version)}"

  if [[ -z "$VERSION" ]]
  then
    echo "Missing version number" >&2
    exit 2
  fi

  CURRENT_VERSION="$(current_version)"

  if [[ "$CURRENT_VERSION" == "$VERSION" ]]
  then
    echo "Version is already $VERSION" >&2
    exit 1
  fi

  TMPFILE="$(mktemp)"

  # patch build.json
  jq -er --arg v "$VERSION" '.args.TAILSCALE_VERSION = $v' build.json > "$TMPFILE"
  mv "$TMPFILE" build.json

  # patch config.json
  jq -er --arg v "$VERSION" '.version = $v' config.json > "$TMPFILE"
  mv "$TMPFILE" config.json

  # Update changelog
  cat > "$TMPFILE" <<EOF
  # $VERSION
  - Update tailscale to $VERSION

EOF
  cat ./CHANGELOG.md >> "$TMPFILE"
  mv "$TMPFILE" ./CHANGELOG.md

  git status
  git add build.json config.json CHANGELOG.md
  git diff --cached
fi

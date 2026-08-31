# syntax=docker/dockerfile:1

ARG AIS_CATCHER_COMMIT=8833c64b3da0c42e9a724b9bd13eaab2fffadcca
ARG AIS_CATCHER_SOURCE_SHA256=597ec260638d55e51d4aea5aeccd8b4a8d9f514a1bdf637870363def645eba3c

FROM docker.io/library/debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171 AS build

ARG AIS_CATCHER_COMMIT
ARG AIS_CATCHER_SOURCE_SHA256

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install --no-install-recommends --yes \
    ca-certificates \
    cmake \
    curl \
    g++ \
    libssl-dev \
    libusb-1.0-0-dev \
    librtlsdr-dev \
    make \
    patch \
    pkg-config \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/ais-catcher

RUN curl --fail --silent --show-error --location \
    "https://github.com/jvde-github/AIS-catcher/archive/${AIS_CATCHER_COMMIT}.tar.gz" \
    --output /tmp/ais-catcher.tar.gz \
  && printf '%s  %s\n' "${AIS_CATCHER_SOURCE_SHA256}" /tmp/ais-catcher.tar.gz \
    > /tmp/ais-catcher.sha256 \
  && sha256sum --check --strict /tmp/ais-catcher.sha256 \
  && tar --extract --gzip --file /tmp/ais-catcher.tar.gz --strip-components=1 \
  && rm /tmp/ais-catcher.sha256 /tmp/ais-catcher.tar.gz

COPY patches/redact-uuid-from-network-logs.patch /tmp/redact-uuid-from-network-logs.patch

RUN patch --strip=1 < /tmp/redact-uuid-from-network-logs.patch \
  && rm /tmp/redact-uuid-from-network-logs.patch

RUN cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/opt/ais-catcher \
    -DRTLSDR=ON \
    -DWEBVIEWER=ON \
    -DOPENSSL=ON \
    -DZLIB=ON \
    -DAIRSPY=OFF \
    -DAIRSPYHF=OFF \
    -DHACKRF=OFF \
    -DHYDRASDR=OFF \
    -DNMEA2000=OFF \
    -DPSQL=OFF \
    -DSAMPLERATE=OFF \
    -DSDRPLAY=OFF \
    -DSOAPYSDR=OFF \
    -DSOXR=OFF \
    -DSQLITE=OFF \
    -DZMQ=OFF \
  && cmake --build build --parallel \
  && cmake --install build

FROM ghcr.io/home-assistant/base-debian:bookworm@sha256:60cd882d5200157082e568a0b775cca0d9cb5704452ada3cf6f206c4dd6d83c5

ARG BUILD_VERSION=0.1.7
ARG BUILD_ARCH

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}" \
  org.opencontainers.image.title="AIS-catcher Home Assistant app" \
  org.opencontainers.image.source="https://github.com/pschmitt/home-assistant-apps/tree/main/ais-catcher"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install --no-install-recommends --yes \
    ca-certificates \
    libssl3 \
    libusb-1.0-0 \
    librtlsdr0 \
    python3 \
    zlib1g \
  && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/ais-catcher/bin/AIS-catcher /usr/bin/AIS-catcher
COPY generate_config.py /usr/bin/generate_config.py
COPY run.sh /run.sh

RUN chmod 0755 /usr/bin/AIS-catcher /usr/bin/generate_config.py /run.sh

CMD ["/run.sh"]

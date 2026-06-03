FROM debian:bullseye-slim

ARG BUILD_ARCH
ARG BUILD_VERSION
ARG FLICD_VERSION=${BUILD_VERSION}

LABEL maintainer="Philipp Schmitt <philipp@schmitt.co>"

RUN apt-get update && \
    # Dependencies
    apt-get install -y git jq && \
    case $(arch) in \
        x86_64|amd64) export ARCH=x86_64 ;; \
        i386) export ARCH=i386 ;; \
        armv6l|armv7l) export ARCH=armv6l ;; \
        aarch64) export ARCH=aarch64 ;; \
    esac && \
    # Flicd
    git clone --depth 1 -b "${FLICD_VERSION}" \
        https://github.com/50ButtonsEach/fliclib-linux-hci \
        /tmp/src && \
    cp "/tmp/src/bin/${ARCH}/flicd" /usr/bin/flicd && \
    chmod +x /usr/bin/flicd && \
    # Cleanup
    mkdir /config && \
    rm -rf /tmp/src && \
    apt-get remove --purge -y git && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

COPY run.sh /run.sh

WORKDIR /data
VOLUME ["/data"]
EXPOSE 5551
ENTRYPOINT ["/run.sh"]

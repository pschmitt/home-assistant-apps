FROM debian:bullseye-slim

ARG BUILD_ARCH
ARG BUILD_VERSION

LABEL maintainer="Philipp Schmitt <philipp@schmitt.co>"

RUN apt-get update && \
    apt-get install -y apt-transport-https wget gnupg jq && \
    echo "deb [trusted=yes] https://apt.pilight.org/ stable main" > /etc/apt/sources.list.d/pilight.list && \
    wget -O - https://apt.pilight.org/pilight.key | apt-key add - && \
    apt-get update && \
    if [ "$(uname -m)" = armv7l ]; \
    then \
      wget -O /tmp/libmbedx509-0_2.6.0-1_armhf.deb http://apt.pilight.org/pool/stable/main/l/libmbedx509-0/libmbedx509-0_2.6.0-1_armhf.deb && \
      wget -O /tmp/libmbedtls10_2.6.0-1_armhf.deb http://apt.pilight.org/pool/stable/main/l/libmbedtls10/libmbedtls10_2.6.0-1_armhf.deb && \
      wget -O /tmp/libmbedcrypto0_2.6.0-1_armhf.deb http://apt.pilight.org/pool/stable/main/l/libmbedcrypto0/libmbedcrypto0_2.6.0-1_armhf.deb && \
      dpkg -i /tmp/libmbed*.deb && \
      rm -rf /tmp/libmbed*.deb; \
    fi && \
    apt-get install -y pilight && \
    apt-get remove -y --purge wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY pilight-config.json /etc/pilight/config.json
COPY run.sh /run.sh

EXPOSE 5000/tcp 5001/tcp

ENTRYPOINT ["/run.sh"]

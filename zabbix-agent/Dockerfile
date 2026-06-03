FROM alpine:edge

ARG BUILD_ARCH
ARG BUILD_VERSION

LABEL org.opencontainers.image.authors="Philipp Schmitt <philipp@schmitt.co>, Lukas Magauer <lukas@magauer.eu>" \
      org.opencontainers.image.url="https://github.com/pschmitt/home-assistant-apps/tree/main/zabbix-agent" \
      org.opencontainers.image.title="Zabbix Agent image for Home Assistant Add-on" \
      org.opencontainers.image.base.name="alpine"

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --no-cache jq "zabbix-agent=~7.4"

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

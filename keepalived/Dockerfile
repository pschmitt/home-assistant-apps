FROM osixia/keepalived

ARG BUILD_ARCH
ARG BUILD_VERSION

LABEL maintainer="Philipp Schmitt <philipp@schmitt.co>"

ENV LANG=C.UTF-8

# Install requirements for add-on
RUN apk add --no-cache jq

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

ENTRYPOINT [ "/run.sh" ]

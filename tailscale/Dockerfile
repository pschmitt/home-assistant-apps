FROM alpine

ARG BUILD_ARCH
ARG TAILSCALE_VERSION

LABEL maintainer "Philipp Schmitt <philipp@schmitt.co>"

ENV LANG C.UTF-8

# Install dependencies
RUN apk add --no-cache bash jq iptables ip6tables

# Download and install tailscale to /bin from
# https://pkgs.tailscale.com/stable/#static
COPY install.sh /
RUN chmod a+x /install.sh && /install.sh ${BUILD_ARCH} ${TAILSCALE_VERSION}

COPY run.sh /run.sh
RUN chmod a+x /run.sh
ENTRYPOINT ["/run.sh"]

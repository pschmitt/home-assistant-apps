FROM alpine

ENV LANG=C.UTF-8

COPY avahi-daemon.conf /etc/avahi/avahi-daemon.conf
COPY run.sh /run.sh

RUN apk add --no-cache avahi bash jq && chmod +x /run.sh

CMD ["/run.sh"]

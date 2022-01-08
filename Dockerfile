FROM alpine:3.15.0

LABEL authors="Pascal Höhnel"

RUN apk update \
  && rm -rf /tmp/* /var/cache/apk/*
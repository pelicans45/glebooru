#FROM python:3.11.1-alpine3.17
FROM mgesoftware/python3.11-base:latest
WORKDIR /opt/app

ARG PUID=1000
ARG PGID=1000

COPY requirements.txt /tmp/

RUN apk --no-cache add \
    build-base \
    libheif \
    libheif-dev \
    libavif \
    libavif-dev \
    ffmpeg \
    && pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && apk --no-cache del py3-pip \
    && rm /tmp/requirements.txt \
    && apk --no-cache add \
    dumb-init \
    && mkdir -p /opt/app /data \
    && addgroup -g ${PGID} app \
    && adduser -SDH -h /opt/app -g '' -G app -u ${PUID} app \
    && chown -R app:app /opt/app /data

ARG CACHE_DATE=2016-01-01

COPY ./ /opt/app/
RUN rm -rf /opt/app/szurubooru/tests

CMD ["/opt/app/docker-start.sh"]

USER app
ARG PORT=6666
ENV PORT=${PORT}
EXPOSE ${PORT}

ARG THREADS=4
ENV THREADS=${THREADS}

VOLUME ["/data/"]

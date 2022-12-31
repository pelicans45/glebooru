FROM python:3.11.1-alpine3.17 as prereqs
WORKDIR /opt/app

ARG PUID=1000
ARG PGID=1000

RUN apk del .python-rundeps \
    && apk add --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main python3-dev=3.11.1-r2 \
    && apk --no-cache add \
    python3-dev \
    py3-pip \
    build-base \
    libheif \
    libheif-dev \
    libavif \
    libavif-dev \
    ffmpeg \
    # from requirements.txt:
    py3-yaml \
    py3-psycopg2 \
    py3-sqlalchemy \
    py3-certifi \
    py3-numpy \
    py3-pillow \
    py3-pynacl \
    py3-tz \
    py3-pyrfc3339 \
    && pip3 install --no-cache-dir --disable-pip-version-check \
    "alembic>=0.8.5" \
    "coloredlogs==5.0" \
    "pyheif==0.6.1" \
    "heif-image-plugin>=0.3.2" \
    youtube_dl \
    "pillow-avif-plugin>=1.1.0" \
    && apk --no-cache del py3-pip \
    && apk --no-cache add \
    dumb-init \
    py3-setuptools \
    py3-waitress \
    && mkdir -p /opt/app /data \
    && addgroup -g ${PGID} app \
    && adduser -SDH -h /opt/app -g '' -G app -u ${PUID} app \
    && chown -R app:app /opt/app /data

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

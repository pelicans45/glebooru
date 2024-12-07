FROM python:3.12.4-slim-bookworm
WORKDIR /opt/app

ARG PUID=1000
ARG PGID=1000

RUN apt-get update && apt-get install -y \
    build-essential \
    libheif1 \
    libheif-dev \
    libavif15 \
    libavif-dev \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

RUN mkdir -p /opt/app /data \
    && addgroup --gid ${PGID} app \
    && useradd -u ${PUID} -g app -d /opt/app app \
    && chown -R app:app /opt/app /data

COPY . ./
RUN rm -rf /opt/app/szurubooru/tests

RUN chown -R app /opt/app && chmod +x /opt/app/docker-start.sh

USER app
ARG PORT=6666
ENV PORT=${PORT}
EXPOSE ${PORT}

ARG THREADS=4
ENV THREADS=${THREADS}

CMD ["/opt/app/docker-start.sh"]
#CMD ["/opt/app/app.py"]
VOLUME ["/data"]

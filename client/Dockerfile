FROM node:lts as builder
WORKDIR /opt/app

COPY package.json package-lock.json ./
RUN npm install

ARG CACHE_DATE=2016-01-01

COPY . ./

RUN BASE_URL="__BASEURL__" node build.js --gzip


FROM scratch as approot

COPY docker-start.sh /

WORKDIR /etc/nginx
COPY nginx.conf.docker ./nginx.conf

WORKDIR /var/www
COPY --from=builder /opt/app/public/ .


FROM nginx:alpine as release

RUN apk --no-cache add dumb-init
COPY --from=approot / /

CMD ["/docker-start.sh"]
VOLUME ["/data"]

ARG DOCKER_REPO
ARG BUILD_DATE
ARG SOURCE_COMMIT

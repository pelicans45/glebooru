FROM node:lts as builder
WORKDIR /opt/app

ENV GLEBOORU_DEV=1

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

RUN node build.js --gzip


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

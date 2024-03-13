FROM node:lts-alpine3.18
WORKDIR /opt/app

ENV GLEBOORU_DEV=1

RUN apk --no-cache add nginx dumb-init
COPY nginx.docker.conf /etc/nginx/nginx.conf
RUN rm -rf /var/www && ln -s /opt/app/public /var/www

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

RUN node build.js --gzip

RUN ls -ahltr /var/www/

CMD ["./docker-start.sh"]
VOLUME ["/data"]

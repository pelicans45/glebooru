FROM node:22-bookworm-slim
WORKDIR /opt/app

ENV GLEBOORU_DEV=1

RUN apt-get update && apt-get install -y nginx && apt-get clean && rm -rf /var/lib/apt/lists
COPY nginx.docker.conf /etc/nginx/nginx.conf
RUN rm -rf /var/www && mkdir /var/www

COPY package.json package-lock.json ./
RUN npm install --include=dev

COPY . ./

RUN node build.js

CMD ["./docker-start.sh"]
VOLUME ["/data"]

FROM node:22.4.0-bookworm-slim
WORKDIR /opt/app

ARG DEV
ENV GLEBOORU_DEV=${DEV}

RUN apt-get update && apt-get install -y nginx && apt-get clean && rm -rf /var/lib/apt/lists
COPY nginx.docker.conf /etc/nginx/nginx.conf
RUN rm -rf /var/www && mkdir /var/www

COPY package.json package-lock.json ./
RUN npm install --include=dev

COPY . ./

RUN node build.js

ENTRYPOINT ["/bin/bash"]
CMD ["./docker-start.sh"]
VOLUME ["/data"]

#!/usr/bin/dumb-init /bin/sh
set -e

mkdir -p /tmp/nginx-cache
chmod a+rwx /tmp/nginx-cache

# Integrate environment variables
sed -i "s|__BACKEND__|${BACKEND_HOST}|" \
    /etc/nginx/nginx.conf

if [ "$GLEBOORU_WATCH" == "1" ]; then
    node build.js --watch --skip-init &
fi

# Start server
exec nginx

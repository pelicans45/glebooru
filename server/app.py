#!/usr/bin/env python3
import fastwsgi
import logging

from szurubooru.facade import app

host = "0.0.0.0"
port = 6666

#fastwsgi.server.num_workers = 2

if __name__ == "__main__":
    logging.info(f"Starting server on http://{host}:{port}")
    fastwsgi.run(wsgi_app=app, host=host, port=port)

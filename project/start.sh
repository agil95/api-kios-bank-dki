#!/bin/bash
cd /
export FLASK_APP=project
# export FLASK_DEBUG=1
# export FLASK_RUN_HOST=0.0.0.0
# export FLASK_RUN_PORT=5000
# flask run --with-threads
gunicorn --conf project/gunicorn_conf.py --bind 0.0.0.0:5000 "project:create_app()"
#!/bin/bash
cd /home/kios/Documents/Api_Kios_Pelabuhan
export FLASK_APP=project
export FLASK_DEBUG=1
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
flask run --with-threads
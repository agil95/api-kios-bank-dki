# import necessary modul
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# ======================================
from datetime import timedelta
import os


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
key = '68c6dfdec843af1818707293ff394c50'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__, static_folder="static")
    # set CORS
    CORS(app)
    # CORS(app, resources={r"/api/*": {"origins": "*"}})

    # set Key App
    app.config['SECRET_KEY'] = key

    # SQLITE Connection
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # MYSQL Connection
    # userpass = 'mysql+pymysql://root:@'
    # basedir = '127.0.0.1'
    # dbname = '/kios_pelabuhan'
    # socket = '?unix_socket=/opt/lampp/var/mysql/mysql.sock'
    # dbname = dbname + socket

    userpass = 'mysql+pymysql://root:root@'
    basedir = '127.0.0.1'
    dbname = '/kios_pelabuhan'
    socket = '?unix_socket=/var/run/mysqld/mysqld.sock'
    dbname = dbname + socket
    app.config['SQLALCHEMY_DATABASE_URI'] = userpass + basedir + dbname
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False

    db.init_app(app)

    # Register The Blueprint Model
    # blueprint for non-auth parts of app
    from .controllers.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .controllers.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app

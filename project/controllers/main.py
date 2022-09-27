from dataclasses import dataclass
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import Date, cast
from datetime import datetime, timedelta
# from .models import Log, Config
# from . import db
import json


main = Blueprint('main', __name__)


@main.route('/index')
@main.route('/')
def index():
    data = {
        'pageTitle': 'Home',
        'title': 'Selamat Datang di Kios'
    }
    return render_template('index.html', data=data)


@main.route('/destination')
def destination():
    data = {
        'pageTitle': 'Pilih Tujuan',
        'title': 'Tiket Kapal'
    }
    return render_template('pages/destination.html', data=data)

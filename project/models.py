from email.policy import default
from flask_login import UserMixin
from datetime import datetime

from project.controllers.main import destination
from . import db
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER, BIGINT, ENUM


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(BIGINT(20, unsigned=True), primary_key=True)
    email = db.Column(VARCHAR(255), unique=True)
    password = db.Column(VARCHAR(255))
    name = db.Column(VARCHAR(255))
    username = db.Column(VARCHAR(255), unique=True)
    status = db.Column(ENUM("ACTIVE", "INACTIVE"))
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


class LogUang(db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(BIGINT(20, unsigned=True), primary_key=True)
    customer = db.Column(VARCHAR(100), nullable=False)
    income = db.Column(BIGINT(20), default=0)
    status = db.Column(VARCHAR(100))
    verify_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)
    description = db.Column(TEXT, nullable=True)

    def __init__(self, id, customer, income, status, verify_at, description):
        self.id = id
        self.customer = customer
        self.income = income
        self.status = status
        self.verify_at = verify_at
        self.description = description

    @property
    def serialize(self):
        return {
            "id": self.id,
            "customer": self.customer,
            "income": self.income,
            "status": self.status,
            "verify_at": self.verify_at,
            "description": self.description
        }


class LogTransaction(db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(BIGINT(20, unsigned=True), primary_key=True)
    ref_number = db.Column(VARCHAR(255), nullable=False)
    booking_code = db.Column(VARCHAR(100), nullable=False)
    passanger_code = db.Column(VARCHAR(100), nullable=False)
    passanger = db.Column(VARCHAR(255))
    origin = db.Column(VARCHAR(255))
    departure_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)
    destination = db.Column(VARCHAR(255))
    arrive_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)
    status = db.Column(VARCHAR(255))
    price = db.Column(BIGINT(20))
    money_changes = db.Column(BIGINT(20), nullable=True)
    description = db.Column(TEXT, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)
    ticket_type = db.Column(ENUM("Pergi", "Pulang"))

    def __init__(self, id, ref_number, booking_code, passanger_code, passanger, origin, departure_at, 
                destination, arrive_at, status, price, money_changes, description, paid_at, ticket_type):
        self.id = id
        self.ref_number = ref_number
        self.booking_code = booking_code
        self.passanger_code = passanger_code
        self.passanger = passanger
        self.origin = origin
        self.departure_at = departure_at
        self.destination = destination
        self.arrive_at = arrive_at
        self.status = status
        self.price = price
        self.money_changes = money_changes
        self.description = description
        self.paid_at = paid_at
        self.ticket_type = ticket_type

    @property
    def serialize(self):
        return {
            "id": self.id,
            "ref_number": self.ref_number,
            "booking_code": self.booking_code,
            "passanger_code": self.passanger_code,
            "passanger": self.passanger,
            "origin": self.origin,
            "departure_at": self.departure_at,
            "destination": self.destination,
            "arrive_at": self.arrive_at,
            "status": self.status,
            "price": self.price,
            "money_changes": self.money_changes,
            "description": self.description,
            "paid_at": self.paid_at,
            "ticket_type": self.ticket_type
        }


class Config(db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(BIGINT(20, unsigned=True), primary_key=True)
    port_device_1 = db.Column(VARCHAR(255))
    baudrate_device_1 = db.Column(INTEGER(11))
    port_device_2 = db.Column(VARCHAR(255))
    baudrate_device_2 = db.Column(INTEGER(11))
    header_1 = db.Column(VARCHAR(255))
    header_2 = db.Column(VARCHAR(255))
    header_3 = db.Column(VARCHAR(255))
    footer_1 = db.Column(VARCHAR(255))
    status = db.Column(VARCHAR(255))
    description = db.Column(TEXT, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # serializer fields
    # create_fields = update_fields = ['manless', 'server_1', 'key_1', 'server_2',
    #                                  'key_2', 'port', 'baudrate', 'timeout_scan', 'status', 'description', 'created_at']

    def __init__(self, id, port_device_1, baudrate_device_1, port_device_2, baudrate_device_2, header_1, header_2, header_3, footer_1, status, description, created_at):
        self.id = id
        self.port_device_1 = port_device_1
        self.baudrate_device_1 = baudrate_device_1
        self.port_device_2 = port_device_2
        self.baudrate_device_2 = baudrate_device_2
        self.header_1 = header_1
        self.header_2 = header_2
        self.header_3 = header_3
        self.footer_1 = footer_1
        self.status = status
        self.description = description
        self.created_at = created_at

    def dump_datetime(value):
        """Deserialize datetime object into string form for JSON processing."""
        if value is None:
            return None
        return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'port_device_1': self.port_device_1,
            'baudrate_device_1': self.baudrate_device_1,
            'port_device_2': self.port_device_2,
            'header_1': self.header_1,
            'header_2': self.header_2,
            'header_3': self.header_3,
            'footer_1': self.footer_1,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at,
        }

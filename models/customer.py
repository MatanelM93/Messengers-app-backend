from typing import List
from requests import Response
from flask import url_for, request

from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel
from db import db
from uuid import uuid4


class CustomerModel(db.Model):
    __tablename__ = "customers"

    # columns -
    id = db.Column(db.String(40), primary_key=True)  # auto increment id
    first_name = db.Column(db.String(40), nullable=False)  # must
    last_name = db.Column(db.String(40), nullable=False)  # must
    email = db.Column(db.String(80), nullable=False, unique=True)  # must!
    password = db.Column(db.String(80), nullable=False)  # must!
    phone_1 = db.Column(db.String(15), nullable=False)  # must
    phone_2 = db.Column(db.String(15))
    message = db.Column(db.String(255))

    # relationships - every new user gets confirmation model, and must own an address.
    address = db.relationship(
        "AddressModel", lazy="dynamic", cascade="all, delete-orphan"  # fk - address
    )
    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"  # user confirmation relationship
    )

    def __init__(self, first_name: str, last_name: str, email: str, password: str, phone_1: str,
                 phone_2: str = None, message: str = None):
        self.id = uuid4().hex
        self.first_name = first_name  # must!
        self.last_name = last_name  # must!
        self.email = email  # must!
        self.password = password  # must!
        self.phone_1 = phone_1  # must!
        self.phone_2 = phone_2 if phone_2 else None
        self.message = message if message else None

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        # returns the latest confirmation model that was given to the customer
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def send_confirmation_email(self) -> Response:
        # this function handles the parameters required for email sending via Mailgun

        subject = "Registration Confirmation"  # name of the mail subject
        link = request.url_root[:-1] + url_for(
            "customerconfirmation", confirmation_id=self.most_recent_confirmation.id  # this url will confirm the user
        )
        text = f"Please click the link to confirm your registration {link}"  # actual text - for plain text
        html = f'<html>Please click the link to confirm your registration <a href="{link}">link</a>'  # for text/html

        return Mailgun.send_email([self.email], subject, text, html)

    @classmethod
    def find_by_id(cls, _id: str) -> "CustomerModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email: str) -> "CustomerModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_all(cls) -> List["CustomerModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()



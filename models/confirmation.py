from typing import List
from uuid import uuid4
from time import time

from db import db

CONFIRMATION_EXPIRATION_DELTA = 1800  # 30 minutes


class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"

    # columns -
    id = db.Column(db.String(50), primary_key=True)  # auto increment id
    expire_at = db.Column(db.Integer, nullable=False)  # must!
    confirmed = db.Column(db.Boolean, nullable=False)  # must!
    customer_id = db.Column(db.String(40), db.ForeignKey("customers.id"), nullable=False)  # must!

    # relationship - every customer gets a confirmation model on registration
    customer = db.relationship("CustomerModel")  # fk - customer_id

    def __init__(self, customer_id: int, **kwargs):
        # generating a confirmation model by customer id
        super().__init__(**kwargs)
        self.customer_id = customer_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA  # timeout set to 30min from creation
        self.confirmed = False  # initial confirmation is at false state

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["ConfirmationModel"]:
        return cls.query.all()

    @property
    def expired(self) -> bool:  # if confirmation expired, return false
        return time() > self.expired_at

    def force_to_expire(self) -> None:  # if generating new confirmation, should force current confirmation to expire
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

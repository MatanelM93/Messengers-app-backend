from uuid import uuid4

from db import db
from typing import List


class StoreModel(db.Model):
    __tablename__ = "stores"

    # columns -
    id = db.Column(db.String(40), primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)  # must!
    password = db.Column(db.String(80), nullable=False)  # must!
    phone1 = db.Column(db.String(15), nullable=False)  # must!
    phone2 = db.Column(db.String(15))

    def __init__(self, email: str, password: str, phone1: str, phone2=None):
        self.id = uuid4().hex
        self.email = email  # must!
        self.password = password  # must!
        self.phone1 = phone1  # must!
        self.phone2 = phone2 if phone2 else None

    @classmethod
    def find_by_id(cls, _id: int) -> "StoreModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email: int) -> "StoreModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_all(cls) -> List["StoreModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

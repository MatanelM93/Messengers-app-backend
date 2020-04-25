from typing import List

from db import db


class AddressModel(db.Model):
    __tablename__ = "address"

    # columns -
    id = db.Column(db.Integer, primary_key=True)  # auto increment id
    city = db.Column(db.String(40), nullable=False)  # must!
    street = db.Column(db.String(80), nullable=False)  # must!
    number = db.Column(db.Integer, nullable=False)  # must!
    postal = db.Column(db.Integer, nullable=False)  # must!
    entrance = db.Column(db.String(2))
    floor = db.Column(db.Integer)
    apartment = db.Column(db.Integer)
    customer_id = db.Column(db.String(40), db.ForeignKey("customers.id"), nullable=False)  # must!

    # relationship with -
    customer = db.relationship("CustomerModel")  # fk - customer_id

    def __init__(self, city: str, street: str, number: int, postal: int, customer_id: str,
                 entrance: str = None, floor: int = None, apartment: int = None, **kwargs):
        super().__init__(**kwargs)
        self.city = city
        self.street = street
        self.number = number
        self.postal = postal
        self.customer_id = customer_id
        self.entrance = entrance if entrance else None
        self.floor = floor if floor else None
        self.apartment = apartment if apartment else None

    @classmethod
    def find_by_id(cls, _id) -> "AddressModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["AddressModel"]:
        return cls.query.all()

    @classmethod
    def find_by_city(cls, city: str) -> List["AddressModel"]:
        return cls.query.filter_by(city=city)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
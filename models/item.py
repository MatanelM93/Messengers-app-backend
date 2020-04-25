from db import db
from typing import List


class ItemModel(db.Model):
    __tablename__ = "items"

    # columns -
    id = db.Column(db.Integer, primary_key=True)  # auto increment id
    category = db.Column(db.String(50), nullable=False)  # must!
    name = db.Column(db.String(80), nullable=False, unique=True)  # must! + unique
    price = db.Column(db.Float, nullable=False)  # must!

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "ItemModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["ItemModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

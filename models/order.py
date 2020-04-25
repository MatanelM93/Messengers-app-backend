import os
from typing import List, Union
import stripe

from db import db
from models.item import ItemModel

CURRENCY = "usd"


class StoreOrderModel(db.Model):
    __tablename__ = "store_orders"

    # columns -
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))  # must!
    store_id = db.Column(db.String(40), db.ForeignKey("stores.id"))  # must!

    # relationships with -
    orders = db.relationship("OrderModel")  # fk - order_id
    stores = db.relationship("StoreModel")  # fk - store_id

    def __init__(self, order_id: int, store_id: str, **kwargs):
        super().__init__(**kwargs)
        self.order_id = order_id  # must!
        self.store_id = store_id  # must!

    @classmethod
    def find_by_store_id(cls, store_id: str) -> List["StoreOrderModel"]:
        return cls.query.filter_by(store_id=store_id)

    @classmethod
    def find_by_order_id(cls, order_id) -> "StoreOrderModel":
        return cls.query.filter_by(order_id=order_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()


class ItemsInOrder(db.Model):
    __tablename__ = "items_in_order"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    quantity = db.Column(db.Integer)

    # relationship with the tables -
    item = db.relationship("ItemModel")  # fk - item_id field
    order = db.relationship("OrderModel", back_populates="items")  # fk - order_id field

    @classmethod
    def find_by_id(cls, _id: int) -> "ItemsInOrder":
        return cls.query.filter_by(id=_id).first()


class OrderModel(db.Model):
    __tablename__ = "orders"

    # fields -
    id = db.Column(db.Integer, primary_key=True)  # auto increment id
    status = db.Column(db.String(20), nullable=False)  # statused are : pending, picked, stumbled, delivered
    customer_id = db.Column(db.String(40), db.ForeignKey("customers.id"), nullable=False)  # must!
    message = db.Column(db.String(255))
    items = db.relationship("ItemsInOrder", back_populates="order")  # must!

    # relationship with the tables -
    customers = db.relationship("CustomerModel")  # fk - customer_id field

    @property
    def order_items(self) -> List['ItemsInOrder']:
        return [ItemsInOrder.find_by_id(item.id) for item in self.items]

    @property
    def amount(self):
        return int(sum([ItemModel.find_by_id(item_data.item_id).price * item_data.quantity for item_data in self.items]) * 100)

    @classmethod
    def find_by_id(cls, _id: int) -> "OrderModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["OrderModel"]:
        return cls.query.all()

    @classmethod
    def find_customer_order(cls, customer_id: str) -> "OrderModel":
        return cls.query.filter_by(customer_id=customer_id).first()

    @classmethod
    def find_customer_pending_order(cls, customer_id: str) -> Union["OrderModel", None]:
        base = cls.query.filter_by(customer_id=customer_id)
        order = base.filter_by(status="pending").first()
        if order:
            return order
        order = base.filter_by(status="picked").first()
        if order:
            return order
        order = base.filter_by(status="stumbled").first()
        if order:
            return order
        return None

    @classmethod
    def find_customer_completed_orders(cls, customer_id: str) -> List["OrderModel"]:
        return cls.query.filter_by(customer_id=customer_id).filter_by(status="delivered")

    @classmethod
    def is_item_in_order(cls, _id: int, item_id: int) -> bool:
        if cls.query.filter_by(id=_id).filter_by(item_id=item_id).first():
            return True
        return False

    def charge_with_stripe(self, token: str) -> stripe.Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        return stripe.Charge.create(
            amount=self.amount,  # amount of cents (100 means USD$1.00)
            currency=CURRENCY,
            description=self.message,
            source=token
        )

    def set_status(self, new_status: str) -> None:
        self.status = new_status
        self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

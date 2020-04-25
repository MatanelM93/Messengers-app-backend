from ma import ma
from models.order import OrderModel, ItemsInOrder


class OrderSchema(ma.ModelSchema):
    class Meta:
        model = OrderModel


class ItemsInOrderSchema(ma.ModelSchema):
    class Meta:
        model = ItemsInOrder
        load_only = ("id", "order_id", "order")  # these column will be loaded only, and not dumped

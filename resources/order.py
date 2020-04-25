from collections import Counter
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from typing import List

from libs.util import store_method, customer_method
from models.customer import CustomerModel
from models.item import ItemModel
from models.order import OrderModel, ItemsInOrder, StoreOrderModel
from models.store import StoreModel
from schemas.order import OrderSchema, ItemsInOrderSchema

order_schema = OrderSchema()
item_in_order_schema = ItemsInOrderSchema()


HAS_ONE_ORDER_ALREADY = "Customer will not be able to hold over one order"
ITEM_ID_NOT_FOUND = "Item id: {} not found"
CUSTOMER_NOT_FOUND = "Unauthorized user"
ORDER_NOT_FOUND = "Order not found"
ERROR_DELETING_ORDER = "Could not perform object deletion"
SUCCESS_DELETING_ORDER = "Order has been completely deleted"
ERROR_PICKING_ORDER = "Error occurred while picking the order"
UNAUTHORIZED_REQUEST = "You are not authorized for this request"
SUCCESS_PICKING_ORDER = "Order has been successfully picked"
ERROR_UPDATING_ORDER = "Could not perform object update"
SUCCESS_UPDATING_ORDER = "Order has been successfully updated"
ORDER_PICKED_ALREADY = "Order has been already managed by a messenger"


class Order(Resource):
    method_decorators = {'get': [customer_method],
                         'post': [customer_method],
                         'delete': [customer_method],
                         'put': [customer_method]}

    @classmethod
    @jwt_required
    def get(cls):
        customer_id = get_jwt_identity()
        order = OrderModel.find_customer_pending_order(customer_id)

        if not order:
            return {"message": ORDER_NOT_FOUND}, 404

        items = fetching_order(order.order_items)
        message = order.message
        return {'id': order.id, 'status': order.status, 'items': items, 'message': message}, 200

    @classmethod
    @jwt_required
    def post(cls):
        data = request.get_json()
        items = []
        item_id_quantities = Counter(data["item_ids"])

        customer_id = get_jwt_identity()

        if OrderModel.find_customer_pending_order(customer_id):
            return {"message": HAS_ONE_ORDER_ALREADY}, 400

        for _id, count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": ITEM_ID_NOT_FOUND.format(_id)}, 404
            items.append(ItemsInOrder(item_id=_id, quantity=count))

        message = data['message']
        order = OrderModel(items=items, status="pending", customer_id=customer_id, message=message)
        order.charge_with_stripe(data["token"])
        order.save_to_db()

        return order_schema.dump(order)

    @classmethod
    @jwt_required
    def delete(cls):
        customer_id = get_jwt_identity()
        order = OrderModel.find_customer_pending_order(customer_id)
        if not order:
            return {"message": ORDER_NOT_FOUND}, 404

        try:
            order.delete_from_db()
        except:
            return {"message": ERROR_DELETING_ORDER}, 500

        return {"message": SUCCESS_DELETING_ORDER}, 200

    @classmethod
    @jwt_required
    def put(cls):
        customer_id = get_jwt_identity()
        order = OrderModel.find_customer_pending_order(customer_id)

        if not order:
            return {"message": ORDER_NOT_FOUND}, 404

        order.set_status("delivered")
        try:
            order.save_to_db()
        except:
            return {"message": ERROR_UPDATING_ORDER}, 500
        return {"message": SUCCESS_UPDATING_ORDER}, 200


class OrderList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        uid = get_jwt_identity()
        orders = []

        if StoreModel.find_by_id(uid):
            for order in OrderModel.find_all():
                if order.status == 'pending':
                    items = fetching_order(order.order_items)
                    message = order.message
                    orders.append({'id': order.id, 'status': order.status, 'items': items, 'message': message})
            return orders, 200
        elif CustomerModel.find_by_id(uid):
            for order in OrderModel.find_customer_completed_orders(customer_id=uid):
                items = fetching_order(order.order_items)
                message = order.message
                orders.append({'id': order.id, 'items': items, 'message': message})
            return orders, 200
        return 401


class StoreOrder(Resource):
    method_decorators = {'get': [customer_method]}

    @classmethod
    @jwt_required
    def get(cls):
        customer_id = get_jwt_identity()
        order = OrderModel.find_customer_pending_order(customer_id)
        store_order = StoreOrderModel.find_by_order_id(order.id)
        store = StoreModel.find_by_id(store_order.store_id)
        store_data = {"email": store.email, "phone1": store.phone1}
        if store.phone2:
            store_data['phone2'] = store.phone2
        return store_data, 200


class StoreOrderList(Resource):
    method_decorators = {'get': [store_method],
                         'post': [store_method],
                         'delete': [store_method],
                         'put': [store_method]}

    @classmethod
    @jwt_required
    def get(cls):
        store_id = get_jwt_identity()
        orders_id = StoreOrderModel.find_by_store_id(store_id)
        orders = []
        for store_order in orders_id:
            order = OrderModel.find_by_id(store_order.id)
            items = fetching_order(order.order_items)
            message = order.message
            orders.append({'id': order.id, 'status': order.status, 'items': items, 'message': message})

        return orders

    @classmethod
    @jwt_required
    def post(cls):
        store_id = get_jwt_identity()
        data = request.get_json()
        order = OrderModel.find_by_id(data['id'])
        if not order:
            return {"message": ORDER_NOT_FOUND}, 404
        if order.status != "pending":
            return {"message": ORDER_PICKED_ALREADY}, 400
        order.set_status("picked")

        store_order = StoreOrderModel(store_id=store_id, order_id=order.id)
        try:
            order.save_to_db()
            store_order.save_to_db()
        except:
            return {"message": ERROR_PICKING_ORDER}, 500

        return {"message": SUCCESS_PICKING_ORDER}, 200

    @classmethod
    @jwt_required
    def delete(cls):
        pass

    @classmethod
    @jwt_required
    def put(cls):
        data = request.get_json()
        order = OrderModel.find_by_id(data['id'])
        order.set_status("stumbled")
        try:
            order.save_to_db()
        except:
            return {"message": ERROR_UPDATING_ORDER}, 500

        return {"message": SUCCESS_UPDATING_ORDER}, 200


def fetching_order(order_items: List["ItemsInOrder"]) -> List[dict]:
    items = []
    for item in order_items:
        item_in_order = item_in_order_schema.dump(item)
        quantity = item_in_order['quantity']
        item_name = ItemModel.find_by_id(item_in_order['item']).name
        items.append({"name": item_name, "quantity": quantity})
    return items

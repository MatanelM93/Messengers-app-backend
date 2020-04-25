from flask_restful import Api

from resources.address import Address
from resources.item import Item, ItemList, AddAllItems
from resources.store import Store, StoreList, StoreRegister, StoreLogin
from resources.customer import (
    Customer,
    CustomerList,
    CustomerRegister,
    CustomerLogin,
    CustomerLogout,
    TokenRefresh,
    CustomerConfirmation,
    CustomerType,
)
from resources.order import Order, OrderList, StoreOrderList, StoreOrder
from resources.confirmation import Confirmation, ConfirmationList

from app import app


class Routes(object):
    api = Api(app)

    def routes(self):
        # call this method to add the routes to the application
        self.api.add_resource(Item, '/item/<string:name>')
        self.api.add_resource(ItemList, '/items')
        self.api.add_resource(AddAllItems, '/add_all_items')
        self.api.add_resource(Store, '/store/<string:_id>')
        self.api.add_resource(StoreList, '/stores')
        self.api.add_resource(StoreRegister, '/store/register')
        self.api.add_resource(StoreLogin, '/store/login')
        self.api.add_resource(Customer, '/customer/<string:_id>')
        self.api.add_resource(CustomerRegister, '/customer/register')
        self.api.add_resource(CustomerLogin, '/customer/login')
        self.api.add_resource(CustomerList, '/customers')
        self.api.add_resource(CustomerLogout, '/logout')
        self.api.add_resource(CustomerConfirmation, '/customerconfirmation/<string:confirmation_id>')
        self.api.add_resource(TokenRefresh, '/refresh')
        self.api.add_resource(Order, '/order')
        self.api.add_resource(OrderList, '/orders')
        self.api.add_resource(StoreOrderList, '/store/orders')
        self.api.add_resource(StoreOrder, '/info-order')
        self.api.add_resource(Confirmation, '/confirmation')
        self.api.add_resource(ConfirmationList, '/confirmations')
        self.api.add_resource(CustomerType, '/type')
        self.api.add_resource(Address, '/address/<int:_id>')

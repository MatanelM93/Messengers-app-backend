import functools
from flask_jwt_extended.view_decorators import _decode_jwt_from_request
from flask_restful import abort

from models.store import StoreModel
from models.customer import CustomerModel

from admins import ADMINS


UNAUTHORIZED_REQUEST = "Unauthorized request"


def customer_method(func):
    @functools.wraps(func)
    def validate_customer(*args, **kwargs):
        jwt_data = _decode_jwt_from_request(request_type='access')
        uid = jwt_data[0]['identity']
        if CustomerModel.find_by_id(uid):
            return func(*args, **kwargs)
        abort(401)

    return validate_customer


def store_method(func):
    @functools.wraps(func)
    def validate_store(*args, **kwargs):
        jwt_data = _decode_jwt_from_request(request_type='access')
        uid = jwt_data[0]['identity']
        if StoreModel.find_by_id(uid):
            return func(*args, **kwargs)
        abort(401)

    return validate_store


def admin_method(func):
    @functools.wraps(func)
    def validate_admin(*args, **kwargs):
        jwt_data = _decode_jwt_from_request(request_type='access')
        uid = jwt_data[0]['identity']
        admin_email = StoreModel.find_by_id(uid).email
        if admin_email in ADMINS:
            return func(*args, **kwargs)
        abort(401)

    return validate_admin


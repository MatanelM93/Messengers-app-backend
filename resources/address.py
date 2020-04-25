from flask import request
from flask_restful import Resource

from libs.util import admin_method
from models.address import AddressModel
from schemas.address import AddressSchema

address_schema = AddressSchema()

ADDRESS_NOT_FOUND = "Address not found"
ERROR_SAVING_ADDRESS = "Could not perform address saving"


class Address(Resource):
    method_decorators = {'get': [admin_method],
                         'post': [admin_method],
                         'delete': [admin_method],
                         'put': [admin_method]}

    @classmethod
    def get(cls, _id):
        address = AddressModel.find_by_id(_id)
        if address:
            return address_schema.dump(address), 200
        return {"message": ADDRESS_NOT_FOUND}, 404

    @classmethod
    def post(cls, _id):
        data = request.get_json()
        address = address_schema.load(data)
        try:
            address.save_to_db()
        except:
            return {"message": ERROR_SAVING_ADDRESS}, 500

    @classmethod
    def delete(cls, _id):
        pass

    @classmethod
    def put(cls, _id):
        pass

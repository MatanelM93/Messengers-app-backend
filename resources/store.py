from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import safe_str_cmp

from libs.util import admin_method
from models.store import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()


STORE_NOT_FOUND = "Store not found"
ERROR_EMAIL_EXISTS = "Store email is already exists."
ERROR_ID_EXISTS = "Store id is already exists."
IDENTIFICATION_ERROR = "Store credentials are incorrect"
ERROR_SAVING_STORE = "Could not perform store save"
SUCCESS_SAVING_STORE = "Store has been successfully saved"
SUCCESS_LOGOUT = "Logged out successfully"
ERROR_DELETING_STORE = "Could not perform store deletion"
SUCCESS_DELETING_STORE = "Store deleted completely"


class StoreRegister(Resource):
    method_decorators = {'post': [admin_method]}

    @classmethod
    def post(cls):
        data = request.get_json()
        store = store_schema.load(data)
        if StoreModel.find_by_email(store.email):
            return {"message": ERROR_EMAIL_EXISTS}, 400

        try:
            store.save_to_db()
        except:
            return {"message": ERROR_SAVING_STORE}, 500

        return store_schema.dump(store)


class StoreLogin(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        store_data = {
            'email': data['email'],
            'password': data['password']
        }
        store = StoreModel.find_by_email(store_data['email'])

        if store and safe_str_cmp(store_data['password'], store.password):
            access_token = create_access_token(identity=store.id, fresh=True)
            refresh_token = create_refresh_token(store.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": IDENTIFICATION_ERROR}, 400


class StoreTokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def get(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=True)
        return {"access_token": new_token}, 200


class Store(Resource):
    method_decorators = {'get': [admin_method],
                         'post': [admin_method],
                         'delete': [admin_method],
                         'put': [admin_method]}

    @classmethod
    @jwt_required
    def get(cls, _id: str):
        store = StoreModel.find_by_id(_id)
        if store:
            return store_schema.dump(store), 200
        return { "message": STORE_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls, _id: str):
        if StoreModel.find_by_id(_id):
            return {"message": ERROR_ID_EXISTS}, 400

        data = request.get_json()
        if StoreModel.find_by_email(data["email"]):
            return {"message": "Store email already exists"}, 400

        store = store_schema.load(data)

        try:
            store.save_to_db()
        except:
            return {"message": "Error saving store"}, 500

        return store_schema.dump(store)

    @classmethod
    @jwt_required
    def delete(cls, _id: str):
        store = StoreModel.find_by_id(_id)
        if not store:
            return {"message" : STORE_NOT_FOUND}, 404

        try:
            store.delete_from_db()
        except:
            return {"message": ERROR_DELETING_STORE}, 500

        return {"message": SUCCESS_DELETING_STORE}, 200

    @classmethod
    @jwt_required
    def update(cls, _id: str):
        pass


class StoreList(Resource):
    method_decorators = {'get': [admin_method]}

    @classmethod
    @jwt_required
    def get(cls):
        return [store_schema.dump(store) for store in StoreModel.find_all()]

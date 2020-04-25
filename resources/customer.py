import traceback

from flask_restful import Resource
from flask import request, render_template, make_response, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from werkzeug.security import safe_str_cmp

from libs.util import admin_method
from models.address import AddressModel
from models.confirmation import ConfirmationModel
from models.customer import CustomerModel
from models.store import StoreModel
from schemas.customer import CustomerSchema
from blacklist import BLACKLIST

customer_schema = CustomerSchema()

ERROR_ID_EXISTS = "Customer id is already exists"
ERROR_EMAIL_EXISTS = "Customer email is already exists"
USER_REGISTERED = "Customer registered successfully, please click the link in your mailbox to verify your email address"
ERROR_SAVING_USER = "Could not perform user deletion"
SUCCESS_SAVING_USER = "Customer has been saved successfully"
ERROR_USER_CONFIRMATION = "Customer has not been confirmed, please check your email box"
IDENTIFICATION_ERROR = "Customer credentials are incorrect"
USER_LOGGED_OUT = "Customer logged out successfully"
CUSTOMER_NOT_FOUND = "Customer not found"
SUCCESS_DELETING_CUSTOMER = "Customer deleted successfully"
ERROR_DELETING_CUSTOMER = "Could not perform customer deletion"


class CustomerRegister(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        if CustomerModel.find_by_email(data["email"]):
            return {"message": ERROR_EMAIL_EXISTS}, 400

        address_data = data['address']
        data.pop('address', None)
        user = customer_schema.load(data)
        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            address = AddressModel(**address_data, customer_id=user.id)
            address.save_to_db()
            confirmation.save_to_db()
            link = request.url_root[:-1] + url_for(
                "customerconfirmation", confirmation_id=user.most_recent_confirmation.id
            )  # support for emails foreign to Mailgun
        except:
            traceback.print_exc()
            return {"message": ERROR_SAVING_USER}, 500

        user.send_confirmation_email()
        return {"message": USER_REGISTERED, "confirmation_link": link}, 200


class CustomerLogin(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        user_data = {
            "email": data['email'],
            "password": data['password']
        }
        user = CustomerModel.find_by_email(user_data['email'])
        if user and safe_str_cmp(user.password, user_data['password']):  # confirm password matching
            is_confirmed = user.most_recent_confirmation.confirmed  # true for confirmed email, else false
            if is_confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return { "access_token": access_token, "refresh_token": refresh_token}, 200  # successful login
            return {"message": ERROR_USER_CONFIRMATION}, 400  # user not confirmed his email
        return {"message": IDENTIFICATION_ERROR}, 400  # user password or email not matched


class CustomerLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": USER_LOGGED_OUT}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def get(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=True)
        return {"access_token": new_token}, 200


class Customer(Resource):
    method_decorators = {'get': [admin_method],
                         'post': [admin_method],
                         'delete': [admin_method],
                         'put': [admin_method]}

    @classmethod
    def get(cls, _id: str):
        customer = CustomerModel.find_by_id(_id)
        if customer:
            return customer_schema.dump(customer), 200
        return {"message": CUSTOMER_NOT_FOUND}, 404

    @classmethod
    def post(cls, _id: str):
        if CustomerModel.find_by_id(_id):
            return {"message": ERROR_ID_EXISTS}, 400

        data = request.get_json()
        if CustomerModel.find_by_email(data["email"]):
            return {"message": ERROR_EMAIL_EXISTS}, 400

        customer = customer_schema.load(data)
        try:
            customer.save_to_db()
        except:
            return {"message": ERROR_SAVING_USER}, 500

        return {"message": SUCCESS_SAVING_USER}, 200

    @classmethod
    def delete(cls, _id: str):
        customer = CustomerModel.find_by_id(_id)
        if not customer:
            return {"message": CUSTOMER_NOT_FOUND}, 404
        try:
            customer.delete_from_db()
        except:
            return {"message": ERROR_DELETING_CUSTOMER}, 500

        return {"message": SUCCESS_DELETING_CUSTOMER}, 200

    @classmethod
    def update(cls, _id: str):
        pass


class CustomerConfirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        user = CustomerModel.find_by_id(confirmation.customer_id)
        if not user:
            return {"message": CUSTOMER_NOT_FOUND}, 404

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Context-Type": "text/html"}
        return make_response(render_template("confirmed.html"), 200, headers)


class CustomerList(Resource):
    @classmethod
    def get(cls):
        return [customer_schema.dump(customer) for customer in CustomerModel.find_all()]


class CustomerType(Resource):
    # this end point returns the type of the user
    @classmethod
    @jwt_required
    def get(cls):
        uid = get_jwt_identity()
        if CustomerModel.find_by_id(uid):
            return {"type": "customer"}, 200
        store = StoreModel.find_by_id(uid)
        if store:
            return {"type": "messenger"}, 200
        return {"message": CUSTOMER_NOT_FOUND}, 404

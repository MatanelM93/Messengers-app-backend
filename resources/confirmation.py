from flask_restful import Resource
from flask import request, make_response, render_template

from libs.util import admin_method
from models.confirmation import ConfirmationModel
from schemas.confirmation import ConfirmationSchema


confirmation_schema = ConfirmationSchema()

CONFIRMATION_NOT_FOUND = "Not found"
CONFIRMATION_EXPIRED = "Expired"
CONFIRMATION_ALREADY_CONFIRMED = "Already confirmed"


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": CONFIRMATION_NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": CONFIRMATION_EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": CONFIRMATION_ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type":"text/html"}
        return make_response(render_template(
            "confirmed.html"
        ), 200, headers)


class ConfirmationList(Resource):
    method_decorators = {'get': [admin_method]}
    @classmethod
    def get(cls):
        return [confirmation_schema.dump(confirmation) for confirmation in ConfirmationModel.find_all()]

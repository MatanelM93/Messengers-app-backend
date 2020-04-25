from flask_restful import Resource
from flask import request
import csv

from libs.util import admin_method
from models.item import ItemModel
from schemas.item import ItemSchema


item_schema = ItemSchema()

ADDED_ITEMS_TABLE = "Items has been added"
ERROR_INSERTING_ITEM = "item error inserting"
ITEM_NOT_FOUND = "Item not found"
ERROR_NAME_EXISTS = "item name exists"


class Item(Resource):
    method_decorators = {'post': [admin_method],
                         'delete': [admin_method],
                         'put': [admin_method]}

    @classmethod
    def get(cls, name:str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    def post(cls, name:str):
        if ItemModel.find_by_name(name):
            return {"message": ERROR_NAME_EXISTS}, 400
        data = request.get_json()
        data["name"] = name

        item = item_schema.load(data)

        try:
            item.save_to_db()
        except:
            return { "message": ERROR_INSERTING_ITEM}, 500

        return item_schema.dump(item), 200

    @classmethod
    def delete(cls, id):
        pass

    @classmethod
    def put(cls, name):
        pass


class ItemList(Resource):
    @classmethod
    def get(cls):
        return [item_schema.dump(item) for item in ItemModel.find_all()]


class AddAllItems(Resource):
    # this endpoint initialize items table
    @classmethod
    def post(cls):
        with open('C:/Users/MatanelM/PycharmProjects/COVID-19/libs/food.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item = ItemModel(**row)
                if ItemModel.find_by_name(item.name):
                    return {"message": "Item {} is already exists".format(item.name)}, 400
                item.save_to_db()
        return {"message": ADDED_ITEMS_TABLE}, 200

from ma import ma
from models.store import StoreModel


class StoreSchema(ma.ModelSchema):
    class Meta:
        model = StoreModel
        load_only = ("password",)  # store password column will be loaded only, and not dumped
        dump_only = ("id",)  # store id will be dumped only, and not loaded

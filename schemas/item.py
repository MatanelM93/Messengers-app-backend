from ma import ma
from models.item import ItemModel


class ItemSchema(ma.ModelSchema):
    class Meta:
        model = ItemModel
        dump_only = ("id",)  # these column will be dumped only, and not loaded
        include_fk = True

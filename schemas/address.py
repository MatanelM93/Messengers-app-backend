from ma import ma
from models.address import AddressModel


class AddressSchema(ma.ModelSchema):
    class Meta:
        model = AddressModel
        load_only = ("customer", )  # this field is only for loading the data, not for dumping
        dump_only = ("id",)  # this field is only for dumping data, and not for loading

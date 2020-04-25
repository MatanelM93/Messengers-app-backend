from ma import ma
from models.customer import CustomerModel


class CustomerSchema(ma.ModelSchema):
    class Meta:
        model = CustomerModel
        load_only = ("password", )  # this value should be loaded only, and not be dumped
        dump_only = ("id", "confirmation")  # these columns will be dumped only, and not loaded

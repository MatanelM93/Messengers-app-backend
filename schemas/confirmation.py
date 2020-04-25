from ma import ma
from models.confirmation import ConfirmationModel


class ConfirmationSchema(ma.ModelSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",)  # this value is only for loading, and should not be dumped when asking the data
        dump_only = ("id", "expired_at", "confirmed")   # this data is only for dumping, and should not be loaded
        include_fk = True

from db import db


class ZipcodeModel(db.Model):
    __tablename__ = "zipcodes"

    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.Integer)
    lat = db.Column(db.Float(precision=3))
    lng = db.Column(db.Float(precision=3))

    # items = db.relationship(
    #     "ItemModel", lazy="dynamic"
    # )  # back references storeid foreign key in ItemModel. Knows that this is a list (one to many)

    def __init__(self, zipcode, lat, lng):
        self.zipcode = zipcode
        self.lat = lat
        self.lng = lng

    def json(self):
        return {"zipcode": self.zipcode, "lat": self.lat, "lng": self.lng}
        # "items": [item.json() for item in self.items.all()],
        # lazy=dynamic and .all() here means items list will get created only when json() method is called

    @classmethod
    def find_by_name(cls, zipcode):
        # this line replaces everything below
        return cls.query.filter_by(zipcode=zipcode).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

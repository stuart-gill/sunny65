from db import db


class ZipcodeModel(db.Model):
    __tablename__ = "zipcodes"

    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.String, unique=True)
    lat = db.Column(db.Float(precision=6))
    lng = db.Column(db.Float(precision=5))

    campsites = db.relationship("CampsiteModel", secondary="travel_time")

    # items = db.relationship(
    #     "ItemModel", lazy="dynamic"
    # )  # back references storeid foreign key in ItemModel. Knows that this is a list (one to many)

    def __init__(self, zipcode, lat, lng):
        self.zipcode = zipcode
        self.lat = lat
        self.lng = lng

    def json(self):
        return {
            "zipcode": self.zipcode,
            "lat": self.lat,
            "lng": self.lng,
            "campsites_with_computed_travel_times": {
                "count": len(self.campsites),
                "campsites": [
                    campsite.json_without_forecasts() for campsite in self.campsites
                ],
            },
        }
        # "items": [item.json() for item in self.items.all()],
        # lazy=dynamic and .all() here means items list will get created only when json() method is called

    @classmethod
    def find_by_zipcode(cls, zipcode):
        return cls.query.filter_by(zipcode=zipcode).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            print("duplicate zipcode entry detected!")

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

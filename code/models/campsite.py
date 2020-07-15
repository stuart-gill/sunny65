from db import db


class CampsiteModel(db.Model):
    __tablename__ = "campsites"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    lat = db.Column(db.Float(precision=3))
    lng = db.Column(db.Float(precision=3))
    weather_url = db.Column(db.String)
    weather_forecast = db.Column(db.String)

    zipcodes = db.relationship("ZipcodeModel", secondary="travel_time")

    # state_id = db.Column(db.Integer, db.ForeignKey("states.id"))
    # state = db.relationship("StateModel")  # hooks items and stores tables together

    def __init__(self, name, lat, lng, weather_url=None, weather_forecast=None):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.weather_url = weather_url
        self.weather_forecast = weather_forecast

    def json(self):
        return {
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "weather_url": self.weather_url,
            "weather_forecast": self.weather_forecast,
        }

    @classmethod
    def find_by_name(cls, name):
        # this line replaces everything below
        return cls.query.filter_by(
            name=name
        ).first()  # gets first row, converts row to ItemModel object and returns that. Query is part of sqlalchemy

        # connection = sqlite3.connect("data.db")
        # cursor = connection.cursor()

        # query = "SELECT * FROM items WHERE name = ?"
        # result = cursor.execute(query, (name,))
        # row = result.fetchone()
        # connection.close()

        # if row:
        #     return cls(name=row[1], price=row[2])

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id)

    def upsert(self):  # works for both insert and update functions
        db.session.add(self)
        db.session.commit()

        # connection = sqlite3.connect("data.db")
        # cursor = connection.cursor()

        # query = "INSERT INTO items (name, price) VALUES (?,?)"
        # cursor.execute(query, (self.name, self.price))
        # connection.commit()
        # connection.close()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

        # connection = sqlite3.connect("data.db")
        # cursor = connection.cursor()

        # query = "UPDATE items SET price = ? WHERE name = ?"
        # cursor.execute(query, (self.price, self.name))
        # connection.commit()
        # connection.close()

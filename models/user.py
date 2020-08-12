from db import db

# user is in models instead of resources because there are no API endpoints for User information
# model is the internal representation, resource is the external representation


class UserModel(db.Model):

    # these next lines are how you connect to database
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    # leave id off object creation since DB autoincrements it... we should never be entering an ID
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):

        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        # note here that id is the column name, _id is the variable
        return cls.query.filter_by(id=_id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


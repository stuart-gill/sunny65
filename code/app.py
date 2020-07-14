from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
# confusing-- I think this keep flask from tracking changes but lets SQLalchemy do it??
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False
app.secret_key = "stuart"
api = Api(app)

# these 3 lines create the database file (data.db as listed above) and all tables
@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWT(
    app, authenticate, identity
)  # JWT will create /auth endpoint... that endpoint will return JWT token

api.add_resource(Store, "/store/<string:name>")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(StoreList, "/stores")

api.add_resource(UserRegister, "/register")


# conditional ensures that app is only run when we run app.py, and not if/when we import it to another file
# only the file you directly run is __main__
if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5000, debug=True)

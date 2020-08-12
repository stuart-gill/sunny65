from app import app
from db import db


db.init_app(app)

# these 3 lines create the database file (data.db as listed above) and all tables
@app.before_first_request
def create_tables():
    db.create_all()


from app import app

from app.db import db
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

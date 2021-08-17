from app.db import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.Integer)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
    description = db.Column(db.Text)

    def __init__(self, currency, amount, timestamp, description):
        self.currency = currency
        self.amount = amount
        self.timestamp = timestamp
        self.description = description

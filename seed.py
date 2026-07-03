from app import app
from database import db
from models import Resource

resources = [
    "EEE Seminar Hall",
    "CS Seminar Hall",
    "Architecture Seminar Hall",
    "SS Lab",
    "APJ Hall"
]

with app.app_context():

    for name in resources:

        existing = Resource.query.filter_by(name=name).first()

        if not existing:
            db.session.add(
                Resource(name=name)
            )

    db.session.commit()

print("Resources added successfully.")
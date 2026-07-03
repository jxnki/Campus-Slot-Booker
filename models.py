from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False,default="Student")
    department = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    bookings = db.relationship("Booking", back_populates="user")


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )
    bookings = db.relationship("Booking", back_populates="resource")
    def __repr__(self):
        return f"<Resource {self.name}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    booking_date = db.Column(db.Date, nullable=False)

    start_time = db.Column(db.Time, nullable=False)

    end_time = db.Column(db.Time, nullable=False)
    reason = db.Column(
        db.Text,
        nullable=False
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resource.id"),
        nullable=False
    )

    user = db.relationship("User", back_populates="bookings")
    resource = db.relationship("Resource", back_populates="bookings")
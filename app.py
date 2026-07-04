from flask import Flask, render_template, request, redirect, session, flash, jsonify
from config import Config
from database import db
from models import User,Resource, Booking
from datetime import datetime, date
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.context_processor
def inject_admin_recent_activity():
    if session.get("role") != "Admin":
        return {
            "admin_recent_activity": [],
            "admin_notification_count": 0
        }

    recent_activity = Booking.query.filter_by(
        status="Pending"
    ).order_by(Booking.id.desc()).limit(3).all()
    activity_feed = []
    last_seen_notification_id = session.get("admin_notifications_seen_id", 0)

    for booking in recent_activity:
        activity_feed.append({
            "title": f"{booking.user.name} booked {booking.resource.name}",
            "meta": f"Booking #{booking.id} · {booking.booking_date.strftime('%d/%m/%Y')} · {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}",
            "status": booking.status
        })

    unread_count = Booking.query.filter(
        Booking.status == "Pending",
        Booking.id > last_seen_notification_id
    ).count()

    return {
        "admin_recent_activity": activity_feed,
        "admin_notification_count": unread_count
    }


@app.route("/admin-notifications/mark-read", methods=["POST"])
def mark_admin_notifications_read():
    if "user_id" not in session:
        return jsonify({"ok": False}), 401

    if session.get("role") != "Admin":
        return jsonify({"ok": False}), 403

    latest_pending = Booking.query.filter_by(status="Pending").order_by(Booking.id.desc()).first()
    session["admin_notifications_seen_id"] = latest_pending.id if latest_pending else 0

    return jsonify({"ok": True, "count": 0})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        department = request.form["department"]

        year = int(request.form["year"])
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash(
                "This email is already registered.",
                "error"
            )

            return render_template("register.html")
        student = User(
            name=name,
            email=email,
            department=department,
            year=year,
            password=hashed_password
        )

        db.session.add(student)
        db.session.commit()

        flash(
            "Registration successful! Please log in.",
            "success"
        )

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        selected_role = request.form.get("role", "Student")

        user = User.query.filter_by(email=email).first()

        if user and user.role == selected_role and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role

            if user.role == "Admin":
                return redirect("/admin-dashboard")

            return redirect("/student-dashboard")

        flash(
            "Invalid login details",
            "error"
        )

        return render_template(
            "login.html",
            selected_role=selected_role
        )

    return render_template(
        "login.html",
        selected_role="Student"
    )

@app.route("/book/<int:resource_id>", methods=["GET", "POST"])
def book_slot(resource_id):

    resource_obj = db.session.get(Resource, resource_id)

    if request.method == "POST":

        booking_date = datetime.strptime(
        request.form["booking_date"],
        "%Y-%m-%d"
    ).date()

        if booking_date < date.today():
            flash(
                "You cannot book a past date.",
                "error"
            )

            return render_template(
                "book_slot.html",
                resource=resource_obj
            )
            
        start_time = datetime.strptime(
            request.form["start_time"],
            "%H:%M"
        ).time()

        end_time = datetime.strptime(
            request.form["end_time"],
            "%H:%M"
        ).time()
        reason = request.form["reason"]
        if end_time <= start_time:

            flash(
                "End time must be later than the start time.",
                "error"
            )

            return render_template(
                "book_slot.html",
                resource=resource_obj
            )
        # Check if another booking overlaps this time slot
        existing_booking = Booking.query.filter(

            Booking.resource_id == resource_obj.id,

            Booking.booking_date == booking_date,

            Booking.start_time < end_time,

            Booking.end_time > start_time

        ).first()

        if existing_booking:
            flash(
                "This resource is already booked during the selected time.",
                "error"
            )

            return render_template(
                "book_slot.html",
                resource=resource_obj
            )

        # Create the booking only if no overlap exists
        booking = Booking(
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            user_id=session["user_id"],
            resource_id=resource_obj.id
        )

        db.session.add(booking)
        db.session.commit()
        flash(
            "Booking request submitted successfully.",
            "success"
        )

        return redirect("/my-bookings")

    return render_template(
        "book_slot.html",
        resource=resource_obj
    )
  
@app.route("/student-dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Student":
        return redirect("/admin-dashboard")

    resources = Resource.query.filter_by(
        is_active=True
    ).all()

    total_bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).count()

    pending_bookings = Booking.query.filter_by(
        user_id=session["user_id"],
        status="Pending"
    ).count()

    approved_bookings = Booking.query.filter_by(
        user_id=session["user_id"],
        status="Approved"
    ).count()

    recent_activity = Booking.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Booking.id.desc()).limit(3).all()

    activity_feed = []

    for booking in recent_activity:
        activity_feed.append({
            "title": f"{booking.resource.name} booking #{booking.id}",
            "meta": f"{booking.booking_date.strftime('%d/%m/%Y')} · {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}",
            "status": booking.status
        })

    return render_template(
        "student_dashboard.html",
        resources=resources,
        student_name=session["user_name"],
        active_resource_count=len(resources),
        total_booking_count=total_bookings,
        pending_booking_count=pending_bookings,
        approved_booking_count=approved_bookings,
        activity_feed=activity_feed
    )

@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Student":
        return redirect("/admin-dashboard")
    
    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")

    bookings = Booking.query.all()

    total_bookings = len(bookings)
    pending_bookings = Booking.query.filter_by(status="Pending").count()
    approved_bookings = Booking.query.filter_by(status="Approved").count()
    active_resources = Resource.query.filter_by(is_active=True).count()

    return render_template(
        "admin_dashboard.html",
        bookings=bookings,
        total_booking_count=total_bookings,
        pending_booking_count=pending_bookings,
        approved_booking_count=approved_bookings,
        active_resource_count=active_resources
    )

@app.route("/approve/<int:booking_id>",methods=["POST"])
def approve_booking(booking_id):
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")

    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking.status == "Pending":

        booking.status = "Approved"

        db.session.commit()
        flash(
            "Booking approved.",
            "success"
        )


    return redirect("/admin-dashboard")

@app.route("/reject/<int:booking_id>",methods=["POST"])
def reject_booking(booking_id):
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")


    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking.status == "Pending":

        booking.status = "Rejected"

        db.session.commit()
        flash(
            "Booking rejected.",
            "info"
        )

    return redirect("/admin-dashboard")

@app.route("/cancel-booking/<int:booking_id>")
def cancel_booking(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking is None:
        return redirect("/my-bookings")

    if booking.user_id != session["user_id"]:
        return redirect("/my-bookings")

    if booking.status != "Pending":
        return redirect("/my-bookings")

    booking.status = "Cancelled"

    db.session.commit()
    flash(
        "Booking cancelled.",
        "info"
    )

    return redirect("/my-bookings")
@app.route("/edit-booking/<int:booking_id>", methods=["GET", "POST"])
def edit_booking(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Student":
        return redirect("/admin-dashboard")

    booking = db.session.get(Booking, booking_id)

    if booking is None:
        return redirect("/my-bookings")

    if booking.user_id != session["user_id"]:
        return redirect("/my-bookings")

    if booking.status != "Pending":
        return redirect("/my-bookings")

    if request.method == "POST":

        booking_date = datetime.strptime(
            request.form["booking_date"],
            "%Y-%m-%d"
        ).date()

        start_time = datetime.strptime(
            request.form["start_time"],
            "%H:%M"
        ).time()

        end_time = datetime.strptime(
            request.form["end_time"],
            "%H:%M"
        ).time()
        reason = request.form["reason"]
        if booking_date < date.today():
            flash(
                "You cannot book a past date.",
                "error"
            )

            return render_template(
                "edit_booking.html",
                booking=booking
            )

        if end_time <= start_time:
            flash(
                "End time must be later than the start time.",
                "error"
            )

            return render_template(
                "edit_booking.html",
                booking=booking
            )

        existing_booking = Booking.query.filter(

            Booking.resource_id == booking.resource_id,

            Booking.booking_date == booking_date,

            Booking.start_time < end_time,

            Booking.end_time > start_time,

            Booking.id != booking.id

        ).first()

        if existing_booking:
            flash(
                "This resource is already booked during the selected time.",
                "error"
            )

            return render_template(
                "edit_booking.html",
                booking=booking
            )
        
        booking.booking_date = booking_date
        booking.start_time = start_time
        booking.end_time = end_time
        booking.reason = reason
        db.session.commit()
        flash(
            "Booking updated successfully.",
            "success"
        )

        return redirect("/my-bookings")

    return render_template(
        "edit_booking.html",
        booking=booking
    )

@app.route("/manage-resources")
def manage_resources():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")

    resources = Resource.query.order_by(
        Resource.name
    ).all()

    return render_template(
        "manage_resources.html",
        resources=resources
    )

@app.route("/add-resource", methods=["GET", "POST"])
def add_resource():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")

    if request.method == "POST":

        name = request.form["name"]

        existing = Resource.query.filter_by(
            name=name
        ).first()

        if existing:
            flash(
                "Resource already exists.",
                "error"
            )

            return render_template(
                "add_resource.html"
            )
        
        resource = Resource(
            name=name,
        )

        db.session.add(resource)
        db.session.commit()
        flash(
            "Resource added successfully.",
            "success"
        )

        return redirect("/manage-resources")

    return render_template("add_resource.html")

@app.route("/deactivate-resource/<int:resource_id>",methods=["POST"])
def deactivate_resource(resource_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")

    resource = db.session.get(
        Resource,
        resource_id
    )

    if resource is not None:

        resource.is_active = False

        db.session.commit()
        flash(
            "Resource deactivated.",
            "info"
        )

    return redirect("/manage-resources")

@app.route("/activate-resource/<int:resource_id>",methods=["POST"])
def activate_resource(resource_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return redirect("/student-dashboard")

    resource = db.session.get(
        Resource,
        resource_id
    )

    if resource is not None:

        resource.is_active = True

        db.session.commit()
        flash(
            "Resource activated.",
            "success"
        )

    return redirect("/manage-resources")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

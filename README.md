# Campus Slot Booker

A Flask web application for booking campus resources such as seminar halls and labs. Students can register, log in, and request bookings, while administrators can review, approve, or reject requests and manage available resources.

---

## Features

- Student and Admin roles with separate dashboards
- User registration and login with secure password hashing (Werkzeug)
- Book resources by selecting a date and time slot
- Prevent overlapping bookings for the same resource
- Students can view, edit, or cancel their pending bookings
- **Recent Activity Feed** on the student dashboard showing updates such as booking approvals, rejections, and newly created requests
- Admins can approve or reject booking requests
- **Notification Badge** on the admin dashboard showing the number of pending booking requests awaiting review
- Admins can add, activate, or deactivate resources

---

## Tech Stack

- **Backend:** Python, Flask
- **ORM:** Flask-SQLAlchemy
- **Database:** ShaktiDB (PostgreSQL-compatible relational database)
- **Database Driver:** psycopg2
- **Authentication:** Werkzeug Password Hashing with Flask Sessions
- **Frontend:** HTML, CSS, Jinja Templates

---

## Project Structure

```text
Campus-Slot-Booker/
├── app.py              # Flask application and routes
├── config.py           # Loads configuration from .env
├── database.py         # SQLAlchemy database instance
├── models.py           # Database models (User, Resource, Booking)
├── init_db.py          # Creates database tables
├── seed.py             # Inserts default resources
├── requirements.txt
├── .env
├── .gitignore
├── static/
│   └── css/
└── templates/
```

---

## Prerequisites

- Python 3.9 or later
- ShaktiDB installed and running
- pip

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/jxnki/Campus-Slot-Booker.git
cd Campus-Slot-Booker
```

---

## 2. Create and activate a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install the required dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create a database in ShaktiDB

Start ShaktiDB and connect using:

```bash
sudo -u postgres psql
```

Create a database:

```sql
CREATE DATABASE database_name;
```

Connect to the database:

```sql
\c database_name
```

---

## 5. Configure the application

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=campus_slot_booker_secret_key
DATABASE_URL=postgresql://postgres@localhost:5432/database_name
```

If your ShaktiDB installation uses password authentication:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/database_name
```

---

## 6. Create the database tables

Run:

```bash
python init_db.py
```

This creates all the required database tables in ShaktiDB using SQLAlchemy ORM.

---

## 7. Start the application

Run:

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 8. Insert the default resources

Run:

```bash
python seed.py
```

This inserts the default resources required by the application.

> **Note:** This only needs to be run during the initial setup or whenever the database is recreated.

---

# Usage

## Student

- Register a new account
- Log in
- Book available campus resources
- View your bookings
- Edit or cancel pending bookings
- Check the **Recent Activity Feed** for updates on your booking requests

## Admin

- Log in with an administrator account
- View all booking requests
- Monitor pending requests using the notification badge
- Approve or reject booking requests
- Add, activate, or deactivate resources

---

# Database

The application uses **SQLAlchemy ORM** to interact with **ShaktiDB**.

To set up the database:

```bash
python init_db.py
```

To insert the default resources:

```bash
python seed.py
```

---

# Important Notes

- Keep your `.env` file private.
- Never commit the `.env` file to GitHub.
- Ensure `.env` is included in `.gitignore`.
- ShaktiDB is PostgreSQL-compatible, so the application connects using the PostgreSQL protocol through `psycopg2`.
- If you recreate the database, run `python init_db.py`, start the application with `python app.py`, and then run `python seed.py` again.

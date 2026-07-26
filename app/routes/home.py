from flask import Blueprint, render_template
from sqlalchemy.exc import SQLAlchemyError
from app.models.employee import Employee
from app.models import db

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def index():
    total_employees = 0
    total_departments = 0

    try:
        total_employees = db.session.query(Employee).count()
        total_departments = db.session.query(Employee.department).distinct().count()
    except SQLAlchemyError:
        # Database table may not exist yet; render the dashboard with defaults.
        db.session.rollback()

    return render_template("home.html", total_employees=total_employees, total_departments=total_departments)

@home_bp.route("/home")
def home():
    return index()

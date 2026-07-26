from flask import Blueprint, render_template

from app.models import db
from app.models.employee import Employee

department_bp = Blueprint("department", __name__)


@department_bp.route("/department")
def departmentHome():
    departments = (
        db.session.query(Employee.department)
        .distinct()
        .order_by(Employee.department)
        .all()
    )
    department_names = [name for (name,) in departments if name]

    return render_template("department.html", departments=department_names)
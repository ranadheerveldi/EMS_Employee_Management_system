
from flask import Blueprint, request, redirect, url_for, render_template, flash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.employee import Employee
from app.models import db

employee_bp = Blueprint("employee", __name__)

@employee_bp.route("/employee/<int:id>/<string:name>")
def searchByNameId(id, name):
    return f"ID : {id} Name : {name}"

@employee_bp.route("/employee")
def displaySpecific():
    department = request.args.get("department")
    page = request.args.get("page")

    return f"Department : {department} Page : {page}"

@employee_bp.route("/employeeDepartment")
def gotodept():
    return redirect(url_for("department.departmentHome"))

@employee_bp.route("/employee/register")
def register_employee():
    return redirect(url_for("employee.employeeAdd"))

@employee_bp.route("/employee/list")
def employee_list():
    name = request.args.get("name", "").strip()
    email = request.args.get("email", "").strip()
    department = request.args.get("department", "").strip()
    min_salary = request.args.get("min_salary", "").strip()
    max_salary = request.args.get("max_salary", "").strip()

    sort_by = request.args.get("sort_by", "name")
    sort_order = request.args.get("sort_order", "asc")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Employee.query

    if name:
        query = query.filter(Employee.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Employee.email.ilike(f"%{email}%"))
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))

    if min_salary:
        try:
            query = query.filter(Employee.salary >= float(min_salary))
        except ValueError:
            flash("Minimum salary must be a valid number.", "danger")

    if max_salary:
        try:
            query = query.filter(Employee.salary <= float(max_salary))
        except ValueError:
            flash("Maximum salary must be a valid number.", "danger")

    sortable_columns = {
        "name": Employee.name,
        "email": Employee.email,
        "department": Employee.department,
        "salary": Employee.salary,
    }

    sort_column = sortable_columns.get(sort_by, Employee.name)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    employees = pagination.items

    departments = [row[0] for row in db.session.query(Employee.department).distinct().order_by(Employee.department).all()]
    query_params = request.args.to_dict()
    if "page" in query_params:
        query_params.pop("page")

    return render_template(
        "employee.html",
        employees=employees,
        pagination=pagination,
        total_records=pagination.total,
        current_page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search_name=name,
        search_email=email,
        search_department=department,
        min_salary=min_salary,
        max_salary=max_salary,
        departments=departments,
        query_params=query_params,
    )

@employee_bp.route("/employee/add", methods=["POST", "GET"])
def employeeAdd():
    if request.method == "POST":
        try:
            employee = Employee(
                name=request.form["name"],
                email=request.form["email"],
                password=request.form["password"],
                salary=float(request.form["salary"]),
                department=request.form["department"],
            )

            db.session.add(employee)
            db.session.commit()
            flash("Employee added successfully.", "success")

            return redirect(url_for("employee.employee_list"))
        except ValueError:
            db.session.rollback()
            flash("Salary must be a valid number.", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("An employee with this email already exists.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Unable to add employee due to a database error.", "danger")

    return render_template("add_employee.html")

@employee_bp.route("/employee/employeeDetail/<int:id>", methods=["GET"])
def employeeDetail(id):
    employee = Employee.query.get_or_404(id)
    return render_template("employee_detail.html", employee=employee)

@employee_bp.route("/employee/employeeUpdate/<int:id>", methods=["POST", "GET"])
def employeeUpdate(id):
    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        try:
            employee.name = request.form["name"]
            employee.email = request.form["email"]
            employee.password = request.form["password"]
            employee.salary = float(request.form["salary"])
            employee.department = request.form["department"]

            db.session.commit()
            flash("Employee updated successfully.", "success")

            return redirect(url_for("employee.employee_list"))
        except ValueError:
            db.session.rollback()
            flash("Salary must be a valid number.", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("An employee with this email already exists.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Unable to update employee due to a database error.", "danger")

    return render_template("update_employee.html", employee=employee)

@employee_bp.route("/employee/employeeDelete/<int:id>")
def employeeDelete(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted successfully.", "success")

    return redirect(url_for("employee.employee_list"))

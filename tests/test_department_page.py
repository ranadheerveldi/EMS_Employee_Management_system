import os
import unittest

from flask import Flask

from app.models import db
from app.models.employee import Employee
from app.routes.department import department_bp
from app.routes.employee import employee_bp
from app.routes.home import home_bp


class DepartmentPageTestCase(unittest.TestCase):
    def setUp(self):
        template_folder = os.path.join(os.path.dirname(__file__), "..", "app", "templates")
        self.app = Flask(__name__, template_folder=template_folder)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )

        db.init_app(self.app)
        self.app.register_blueprint(home_bp)
        self.app.register_blueprint(employee_bp)
        self.app.register_blueprint(department_bp)

        with self.app.app_context():
            db.create_all()
            db.session.add_all(
                [
                    Employee(name="Alice", email="alice@example.com", password="pass", salary=5000, department="Engineering"),
                    Employee(name="Bob", email="bob@example.com", password="pass", salary=4000, department="HR"),
                ]
            )
            db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_department_page_lists_departments(self):
        response = self.client.get("/department")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Engineering", response.data)
        self.assertIn(b"HR", response.data)


if __name__ == "__main__":
    unittest.main()

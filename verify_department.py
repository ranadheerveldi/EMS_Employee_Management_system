from app import create_app
from app.models import db
from app.models.employee import Employee

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add_all([
        Employee(name='Alice', email='alice@example.com', password='pass', salary=5000, department='Engineering'),
        Employee(name='Bob', email='bob@example.com', password='pass', salary=4000, department='HR'),
    ])
    db.session.commit()

with app.test_client() as client:
    response = client.get('/department')
    print(response.status_code)
    print('Engineering' in response.get_data(as_text=True))
    print('HR' in response.get_data(as_text=True))

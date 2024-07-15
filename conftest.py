import pytest
from app import app, db

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_blog.db'
    testing_client = app.test_client()

    with app.app_context():
        db.create_all()

    yield testing_client

    with app.app_context():
        db.drop_all()
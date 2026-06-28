import sys
import os
import pytest

# Add the parent directory to sys.path to allow importing milkdown_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from milkdown_app.app import app as flask_app, init_db

@pytest.fixture(autouse=True, scope="session")
def setup_db():
    init_db()

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

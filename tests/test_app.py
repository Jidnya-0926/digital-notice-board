import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def test_home_page():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_login_page():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200


def test_add_notice_page():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/add")

    assert response.status_code == 200
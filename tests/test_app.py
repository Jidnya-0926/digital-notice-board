import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as app_module

app = app_module.app

TEST_DATABASE = "tests/test_notices.db"

app_module.DATABASE = TEST_DATABASE


def setup_module():
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

    app_module.init_db()


def teardown_module():
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


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
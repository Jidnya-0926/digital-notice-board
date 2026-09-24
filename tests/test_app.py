import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

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


def test_student_login_page():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/student-login")

    assert response.status_code == 200


def test_admin_login_page():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200


def test_add_notice_requires_admin_login():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get(
        "/add",
        follow_redirects=False
    )

    assert response.status_code == 302

    assert response.location.endswith("/login")


def test_admin_can_access_add_notice():

    app.config["TESTING"] = True

    client = app.test_client()

    login_response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 302

    response = client.get("/add")

    assert response.status_code == 200


def test_student_notices_requires_login():

    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get(
        "/notices",
        follow_redirects=False
    )

    assert response.status_code == 302

    assert response.location.endswith("/")


def test_student_can_login_and_view_notices():

    app.config["TESTING"] = True

    client = app.test_client()

    login_response = client.post(
        "/student-login",
        data={
            "erp_id": "STUDENT001",
            "password": "student123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 302

    response = client.get("/notices")

    assert response.status_code == 200
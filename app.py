from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "notices.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            important INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():

    search = request.args.get("search", "")
    category = request.args.get("category", "")

    conn = get_db()

    query = "SELECT * FROM notices WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend(["%" + search + "%", "%" + search + "%"])

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id DESC"

    notices = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "index.html",
        notices=notices,
        search=search,
        category=category
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            return redirect(url_for("admin"))

    return render_template("login.html")


@app.route("/admin")
def admin():

    conn = get_db()

    notices = conn.execute(
        "SELECT * FROM notices ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("admin.html", notices=notices)


@app.route("/add", methods=["GET", "POST"])
def add_notice():

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        date = request.form["date"]
        description = request.form["description"]

        important = 1 if "important" in request.form else 0

        conn = get_db()

        conn.execute("""
            INSERT INTO notices
            (title, category, date, description, important)
            VALUES (?, ?, ?, ?, ?)
        """, (title, category, date, description, important))

        conn.commit()
        conn.close()

        return redirect(url_for("admin"))

    return render_template("add_notice.html")


@app.route("/delete/<int:notice_id>")
def delete_notice(notice_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM notices WHERE id = ?",
        (notice_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


if __name__ == "__main__":

    init_db()

    app.run(debug=True)
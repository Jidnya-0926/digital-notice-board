from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

DATABASE = "notices.db"

app.secret_key = "digital-notice-board-secret-key"


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
            important INTEGER DEFAULT 0,
            registration_link TEXT
        )
    """)

    columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(notices)"
        ).fetchall()
    ]

    if "registration_link" not in columns:

        conn.execute(
            "ALTER TABLE notices ADD COLUMN registration_link TEXT"
        )

    count = conn.execute(
        "SELECT COUNT(*) FROM notices"
    ).fetchone()[0]

    if count == 0:

        default_notices = [

            (
                "Internal Assessment 2 Schedule",
                "Examination",
                "2026-10-05",
                "Internal Assessment 2 examinations will begin from 5 October 2026. Students are requested to check the examination timetable and prepare accordingly.",
                1,
                ""
            ),

            (
                "Annual College Fest 2026",
                "Event",
                "2026-10-15",
                "The Annual College Fest 2026 will be conducted on the college campus. Students interested in participating should register with their respective coordinators.",
                0,
                ""
            ),

            (
                "Project Submission Deadline",
                "Academic",
                "2026-10-20",
                "All students must submit their academic mini-projects by 20 October 2026. Late submissions may not be accepted.",
                1,
                ""
            ),

            (
                "College Library Timings",
                "General",
                "2026-09-30",
                "The college library will remain open from 8:00 AM to 6:00 PM on working days. Students are requested to carry their valid college ID cards.",
                0,
                ""
            ),

            (
                "Semester End Examination Form",
                "Examination",
                "2026-10-25",
                "Students must complete the Semester End Examination form submission before the deadline.",
                1,
                ""
            ),

            (
                "Technical Workshop on Web Development",
                "Event",
                "2026-10-08",
                "A hands-on technical workshop on modern web development will be conducted in the computer laboratory.",
                0,
                ""
            ),

            (
                "Attendance Requirement Notice",
                "Academic",
                "2026-10-12",
                "Students are reminded to maintain the required attendance percentage for appearing in the semester examinations.",
                1,
                ""
            ),

            (
                "Campus Cleanliness Drive",
                "General",
                "2026-10-03",
                "The college will organize a campus cleanliness drive. Students are encouraged to participate.",
                0,
                ""
            )

        ]

        conn.executemany("""
            INSERT INTO notices
            (
                title,
                category,
                date,
                description,
                important,
                registration_link
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, default_notices)

    conn.commit()
    conn.close()


# =========================================================
# ROLE SELECTION
# =========================================================

@app.route("/")
def role_login():

    return render_template("role_login.html")


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        erp_id = request.form["erp_id"]
        password = request.form["password"]

        if erp_id == "STUDENT001" and password == "student123":

            session["student_logged_in"] = True
            session["student_erp_id"] = erp_id

            return redirect(url_for("index"))

    return render_template("student_login.html")


# =========================================================
# STUDENT NOTICE BOARD
# =========================================================

@app.route("/notices")
def index():

    if not session.get("student_logged_in"):

        return redirect(url_for("role_login"))

    search = request.args.get(
        "search",
        ""
    )

    category = request.args.get(
        "category",
        ""
    )

    conn = get_db()

    query = """
        SELECT *
        FROM notices
        WHERE 1=1
    """

    params = []

    if search:

        query += """
            AND (
                title LIKE ?
                OR description LIKE ?
            )
        """

        params.extend([
            "%" + search + "%",
            "%" + search + "%"
        ])

    if category:

        query += """
            AND category = ?
        """

        params.append(category)

    query += " ORDER BY id DESC"

    notices = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        notices=notices,
        search=search,
        category=category
    )


# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route("/student-logout")
def student_logout():

    session.pop("student_logged_in", None)
    session.pop("student_erp_id", None)

    return redirect(url_for("role_login"))


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect(url_for("admin"))

    return render_template("login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    conn = get_db()

    notices = conn.execute("""
        SELECT *
        FROM notices
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        notices=notices
    )


# =========================================================
# ADD NOTICE
# =========================================================

@app.route("/add", methods=["GET", "POST"])
def add_notice():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]

        category = request.form["category"]

        date = request.form["date"]

        description = request.form["description"]

        registration_link = request.form.get(
            "registration_link",
            ""
        ).strip()

        important = (
            1
            if "important" in request.form
            else 0
        )

        conn = get_db()

        conn.execute("""
            INSERT INTO notices
            (
                title,
                category,
                date,
                description,
                important,
                registration_link
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            category,
            date,
            description,
            important,
            registration_link
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin"))

    return render_template("add_notice.html")


# =========================================================
# DELETE NOTICE
# =========================================================

@app.route("/delete/<int:notice_id>")
def delete_notice(notice_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    conn = get_db()

    conn.execute(
        "DELETE FROM notices WHERE id = ?",
        (notice_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(url_for("role_login"))


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )
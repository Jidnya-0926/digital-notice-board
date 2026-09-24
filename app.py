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
                1
            ),

            (
                "Annual College Fest 2026",
                "Event",
                "2026-10-15",
                "The Annual College Fest 2026 will be conducted on the college campus. Students interested in participating should register with their respective coordinators.",
                0
            ),

            (
                "Project Submission Deadline",
                "Academic",
                "2026-10-20",
                "All students must submit their academic mini-projects by 20 October 2026. Late submissions may not be accepted.",
                1
            ),

            (
                "College Library Timings",
                "General",
                "2026-09-30",
                "The college library will remain open from 8:00 AM to 6:00 PM on working days. Students are requested to carry their valid college ID cards.",
                0
            ),

            (
                "Semester End Examination Form",
                "Examination",
                "2026-10-25",
                "Students must complete the Semester End Examination form submission before the deadline. Verify all personal and academic details before submitting.",
                1
            ),

            (
                "Technical Workshop on Web Development",
                "Event",
                "2026-10-08",
                "A hands-on technical workshop on modern web development will be conducted in the computer laboratory. Students from all IT-related branches can participate.",
                0
            ),

            (
                "Attendance Requirement Notice",
                "Academic",
                "2026-10-12",
                "Students are reminded to maintain the required attendance percentage for appearing in the semester examinations.",
                1
            ),

            (
                "Campus Cleanliness Drive",
                "General",
                "2026-10-03",
                "The college will organize a campus cleanliness drive. Students are encouraged to participate and help maintain a clean and healthy campus environment.",
                0
            )

        ]

        conn.executemany("""
            INSERT INTO notices
            (title, category, date, description, important)
            VALUES (?, ?, ?, ?, ?)
        """, default_notices)

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
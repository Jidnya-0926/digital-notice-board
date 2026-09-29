
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re

app = Flask(__name__)

DATABASE = "notices.db"

app.secret_key = "digital-notice-board-secret-key"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = get_db()

    # =====================================================
    # NOTICES TABLE
    # =====================================================

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

    # Check registration_link column
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

    # =====================================================
    # STUDENTS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            college_id TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # =====================================================
    # DEFAULT NOTICES
    # =====================================================

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
# STUDENT REGISTRATION
# =========================================================

@app.route("/student-register", methods=["GET", "POST"])
def student_register():

    error = ""
    success = ""

    if request.method == "POST":

        college_id = request.form.get(
            "college_id",
            ""
        ).strip()

        student_name = request.form.get(
            "student_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        # Password automatically becomes College ID
        password = college_id

        # -------------------------------------------------
        # Validate College ID
        # -------------------------------------------------

        if not re.fullmatch(r"\d{9}", college_id):

            error = (
                "Invalid College ID. "
                "Enter a valid 9-digit College ID."
            )

            return render_template(
                "student_register.html",
                error=error
            )

        # -------------------------------------------------
        # Validate Student Name
        # -------------------------------------------------

        if not re.fullmatch(
            r"[A-Za-z ]{2,50}",
            student_name
        ):

            error = "Enter a valid student name."

            return render_template(
                "student_register.html",
                error=error
            )

        # -------------------------------------------------
        # Validate Xavier Student Email
        # -------------------------------------------------

        email_pattern = (
            r"^(\d{9})\."
            r"[a-zA-Z][a-zA-Z0-9._-]*"
            r"@student\.xavier\.ac\.in$"
        )

        email_match = re.fullmatch(
            email_pattern,
            email
        )

        if not email_match:

            error = (
                "Invalid Xavier student email. "
                "Use format: "
                "COLLEGEID.studentname@student.xavier.ac.in"
            )

            return render_template(
                "student_register.html",
                error=error
            )

        # -------------------------------------------------
        # Check College ID matches Email
        # -------------------------------------------------

        email_college_id = email_match.group(1)

        if email_college_id != college_id:

            error = (
                "College ID does not match the ID "
                "present in the Xavier email."
            )

            return render_template(
                "student_register.html",
                error=error
            )

        # -------------------------------------------------
        # Check Existing Student
        # -------------------------------------------------

        conn = get_db()

        existing_student = conn.execute("""
            SELECT *
            FROM students
            WHERE college_id = ?
               OR email = ?
        """, (
            college_id,
            email
        )).fetchone()

        if existing_student:

            conn.close()

            error = (
                "This College ID or email is already registered."
            )

            return render_template(
                "student_register.html",
                error=error
            )

        # -------------------------------------------------
        # Register Student
        # -------------------------------------------------

        conn.execute("""
            INSERT INTO students
            (
                college_id,
                student_name,
                email,
                password
            )
            VALUES (?, ?, ?, ?)
        """, (
            college_id,
            student_name,
            email,
            password
        ))

        conn.commit()
        conn.close()

        success = (
            "Registration successful! "
            "Your password is your College ID."
        )

        return render_template(
            "student_register.html",
            success=success
        )

    return render_template(
        "student_register.html",
        error=error,
        success=success
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    error = ""

    if request.method == "POST":

        college_id = request.form.get(
            "college_id",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        conn = get_db()

        student = conn.execute("""
            SELECT *
            FROM students
            WHERE college_id = ?
              AND password = ?
        """, (
            college_id,
            password
        )).fetchone()

        conn.close()

        if student:

            session["student_logged_in"] = True

            session["student_college_id"] = (
                student["college_id"]
            )

            session["student_name"] = (
                student["student_name"]
            )

            return redirect(
                url_for("index")
            )

        error = "Invalid College ID or password."

    return render_template(
        "student_login.html",
        error=error
    )


# =========================================================
# STUDENT NOTICE BOARD
# =========================================================

@app.route("/notices")
def index():

    if not session.get("student_logged_in"):

        return redirect(
            url_for("role_login")
        )

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

    query += """
        ORDER BY id DESC
    """

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
# NOTICE DETAILS
# =========================================================

@app.route("/notice/<int:notice_id>")
def notice_details(notice_id):

    # Only logged-in students can view notice details
    if not session.get("student_logged_in"):

        return redirect(
            url_for("role_login")
        )

    conn = get_db()

    notice = conn.execute("""
        SELECT *
        FROM notices
        WHERE id = ?
    """, (
        notice_id,
    )).fetchone()

    conn.close()

    # Notice does not exist
    if not notice:

        return "Notice not found", 404

    return render_template(
        "notice_details.html",
        notice=notice
    )


# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route("/student-logout")
def student_logout():

    session.pop(
        "student_logged_in",
        None
    )

    session.pop(
        "student_college_id",
        None
    )

    session.pop(
        "student_name",
        None
    )

    return redirect(
        url_for("role_login")
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if (
            username == "admin"
            and password == "admin123"
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        error = (
            "Invalid admin username or password."
        )

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

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

        return redirect(
            url_for("login")
        )

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

        return redirect(
            url_for("admin")
        )

    return render_template(
        "add_notice.html"
    )


# =========================================================
# EDIT NOTICE
# =========================================================

@app.route(
    "/edit/<int:notice_id>",
    methods=["GET", "POST"]
)
def edit_notice(notice_id):

    # Only logged-in admin can edit notices
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

    conn = get_db()

    # Find the notice
    notice = conn.execute("""
        SELECT *
        FROM notices
        WHERE id = ?
    """, (
        notice_id,
    )).fetchone()

    # Notice does not exist
    if not notice:

        conn.close()

        return "Notice not found", 404

    # -----------------------------------------------------
    # UPDATE NOTICE
    # -----------------------------------------------------

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        date = request.form.get(
            "date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        registration_link = request.form.get(
            "registration_link",
            ""
        ).strip()

        important = (
            1
            if "important" in request.form
            else 0
        )

        # Basic validation
        if not title:

            conn.close()

            return render_template(
                "edit_notice.html",
                notice=notice,
                error="Notice title cannot be empty."
            )

        if not category:

            conn.close()

            return render_template(
                "edit_notice.html",
                notice=notice,
                error="Please select a category."
            )

        if not date:

            conn.close()

            return render_template(
                "edit_notice.html",
                notice=notice,
                error="Please select a date."
            )

        if not description:

            conn.close()

            return render_template(
                "edit_notice.html",
                notice=notice,
                error="Notice description cannot be empty."
            )

        # -------------------------------------------------
        # Update database
        # -------------------------------------------------

        conn.execute("""
            UPDATE notices

            SET
                title = ?,
                category = ?,
                date = ?,
                description = ?,
                important = ?,
                registration_link = ?

            WHERE id = ?
        """, (
            title,
            category,
            date,
            description,
            important,
            registration_link,
            notice_id
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for("admin")
        )

    # GET request
    conn.close()

    return render_template(
        "edit_notice.html",
        notice=notice,
        error=""
    )


# =========================================================
# DELETE NOTICE
# =========================================================

@app.route("/delete/<int:notice_id>")
def delete_notice(notice_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

    conn = get_db()

    conn.execute(
        "DELETE FROM notices WHERE id = ?",
        (notice_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("role_login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )

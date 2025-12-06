import os
import sqlite3
from datetime import date
from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

# ---------------------------
# Flask Setup
# ---------------------------
app = Flask(__name__, template_folder="templates")

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # project/ folder
DB_EVENTS = os.path.join(BASE_DIR, "events.db")         # project/events.db
DB_STUDENTS = os.path.join(BASE_DIR, "students.db")     # project/students.db

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
PHOTOS_FOLDER = os.path.join(BASE_DIR, "photos")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PHOTOS_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------
# DB Helpers
# ---------------------------
def get_event_db():
    conn = sqlite3.connect(DB_EVENTS, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def run_query(db_path, query):
    if not os.path.exists(db_path):
        return None, f"Database {db_path} not found!"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        columns = [col[0] for col in cur.description]
        conn.close()
        return {"columns": columns, "rows": [dict(row) for row in rows]}, None
    except Exception as e:
        return None, str(e)

# ---------------------------
# Event Management
# ---------------------------
def fetch_events():
    with get_event_db() as conn:
        cursor = conn.execute("SELECT * FROM events ORDER BY date ASC")
        events = [dict(row) for row in cursor.fetchall()]
        for e in events:
            e["photo_url"] = f"/uploads/{e['photo']}" if e["photo"] else "/static/default.jpg"
        return events

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/photos/<filename>")
def student_photo(filename):
    return send_from_directory(PHOTOS_FOLDER, filename)

@app.route("/api/staff/login")
def staff_login():
    username = request.args.get("username", "").strip()
    password = request.args.get("password", "").strip()
    access_key = request.args.get("access_key", "").strip()

    with get_event_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff WHERE username=? AND password=? AND access_key=?",
                       (username, password, access_key))
        user = cursor.fetchone()

    return jsonify({"success": True if user else False})

@app.route("/api/staff/add_event", methods=["POST"])
def add_event():
    event_name = request.form.get("event_name")
    date_ = request.form.get("date")
    time = request.form.get("time")
    place = request.form.get("place")
    chief_guest = request.form.get("chief_guest")
    student_access_key = request.form.get("student_access_key")

    poster_filename = None
    if "poster" in request.files:
        poster = request.files["poster"]
        if poster.filename:
            poster_filename = secure_filename(poster.filename)
            poster.save(os.path.join(app.config["UPLOAD_FOLDER"], poster_filename))

    try:
        with get_event_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (event_name, date, time, place, chief_guest, photo, student_access_key)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event_name, date_, time, place, chief_guest, poster_filename, student_access_key))

            table_name = event_name.replace(" ", "_")
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_roll TEXT UNIQUE,
                student_name TEXT NOT NULL,
                department TEXT NOT NULL,
                reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/register", methods=["POST"])
def register_student():
    data = request.get_json()
    event_id = data["event_id"]
    student_roll = data["student_roll"]
    student_name = data["student_name"]
    department = data["department"]
    access_key = data["access_key"]

    with get_event_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_name, student_access_key FROM events WHERE id=?", (event_id,))
        event = cursor.fetchone()

        if not event:
            return jsonify({"success": False, "error": "Event not found!"})
        if access_key != event["student_access_key"]:
            return jsonify({"success": False, "error": "Invalid Access Key!"})

        event_table = event["event_name"].replace(" ", "_")
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{event_table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_roll TEXT UNIQUE,
            student_name TEXT NOT NULL,
            department TEXT NOT NULL,
            reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        try:
            cursor.execute(f"""INSERT INTO "{event_table}" (student_roll, student_name, department)
                               VALUES (?,?,?)""", (student_roll, student_name, department))
            conn.commit()
            return jsonify({"success": True})
        except sqlite3.IntegrityError:
            return jsonify({"success": False, "error": "Student already registered!"})

# ---------------------------
# Database Viewer
# ---------------------------
@app.route("/api/databases")
def get_databases():
    dbs = []
    if os.path.exists(DB_STUDENTS):
        dbs.append("students.db")
    if os.path.exists(DB_EVENTS):
        dbs.append("events.db")
    return jsonify({"databases": dbs})

@app.route("/api/<db_name>/tables")
def get_tables(db_name):
    db_path = os.path.join(BASE_DIR, db_name)
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    result, error = run_query(db_path, query)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"tables": [row["name"] for row in result["rows"]]})

@app.route("/api/<db_name>/table/<table_name>")
def get_table_data(db_name, table_name):
    db_path = os.path.join(BASE_DIR, db_name)
    query = f"SELECT * FROM {table_name} LIMIT 50;"
    result, error = run_query(db_path, query)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result)

# ---------------------------
# Navigation + Pages
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html", events=fetch_events())

@app.route("/home")
def home():
    return render_template("index.html", events=fetch_events())

@app.route("/staff")
def staff():
    return render_template("staff.html")

@app.route("/database")
def database():
    return render_template("database.html")

@app.route("/api/events")
def api_events():
    return jsonify(fetch_events())

@app.route("/api/today")
def api_today():
    today_str = date.today().isoformat()
    events = fetch_events()
    today_events = [e for e in events if e["date"] == today_str]
    return jsonify(today_events)

@app.route("/api/student/<roll_no>")
def get_student(roll_no):
    if not os.path.exists(DB_STUDENTS):
        return jsonify({"success": False, "error": "students.db not found!"})

    with sqlite3.connect(DB_STUDENTS) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students_data WHERE student_roll=?", (roll_no,))
        student = cursor.fetchone()

    if student:
        return jsonify({"success": True, "student": dict(student)})
    else:
        return jsonify({"success": False, "error": "Student not found!"})

# ---------------------------




# Main
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)

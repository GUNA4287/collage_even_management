import sqlite3

DB_PATH = "students.db"  # Database name

def create_student_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create students_data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students_data (
        student_roll TEXT PRIMARY KEY,
        student_name TEXT NOT NULL,
        department TEXT NOT NULL,
        year_of_passing INTEGER NOT NULL,
        student_photo TEXT
    )
    """)

    # 2. Insert 5 demo student records
    demo_students = [
        ("23ER001", "P.Keerthana", "IT", 2, "photos/23ER001.jpg"),
        ("23ER002", "P.Harshini", "BCA", 3, "photos/23ER002.jpg"),
        ("23ER003", "M.Sharmi", "CS", 1, "photos/23ER003.jpg"),
        ("23ER004", "K.Saranya", "IT", 2, "photos/23ER004.jpg"),
        ("23ER005", "R.Priya", "IT", 2, "photos/23ER005.jpg"),
        ("23ER006", "D.Divya", "BCA", 2, "photos/23ER006.jpg"),
        ("23ER007", "B.Abhi", "IT", 2, "photos/23ER007.jpg"),
        ("23ER008", "P.Swetha", "BCA", 3, "photos/23ER008.jpg"),
        ("23ER009", "S.Kaviya", "CS", 1, "photos/23ER009.jpg"),
        ("23ER010", "K.Suba", "IT", 2, "photos/23ER010.jpg"),
        ("23ER011", "T.Benita", "IT", 2, "photos/23ER011.jpg"),
        ("23ER012", "D.Jenita", "BCA", 3, "photos/23ER012.jpg"),
        ("23ER013", "M.Leena", "IT", 2, "photos/23ER013.jpg"),
        ("23ER014", "T.Kalai", "IT", 2, "photos/23ER014.jpg"),
        ("23ER015", "D.Nancy", "BCA", 3, "photos/23ER015.jpg"),
    ]

    try:
        cursor.executemany("""
        INSERT INTO students_data (student_roll, student_name, department, year_of_passing, student_photo)
        VALUES (?, ?, ?, ?, ?)
        """, demo_students)
        print("5 demo student records inserted successfully!")
    except sqlite3.IntegrityError:
        print("Some records already exist. Skipping duplicate insertions.")

    conn.commit()
    conn.close()
    print("Database and students_data table created successfully!")

if __name__ == "__main__":
    create_student_database()

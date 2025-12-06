import sqlite3

# Database file
DB_PATH = 'events.db'

# Connect to SQLite database (it will create the file if not exists)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create 'staff' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    access_key TEXT NOT NULL
)
""")

# Insert example staff users
staff_users = [
    ('Jamuna', 'Bca@01', 'J@001'),
    ('Kokila', 'Cs@01', 'K@002'),
    ('Uma', 'It@01', 'S@003')
]

# Insert users (ignore if username already exists)
for user in staff_users:
    cursor.execute("""
    INSERT OR IGNORE INTO staff (username, password, access_key)
    VALUES (?, ?, ?)
    """, user)

# Commit changes and close
conn.commit()
conn.close()

print("Staff table created and sample users added successfully.")

# create_db.py
import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("events.db")
cursor = conn.cursor()

# Drop old events table if it exists (for fresh start)
#cursor.execute("DROP TABLE IF EXISTS events")

# Create the new events table with required columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    place TEXT NOT NULL,
    chief_guest TEXT,
    photo Image,
    student_access_key TEXT NOT NULL
)
""")

# Sample events to insert
sample_events = [
    ('Music Fest', '2025-09-02', '09:00', 'Main Stage', 'Mr. A. Kumar', 'https://example.com/musicfest.jpg', 'STUD123'),
    ('Tech Symposium', '2025-08-25', '10:00', 'Auditorium', 'Dr. S. Meena', 'https://example.com/techsymp.jpg', 'TECH456'),
    ('Sports Meet', '2025-09-15', '09:00', 'Sports Ground', 'Ms. P. Latha', 'https://example.com/sportsmeet.jpg', 'SPORT789')
]

# Insert sample events
cursor.executemany("""
INSERT INTO events (event_name, date, time, place, chief_guest, photo, student_access_key)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", sample_events)

# Commit and close
conn.commit()
conn.close()

print("Database 'events.db' created with updated 'events' table and sample data inserted!")

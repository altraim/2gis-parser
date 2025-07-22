import sqlite3

DB_NAME = "reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            author TEXT,
            text TEXT,
            rating INTEGER,
            date TEXT,
            branch_url TEXT
        )      
    """)
    conn.commit()
    conn.close()

def get_existing_ids():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM reviews")
    rows = c.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def save_reviews(reviews):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for r in reviews:
        try:
            c.execute("INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?)", (
                r["id"], r["author"], r["text"], r["rating"], r["date"], r["branch_url"]
            ))
        except sqlite3.IntegrityError:
            pass # Уже в базе
    conn.commit()
    conn.close()
import sqlite3

conn = sqlite3.connect('votes.db')
c = conn.cursor()

# Create the votes table
c.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        candidate TEXT PRIMARY KEY,
        count INTEGER DEFAULT 0
    )
''')

# Insert initial vote counts
candidates = ['Janasena', 'TDP', 'YSRCP', 'NOTA']
for candidate in candidates:
    c.execute("INSERT OR IGNORE INTO votes (candidate, count) VALUES (?, ?)", (candidate, 0))

# Create IP tracking table
c.execute('''
    CREATE TABLE IF NOT EXISTS voters (
        ip TEXT PRIMARY KEY
    )
''')

conn.commit()
conn.close()

print("Database initialized ✅")

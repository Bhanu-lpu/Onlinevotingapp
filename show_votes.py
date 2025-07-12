import sqlite3

conn = sqlite3.connect('votes.db')
cursor = conn.cursor()

print("Votes:\n----------")
for row in cursor.execute("SELECT * FROM votes"):
    print(row)

print("\nVoters:\n----------")
for row in cursor.execute("SELECT * FROM voters"):
    print(row)

conn.close()

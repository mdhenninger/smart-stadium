import sqlite3

conn = sqlite3.connect('data/history.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", [table[0] for table in tables])

# Check if there are any tables with team-related data
for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("Columns:", [col[1] for col in columns])
    
    # Get sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    print("Sample rows:", len(rows))
    for row in rows[:2]:
        print("  ", row)

conn.close()
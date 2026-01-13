import sqlite3

conn = sqlite3.connect('radars.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM radars')
count = cur.fetchone()[0]
print(f'✅ {count} radars dans la base de données')

if count > 0:
    cur.execute('SELECT * FROM radars LIMIT 3')
    rows = cur.fetchall()
    for row in rows:
        print(f'  - Radar #{row[1]} type {row[2]} à {row[7]}, {row[8]}')
    
    cur.execute('SELECT DISTINCT type FROM radars')
    types = [row[0] for row in cur.fetchall()]
    print(f'Types: {types}')
else:
    print('❌ La base de données est vide!')

conn.close()

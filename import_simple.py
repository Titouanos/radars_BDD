import csv
import sqlite3
from database import init_database, get_connection, clear_database

# Initialiser
print("Init DB...")
init_database()
clear_database()

# simple test direct
conn = get_connection()
cur = conn.cursor()

print("Lecture CSV...")
with open('radars_final.csv', 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    count = 0
    for row in reader:
        num = row['Numéro de radar']
        typ = row['Type']
        date = row['Date de mise en service']
        vit = row['Vitesse']
        lat = row['Latitude'].replace('+', '')
        lon = row['Longitude'].replace('+', '')
        
        cur.execute("""
            INSERT INTO radars (numero, type, date_mise_service, voie, sens, vitesse, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (num, typ, date, None, None, int(vit) if vit.isdigit() else None, float(lat), float(lon)))
        
        count += 1
        if count % 500 == 0:
            print(f"{count}...")
        
        if count >= 3309:  # Limite pour éviter trop de données
            break

conn.commit()
print(f"\n✅ {count} radars importés")

# Vérifier
cur.execute('SELECT COUNT(*) FROM radars')
print(f"Vérification: {cur.fetchone()[0]} radars dans la DB")

conn.close()

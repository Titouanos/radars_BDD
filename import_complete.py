"""
Script complet d'import des radars avec téléchargement intégré
"""
import csv
import sqlite3
import requests
from database import init_database, get_connection, clear_database

CSV_URL = "https://www.data.gouv.fr/fr/datasets/r/17f7cfd9-a5fe-4b6a-9f5d-3625feaa396e"
CSV_FILE = "radars_final.csv"

def download_csv():
    """Télécharge le fichier CSV"""
    print(f"📥 Téléchargement depuis data.gouv.fr...")
    response = requests.get(CSV_URL)
    print(f"   Status: {response.status_code}")
    
    with open(CSV_FILE, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ Fichier téléchargé ({len(response.content)} bytes)")

def import_radars():
    """Importe les radars dans la base de données"""
    # Initialiser la base
    print("📊 Initialisation de la base de données...")
    init_database()
    
    # Nettoyer
    print("🗑️  Nettoyage des anciennes données...")
    clear_database()
    
    # Importer
    print(f"📁 Lecture du fichier {CSV_FILE}...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    imported_count = 0
    error_count = 0
    
    try:
        with open(CSV_FILE, 'r', encoding='latin-1') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            print(f"📋 Colonnes: {csv_reader.fieldnames}")
            
            for i, row in enumerate(csv_reader):
                try:
                    # Le CSV a ce format: Numéro;Type;Date;Vitesse;Latitude;Longitude
                    # IMPORTANT: Les headers ont des espaces au début !
                    # Extraction - utiliser .strip() sur les clés
                    numero = row.get(' Numéro', row.get('Numéro de radar', '')).strip()
                    radar_type = row.get(' Type', row.get('Type', '')).strip()
                    date_service = row.get(' Date de mise en service', row.get('Date de mise en service', '')).strip()
                    
                    # Pas de colonnes Voie et Sens dans ce CSV
                    voie = None
                    sens = None
                    
                    vitesse_str = row.get(' Vitesse', row.get('Vitesse', '')).strip()
                    vitesse = int(vitesse_str) if vitesse_str and vitesse_str.isdigit() else None
                    
                    latitude_str = row.get(' Latitude', row.get('Latitude', '')).strip().replace('+', '')
                    longitude_str = row.get(' Longitude', row.get('Longitude', '')).strip().replace('+', '')
                    
                    if not latitude_str or not longitude_str:
                        error_count += 1
                        continue
                    
                    latitude = float(latitude_str)
                    longitude = float(longitude_str)
                    
                    # Insertion
                    cursor.execute("""
                        INSERT INTO radars (numero, type, date_mise_service, voie, sens, vitesse, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (numero, radar_type, date_service, voie, sens, vitesse, latitude, longitude))
                    
                    imported_count += 1
                    
                    if imported_count % 500 == 0:
                        print(f"  ⏳ {imported_count} radars importés...")
                    
                except Exception as e:
                    error_count += 1
                    if i < 5:
                        print(f"⚠️  Ligne {i}: {e}")
                    continue
        
        conn.commit()
        print(f"\n✅ Import terminé avec succès !")
        print(f"   📍 {imported_count} radars importés")
        if error_count > 0:
            print(f"   ⚠️  {error_count} entrées ignorées")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import : {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Script d'import complet des radars")
    print("=" * 50)
    
    # Télécharger
    download_csv()
    
    # Importer
    import_radars()
    
    # Vérifier
    print("\n🔍 Vérification...")
    conn = sqlite3.connect('radars.db')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM radars')
    count = cur.fetchone()[0]
    print(f"✅ {count} radars dans la base de données")
    conn.close()
    
    print("=" * 50)

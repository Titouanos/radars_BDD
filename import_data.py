import csv
import sqlite3
from database import init_database, get_connection, clear_database
import os

CSV_FILE = "radars.csv"

def import_radars_from_csv():
    """Importe les données du fichier CSV dans la base de données"""
    
    if not os.path.exists(CSV_FILE):
        print(f"❌ Erreur : le fichier {CSV_FILE} n'existe pas")
        print("Veuillez télécharger le fichier depuis data.gouv.fr")
        return
    
    # Initialiser la base de données
    print("📊 Initialisation de la base de données...")
    init_database()
    
    # Effacer les anciennes données si elles existent
    print("🗑️  Nettoyage des anciennes données...")
    clear_database()
    
    # Lire et importer les données
    print(f"📁 Lecture du fichier {CSV_FILE}...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    imported_count = 0
    error_count = 0
    
    try:
        with open(CSV_FILE, 'r', encoding='latin-1') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            
            print(f"📋 Colonnes trouvées dans le CSV: {csv_reader.fieldnames}")
            
            for i, row in enumerate(csv_reader):
                if i == 0:
                    print(f"🔍 Première ligne: {row}")
                
                try:
                    # Extraction et nettoyage des données
                    numero = row.get('Numéro de radar', '').strip()
                    radar_type = row.get('Type', '').strip()
                    date_service = row.get('Date de mise en service', '').strip()
                    voie = row.get('Voie', '').strip()
                    sens = row.get('Sens', '').strip()
                    
                    # Conversion de la vitesse
                    vitesse_str = row.get('Vitesse', '').strip()
                    vitesse = int(vitesse_str) if vitesse_str and vitesse_str.isdigit() else None
                    
                    # Conversion des coordonnées
                    latitude_str = row.get('Latitude', '').strip().replace('+', '')
                    longitude_str = row.get('Longitude', '').strip().replace('+', '')
                    
                    if not latitude_str or not longitude_str:
                        error_count += 1
                        if i < 5:
                            print(f"⚠️  Ligne {i+1}: Coordonnées manquantes")
                        continue
                    
                    latitude = float(latitude_str)
                    longitude = float(longitude_str)
                    
                    # Insertion dans la base de données
                    cursor.execute("""
                        INSERT INTO radars (numero, type, date_mise_service, voie, sens, vitesse, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (numero, radar_type, date_service, voie, sens, vitesse, latitude, longitude))
                    
                    imported_count += 1
                    
                    if imported_count % 100 == 0:
                        print(f"  ⏳ {imported_count} radars importés...")
                    
                except (ValueError, KeyError) as e:
                    error_count += 1
                    if i < 10:
                        print(f"⚠️  Ligne {i+1}: Erreur {e}")
                    continue
        
        conn.commit()
        print(f"\n✅ Import terminé avec succès !")
        print(f"   📍 {imported_count} radars importés")
        if error_count > 0:
            print(f"   ⚠️  {error_count} entrées ignorées (données invalides)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import : {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Démarrage de l'import des données des radars...")
    print("=" * 50)
    import_radars_from_csv()
    print("=" * 50)

"""
Serveur API pour les radars - Charge les donnees depuis le CSV
"""
from flask import Flask, jsonify, send_from_directory
import csv
import os

app = Flask(__name__, static_folder='web')

def load_radars_from_csv():
    """Charge les radars depuis le fichier CSV"""
    radars = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'radars.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            try:
                lat = row.get('latitude', '')
                lon = row.get('longitude', '')
                if not lat or not lon:
                    continue
                    
                radar = {
                    'id': row.get('id', ''),
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'type': row.get('type', 'Radar'),
                    'vitesse_vl': row.get('vitesse_vehicules_legers_kmh', ''),
                    'vitesse_pl': row.get('vitesse_poids_lourds_kmh', ''),
                    'route': row.get('route', ''),
                    'direction': row.get('direction', '')
                }
                radars.append(radar)
            except (ValueError, KeyError) as e:
                continue
    
    return radars

# Cache des radars
RADARS_CACHE = None

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/api/radars')
def get_radars():
    global RADARS_CACHE
    if RADARS_CACHE is None:
        RADARS_CACHE = load_radars_from_csv()
    return jsonify(RADARS_CACHE)

if __name__ == '__main__':
    print("Serveur demarre sur http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

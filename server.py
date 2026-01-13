"""
Serveur API simple pour les radars - PostgreSQL
"""
from flask import Flask, jsonify, send_from_directory
import psycopg2
import os

app = Flask(__name__, static_folder='web')

# Configuration PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'radars'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/api/radars')
def get_radars():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT r.id, r.latitude, r.longitude, t.libelle as type,
               r.vitesse_vl_kmh, r.vitesse_pl_kmh, r.route, r.direction
        FROM radar r
        JOIN type_radar t ON r.type_id = t.id
    """)
    
    columns = ['id', 'latitude', 'longitude', 'type', 'vitesse_vl', 'vitesse_pl', 'route', 'direction']
    radars = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return jsonify(radars)

if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

import sqlite3
from typing import List, Optional, Dict, Any
import os

DATABASE_PATH = "radars.db"

def get_connection():
    """Crée et retourne une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données avec le schéma nécessaire"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Création de la table radars
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS radars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            type TEXT NOT NULL,
            date_mise_service TEXT,
            voie TEXT,
            sens TEXT,
            vitesse INTEGER,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)
    
    # Création des indexes pour optimiser les recherches
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_type ON radars(type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_vitesse ON radars(vitesse)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_location ON radars(latitude, longitude)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès")

def get_radars(
    page: int = 1,
    limit: int = 100,
    radar_type: Optional[str] = None,
    vitesse_min: Optional[int] = None,
    vitesse_max: Optional[int] = None,
    search: Optional[str] = None
) -> tuple[List[Dict[str, Any]], int]:
    """
    Récupère les radars avec filtrage et pagination
    
    Returns:
        tuple: (liste des radars, nombre total de résultats)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Construction de la requête avec filtres
    query = "SELECT * FROM radars WHERE 1=1"
    params = []
    
    if radar_type:
        query += " AND type = ?"
        params.append(radar_type)
    
    if vitesse_min is not None:
        query += " AND vitesse >= ?"
        params.append(vitesse_min)
    
    if vitesse_max is not None:
        query += " AND vitesse <= ?"
        params.append(vitesse_max)
    
    if search:
        query += " AND (voie LIKE ? OR sens LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])
    
    # Compte total pour la pagination
    count_query = f"SELECT COUNT(*) as total FROM ({query})"
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Ajout de la pagination
    offset = (page - 1) * limit
    query += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    # Exécution de la requête
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Conversion en dictionnaires
    radars = [dict(row) for row in rows]
    
    conn.close()
    return radars, total

def get_radar_by_id(radar_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un radar par son ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM radars WHERE id = ?", (radar_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_radar_types() -> List[str]:
    """Récupère la liste des types de radars disponibles"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT type FROM radars ORDER BY type")
    types = [row['type'] for row in cursor.fetchall()]
    
    conn.close()
    return types

def get_stats() -> Dict[str, Any]:
    """Récupère les statistiques sur les radars"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Nombre total
    cursor.execute("SELECT COUNT(*) as total FROM radars")
    total = cursor.fetchone()['total']
    
    # Répartition par type
    cursor.execute("""
        SELECT type, COUNT(*) as count 
        FROM radars 
        GROUP BY type 
        ORDER BY count DESC
    """)
    types_distribution = [dict(row) for row in cursor.fetchall()]
    
    # Vitesse moyenne
    cursor.execute("SELECT AVG(vitesse) as avg_speed FROM radars WHERE vitesse IS NOT NULL")
    avg_speed = cursor.fetchone()['avg_speed']
    
    # Vitesse min et max
    cursor.execute("SELECT MIN(vitesse) as min_speed, MAX(vitesse) as max_speed FROM radars WHERE vitesse IS NOT NULL")
    speed_range = cursor.fetchone()
    
    conn.close()
    
    return {
        "total": total,
        "types_distribution": types_distribution,
        "average_speed": round(avg_speed, 1) if avg_speed else None,
        "min_speed": speed_range['min_speed'],
        "max_speed": speed_range['max_speed']
    }

def clear_database():
    """Efface toutes les données de la table radars"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM radars")
    conn.commit()
    conn.close()
    print("✅ Données effacées")

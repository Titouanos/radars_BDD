#!/bin/bash
# =============================================================================
# Script d'import complet - Radars Automatiques France
# =============================================================================
# Usage: ./import.sh [nom_base] [fichier_csv]
# Exemple: ./import.sh radars_france data/radars.csv
# =============================================================================

set -e

# Paramètres
DB_NAME="${1:-radars_france}"
CSV_FILE="${2:-data/radars.csv}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 Import des radars dans la base '$DB_NAME'"
echo "📁 Fichier CSV: $CSV_FILE"
echo ""

# Vérification du fichier CSV
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ Erreur: Le fichier $CSV_FILE n'existe pas"
    echo "   Téléchargez-le depuis: https://www.data.gouv.fr/fr/datasets/radars-automatiques/"
    exit 1
fi

# Création de la base si nécessaire
echo "📦 Vérification de la base de données..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "   Création de la base $DB_NAME..."
    createdb "$DB_NAME"
fi

# Activation de PostGIS
echo "🌍 Activation de PostGIS..."
psql -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS postgis;" -q

# Exécution des scripts SQL
echo "📋 Création des tables..."
psql -d "$DB_NAME" -f "$SCRIPT_DIR/sql/01_create_tables.sql" -q

echo "📥 Import des données de référence..."
psql -d "$DB_NAME" -f "$SCRIPT_DIR/sql/02_import_data.sql" -q

echo "📊 Import du CSV ($CSV_FILE)..."
psql -d "$DB_NAME" -c "\copy radar_import FROM '$CSV_FILE' WITH (FORMAT csv, HEADER true, DELIMITER ',')" -q 2>/dev/null || true

# Transformation des données
echo "🔄 Transformation des données..."
psql -d "$DB_NAME" -q << 'EOF'
INSERT INTO radar (id, latitude, longitude, direction, emplacement, route, 
    longueur_troncon_km, vitesse_vl_kmh, vitesse_pl_kmh, date_installation, 
    date_creation, date_modification, type_id, equipement_id, departement_code)
SELECT 
    ri.id::INTEGER, ri.latitude::DECIMAL(9,6), ri.longitude::DECIMAL(9,6),
    NULLIF(TRIM(ri.direction), ''), NULLIF(TRIM(ri.emplacement), ''),
    NULLIF(TRIM(ri.route), ''), NULLIF(ri.longueur_troncon_km, '')::DECIMAL(5,2),
    NULLIF(ri.vitesse_vehicules_legers_kmh, '')::SMALLINT,
    NULLIF(ri.vitesse_poids_lourds_kmh, '')::SMALLINT,
    ri.date_installation::DATE, ri.date_heure_creation::TIMESTAMPTZ,
    ri.date_heure_dernier_changement::TIMESTAMPTZ, tr.id, eq.id, ri.departement
FROM radar_import ri
LEFT JOIN type_radar tr ON tr.libelle = ri.type
LEFT JOIN equipement eq ON eq.nom = ri.equipement
WHERE ri.id IS NOT NULL AND ri.id != 'id'
ON CONFLICT (id) DO UPDATE SET
    latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude,
    date_modification = EXCLUDED.date_modification;
EOF

echo "📇 Création des index..."
psql -d "$DB_NAME" -f "$SCRIPT_DIR/sql/03_indexes.sql" -q

# Statistiques finales
echo ""
echo "✅ Import terminé avec succès !"
echo ""
psql -d "$DB_NAME" -c "SELECT 'Radars' as table, COUNT(*) as lignes FROM radar 
    UNION ALL SELECT 'Types', COUNT(*) FROM type_radar
    UNION ALL SELECT 'Équipements', COUNT(*) FROM equipement
    UNION ALL SELECT 'Départements', COUNT(*) FROM departement
    UNION ALL SELECT 'Régions', COUNT(*) FROM region;"

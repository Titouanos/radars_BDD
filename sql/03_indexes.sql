-- =============================================================================
-- SCRIPT DE CRÉATION DES INDEX - Radars Automatiques France
-- =============================================================================
-- PostgreSQL 15+ avec PostGIS

-- Index spatial GIST (requêtes géospatiales)
CREATE INDEX IF NOT EXISTS idx_radar_geom ON radar USING GIST (geom);

-- Index sur clés étrangères
CREATE INDEX IF NOT EXISTS idx_radar_departement ON radar (departement_code);
CREATE INDEX IF NOT EXISTS idx_radar_type ON radar (type_id);
CREATE INDEX IF NOT EXISTS idx_radar_equipement ON radar (equipement_id);
CREATE INDEX IF NOT EXISTS idx_departement_region ON departement (region_code);

-- Index sur colonnes filtrées
CREATE INDEX IF NOT EXISTS idx_radar_vitesse_vl ON radar (vitesse_vl_kmh) WHERE vitesse_vl_kmh IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_radar_date_installation ON radar (date_installation);
CREATE INDEX IF NOT EXISTS idx_radar_route ON radar (route) WHERE route IS NOT NULL;

-- Index composites
CREATE INDEX IF NOT EXISTS idx_radar_type_dept ON radar (type_id, departement_code);
CREATE INDEX IF NOT EXISTS idx_radar_dept_vitesse ON radar (departement_code, vitesse_vl_kmh) WHERE vitesse_vl_kmh IS NOT NULL;

-- Mise à jour des statistiques
ANALYZE radar;
ANALYZE departement;
ANALYZE region;

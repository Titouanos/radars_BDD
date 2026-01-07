-- =============================================================================
-- REQUÊTES SQL MÉTIER - Radars Automatiques France
-- =============================================================================
-- 10 requêtes utiles pour l'exploitation des données
-- =============================================================================

-- -----------------------------------------------------------------------------
-- REQUÊTE 1 : Lister tous les radars par type
-- -----------------------------------------------------------------------------
SELECT 
    r.id,
    r.emplacement,
    r.route,
    r.vitesse_vl_kmh,
    t.libelle AS type_radar,
    d.nom AS departement
FROM radar r
JOIN type_radar t ON r.type_id = t.id
JOIN departement d ON r.departement_code = d.code
ORDER BY t.libelle, d.nom;

-- -----------------------------------------------------------------------------
-- REQUÊTE 2 : Lister les radars d'un département spécifique
-- -----------------------------------------------------------------------------
-- Exemple : département du Nord (59)
SELECT 
    r.id,
    t.libelle AS type,
    r.emplacement,
    r.route,
    r.direction,
    r.vitesse_vl_kmh,
    r.latitude,
    r.longitude
FROM radar r
JOIN type_radar t ON r.type_id = t.id
WHERE r.departement_code = '59'
ORDER BY t.libelle, r.route;

-- -----------------------------------------------------------------------------
-- REQUÊTE 3 : Compter les radars par type
-- -----------------------------------------------------------------------------
SELECT 
    t.libelle AS type_radar,
    COUNT(*) AS nombre,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pourcentage
FROM radar r
JOIN type_radar t ON r.type_id = t.id
GROUP BY t.libelle
ORDER BY nombre DESC;

-- -----------------------------------------------------------------------------
-- REQUÊTE 4 : Radars contrôlant une vitesse supérieure à X km/h
-- -----------------------------------------------------------------------------
-- Exemple : vitesse > 90 km/h (autoroutes et voies express)
SELECT 
    r.id,
    r.emplacement,
    r.route,
    r.vitesse_vl_kmh,
    r.direction,
    d.nom AS departement,
    t.libelle AS type
FROM radar r
JOIN departement d ON r.departement_code = d.code
JOIN type_radar t ON r.type_id = t.id
WHERE r.vitesse_vl_kmh > 90
ORDER BY r.vitesse_vl_kmh DESC, d.nom;

-- -----------------------------------------------------------------------------
-- REQUÊTE 5 : Statistiques par région
-- -----------------------------------------------------------------------------
SELECT 
    reg.nom AS region,
    COUNT(r.id) AS nb_radars,
    COUNT(DISTINCT r.departement_code) AS nb_departements,
    ROUND(AVG(r.vitesse_vl_kmh), 0) AS vitesse_moyenne_vl,
    COUNT(CASE WHEN t.libelle = 'Radar fixe' THEN 1 END) AS radars_fixes,
    COUNT(CASE WHEN t.libelle = 'Radar feu rouge' THEN 1 END) AS radars_feu_rouge,
    COUNT(CASE WHEN t.libelle = 'Radar discriminant' THEN 1 END) AS radars_discriminants
FROM radar r
JOIN departement d ON r.departement_code = d.code
JOIN region reg ON d.region_code = reg.code
JOIN type_radar t ON r.type_id = t.id
GROUP BY reg.code, reg.nom
ORDER BY nb_radars DESC;

-- -----------------------------------------------------------------------------
-- REQUÊTE 6 : Radars dans un rayon de X km d'un point GPS (PostGIS)
-- -----------------------------------------------------------------------------
-- Exemple : 10 km autour de la Tour Eiffel (48.8584, 2.2945)
SELECT 
    r.id,
    r.emplacement,
    r.route,
    r.vitesse_vl_kmh,
    t.libelle AS type,
    ROUND(ST_Distance(r.geom, ST_SetSRID(ST_MakePoint(2.2945, 48.8584), 4326)::GEOGRAPHY)::NUMERIC / 1000, 2) AS distance_km
FROM radar r
JOIN type_radar t ON r.type_id = t.id
WHERE ST_DWithin(
    r.geom,
    ST_SetSRID(ST_MakePoint(2.2945, 48.8584), 4326)::GEOGRAPHY,
    10000  -- 10 km en mètres
)
ORDER BY distance_km;

-- -----------------------------------------------------------------------------
-- REQUÊTE 7 : Top 10 des routes les plus équipées
-- -----------------------------------------------------------------------------
SELECT 
    r.route,
    COUNT(*) AS nb_radars,
    ARRAY_AGG(DISTINCT d.nom) AS departements_traverses,
    ROUND(AVG(r.vitesse_vl_kmh), 0) AS vitesse_moyenne,
    MIN(r.vitesse_vl_kmh) AS vitesse_min,
    MAX(r.vitesse_vl_kmh) AS vitesse_max
FROM radar r
JOIN departement d ON r.departement_code = d.code
WHERE r.route IS NOT NULL
GROUP BY r.route
ORDER BY nb_radars DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- REQUÊTE 8 : Évolution des installations par année
-- -----------------------------------------------------------------------------
SELECT 
    EXTRACT(YEAR FROM date_installation) AS annee,
    COUNT(*) AS nb_installations,
    SUM(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM date_installation)) AS cumul
FROM radar
GROUP BY EXTRACT(YEAR FROM date_installation)
ORDER BY annee;

-- -----------------------------------------------------------------------------
-- REQUÊTE 9 : Radars discriminants avec vitesses différenciées PL/VL
-- -----------------------------------------------------------------------------
SELECT 
    r.id,
    r.emplacement,
    r.route,
    r.vitesse_vl_kmh AS "Vitesse VL",
    r.vitesse_pl_kmh AS "Vitesse PL",
    r.vitesse_vl_kmh - r.vitesse_pl_kmh AS "Différence",
    d.nom AS departement
FROM radar r
JOIN departement d ON r.departement_code = d.code
JOIN type_radar t ON r.type_id = t.id
WHERE t.libelle = 'Radar discriminant'
    AND r.vitesse_vl_kmh IS NOT NULL 
    AND r.vitesse_pl_kmh IS NOT NULL
ORDER BY r.vitesse_vl_kmh - r.vitesse_pl_kmh DESC;

-- -----------------------------------------------------------------------------
-- REQUÊTE 10 : Densité de radars par département (avec superficie)
-- -----------------------------------------------------------------------------
-- Note : nécessite une table des superficies ou un calcul approximatif
SELECT 
    d.code,
    d.nom AS departement,
    reg.nom AS region,
    COUNT(r.id) AS nb_radars,
    STRING_AGG(DISTINCT t.libelle, ', ' ORDER BY t.libelle) AS types_presents
FROM departement d
JOIN region reg ON d.region_code = reg.code
LEFT JOIN radar r ON r.departement_code = d.code
LEFT JOIN type_radar t ON r.type_id = t.id
GROUP BY d.code, d.nom, reg.nom
HAVING COUNT(r.id) > 0
ORDER BY nb_radars DESC;

-- =============================================================================
-- REQUÊTES BONUS
-- =============================================================================

-- BONUS 1 : Recherche de radars par nom de route (recherche partielle)
SELECT * FROM radar WHERE route ILIKE '%A1%';

-- BONUS 2 : Export GeoJSON pour cartographie
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(r.geom)::json,
            'properties', json_build_object(
                'id', r.id,
                'type', t.libelle,
                'vitesse', r.vitesse_vl_kmh,
                'route', r.route
            )
        )
    )
) AS geojson
FROM radar r
JOIN type_radar t ON r.type_id = t.id
LIMIT 100;

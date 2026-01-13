-- =============================================================================
-- SCRIPT D'IMPORT DES DONNÉES - Radars Automatiques France
-- =============================================================================
-- SGBD         : PostgreSQL 15+ avec PostGIS 3.3+
-- Auteur       : Projet ESIR BDD
-- Date         : 05/01/2026
-- Description  : Import des données de référence et des radars depuis CSV
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. INSERTION DES RÉGIONS
-- -----------------------------------------------------------------------------
INSERT INTO region (code, nom) VALUES
    ('84', 'Auvergne-Rhône-Alpes'),
    ('27', 'Bourgogne-Franche-Comté'),
    ('53', 'Bretagne'),
    ('24', 'Centre-Val de Loire'),
    ('94', 'Corse'),
    ('44', 'Grand Est'),
    ('32', 'Hauts-de-France'),
    ('11', 'Île-de-France'),
    ('28', 'Normandie'),
    ('75', 'Nouvelle-Aquitaine'),
    ('76', 'Occitanie'),
    ('52', 'Pays de la Loire'),
    ('93', 'Provence-Alpes-Côte d''Azur'),
    ('01', 'Guadeloupe'),
    ('02', 'Martinique'),
    ('03', 'Guyane'),
    ('04', 'La Réunion'),
    ('06', 'Mayotte')
ON CONFLICT (code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. INSERTION DES DÉPARTEMENTS
-- -----------------------------------------------------------------------------
INSERT INTO departement (code, nom, region_code) VALUES
    -- Auvergne-Rhône-Alpes (84)
    ('01', 'Ain', '84'),
    ('03', 'Allier', '84'),
    ('07', 'Ardèche', '84'),
    ('15', 'Cantal', '84'),
    ('26', 'Drôme', '84'),
    ('38', 'Isère', '84'),
    ('42', 'Loire', '84'),
    ('43', 'Haute-Loire', '84'),
    ('63', 'Puy-de-Dôme', '84'),
    ('69', 'Rhône', '84'),
    ('73', 'Savoie', '84'),
    ('74', 'Haute-Savoie', '84'),
    -- Bourgogne-Franche-Comté (27)
    ('21', 'Côte-d''Or', '27'),
    ('25', 'Doubs', '27'),
    ('39', 'Jura', '27'),
    ('58', 'Nièvre', '27'),
    ('70', 'Haute-Saône', '27'),
    ('71', 'Saône-et-Loire', '27'),
    ('89', 'Yonne', '27'),
    ('90', 'Territoire de Belfort', '27'),
    -- Bretagne (53)
    ('22', 'Côtes-d''Armor', '53'),
    ('29', 'Finistère', '53'),
    ('35', 'Ille-et-Vilaine', '53'),
    ('56', 'Morbihan', '53'),
    -- Centre-Val de Loire (24)
    ('18', 'Cher', '24'),
    ('28', 'Eure-et-Loir', '24'),
    ('36', 'Indre', '24'),
    ('37', 'Indre-et-Loire', '24'),
    ('41', 'Loir-et-Cher', '24'),
    ('45', 'Loiret', '24'),
    -- Corse (94)
    ('2A', 'Corse-du-Sud', '94'),
    ('2B', 'Haute-Corse', '94'),
    -- Grand Est (44)
    ('08', 'Ardennes', '44'),
    ('10', 'Aube', '44'),
    ('51', 'Marne', '44'),
    ('52', 'Haute-Marne', '44'),
    ('54', 'Meurthe-et-Moselle', '44'),
    ('55', 'Meuse', '44'),
    ('57', 'Moselle', '44'),
    ('67', 'Bas-Rhin', '44'),
    ('68', 'Haut-Rhin', '44'),
    ('88', 'Vosges', '44'),
    -- Hauts-de-France (32)
    ('02', 'Aisne', '32'),
    ('59', 'Nord', '32'),
    ('60', 'Oise', '32'),
    ('62', 'Pas-de-Calais', '32'),
    ('80', 'Somme', '32'),
    -- Île-de-France (11)
    ('75', 'Paris', '11'),
    ('77', 'Seine-et-Marne', '11'),
    ('78', 'Yvelines', '11'),
    ('91', 'Essonne', '11'),
    ('92', 'Hauts-de-Seine', '11'),
    ('93', 'Seine-Saint-Denis', '11'),
    ('94', 'Val-de-Marne', '11'),
    ('95', 'Val-d''Oise', '11'),
    -- Normandie (28)
    ('14', 'Calvados', '28'),
    ('27', 'Eure', '28'),
    ('50', 'Manche', '28'),
    ('61', 'Orne', '28'),
    ('76', 'Seine-Maritime', '28'),
    -- Nouvelle-Aquitaine (75)
    ('16', 'Charente', '75'),
    ('17', 'Charente-Maritime', '75'),
    ('19', 'Corrèze', '75'),
    ('23', 'Creuse', '75'),
    ('24', 'Dordogne', '75'),
    ('33', 'Gironde', '75'),
    ('40', 'Landes', '75'),
    ('47', 'Lot-et-Garonne', '75'),
    ('64', 'Pyrénées-Atlantiques', '75'),
    ('79', 'Deux-Sèvres', '75'),
    ('86', 'Vienne', '75'),
    ('87', 'Haute-Vienne', '75'),
    -- Occitanie (76)
    ('09', 'Ariège', '76'),
    ('11', 'Aude', '76'),
    ('12', 'Aveyron', '76'),
    ('30', 'Gard', '76'),
    ('31', 'Haute-Garonne', '76'),
    ('32', 'Gers', '76'),
    ('34', 'Hérault', '76'),
    ('46', 'Lot', '76'),
    ('48', 'Lozère', '76'),
    ('65', 'Hautes-Pyrénées', '76'),
    ('66', 'Pyrénées-Orientales', '76'),
    ('81', 'Tarn', '76'),
    ('82', 'Tarn-et-Garonne', '76'),
    -- Pays de la Loire (52)
    ('44', 'Loire-Atlantique', '52'),
    ('49', 'Maine-et-Loire', '52'),
    ('53', 'Mayenne', '52'),
    ('72', 'Sarthe', '52'),
    ('85', 'Vendée', '52'),
    -- Provence-Alpes-Côte d'Azur (93)
    ('04', 'Alpes-de-Haute-Provence', '93'),
    ('05', 'Hautes-Alpes', '93'),
    ('06', 'Alpes-Maritimes', '93'),
    ('13', 'Bouches-du-Rhône', '93'),
    ('83', 'Var', '93'),
    ('84', 'Vaucluse', '93'),
    -- Outre-mer
    ('971', 'Guadeloupe', '01'),
    ('972', 'Martinique', '02'),
    ('973', 'Guyane', '03'),
    ('974', 'La Réunion', '04'),
    ('976', 'Mayotte', '06')
ON CONFLICT (code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. INSERTION DES TYPES DE RADARS
-- -----------------------------------------------------------------------------
INSERT INTO type_radar (id, libelle, description, controle_vitesse) VALUES
    (1, 'Radar fixe', 'Radar de vitesse fixe classique, contrôle dans un sens', TRUE),
    (2, 'Radar discriminant', 'Radar différenciant véhicules légers et poids lourds', TRUE),
    (3, 'Radar Vitesse Moyenne', 'Radar tronçon calculant la vitesse moyenne', TRUE),
    (4, 'Radar feu rouge', 'Radar de franchissement de feu rouge', FALSE),
    (5, 'Radar Passage à Niveau', 'Radar de franchissement de passage à niveau', FALSE),
    (6, 'Itinéraire', 'Section de radar vitesse moyenne (point intermédiaire)', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Reset sequence après insertion manuelle des IDs
SELECT setval('type_radar_id_seq', (SELECT MAX(id) FROM type_radar));

-- -----------------------------------------------------------------------------
-- 4. INSERTION DES ÉQUIPEMENTS
-- -----------------------------------------------------------------------------
INSERT INTO equipement (id, nom, pays) VALUES
    (1, 'MORPHO', 'France'),
    (2, 'PARIFEX', 'France'),
    (3, 'FARECO', 'France'),
    (4, 'AXIMUM', 'France')
ON CONFLICT (id) DO NOTHING;

-- Reset sequence après insertion manuelle des IDs
SELECT setval('equipement_id_seq', (SELECT MAX(id) FROM equipement));

-- -----------------------------------------------------------------------------
-- 5. CRÉATION DE LA TABLE TEMPORAIRE POUR L'IMPORT CSV
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS radar_import;

CREATE TEMPORARY TABLE radar_import (
    date_heure_dernier_changement TEXT,
    date_heure_creation TEXT,
    departement TEXT,
    latitude TEXT,
    longitude TEXT,
    id TEXT,
    direction TEXT,
    equipement TEXT,
    date_installation TEXT,
    type TEXT,
    emplacement TEXT,
    route TEXT,
    longueur_troncon_km TEXT,
    vitesse_poids_lourds_kmh TEXT,
    vitesse_vehicules_legers_kmh TEXT
);

-- -----------------------------------------------------------------------------
-- 6. IMPORT DU FICHIER CSV
-- -----------------------------------------------------------------------------
-- IMPORTANT : Adapter le chemin du fichier selon votre installation
-- Option 1 : Chemin absolu (modifier selon votre environnement)
-- Option 2 : Utiliser \copy depuis psql

-- Exemple avec COPY (nécessite droits superuser) :
-- COPY radar_import FROM '/chemin/vers/radars.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Exemple avec \copy depuis psql (recommandé) :
-- \copy radar_import FROM 'data/radars.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- -----------------------------------------------------------------------------
-- 7. TRANSFORMATION ET INSERTION DES RADARS
-- -----------------------------------------------------------------------------
-- Cette requête transforme les données brutes en données normalisées

INSERT INTO radar (
    id,
    latitude,
    longitude,
    direction,
    emplacement,
    route,
    longueur_troncon_km,
    vitesse_vl_kmh,
    vitesse_pl_kmh,
    date_installation,
    date_creation,
    date_modification,
    type_id,
    equipement_id,
    departement_code
)
SELECT 
    ri.id::INTEGER,
    ri.latitude::DECIMAL(9,6),
    ri.longitude::DECIMAL(9,6),
    NULLIF(TRIM(ri.direction), ''),
    NULLIF(TRIM(ri.emplacement), ''),
    NULLIF(TRIM(ri.route), ''),
    NULLIF(ri.longueur_troncon_km, '')::DECIMAL(5,2),
    NULLIF(ri.vitesse_vehicules_legers_kmh, '')::SMALLINT,
    NULLIF(ri.vitesse_poids_lourds_kmh, '')::SMALLINT,
    ri.date_installation::DATE,
    ri.date_heure_creation::TIMESTAMPTZ,
    ri.date_heure_dernier_changement::TIMESTAMPTZ,
    tr.id,
    eq.id,
    ri.departement
FROM radar_import ri
LEFT JOIN type_radar tr ON tr.libelle = ri.type
LEFT JOIN equipement eq ON eq.nom = ri.equipement
WHERE ri.id IS NOT NULL
    AND ri.id != 'id'  -- Exclure l'en-tête si présent
ON CONFLICT (id) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    direction = EXCLUDED.direction,
    emplacement = EXCLUDED.emplacement,
    route = EXCLUDED.route,
    longueur_troncon_km = EXCLUDED.longueur_troncon_km,
    vitesse_vl_kmh = EXCLUDED.vitesse_vl_kmh,
    vitesse_pl_kmh = EXCLUDED.vitesse_pl_kmh,
    date_modification = EXCLUDED.date_modification,
    type_id = EXCLUDED.type_id,
    equipement_id = EXCLUDED.equipement_id;

-- -----------------------------------------------------------------------------
-- 8. NETTOYAGE
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS radar_import;

-- -----------------------------------------------------------------------------
-- 9. VÉRIFICATION DE L'IMPORT
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    v_count_radars INTEGER;
    v_count_types INTEGER;
    v_count_equip INTEGER;
    v_count_dept INTEGER;
    v_count_regions INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count_radars FROM radar;
    SELECT COUNT(*) INTO v_count_types FROM type_radar;
    SELECT COUNT(*) INTO v_count_equip FROM equipement;
    SELECT COUNT(*) INTO v_count_dept FROM departement;
    SELECT COUNT(*) INTO v_count_regions FROM region;
    
    RAISE NOTICE '✅ Import terminé avec succès :';
    RAISE NOTICE '   - Régions      : %', v_count_regions;
    RAISE NOTICE '   - Départements : %', v_count_dept;
    RAISE NOTICE '   - Types        : %', v_count_types;
    RAISE NOTICE '   - Équipements  : %', v_count_equip;
    RAISE NOTICE '   - Radars       : %', v_count_radars;
END $$;

-- =============================================================================
-- INSTRUCTIONS D'UTILISATION
-- =============================================================================
-- 
-- 1. Exécuter d'abord 01_create_tables.sql
-- 
-- 2. Pour importer le CSV, utiliser psql :
--    
--    psql -d votre_base -f sql/02_import_data.sql
--    
--    Puis importer le CSV manuellement :
--    
--    \copy radar_import FROM 'data/radars.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
--    
-- 3. Ou créer un script shell combiné (voir import.sh)
--
-- =============================================================================

-- =============================================================================
-- SCRIPT DE CRÉATION DES TABLES - Radars Automatiques France
-- =============================================================================
-- SGBD         : PostgreSQL 15+ avec PostGIS 3.3+
-- Auteur       : Projet ESIR BDD
-- Date         : 05/01/2026
-- Description  : Création du schéma de base de données pour les radars
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. EXTENSIONS REQUISES
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS postgis;

-- -----------------------------------------------------------------------------
-- 1. SUPPRESSION DES TABLES EXISTANTES (ordre inverse des dépendances)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS radar CASCADE;
DROP TABLE IF EXISTS equipement CASCADE;
DROP TABLE IF EXISTS type_radar CASCADE;
DROP TABLE IF EXISTS departement CASCADE;
DROP TABLE IF EXISTS region CASCADE;

-- -----------------------------------------------------------------------------
-- 2. TABLE REGION
-- -----------------------------------------------------------------------------
-- Régions administratives de France (18 régions depuis 2016)

CREATE TABLE region (
    code        VARCHAR(3)   PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL UNIQUE,
    
    -- Métadonnées
    CONSTRAINT chk_region_code CHECK (code ~ '^[0-9]{1,2}$')
);

COMMENT ON TABLE region IS 'Régions administratives françaises';
COMMENT ON COLUMN region.code IS 'Code INSEE de la région';
COMMENT ON COLUMN region.nom IS 'Nom officiel de la région';

-- -----------------------------------------------------------------------------
-- 3. TABLE DEPARTEMENT
-- -----------------------------------------------------------------------------
-- Départements français (101 départements)

CREATE TABLE departement (
    code        VARCHAR(3)   PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    region_code VARCHAR(3)   NOT NULL,
    
    -- Contraintes
    CONSTRAINT fk_departement_region 
        FOREIGN KEY (region_code) 
        REFERENCES region(code) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    CONSTRAINT chk_departement_code 
        CHECK (code ~ '^[0-9]{1,3}$' OR code IN ('2A', '2B'))
);

COMMENT ON TABLE departement IS 'Départements français';
COMMENT ON COLUMN departement.code IS 'Code INSEE du département (ex: 01, 2A, 974)';
COMMENT ON COLUMN departement.nom IS 'Nom du département';
COMMENT ON COLUMN departement.region_code IS 'Code de la région de rattachement';

-- -----------------------------------------------------------------------------
-- 4. TABLE TYPE_RADAR
-- -----------------------------------------------------------------------------
-- Types de radars automatiques (6 types identifiés)

CREATE TABLE type_radar (
    id               SERIAL      PRIMARY KEY,
    libelle          VARCHAR(50) NOT NULL UNIQUE,
    description      TEXT,
    controle_vitesse BOOLEAN     NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE type_radar IS 'Classification des types de radars automatiques';
COMMENT ON COLUMN type_radar.libelle IS 'Libellé du type de radar';
COMMENT ON COLUMN type_radar.controle_vitesse IS 'Indique si ce type contrôle la vitesse';

-- -----------------------------------------------------------------------------
-- 5. TABLE EQUIPEMENT
-- -----------------------------------------------------------------------------
-- Fabricants/équipementiers des radars

CREATE TABLE equipement (
    id   SERIAL      PRIMARY KEY,
    nom  VARCHAR(50) NOT NULL UNIQUE,
    pays VARCHAR(50) DEFAULT 'France'
);

COMMENT ON TABLE equipement IS 'Fabricants des équipements radar';
COMMENT ON COLUMN equipement.nom IS 'Nom du fabricant';
COMMENT ON COLUMN equipement.pays IS 'Pays d''origine du fabricant';

-- -----------------------------------------------------------------------------
-- 6. TABLE RADAR
-- -----------------------------------------------------------------------------
-- Table principale des radars automatiques

CREATE TABLE radar (
    -- Identifiant
    id                    INTEGER       PRIMARY KEY,
    
    -- Géolocalisation (double stockage pour compatibilité et performance)
    geom                  GEOGRAPHY(POINT, 4326),  -- Colonne PostGIS pour requêtes spatiales
    latitude              DECIMAL(9,6)  NOT NULL,
    longitude             DECIMAL(9,6)  NOT NULL,
    
    -- Informations de localisation
    direction             VARCHAR(255),
    emplacement           VARCHAR(255),
    route                 VARCHAR(100),
    
    -- Paramètres de contrôle
    longueur_troncon_km   DECIMAL(5,2),
    vitesse_vl_kmh        SMALLINT,
    vitesse_pl_kmh        SMALLINT,
    
    -- Dates
    date_installation     DATE          NOT NULL,
    date_creation         TIMESTAMPTZ   NOT NULL,
    date_modification     TIMESTAMPTZ   NOT NULL,
    
    -- Clés étrangères
    type_id               INTEGER       NOT NULL,
    equipement_id         INTEGER,
    departement_code      VARCHAR(3)    NOT NULL,
    
    -- Contraintes de clés étrangères
    CONSTRAINT fk_radar_type 
        FOREIGN KEY (type_id) 
        REFERENCES type_radar(id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_radar_equipement 
        FOREIGN KEY (equipement_id) 
        REFERENCES equipement(id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_radar_departement 
        FOREIGN KEY (departement_code) 
        REFERENCES departement(code) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    -- Contraintes de validation
    CONSTRAINT chk_latitude 
        CHECK (latitude BETWEEN -90 AND 90),
    
    CONSTRAINT chk_longitude 
        CHECK (longitude BETWEEN -180 AND 180),
    
    CONSTRAINT chk_vitesse_vl 
        CHECK (vitesse_vl_kmh IS NULL OR vitesse_vl_kmh BETWEEN 20 AND 150),
    
    CONSTRAINT chk_vitesse_pl 
        CHECK (vitesse_pl_kmh IS NULL OR vitesse_pl_kmh BETWEEN 20 AND 110),
    
    CONSTRAINT chk_longueur_troncon 
        CHECK (longueur_troncon_km IS NULL OR longueur_troncon_km > 0),
    
    CONSTRAINT chk_dates_coherentes 
        CHECK (date_installation <= date_creation::DATE)
);

COMMENT ON TABLE radar IS 'Radars automatiques fixes en France';
COMMENT ON COLUMN radar.id IS 'Identifiant unique du radar (source data.gouv.fr)';
COMMENT ON COLUMN radar.geom IS 'Point géographique PostGIS (SRID 4326 / WGS84)';
COMMENT ON COLUMN radar.latitude IS 'Latitude WGS84';
COMMENT ON COLUMN radar.longitude IS 'Longitude WGS84';
COMMENT ON COLUMN radar.direction IS 'Direction de circulation contrôlée';
COMMENT ON COLUMN radar.emplacement IS 'Lieu-dit ou adresse précise';
COMMENT ON COLUMN radar.route IS 'Identifiant de la route (A1, RN20, RD904, etc.)';
COMMENT ON COLUMN radar.longueur_troncon_km IS 'Longueur du tronçon pour radars vitesse moyenne';
COMMENT ON COLUMN radar.vitesse_vl_kmh IS 'Vitesse limite contrôlée pour véhicules légers (km/h)';
COMMENT ON COLUMN radar.vitesse_pl_kmh IS 'Vitesse limite contrôlée pour poids lourds (km/h)';
COMMENT ON COLUMN radar.date_installation IS 'Date de mise en service du radar';
COMMENT ON COLUMN radar.date_creation IS 'Date de création de l''enregistrement';
COMMENT ON COLUMN radar.date_modification IS 'Date de dernière modification';

-- -----------------------------------------------------------------------------
-- 7. TRIGGER POUR AUTO-GÉNÉRER LA COLONNE GEOM
-- -----------------------------------------------------------------------------
-- Crée automatiquement le point PostGIS à partir de lat/lon lors de l'insertion

CREATE OR REPLACE FUNCTION update_radar_geom()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::GEOGRAPHY;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_radar_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude
    ON radar
    FOR EACH ROW
    EXECUTE FUNCTION update_radar_geom();

COMMENT ON FUNCTION update_radar_geom() IS 'Met à jour automatiquement la colonne geom basée sur lat/lon';

-- -----------------------------------------------------------------------------
-- 8. VÉRIFICATION DE LA CRÉATION
-- -----------------------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '✅ Tables créées avec succès :';
    RAISE NOTICE '   - region';
    RAISE NOTICE '   - departement';
    RAISE NOTICE '   - type_radar';
    RAISE NOTICE '   - equipement';
    RAISE NOTICE '   - radar';
    RAISE NOTICE '✅ Trigger geom créé';
END $$;

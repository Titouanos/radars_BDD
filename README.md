# 🚀 Guide de Lancement Rapide

## Prérequis
- PostgreSQL 16+
- PostGIS
- Python 3 (pour le serveur web)

## 1. Installer la base de données
```bash
# Créer la base et importer les données
./import.sh radars_france data/radars.csv
```

## 2. Lancer l'interface web
```bash
cd web
python3 -m http.server 8080
```
Puis ouvrir : **http://localhost:8080**

## 3. Tester les requêtes SQL
```bash
psql -d radars_france -f sql/04_queries.sql
```

---

## Structure du projet
```
├── sql/                    # Scripts SQL
│   ├── 01_create_tables.sql
│   ├── 02_import_data.sql
│   ├── 03_indexes.sql
│   └── 04_queries.sql
├── web/                    # Interface web
│   ├── index.html
│   └── data/radars.json
├── data/radars.csv         # Données source
└── import.sh               # Script d'installation
```

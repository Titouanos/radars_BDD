# 📍 Radars Fixes en France

Application web interactive pour visualiser et filtrer les **3400+ radars fixes** répertoriés en France. Données officielles de **data.gouv.fr**.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)

## ✨ Fonctionnalités

- 🗺️ **Carte interactive** avec clustering des radars
- 🔍 **Filtrage avancé** par type de radar et vitesse
- 📊 **Statistiques en temps réel**
- 🎨 **Interface moderne** avec design glassmorphism
- 📱 **Responsive** - fonctionne sur mobile, tablette et desktop
- ⚡ **Performance optimisée** avec SQLite

## 🚀 Types de Radars

- **ETD** 🎯 : Radar fixe discriminant
- **ETFR** 🚦 : Radar feu rouge
- **ETPN** 🚂 : Radar passage à niveau
- **ETT** ⚡ : Radar fixe nouvelle génération
- **ETU** 🏙️ : Radar fixe nouvelle génération urbain
- **ETVM** 📏 : Radar tronçon (vitesse moyenne)

## 📋 Installation

### Prérequis

- Python 3.8+
- pip

### Étapes

1. **Installer les dépendances Python**

```bash
pip install -r requirements.txt
```

2. **Importer les données dans la base de données**

```bash
python import_data.py
```

Cette commande va :
- Créer la base de données SQLite `radars.db`
- Importer les ~3400 radars depuis le fichier CSV
- Créer les indexes pour optimiser les performances

3. **Lancer le serveur**

```bash
python main.py
```

Ou avec uvicorn :

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Accéder à l'application**

- **Interface web** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **API alternative** : http://localhost:8000/redoc

## 🛠️ Architecture

### Backend (Python)

- **FastAPI** : Framework web moderne et rapide
- **SQLite** : Base de données légère
- **Pydantic** : Validation des données
- **Uvicorn** : Serveur ASGI

### Frontend

- **HTML5** : Structure sémantique
- **CSS3** : Design moderne avec variables CSS et animations
- **JavaScript** : Logique côté client
- **Leaflet.js** : Carte interactive
- **Leaflet.markercluster** : Clustering des marqueurs

## 📡 API Endpoints

### `GET /api/radars`

Liste tous les radars avec pagination et filtres.

**Query Parameters:**
- `page` : Numéro de page (défaut: 1)
- `limit` : Résultats par page (défaut: 100, max: 1000)
- `type` : Filtrer par type (ETD, ETFR, etc.)
- `vitesse_min` : Vitesse minimale
- `vitesse_max` : Vitesse maximale
- `search` : Recherche textuelle

**Exemple:**
```bash
curl "http://localhost:8000/api/radars?type=ETD&vitesse_min=90&limit=10"
```

### `GET /api/radars/{id}`

Récupère les détails d'un radar spécifique.

### `GET /api/types`

Liste tous les types de radars disponibles.

### `GET /api/stats`

Statistiques globales (total, répartition par type, vitesses).

## 📊 Source des Données

Les données proviennent du jeu de données officiel **"Liste des radars fixes en France"** disponible sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/liste-des-radars-fixes-en-france/).

Source : Ministère de l'Intérieur - Sécurité Routière

## 🎨 Captures d'écran

L'interface propose :
- Une carte interactive en plein écran
- Un panneau latéral de filtres avec glassmorphism
- Des statistiques en temps réel
- Un design dark mode moderne
- Des animations fluides

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 Licence

Ce projet utilise des données ouvertes sous Licence Ouverte / Open Licence.

## 🔮 Améliorations Futures

- [ ] Simulation d'itinéraire avec radars rencontrés
- [ ] Export des données filtrées (CSV, JSON)
- [ ] Mode Street View sur les radars
- [ ] Notifications de nouveaux radars
- [ ] Support multi-langues

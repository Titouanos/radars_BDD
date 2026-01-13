# 📍 Radars Fixes en France

Application **desktop Python** pour visualiser et filtrer les **3400+ radars fixes** répertoriés en France. Données officielles de **data.gouv.fr**.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)

## ✨ Fonctionnalités

- 🗺️ **Carte interactive** avec tkintermapview (OpenStreetMap)
- 🔍 **Filtrage avancé** par type de radar et vitesse
- 📊 **Statistiques en temps réel**
- 🎨 **Interface moderne** avec CustomTkinter (dark mode)
- 🖥️ **Application desktop** - pas besoin de navigateur
- ⚡ **Performance optimisée** avec SQLite
- 📦 **Standalone** - fonctionne offline après installation

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
pip install tkintermapview Pillow customtkinter
```

2. **Importer les données dans la base de données**

```bash
python import_data.py
```

Cette commande va :
- Créer la base de données SQLite `radars.db`
- Importer les ~3400 radars depuis le fichier CSV
- Créer les indexes pour optimiser les performances

3. **Lancer l'application GUI**

```bash
python app_gui.py
```

L'application s'ouvrira dans une fenêtre desktop (1400x900 pixels).

## 🛠️ Architecture

### Backend (Python)

- **SQLite** : Base de données légère
- **database.py** : Fonctions CRUD pour accès aux données

### Interface Graphique

- **CustomTkinter** : Interface moderne (dark mode)
- **tkintermapview** : Carte OpenStreetMap interactive
- **Pillow** : Gestion des images
- **Threading** : Chargement asynchrone des données

## 🖱️ Utilisation de l'Interface

### Panneau de Filtres (Gauche)

- **Types de radars** : Cocher/décocher les types à afficher
- **Vitesse** : Entrer une vitesse min/max pour filtrer
- **Recherche** : Taper une route (ex: "A1") ou ville
- **Appliquer** : Applique les filtres sélectionnés
- **Réinitialiser** : Réinitialise tous les filtres

### Carte Interactive (Droite)

- **Navigation** : Clic gauche + glisser pour déplacer la carte
- **Zoom** : Molette de la souris ou boutons +/-
- **Marqueurs** : Cliquer sur un radar pour voir ses détails
- **Affichage** : Jusqu'à 2000 radars simultanément pour performance

### Statistiques

- **Total** : Nombre total de radars dans la base
- **Affichés** : Nombre de radars correspondant aux filtres
- **Vitesse moy** : Vitesse moyenne des radars affichés

## 📊 Source des Données

Les données proviennent du jeu de données officiel **"Liste des radars fixes en France"** disponible sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/liste-des-radars-fixes-en-france/).

Source : Ministère de l'Intérieur - Sécurité Routière

## 🎨 Interface

L'application propose :
- Une fenêtre desktop moderne (1400x900)
- Panneau de filtres à gauche (320px)
- Carte interactive à droite avec OpenStreetMap
- Design dark mode avec CustomTkinter
- Popups détaillées au clic sur radar
- Statistiques en temps réel

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

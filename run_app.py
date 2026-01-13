#!/usr/bin/env python3
"""
Script de lancement simple pour l'application de visualisation des radars
"""

import sys
import os

def main():
    print("🚀 Démarrage de l'application Radars France...")
    print("=" * 60)
    
    # Vérifier que la base de données existe
    if not os.path.exists("radars.db"):
        print("⚠️  ATTENTION: Base de données 'radars.db' non trouvée!")
        print("📝 Veuillez d'abord importer les données avec:")
        print("   python import_complete.py")
        sys.exit(1)
    
    # Importer et lancer l'application
    try:
        from app_gui import RadarApp
        print("✅ Chargement de l'interface graphique...")
        print("=" * 60)
        print()
        print("🗺️  L'application va s'ouvrir dans une nouvelle fenêtre")
        print("📍 Fonctionnalités disponibles:")
        print("   - Carte interactive avec tous les radars de France")
        print("   - Filtres par type de radar")
        print("   - Filtres par vitesse")
        print("   - Recherche par route/ville")
        print("   - Clic sur un radar pour voir les détails")
        print()
        print("=" * 60)
        
        app = RadarApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print()
        print("📦 Installez les dépendances requises avec:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

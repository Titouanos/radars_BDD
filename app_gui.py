"""
Application GUI pour visualiser les radars fixes en France
Utilise Tkinter pour l'interface et tkintermapview pour la carte
"""

import customtkinter as ctk
from tkintermapview import TkinterMapView
from database import get_radars, get_radar_types, get_stats
from typing import Dict, List
import threading

# Configuration des couleurs pour chaque type de radar
RADAR_COLORS = {
    'ETD': '#3b82f6',   # Bleu
    'ETFR': '#ef4444',  # Rouge  
    'ETPN': '#f59e0b',  # Orange
    'ETT': '#8b5cf6',   # Violet
    'ETU': '#ec4899',   # Rose
    'ETVM': '#10b981'   # Vert
}

RADAR_NAMES = {
    'ETD': '🎯 Fixe Discriminant',
    'ETFR': '🚦 Feu Rouge',
    'ETPN': '🚂 Passage à Niveau',
    'ETT': '⚡ Nouvelle Génération',
    'ETU': '🏙️ NG Urbain',
    'ETVM': '📏 Tronçon'
}

class RadarApp:
    def __init__(self):
        # Configuration de CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("📍 Radars Fixes France - 3400+ radars")
        self.root.geometry("1400x900")
        
        # Variables
        self.all_radars = []
        self.filtered_radars = []
        self.markers = []
        self.type_vars = {}
        
        # Créer l'interface
        self.create_ui()
        
        # Charger les données
        self.load_data()
        
    def create_ui(self):
        """Crée l'interface utilisateur"""
        
        # Container principal
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ===== PANNEAU GAUCHE - Filtres =====
        left_panel = ctk.CTkFrame(main_container, width=320, corner_radius=10)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Titre
        title = ctk.CTkLabel(
            left_panel,
            text="Filtres et Statistiques",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20)
        
        # Frame scrollable pour les filtres
        scroll_frame = ctk.CTkScrollableFrame(left_panel, label_text="")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Section Types de Radars ===
        types_label = ctk.CTkLabel(
            scroll_frame,
            text="⚡ Types de Radars",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        types_label.pack(pady=(10, 5), anchor="w")
        
        # Frame pour les checkboxes
        self.types_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.types_frame.pack(fill="x", pady=5)
        
        # === Section Vitesse ===
        speed_label = ctk.CTkLabel(
            scroll_frame,
            text="🚗 Vitesse Contrôlée (km/h)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        speed_label.pack(pady=(20, 5), anchor="w")
        
        speed_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        speed_frame.pack(fill="x", pady=5)
        
        # Vitesse min
        ctk.CTkLabel(speed_frame, text="Min:").grid(row=0, column=0, padx=5, sticky="w")
        self.speed_min_entry = ctk.CTkEntry(speed_frame, width=80, placeholder_text="0")
        self.speed_min_entry.grid(row=0, column=1, padx=5)
        
        # Vitesse max
        ctk.CTkLabel(speed_frame, text="Max:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.speed_max_entry = ctk.CTkEntry(speed_frame, width=80, placeholder_text="200")
        self.speed_max_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # === Section Recherche ===
        search_label = ctk.CTkLabel(
            scroll_frame,
            text="🔍 Recherche",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        search_label.pack(pady=(20, 5), anchor="w")
        
        self.search_entry = ctk.CTkEntry(
            scroll_frame,
            placeholder_text="Rechercher une route, ville..."
        )
        self.search_entry.pack(fill="x", pady=5)
        
        # === Boutons d'action ===
        buttons_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        apply_btn = ctk.CTkButton(
            buttons_frame,
            text="Appliquer les filtres",
            command=self.apply_filters,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        apply_btn.pack(fill="x", pady=5)
        
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="Réinitialiser",
            command=self.reset_filters,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        )
        reset_btn.pack(fill="x", pady=5)
        
        # === Section Statistiques ===
        stats_label = ctk.CTkLabel(
            scroll_frame,
            text="📊 Statistiques",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_label.pack(pady=(20, 10), anchor="w")
        
        self.stats_frame = ctk.CTkFrame(scroll_frame)
        self.stats_frame.pack(fill="x", pady=5)
        
        # Labels pour les stats
        self.total_label = ctk.CTkLabel(
            self.stats_frame,
            text="Total: -",
            font=ctk.CTkFont(size=14)
        )
        self.total_label.pack(pady=5, padx=10, anchor="w")
        
        self.displayed_label = ctk.CTkLabel(
            self.stats_frame,
            text="Affichés: -",
            font=ctk.CTkFont(size=14)
        )
        self.displayed_label.pack(pady=5, padx=10, anchor="w")
        
        self.avg_speed_label = ctk.CTkLabel(
            self.stats_frame,
            text="Vitesse moy: -",
            font=ctk.CTkFont(size=14)
        )
        self.avg_speed_label.pack(pady=5, padx=10, anchor="w")
        
        # ===== PANNEAU DROIT - Carte =====
        right_panel = ctk.CTkFrame(main_container, corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Label de chargement
        self.loading_label = ctk.CTkLabel(
            right_panel,
            text="🗺️ Chargement de la carte...",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.loading_label.pack(pady=50)
        
        # Carte (sera créée après l'initialisation complète)
        self.map_widget = None
        
    def create_map(self):
        """Crée le widget de carte"""
        print("🗺️ Création de la carte...")
        
        # Trouver le panneau droit (right_panel)
        main_container = self.root.winfo_children()[0]
        right_panel = None
        
        for child in main_container.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                # Le panneau droit est celui qui n'a pas de width fixe
                if not hasattr(child, 'pack_info') or child.pack_info().get('side') == 'right':
                    right_panel = child
                    break
        
        if right_panel and self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None
            
            # Créer la carte
            self.map_widget = TkinterMapView(right_panel, corner_radius=10)
            self.map_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Centrer sur la France
            self.map_widget.set_position(46.603354, 1.888334)
            self.map_widget.set_zoom(6)
            print("✅ Carte créée et centrée sur la France")
    
    def load_data(self):
        """Charge les données depuis la base de données"""
        print("📊 Début du chargement des données...")
        
        # Charger les types de radars (synchrone pour l'UI)
        types = get_radar_types()
        print(f"Types trouvés: {types}")
        
        # Créer les checkboxes pour chaque type
        for radar_type in types:
            var = ctk.BooleanVar(value=True)
            self.type_vars[radar_type] = var
            
            name = RADAR_NAMES.get(radar_type, radar_type)
            
            checkbox = ctk.CTkCheckBox(
                self.types_frame,
                text=name,
                variable=var,
                command=self.on_type_change
            )
            checkbox.pack(pady=5, padx=10, anchor="w")
        
        # Charger tous les radars
        print("📡 Chargement des radars depuis la base de données...")
        self.all_radars, total = get_radars(limit=10000)
        self.filtered_radars = self.all_radars.copy()
        print(f"✅ {len(self.all_radars)} radars chargés")
        
        # Charger les stats
        stats = get_stats()
        self.update_stats(stats)
        
        # Créer la carte après un délai suffisant
        self.root.after(1000, self.create_map)
        
        # Afficher les radars après que la carte soit créée
        self.root.after(3000, self.display_radars)
    
    def update_stats(self, stats):
        """Met à jour les statistiques affichées"""
        self.total_label.configure(text=f"Total: {stats['total']:,} radars")
        self.displayed_label.configure(text=f"Affichés: {len(self.filtered_radars):,} radars")
        if stats.get('average_speed'):
            self.avg_speed_label.configure(text=f"Vitesse moy: {stats['average_speed']:.1f} km/h")
    
    def display_radars(self):
        """Affiche les radars sur la carte"""
        if not self.map_widget:
            print("⚠️ Carte pas encore créée, réessai dans 500ms...")
            self.root.after(500, self.display_radars)
            return
        
        print(f"📍 Affichage de {len(self.filtered_radars)} radars...")
        
        # Effacer les anciens marqueurs
        for marker in self.markers:
            try:
                marker.delete()
            except:
                pass
        self.markers.clear()
        
        # Limiter le nombre de marqueurs pour les performances
        max_markers = 1000
        radars_to_display = self.filtered_radars[:max_markers]
        
        # Ajouter les nouveaux marqueurs
        count = 0
        for radar in radars_to_display:
            try:
                # Créer le marqueur avec un texte simple
                type_name = RADAR_NAMES.get(radar['type'], radar['type'])[:10]  # Limiter la longueur
                
                marker = self.map_widget.set_marker(
                    radar['latitude'],
                    radar['longitude'],
                    text=f"{radar['type']}",
                    command=lambda r=radar: self.show_radar_details(r)
                )
                self.markers.append(marker)
                count += 1
            except Exception as e:
                if count == 0:  # Afficher l'erreur seulement pour le premier
                    print(f"⚠️ Erreur ajout marqueur: {e}")
                continue
        
        print(f"✅ {count} marqueurs affichés sur la carte")
        
        # Mettre à jour le compteur
        self.displayed_label.configure(text=f"Affichés: {count:,} radars")
        
        # Afficher un avertissement si trop de radars
        if len(self.filtered_radars) > max_markers:
            warning_text = f"⚠️ {len(self.filtered_radars)} radars trouvés, affichage des {max_markers} premiers\nUtilisez les filtres pour réduire le nombre"
            print(warning_text)
    
    def apply_filters(self):
        """Applique les filtres sélectionnés"""
        # Récupérer les types sélectionnés
        selected_types = [t for t, var in self.type_vars.items() if var.get()]
        
        # Récupérer les vitesses
        try:
            speed_min = int(self.speed_min_entry.get()) if self.speed_min_entry.get() else None
        except ValueError:
            speed_min = None
            
        try:
            speed_max = int(self.speed_max_entry.get()) if self.speed_max_entry.get() else None
        except ValueError:
            speed_max = None
        
        # Récupérer la recherche
        search_text = self.search_entry.get().strip().lower()
        
        # Filtrer les radars
        self.filtered_radars = []
        for radar in self.all_radars:
            # Filtre par type
            if selected_types and radar['type'] not in selected_types:
                continue
            
            # Filtre par vitesse
            if speed_min and (not radar['vitesse'] or radar['vitesse'] < speed_min):
                continue
            if speed_max and (not radar['vitesse'] or radar['vitesse'] > speed_max):
                continue
            
            # Filtre par recherche
            if search_text:
                voie = (radar['voie'] or '').lower()
                sens = (radar['sens'] or '').lower()
                if search_text not in voie and search_text not in sens:
                    continue
            
            self.filtered_radars.append(radar)
        
        # Mettre à jour l'affichage
        self.display_radars()
    
    def reset_filters(self):
        """Réinitialise tous les filtres"""
        # Réinitialiser les checkboxes
        for var in self.type_vars.values():
            var.set(True)
        
        # Réinitialiser les champs
        self.speed_min_entry.delete(0, 'end')
        self.speed_max_entry.delete(0, 'end')
        self.search_entry.delete(0, 'end')
        
        # Réappliquer
        self.apply_filters()
    
    def on_type_change(self):
        """Appelé quand un type est coché/décoché"""
        # Pas besoin de ré-appliquer automatiquement, l'utilisateur cliquera sur "Appliquer"
        pass
    
    def show_radar_details(self, radar):
        """Affiche les détails d'un radar dans une fenêtre popup"""
        # Créer une fenêtre toplevel
        details_window = ctk.CTkToplevel(self.root)
        details_window.title(f"Radar #{radar.get('numero', radar['id'])}")
        details_window.geometry("400x500")
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Titre
        type_name = RADAR_NAMES.get(radar['type'], radar['type'])
        title = ctk.CTkLabel(
            details_window,
            text=type_name,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame pour les détails
        details_frame = ctk.CTkFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Détails
        details = [
            ("Numéro", radar.get('numero', '-')),
            ("Type", radar['type']),
            ("Vitesse contrôlée", f"{radar.get('vitesse', '-')} km/h" if radar.get('vitesse') else '-'),
            ("Voie", radar.get('voie', '-')),
            ("Sens", radar.get('sens', '-')),
            ("Date de mise en service", radar.get('date_mise_service', '-')),
            ("Latitude", f"{radar['latitude']:.5f}"),
            ("Longitude", f"{radar['longitude']:.5f}"),
        ]
        
        for i, (label, value) in enumerate(details):
            label_widget = ctk.CTkLabel(
                details_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            label_widget.grid(row=i, column=0, sticky="w", padx=10, pady=8)
            
            value_widget = ctk.CTkLabel(
                details_frame,
                text=str(value),
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            value_widget.grid(row=i, column=1, sticky="w", padx=10, pady=8)
        
        # Bouton fermer
        close_btn = ctk.CTkButton(
            details_window,
            text="Fermer",
            command=details_window.destroy,
            height=40
        )
        close_btn.pack(pady=20)
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = RadarApp()
    app.run()

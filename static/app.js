// ===== Configuration =====
const API_BASE_URL = '';
const API_ENDPOINTS = {
    radars: '/api/radars',
    types: '/api/types',
    stats: '/api/stats'
};

// Types de radars avec descriptions et couleurs
const RADAR_TYPES = {
    'ETD': { name: 'Fixe Discriminant', color: '#3b82f6', icon: '🎯' },
    'ETFR': { name: 'Feu Rouge', color: '#ef4444', icon: '🚦' },
    'ETPN': { name: 'Passage à Niveau', color: '#f59e0b', icon: '🚂' },
    'ETT': { name: 'Nouvelle Génération', color: '#8b5cf6', icon: '⚡' },
    'ETU': { name: 'NG Urbain', color: '#ec4899', icon: '🏙️' },
    'ETVM': { name: 'Tronçon (Vitesse Moy.)', color: '#10b981', icon: '📏' }
};

// ===== État Global =====
let map = null;
let markersLayer = null;
let allRadars = [];
let currentFilters = {
    types: [],
    vitesseMin: null,
    vitesseMax: null,
    search: ''
};

// ===== Initialisation =====
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadRadarTypes();
    loadStats();
    loadRadars();
    setupEventListeners();
});

// ===== Carte Leaflet =====
function initMap() {
    // Initialiser la carte centrée sur la France
    map = L.map('map').setView([46.603354, 1.888334], 6);
    
    // Ajouter la couche de tuiles (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Créer le groupe de marqueurs avec clustering
    markersLayer = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true
    });
    
    map.addLayer(markersLayer);
}

// ===== Chargement des Types de Radars =====
async function loadRadarTypes() {
    try {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.types}`);
        const types = await response.json();
        
        const container = document.getElementById('typeFilters');
        container.innerHTML = '';
        
        types.forEach(type => {
            const typeInfo = RADAR_TYPES[type] || { name: type, color: '#6b7280', icon: '📍' };
            
            const div = document.createElement('div');
            div.className = 'checkbox-item';
            div.innerHTML = `
                <input type="checkbox" id="type-${type}" value="${type}" checked>
                <label class="checkbox-label" for="type-${type}">
                    <span>${typeInfo.icon} ${typeInfo.name}</span>
                    <span class="checkbox-count" id="count-${type}">0</span>
                </label>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des types:', error);
        document.getElementById('typeFilters').innerHTML = '<div class="loading">Erreur de chargement</div>';
    }
}

// ===== Chargement des Statistiques =====
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.stats}`);
        const stats = await response.json();
        
        // Mettre à jour le header
        document.getElementById('totalRadars').textContent = stats.total.toLocaleString();
        
        // Mettre à jour les compteurs par type
        stats.types_distribution.forEach(item => {
            const countElement = document.getElementById(`count-${item.type}`);
            if (countElement) {
                countElement.textContent = item.count.toLocaleString();
            }
        });
        
        // Afficher les stats détaillées
        const statsGrid = document.getElementById('statsGrid');
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-card-label">Vitesse Moyenne</div>
                <div class="stat-card-value">${stats.average_speed || '-'} km/h</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-label">Vitesse Min - Max</div>
                <div class="stat-card-value">${stats.min_speed} - ${stats.max_speed} km/h</div>
            </div>
        `;
        
        // Ajouter la répartition par type
        stats.types_distribution.slice(0, 3).forEach(item => {
            const typeInfo = RADAR_TYPES[item.type] || { name: item.type, icon: '📍' };
            const percentage = ((item.count / stats.total) * 100).toFixed(1);
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <div class="stat-card-label">${typeInfo.icon} ${typeInfo.name}</div>
                <div class="stat-card-value">${percentage}%</div>
            `;
            statsGrid.appendChild(card);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des stats:', error);
    }
}

// ===== Chargement des Radars =====
async function loadRadars() {
    showLoading(true);
    
    try {
        // Construire l'URL avec les filtres
        const params = new URLSearchParams({
            limit: 10000 // Charger tous les radars
        });
        
        if (currentFilters.types.length > 0) {
            // Pour l'instant, on charge tous et on filtre côté client
            // Dans une vraie app, on ferait plusieurs requêtes ou on améliorerait l'API
        }
        
        if (currentFilters.vitesseMin) {
            params.append('vitesse_min', currentFilters.vitesseMin);
        }
        
        if (currentFilters.vitesseMax) {
            params.append('vitesse_max', currentFilters.vitesseMax);
        }
        
        if (currentFilters.search) {
            params.append('search', currentFilters.search);
        }
        
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.radars}?${params}`);
        const data = await response.json();
        
        allRadars = data.data;
        displayRadarsOnMap(allRadars);
        
        // Mettre à jour le compteur affiché
        document.getElementById('displayedRadars').textContent = allRadars.length.toLocaleString();
        
    } catch (error) {
        console.error('Erreur lors du chargement des radars:', error);
        alert('Erreur lors du chargement des radars. Veuillez réessayer.');
    } finally {
        showLoading(false);
    }
}

// ===== Affichage des Radars sur la Carte =====
function displayRadarsOnMap(radars) {
    // Effacer les marqueurs existants
    markersLayer.clearLayers();
    
    // Filtrer par types sélectionnés
    const selectedTypes = getSelectedTypes();
    const filteredRadars = selectedTypes.length > 0
        ? radars.filter(r => selectedTypes.includes(r.type))
        : radars;
    
    // Ajouter les nouveaux marqueurs
    filteredRadars.forEach(radar => {
        const typeInfo = RADAR_TYPES[radar.type] || { name: radar.type, color: '#6b7280', icon: '📍' };
        
        // Créer une icône personnalisée
        const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="
                background-color: ${typeInfo.color};
                width: 24px;
                height: 24px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
            ">${typeInfo.icon}</div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        const marker = L.marker([radar.latitude, radar.longitude], { icon })
            .bindPopup(createPopupContent(radar));
        
        marker.on('click', () => showRadarDetails(radar));
        markersLayer.addLayer(marker);
    });
    
    // Mettre à jour le compteur
    document.getElementById('displayedRadars').textContent = filteredRadars.length.toLocaleString();
}

// ===== Contenu du Popup =====
function createPopupContent(radar) {
    const typeInfo = RADAR_TYPES[radar.type] || { name: radar.type, icon: '📍' };
    return `
        <div style="min-width: 200px; color: #e5e7eb;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #f3f4f6;">
                ${typeInfo.icon} ${typeInfo.name}
            </h3>
            <p style="margin: 4px 0; font-size: 14px;">
                <strong>Vitesse:</strong> ${radar.vitesse || '-'} km/h
            </p>
            <p style="margin: 4px 0; font-size: 14px;">
                <strong>Voie:</strong> ${radar.voie || '-'}
            </p>
            <p style="margin: 4px 0; font-size: 14px;">
                <strong>Sens:</strong> ${radar.sens || '-'}
            </p>
        </div>
    `;
}

// ===== Afficher les Détails d'un Radar =====
function showRadarDetails(radar) {
    const modal = document.getElementById('radarModal');
    const modalBody = document.getElementById('modalBody');
    const typeInfo = RADAR_TYPES[radar.type] || { name: radar.type, icon: '📍' };
    
    modalBody.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Type</span>
            <span class="detail-value">${typeInfo.icon} ${typeInfo.name}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Numéro</span>
            <span class="detail-value">${radar.numero || '-'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Vitesse contrôlée</span>
            <span class="detail-value">${radar.vitesse || '-'} km/h</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Voie</span>
            <span class="detail-value">${radar.voie || '-'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Sens</span>
            <span class="detail-value">${radar.sens || '-'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Date de mise en service</span>
            <span class="detail-value">${radar.date_mise_service || '-'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Coordonnées</span>
            <span class="detail-value">${radar.latitude.toFixed(5)}, ${radar.longitude.toFixed(5)}</span>
        </div>
    `;
    
    modal.classList.add('active');
}

// ===== Obtenir les Types Sélectionnés =====
function getSelectedTypes() {
    const checkboxes = document.querySelectorAll('#typeFilters input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// ===== Appliquer les Filtres =====
function applyFilters() {
    currentFilters.types = getSelectedTypes();
    currentFilters.vitesseMin = document.getElementById('vitesseMin').value || null;
    currentFilters.vitesseMax = document.getElementById('vitesseMax').value || null;
    currentFilters.search = document.getElementById('searchInput').value.trim();
    
    loadRadars();
}

// ===== Réinitialiser les Filtres =====
function resetFilters() {
    // Cocher toutes les checkboxes
    document.querySelectorAll('#typeFilters input[type="checkbox"]').forEach(cb => {
        cb.checked = true;
    });
    
    // Réinitialiser les champs
    document.getElementById('vitesseMin').value = '';
    document.getElementById('vitesseMax').value = '';
    document.getElementById('searchInput').value = '';
    
    // Réinitialiser l'état
    currentFilters = {
        types: [],
        vitesseMin: null,
        vitesseMax: null,
        search: ''
    };
    
    loadRadars();
}

// ===== Afficher/Masquer le Loading =====
function showLoading(show) {
    const loading = document.getElementById('mapLoading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// ===== Event Listeners =====
function setupEventListeners() {
    // Boutons de filtres
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
    
    // Recherche en temps réel (avec debounce)
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(applyFilters, 500);
    });
    
    // Changement de type de radar
    document.getElementById('typeFilters').addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            displayRadarsOnMap(allRadars);
        }
    });
    
    // Modal
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('radarModal').classList.remove('active');
    });
    
    document.getElementById('radarModal').addEventListener('click', (e) => {
        if (e.target.id === 'radarModal') {
            document.getElementById('radarModal').classList.remove('active');
        }
    });
    
    // Sidebar mobile
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');
    const closeBtn = document.getElementById('closeSidebar');
    
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.add('active');
    });
    
    closeBtn.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });
    
    // Fermer la sidebar en cliquant sur la carte (mobile)
    map.on('click', () => {
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
        }
    });
}

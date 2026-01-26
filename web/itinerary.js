/**
 * RADARS FRANCE - Module Itinéraire
 * Calcul d'itinéraire avec OSRM et détection des radars sur le trajet
 */

// =============================================================================
// CONFIGURATION
// =============================================================================
const ROUTING_CONFIG = {
    // API OSRM (gratuit, pas de clé nécessaire)
    osrmUrl: 'https://router.project-osrm.org/route/v1/driving/',
    // API Nominatim pour géocodage (gratuit)
    nominatimUrl: 'https://nominatim.openstreetmap.org/search',
    // Distance max pour détecter un radar sur la route (en mètres)
    radarDetectionRadius: 500
};

// =============================================================================
// ÉTAT
// =============================================================================
let currentRoute = null;
let routeLayer = null;
let routeRadarsLayer = null;
let startMarker = null;
let endMarker = null;

// =============================================================================
// INITIALISATION
// =============================================================================
function initItinerary() {
    document.getElementById('calculate-route').addEventListener('click', calculateRoute);
    document.getElementById('clear-route').addEventListener('click', clearRoute);

    // Permettre Enter pour calculer
    document.getElementById('route-start').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') document.getElementById('route-end').focus();
    });
    document.getElementById('route-end').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') calculateRoute();
    });
}

// =============================================================================
// GÉOCODAGE
// =============================================================================
async function geocodeAddress(address) {
    // Si c'est déjà des coordonnées (format: lat,lon ou lat, lon)
    const coordsMatch = address.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
    if (coordsMatch) {
        return {
            lat: parseFloat(coordsMatch[1]),
            lon: parseFloat(coordsMatch[2]),
            display: `${coordsMatch[1]}, ${coordsMatch[2]}`
        };
    }

    // Sinon, géocoder via Nominatim
    const url = `${ROUTING_CONFIG.nominatimUrl}?q=${encodeURIComponent(address)}&format=json&limit=1&countrycodes=fr`;

    try {
        const response = await fetch(url, {
            headers: { 'User-Agent': 'RadarsFrance/1.0' }
        });
        const data = await response.json();

        if (data.length === 0) {
            throw new Error(`Adresse non trouvée: ${address}`);
        }

        return {
            lat: parseFloat(data[0].lat),
            lon: parseFloat(data[0].lon),
            display: data[0].display_name.split(',').slice(0, 2).join(',')
        };
    } catch (error) {
        console.error('Erreur géocodage:', error);
        throw error;
    }
}

// =============================================================================
// CALCUL D'ITINÉRAIRE
// =============================================================================
async function calculateRoute() {
    const startInput = document.getElementById('route-start').value.trim();
    const endInput = document.getElementById('route-end').value.trim();

    if (!startInput || !endInput) {
        alert('Veuillez remplir les champs départ et arrivée');
        return;
    }

    const btn = document.getElementById('calculate-route');
    btn.disabled = true;
    btn.innerHTML = '<span class="mini-spinner"></span> Calcul...';

    try {
        // Géocoder les adresses
        const [startCoords, endCoords] = await Promise.all([
            geocodeAddress(startInput),
            geocodeAddress(endInput)
        ]);

        // Calculer l'itinéraire via OSRM
        const routeUrl = `${ROUTING_CONFIG.osrmUrl}${startCoords.lon},${startCoords.lat};${endCoords.lon},${endCoords.lat}?overview=full&geometries=geojson`;

        const response = await fetch(routeUrl);
        const data = await response.json();

        if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) {
            throw new Error('Impossible de calculer l\'itinéraire');
        }

        const route = data.routes[0];
        currentRoute = {
            coordinates: route.geometry.coordinates,
            distance: route.distance,
            duration: route.duration,
            start: startCoords,
            end: endCoords
        };

        // Afficher l'itinéraire sur la carte
        displayRoute(currentRoute);

        // Trouver les radars sur le trajet
        const radarsOnRoute = findRadarsOnRoute(currentRoute.coordinates);

        // Afficher les résultats
        displayRouteResults(currentRoute, radarsOnRoute);

    } catch (error) {
        console.error('Erreur calcul itinéraire:', error);
        alert(`Erreur: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚗 Calculer';
    }
}

// =============================================================================
// AFFICHAGE DE L'ITINÉRAIRE
// =============================================================================
function displayRoute(route) {
    // Supprimer l'ancien itinéraire
    clearRouteFromMap();

    // Convertir les coordonnées [lon, lat] en [lat, lon] pour Leaflet
    const latLngs = route.coordinates.map(c => [c[1], c[0]]);

    // Tracer la ligne de l'itinéraire
    routeLayer = L.polyline(latLngs, {
        color: '#10b981',
        weight: 6,
        opacity: 0.8,
        lineJoin: 'round'
    }).addTo(map);

    // Marqueurs de départ et d'arrivée
    const startIcon = L.divIcon({
        className: 'route-marker start-marker',
        html: '<div style="background:#10b981;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;border:3px solid white;box-shadow:0 2px 10px rgba(0,0,0,0.3);">A</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    const endIcon = L.divIcon({
        className: 'route-marker end-marker',
        html: '<div style="background:#e74c3c;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;border:3px solid white;box-shadow:0 2px 10px rgba(0,0,0,0.3);">B</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    startMarker = L.marker([route.start.lat, route.start.lon], { icon: startIcon })
        .addTo(map)
        .bindPopup(`<b>Départ</b><br>${route.start.display}`);

    endMarker = L.marker([route.end.lat, route.end.lon], { icon: endIcon })
        .addTo(map)
        .bindPopup(`<b>Arrivée</b><br>${route.end.display}`);

    // Ajuster la vue sur l'itinéraire
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
}

// =============================================================================
// DÉTECTION DES RADARS SUR L'ITINÉRAIRE
// =============================================================================
function findRadarsOnRoute(routeCoordinates) {
    const radarsOnRoute = [];
    const radius = ROUTING_CONFIG.radarDetectionRadius;

    // Pour chaque radar, vérifier s'il est proche de l'itinéraire
    allRadars.forEach(radar => {
        if (!radar.latitude || !radar.longitude) return;

        let minDistance = Infinity;
        let closestPointIndex = 0;

        // Trouver le point de l'itinéraire le plus proche du radar
        routeCoordinates.forEach((coord, index) => {
            const distance = getDistance(
                radar.latitude, radar.longitude,
                coord[1], coord[0]
            );
            if (distance < minDistance) {
                minDistance = distance;
                closestPointIndex = index;
            }
        });

        // Si le radar est assez proche de l'itinéraire
        if (minDistance <= radius) {
            radarsOnRoute.push({
                ...radar,
                distanceFromRoute: Math.round(minDistance),
                routePosition: closestPointIndex / routeCoordinates.length
            });
        }
    });

    // Trier par position sur l'itinéraire
    radarsOnRoute.sort((a, b) => a.routePosition - b.routePosition);

    return radarsOnRoute;
}

// Calcul de distance Haversine (en mètres)
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Rayon de la Terre en mètres
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function toRad(deg) {
    return deg * Math.PI / 180;
}

// =============================================================================
// AFFICHAGE DES RÉSULTATS
// =============================================================================
function displayRouteResults(route, radarsOnRoute) {
    const resultsDiv = document.getElementById('route-results');
    resultsDiv.classList.remove('hidden');

    // Afficher distance et durée
    document.getElementById('route-distance').textContent = formatDistance(route.distance);
    document.getElementById('route-duration').textContent = formatDuration(route.duration);
    document.getElementById('route-radars').textContent = radarsOnRoute.length;

    // Afficher la liste des radars
    const radarList = document.getElementById('radar-list');

    if (radarsOnRoute.length === 0) {
        radarList.innerHTML = '<div class="no-radars-message">🎉 Aucun radar détecté sur cet itinéraire !</div>';
    } else {
        radarList.innerHTML = radarsOnRoute.map(radar => {
            const color = RADAR_COLORS[radar.type] || '#95a5a6';
            const icon = getRadarIcon(radar.type);
            return `
                <div class="radar-item" onclick="zoomToRadar(${radar.latitude}, ${radar.longitude}, ${radar.id})">
                    <div class="radar-icon" style="background: ${color};">${icon}</div>
                    <div class="radar-info">
                        <div class="radar-name">${radar.emplacement || radar.route || 'Radar'}</div>
                        <div class="radar-details">${radar.type}${radar.vitesse ? ` • ${radar.vitesse} km/h` : ''}</div>
                    </div>
                    <div class="radar-distance">${radar.distanceFromRoute}m</div>
                </div>
            `;
        }).join('');
    }

    // Mettre en évidence les radars sur la carte
    highlightRadarsOnRoute(radarsOnRoute);
}

function getRadarIcon(type) {
    const icons = {
        'Radar fixe': '📸',
        'Radar feu rouge': '🚦',
        'Radar discriminant': '🚛',
        'Radar Vitesse Moyenne': '⏱️',
        'Radar Passage à Niveau': '🚧',
        'Itinéraire': '📍'
    };
    return icons[type] || '📡';
}

function formatDistance(meters) {
    if (meters >= 1000) {
        return `${(meters / 1000).toFixed(0)} km`;
    }
    return `${Math.round(meters)} m`;
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
        return `${hours}h${minutes.toString().padStart(2, '0')}`;
    }
    return `${minutes} min`;
}

// =============================================================================
// MISE EN ÉVIDENCE DES RADARS SUR LA ROUTE
// =============================================================================
function highlightRadarsOnRoute(radarsOnRoute) {
    // Supprimer les anciens marqueurs de route
    if (routeRadarsLayer) {
        map.removeLayer(routeRadarsLayer);
    }

    routeRadarsLayer = L.layerGroup();

    radarsOnRoute.forEach((radar, index) => {
        const color = RADAR_COLORS[radar.type] || '#95a5a6';

        // Marqueur pulsant pour les radars sur l'itinéraire
        const pulsingIcon = L.divIcon({
            className: 'route-radar-marker',
            html: `
                <div style="position:relative;">
                    <div style="position:absolute;width:40px;height:40px;background:${color};opacity:0.3;border-radius:50%;animation:pulse-ring 1.5s ease-out infinite;"></div>
                    <div style="position:relative;width:24px;height:24px;background:${color};border:3px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;box-shadow:0 2px 10px rgba(0,0,0,0.3);margin:8px;">
                        ${index + 1}
                    </div>
                </div>
            `,
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });

        const marker = L.marker([radar.latitude, radar.longitude], { icon: pulsingIcon })
            .bindPopup(createPopupContent(radar));

        routeRadarsLayer.addLayer(marker);
    });

    routeRadarsLayer.addTo(map);

    // Ajouter le style d'animation
    if (!document.getElementById('pulse-style')) {
        const style = document.createElement('style');
        style.id = 'pulse-style';
        style.textContent = `
            @keyframes pulse-ring {
                0% { transform: scale(0.5); opacity: 0.5; }
                100% { transform: scale(1.5); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// =============================================================================
// ZOOM SUR UN RADAR
// =============================================================================
function zoomToRadar(lat, lon, id) {
    map.setView([lat, lon], 15);

    // Trouver et ouvrir le popup du radar
    if (routeRadarsLayer) {
        routeRadarsLayer.eachLayer(layer => {
            if (layer.getLatLng &&
                Math.abs(layer.getLatLng().lat - lat) < 0.0001 &&
                Math.abs(layer.getLatLng().lng - lon) < 0.0001) {
                layer.openPopup();
            }
        });
    }
}

// =============================================================================
// EFFACER L'ITINÉRAIRE
// =============================================================================
function clearRoute() {
    clearRouteFromMap();

    // Réinitialiser les champs
    document.getElementById('route-start').value = '';
    document.getElementById('route-end').value = '';

    // Cacher les résultats
    document.getElementById('route-results').classList.add('hidden');

    // Réinitialiser la vue
    map.setView(CONFIG.mapCenter, CONFIG.defaultZoom);

    currentRoute = null;
}

function clearRouteFromMap() {
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }
    if (routeRadarsLayer) {
        map.removeLayer(routeRadarsLayer);
        routeRadarsLayer = null;
    }
    if (startMarker) {
        map.removeLayer(startMarker);
        startMarker = null;
    }
    if (endMarker) {
        map.removeLayer(endMarker);
        endMarker = null;
    }
}

// Exposer les fonctions globalement
window.zoomToRadar = zoomToRadar;
window.initItinerary = initItinerary;

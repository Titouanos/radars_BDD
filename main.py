from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import math

from database import get_radars, get_radar_by_id, get_radar_types, get_stats
from models import Radar, RadarResponse, StatsResponse

app = FastAPI(
    title="API Radars France",
    description="API pour visualiser et filtrer les radars fixes en France",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    """Page d'accueil - retourne l'interface HTML"""
    return FileResponse("static/index.html")

@app.get("/api/radars", response_model=RadarResponse)
async def list_radars(
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre de résultats par page"),
    type: Optional[str] = Query(None, description="Filtrer par type de radar"),
    vitesse_min: Optional[int] = Query(None, ge=0, description="Vitesse minimale"),
    vitesse_max: Optional[int] = Query(None, ge=0, description="Vitesse maximale"),
    search: Optional[str] = Query(None, description="Recherche textuelle (voie, sens)")
):
    """
    Récupère la liste des radars avec filtrage et pagination
    
    - **page**: Numéro de page (défaut: 1)
    - **limit**: Résultats par page (défaut: 100, max: 1000)
    - **type**: Type de radar (ETD, ETFR, ETPN, ETT, ETU, ETVM)
    - **vitesse_min**: Vitesse minimale contrôlée
    - **vitesse_max**: Vitesse maximale contrôlée
    - **search**: Recherche dans voie et sens
    """
    radars, total = get_radars(
        page=page,
        limit=limit,
        radar_type=type,
        vitesse_min=vitesse_min,
        vitesse_max=vitesse_max,
        search=search
    )
    
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    return {
        "data": radars,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

@app.get("/api/radars/{radar_id}", response_model=Radar)
async def get_radar(radar_id: int):
    """Récupère les détails d'un radar spécifique par son ID"""
    radar = get_radar_by_id(radar_id)
    if not radar:
        raise HTTPException(status_code=404, detail="Radar non trouvé")
    return radar

@app.get("/api/types", response_model=list[str])
async def list_types():
    """
    Récupère la liste des types de radars disponibles
    
    Types possibles :
    - ETD : Radar fixe discriminant
    - ETFR : Radar feu rouge
    - ETPN : Radar passage à niveau
    - ETT : Radar fixe nouvelle génération
    - ETU : Radar fixe nouvelle génération urbain
    - ETVM : Radar tronçon (vitesse moyenne)
    """
    return get_radar_types()

@app.get("/api/stats", response_model=StatsResponse)
async def get_statistics():
    """
    Récupère les statistiques globales sur les radars
    
    Retourne :
    - Nombre total de radars
    - Répartition par type
    - Vitesse moyenne contrôlée
    - Vitesses min et max
    """
    return get_stats()

@app.get("/health")
async def health_check():
    """Point de terminaison pour vérifier l'état de l'API"""
    return {"status": "healthy", "message": "API Radars France fonctionne correctement"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur API Radars France...")
    print("📍 Interface web : http://localhost:8000")
    print("📚 Documentation API : http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

from pydantic import BaseModel, Field
from typing import Optional, List

class Radar(BaseModel):
    """Modèle représentant un radar"""
    id: Optional[int] = None
    numero: Optional[str] = None
    type: str
    date_mise_service: Optional[str] = None
    voie: Optional[str] = None
    sens: Optional[str] = None
    vitesse: Optional[int] = None
    latitude: float
    longitude: float

class RadarResponse(BaseModel):
    """Réponse paginée contenant des radars"""
    data: List[Radar]
    total: int
    page: int
    limit: int
    total_pages: int

class StatsResponse(BaseModel):
    """Statistiques sur les radars"""
    total: int
    types_distribution: List[dict]
    average_speed: Optional[float]
    min_speed: Optional[int]
    max_speed: Optional[int]

class TypeDistribution(BaseModel):
    """Distribution d'un type de radar"""
    type: str
    count: int

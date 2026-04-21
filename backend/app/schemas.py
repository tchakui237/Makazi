"""
Makazi — Schémas Pydantic v2 pour la validation des données d'entrée/sortie.

Ces schémas assurent la validation stricte des types et la sérialisation
automatique des réponses JSON de l'API.

La variable `type_quartier` est contrainte à exactement 3 valeurs possibles.
Un validateur bloque les loyers incohérents pour protéger le modèle ML.
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# Types autorisés pour la variable catégorielle
# ──────────────────────────────────────────────────────────────
TypeQuartier = Literal["Administratif", "Résidentiel", "Populaire"]


class ApartmentCreate(BaseModel):
    """
    Schéma de validation pour POST /collect.
    Toutes les valeurs numériques sont contraintes à des plages réalistes.
    """
    type_quartier: TypeQuartier = Field(
        ..., description="Catégorie du quartier"
    )
    chambres: int = Field(..., ge=0, le=10, description="Nombre de chambres")
    douches: int = Field(..., ge=0, le=10, description="Nombre de douches")
    salons: int = Field(..., ge=0, le=5, description="Nombre de salons")
    cuisines: int = Field(..., ge=0, le=5, description="Nombre de cuisines")
    bureaux: int = Field(..., ge=0, le=5, description="Nombre de bureaux")
    forage: bool = Field(..., description="Accès à un forage (eau autonome)")
    eneo: bool = Field(..., description="Raccordement ENEO (électricité)")
    loyer: float = Field(
        ..., gt=0, description="Loyer mensuel en FCFA"
    )

    @field_validator('loyer')
    @classmethod
    def valider_loyer_coherent(cls, v: float, info: ValidationInfo):
        """
        Bloque l'insertion si le loyer est irréaliste pour le quartier choisi.
        """
        tq = info.data.get('type_quartier')
        
        # Si le quartier n'est pas encore validé, on passe
        if not tq:
            return v
            
        # Bornes réalistes pour Yaoundé (marché 2026)
        if tq == "Populaire":
            if v < 15000 or v > 150000:
                raise ValueError("Pour un quartier Populaire, le loyer doit être entre 15 000 et 150 000 FCFA.")
        
        elif tq == "Résidentiel":
            if v < 50000 or v > 600000:
                raise ValueError("Pour un quartier Résidentiel, le loyer doit être entre 50 000 et 600 000 FCFA.")
        
        elif tq == "Administratif":
            if v < 150000 or v > 3000000:
                raise ValueError("Pour un quartier Administratif, le loyer doit être entre 150 000 et 3 000 000 FCFA.")
        
        return v


class ApartmentOut(BaseModel):
    """Schéma de sortie pour un appartement (sérialisation JSON)."""
    id: int
    type_quartier: str
    chambres: int
    douches: int
    salons: int
    cuisines: int
    bureaux: int
    forage: bool
    eneo: bool
    loyer: float
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class PredictionRequest(BaseModel):
    """
    Schéma d'entrée pour POST /predict.
    Identique à ApartmentCreate mais SANS le champ 'loyer' (c'est ce qu'on prédit).
    """
    type_quartier: TypeQuartier = Field(..., description="Catégorie du quartier")
    chambres: int = Field(..., ge=0, le=10)
    douches: int = Field(..., ge=0, le=10)
    salons: int = Field(..., ge=0, le=5)
    cuisines: int = Field(..., ge=0, le=5)
    bureaux: int = Field(..., ge=0, le=5)
    forage: bool = Field(...)
    eneo: bool = Field(...)


class PredictionResponse(BaseModel):
    """Réponse de prédiction avec intervalle de confiance à 95%."""
    predicted_price: float = Field(..., description="Prix estimé Ŷ en FCFA")
    lower_bound: float = Field(..., description="Borne inférieure IC 95% en FCFA")
    upper_bound: float = Field(..., description="Borne supérieure IC 95% en FCFA")


class StatsResponse(BaseModel):
    """Statistiques globales de la base de données et du modèle."""
    total_entries: int = Field(..., description="Nombre total d'appartements en base")
    average_price: float = Field(..., description="Loyer moyen en FCFA")
    r_squared: float | None = Field(None, description="Coefficient de détermination R² du modèle OLS")

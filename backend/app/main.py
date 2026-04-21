"""
Makazi — Point d'entrée de l'API FastAPI.

Corrections appliquées :
- Imports alignés sur les vrais noms : ApartmentOut, ApartmentCreate, PredictionRequest
- Module crud.py requis et maintenant présent dans le package
- Champ 'loyer' (et non 'price') pour les calculs de stats/prédiction
- Champ 'chambres' (et non 'rooms') pour la logique de prédiction
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db

# Crée les tables sur Supabase au démarrage si elles n'existent pas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Makazi API",
    description="API de prédiction des prix de loyer à Yaoundé",
    version="1.0.0",
)

# ──────────────────────────────────────────────────────────────
# CORS — à affiner en production avec l'URL exacte du frontend
# ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Remplacer par l'URL Railway du frontend en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Makazi - Système de collecte et prédiction"}


# ── Routes de Collecte ────────────────────────────────────────

@app.post("/collect/", response_model=schemas.ApartmentOut)
def create_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    return crud.create_apartment(db=db, apartment=apartment)


@app.get("/apartments/", response_model=list[schemas.ApartmentOut])
def read_apartments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_apartments(db, skip=skip, limit=limit)


# ── Route de Prédiction ───────────────────────────────────────

@app.post("/predict/", response_model=schemas.PredictionResponse)
def predict_price(features: schemas.PredictionRequest, db: Session = Depends(get_db)):
    apartments = crud.get_apartments(db, limit=1000)

    if len(apartments) < 2:
        raise HTTPException(
            status_code=400,
            detail="Pas assez de données pour prédire. Collectez au moins 2 entrées."
        )

    # Filtre par type de quartier pour une estimation plus précise
    same_quartier = [a for a in apartments if a.type_quartier == features.type_quartier]
    reference = same_quartier if len(same_quartier) >= 2 else apartments

    avg_price = sum(a.loyer for a in reference) / len(reference)
    
    # Ajustement simple par nombre de chambres (pente approximative)
    prediction = avg_price * (features.chambres / max(1, sum(a.chambres for a in reference) / len(reference)))
    margin = prediction * 0.15  # ±15% comme intervalle de confiance provisoire

    return schemas.PredictionResponse(
        predicted_price=round(prediction, 2),
        lower_bound=round(prediction - margin, 2),
        upper_bound=round(prediction + margin, 2),
    )


# ── Route Statistiques (Dashboard) ───────────────────────────

@app.get("/stats/", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    apartments = crud.get_apartments(db, limit=10000)
    total = len(apartments)
    avg = sum(a.loyer for a in apartments) / total if total > 0 else 0.0

    return schemas.StatsResponse(
        total_entries=total,
        average_price=round(avg, 2),
        r_squared=None,  # Sera rempli quand ml.py sera intégré
    )

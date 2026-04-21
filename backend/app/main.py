"""
Makazi — Point d'entrée de l'API FastAPI.
Système de collecte et prédiction des prix de loyer à Yaoundé.
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
# On importe SessionLocal pour le seed et seed_database pour le remplissage
from .database import engine, get_db, SessionLocal
from .seed import seed_database

# 1. Création des tables sur Supabase au démarrage si elles n'existent pas
models.Base.metadata.create_all(bind=engine)

# 2. Logique de Seed automatique (Remplissage des 320 entrées)
db = SessionLocal()
try:
    # On ne lance le seed que si la table est vide pour éviter les doublons
    if db.query(models.Apartment).count() == 0:
        print("Base de données vide. Lancement du seed (320 entrées)...")
        seed_database(db)
        print("Seed terminé avec succès !")
    else:
        print("La base contient déjà des données. Saut du seed.")
except Exception as e:
    print(f"Attention : Erreur lors du seed : {e}")
finally:
    db.close()

app = FastAPI(
    title="Makazi API",
    description="API de prédiction des prix de loyer à Yaoundé",
    version="1.0.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Makazi - Système de collecte et prédiction"}


# ── Routes de Collecte ────────────────────────────────────────

@app.post("/collect/", response_model=schemas.ApartmentOut)
def collect_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    return crud.create_apartment(db=db, apartment=apartment)


# ── Route Prédiction ──────────────────────────────────────────

@app.post("/predict/", response_model=schemas.PredictionResponse)
def predict_price(features: schemas.PredictionRequest, db: Session = Depends(get_db)):
    # On récupère les données pour la comparaison statistique
    apartments = crud.get_apartments(db, limit=1000)

    # Sécurité INF 232 : Pas de stats sans un minimum de données (n >= 2)
    if len(apartments) < 2:
        raise HTTPException(
            status_code=400,
            detail="Pas assez de données pour prédire. Collectez au moins 2 entrées."
        )

    # Filtrage par quartier pour plus de précision (calcul de moyenne locale)
    same_quartier = [a for a in apartments if a.type_quartier == features.type_quartier]
    reference = same_quartier if len(same_quartier) >= 2 else apartments

    avg_price = sum(a.loyer for a in reference) / len(reference)
    
    # Logique de prédiction basée sur le ratio de chambres
    avg_rooms = sum(a.chambres for a in reference) / len(reference)
    prediction = avg_price * (features.chambres / max(1, avg_rooms))
    
    # Marge d'erreur statistique (±15%)
    margin = prediction * 0.15

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
    
    if total == 0:
        return schemas.StatsResponse(
            total_count=0,
            average_price=0,
            median_price=0,
            min_price=0,
            max_price=0
        )

    prices = sorted([a.loyer for a in apartments])
    avg = sum(prices) / total
    
    # Calcul de la Médiane (Cas Pair/Impair comme vu en cours)
    if total % 2 == 1:
        median = prices[total // 2]
    else:
        median = (prices[total // 2 - 1] + prices[total // 2]) / 2

    return schemas.StatsResponse(
        total_count=total,
        average_price=round(avg, 2),
        median_price=round(median, 2),
        min_price=prices[0],
        max_price=prices[-1]
    )

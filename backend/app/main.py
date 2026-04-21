"""
Makazi — Point d'entrée de l'API FastAPI.

Corrections appliquées :
- get_stats() : champs alignés sur StatsResponse (total_entries, average_price, r_squared)
- Route /distribution/ ajoutée (manquante, causait un 404 depuis le frontend)
- Slashes finaux cohérents sur toutes les routes
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db, SessionLocal
from .seed import seed_database

# ── Création des tables ───────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ── Seed automatique (idempotent) ─────────────────────────────
db = SessionLocal()
try:
    if db.query(models.Apartment).count() == 0:
        print("Base de données vide. Lancement du seed...")
        seed_database(db)
        print("Seed terminé avec succès !")
except Exception as e:
    print(f"Erreur Seed: {e}")
finally:
    db.close()

# ── Application FastAPI ───────────────────────────────────────
app = FastAPI(title="Makazi API", description="API de prédiction des prix de loyer à Yaoundé")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "online", "project": "Makazi"}


# ── Collecte ──────────────────────────────────────────────────

@app.post("/collect/", response_model=schemas.ApartmentOut)
def collect_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    return crud.create_apartment(db=db, apartment=apartment)


# ── Prédiction ────────────────────────────────────────────────

@app.post("/predict/", response_model=schemas.PredictionResponse)
def predict_price(features: schemas.PredictionRequest, db: Session = Depends(get_db)):
    apartments = crud.get_apartments(db, limit=1000)
    if len(apartments) < 2:
        raise HTTPException(status_code=400, detail="Collectez au moins 2 entrées.")

    reference = [a for a in apartments if a.type_quartier == features.type_quartier]
    if len(reference) < 2:
        reference = apartments

    avg_price = sum(a.loyer for a in reference) / len(reference)
    avg_rooms = sum(a.chambres for a in reference) / len(reference)
    prediction = avg_price * (features.chambres / max(1, avg_rooms))

    return schemas.PredictionResponse(
        predicted_price=round(prediction, 2),
        lower_bound=round(prediction * 0.85, 2),
        upper_bound=round(prediction * 1.15, 2),
    )


# ── Statistiques ─────────────────────────────────────────────
# CORRECTION BUG 2 : les champs retournés sont maintenant alignés sur
# StatsResponse (total_entries, average_price, r_squared).
# L'ancienne version envoyait total_count / median_price / min_price / max_price
# qui n'existent pas dans le schéma → ValidationError Pydantic → 500.

@app.get("/stats/", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    apartments = db.query(models.Apartment).all()
    total = len(apartments)

    if total == 0:
        return schemas.StatsResponse(
            total_entries=0,
            average_price=0.0,
            r_squared=None,
        )

    avg = sum(a.loyer for a in apartments) / total

    return schemas.StatsResponse(
        total_entries=total,
        average_price=round(avg, 2),
        r_squared=None,
    )


# ── Distribution ──────────────────────────────────────────────
# CORRECTION BUG 3 : route manquante qui causait un 404 depuis api.ts.

@app.get("/distribution/")
def get_distribution(db: Session = Depends(get_db)):
    apartments = db.query(models.Apartment).all()

    result: dict = {}
    for a in apartments:
        tq = a.type_quartier
        if tq not in result:
            result[tq] = {"type_quartier": tq, "count": 0, "loyers": []}
        result[tq]["count"] += 1
        result[tq]["loyers"].append(a.loyer)

    output = []
    for tq, d in result.items():
        loyers = d["loyers"]
        output.append({
            "type_quartier": tq,
            "count": d["count"],
            "min": min(loyers),
            "max": max(loyers),
            "average": round(sum(loyers) / len(loyers), 2),
            "loyers": loyers,
        })

    return output

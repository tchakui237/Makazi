import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db, SessionLocal
from .seed import seed_database

# 1. Création des tables
models.Base.metadata.create_all(bind=engine)

# 2. Seed automatique sécurisé
db = SessionLocal()
try:
    if db.query(models.Apartment).count() == 0:
        print("Base de données vide. Lancement du seed...")
        seed_database(db)
        db.commit() # Sécurité supplémentaire
        print("Seed terminé avec succès !")
except Exception as e:
    print(f"Erreur Seed: {e}")
finally:
    db.close()

app = FastAPI(title="Makazi API")

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

@app.post("/collect/", response_model=schemas.ApartmentOut)
def collect_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    return crud.create_apartment(db=db, apartment=apartment)

@app.post("/predict/", response_model=schemas.PredictionResponse)
def predict_price(features: schemas.PredictionRequest, db: Session = Depends(get_db)):
    apartments = crud.get_apartments(db, limit=1000)
    if len(apartments) < 2:
        raise HTTPException(status_code=400, detail="Collectez au moins 2 entrées.")

    reference = [a for a in apartments if a.type_quartier == features.type_quartier]
    if len(reference) < 2: reference = apartments

    avg_price = sum(a.loyer for a in reference) / len(reference)
    avg_rooms = sum(a.chambres for a in reference) / len(reference)
    prediction = avg_price * (features.chambres / max(1, avg_rooms))
    
    return schemas.PredictionResponse(
        predicted_price=int(prediction), # Conversion en int pour schemas.py
        lower_bound=int(prediction * 0.85),
        upper_bound=int(prediction * 1.15)
    )

@app.get("/stats/", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    apartments = db.query(models.Apartment).all()
    total = len(apartments)
    
    if total == 0:
        return schemas.StatsResponse(total_count=0, average_price=0, median_price=0, min_price=0, max_price=0)

    prices = sorted([a.loyer for a in apartments])
    
    # Correction ICI : Conversion explicite en INT pour éviter l'erreur 500
    if total % 2 == 1:
        median = prices[total // 2]
    else:
        median = int((prices[total // 2 - 1] + prices[total // 2]) / 2)

    return schemas.StatsResponse(
        total_count=total,
        average_price=int(sum(prices) / total),
        median_price=median,
        min_price=prices[0],
        max_price=prices[-1]
    )

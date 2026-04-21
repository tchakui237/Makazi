"""
Makazi — Opérations CRUD sur la table 'apartments'.

Ce module est l'unique point d'accès à la base de données depuis les routes.
Il encapsule toutes les requêtes SQLAlchemy pour garder main.py propre.
"""

from sqlalchemy.orm import Session
from . import models, schemas


def create_apartment(db: Session, apartment: schemas.ApartmentCreate) -> models.Apartment:
    """Insère un nouvel appartement en base et retourne l'objet créé."""
    db_apartment = models.Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment


def get_apartments(db: Session, skip: int = 0, limit: int = 1000) -> list[models.Apartment]:
    """Récupère une liste paginée d'appartements."""
    return db.query(models.Apartment).offset(skip).limit(limit).all()


def get_apartment_count(db: Session) -> int:
    """Retourne le nombre total d'appartements en base."""
    return db.query(models.Apartment).count()

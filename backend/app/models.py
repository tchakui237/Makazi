"""
Makazi — Modèle ORM SQLAlchemy pour la table 'apartments'.

Chaque enregistrement représente un appartement avec ses caractéristiques
physiques, ses commodités et son loyer mensuel en FCFA.

CONTRAINTE CRITIQUE :
    Le champ `type_quartier` est une variable catégorielle à 3 modalités :
    - "Administratif"
    - "Résidentiel"
    - "Populaire"
    Aucun nom de quartier spécifique n'est utilisé.
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.sql import func

from .database import Base


class Apartment(Base):
    """
    Modèle ORM représentant un appartement à Yaoundé.

    Attributs :
        id            : Identifiant unique auto-incrémenté
        type_quartier : Catégorie du quartier (Administratif/Résidentiel/Populaire)
        chambres      : Nombre de chambres
        douches       : Nombre de douches
        salons        : Nombre de salons
        cuisines      : Nombre de cuisines
        bureaux       : Nombre de bureaux
        forage        : Accès à un forage (eau autonome)
        eneo          : Raccordement au réseau électrique ENEO
        loyer         : Loyer mensuel en FCFA
        created_at    : Date d'insertion automatique
    """

    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_quartier = Column(String, nullable=False, index=True)
    chambres = Column(Integer, nullable=False)
    douches = Column(Integer, nullable=False)
    salons = Column(Integer, nullable=False)
    cuisines = Column(Integer, nullable=False)
    bureaux = Column(Integer, nullable=False)
    forage = Column(Boolean, nullable=False, default=False)
    eneo = Column(Boolean, nullable=False, default=True)
    loyer = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

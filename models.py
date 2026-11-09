"""Modèles SQLAlchemy pour HelpDesk."""

from database import db


class Ticket(db.Model):
    """Représente un ticket d'assistance informatique."""

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    statut = db.Column(db.String(20), nullable=False, default="Ouvert")
    priorite = db.Column(db.String(20), nullable=False, default="Basse")

    def to_dict(self):
        """Convertit le ticket en dictionnaire (utile pour l'API JSON plus tard)."""
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "statut": self.statut,
            "priorite": self.priorite,
        }

    def __repr__(self):
        return f"<Ticket #{self.id} : {self.titre}>"
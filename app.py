"""Routes et initialisation de l'application HelpDesk."""

import os
import secrets

from flask import Flask, flash, redirect, render_template, request, url_for

from database import db
from models import Ticket

app = Flask(__name__)

# Utilise une clé configurée en production ou une clé aléatoire pour le développement local.
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

# Stocke la base SQLite dans le dossier instance/ de l'application Flask.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def initialiser_base_de_donnees():
    """Crée les tables et ajoute les tickets de démonstration une seule fois."""
    with app.app_context():
        db.create_all()
        if Ticket.query.count() == 0:
            db.session.add_all([
                Ticket(titre="Problème de connexion", description="Impossible de me connecter au réseau",
                       statut="Ouvert", priorite="Haute"),
                Ticket(titre="Installer un logiciel", description="Besoin de Word sur mon poste",
                       statut="Fermé", priorite="Basse"),
                Ticket(titre="Écran cassé", description="L'écran de mon laptop ne s'allume plus",
                       statut="En cours", priorite="Moyenne"),
            ])
            db.session.commit()


initialiser_base_de_donnees()

STATUTS_AUTORISES = {"Ouvert", "En cours", "Fermé"}
PRIORITES_AUTORISEES = {"Haute", "Moyenne", "Basse"}


def lire_champs_ticket():
    """Nettoie et valide les champs reçus depuis un formulaire de ticket."""
    titre = request.form.get("titre", "").strip()
    description = request.form.get("description", "").strip()
    statut = request.form.get("statut", "Ouvert")
    priorite = request.form.get("priorite", "Basse")

    if not titre:
        return None, "Le titre est obligatoire."
    if len(titre) > 120:
        return None, "Le titre ne peut pas dépasser 120 caractères."
    if len(description) > 2000:
        return None, "La description ne peut pas dépasser 2 000 caractères."
    if statut not in STATUTS_AUTORISES:
        return None, "Veuillez choisir un statut valide."
    if priorite not in PRIORITES_AUTORISEES:
        return None, "Veuillez choisir une priorité valide."

    return {
        "titre": titre,
        "description": description,
        "statut": statut,
        "priorite": priorite,
    }, None


@app.route("/")
def accueil():
    """Affiche la page d'accueil."""
    return render_template("index.html")


@app.route("/about")
def about():
    """Affiche la page de présentation de HelpDesk."""
    return render_template("about.html")


@app.route("/tickets")
def liste_tickets():
    """Affiche tous les tickets enregistrés dans la base de données."""
    tous_les_tickets = Ticket.query.order_by(Ticket.id).all()
    return render_template("tickets.html", tickets=tous_les_tickets)


@app.route("/tickets/nouveau", methods=["GET"])
def nouveau_ticket_form():
    """Affiche un formulaire vide pour créer un ticket."""
    return render_template("ticket_form.html", ticket=None, action="Créer")


@app.route("/tickets/nouveau", methods=["POST"])
def creer_ticket():
    """Valide et ajoute un ticket, puis redirige vers la liste."""
    champs, erreur = lire_champs_ticket()
    if erreur:
        flash(erreur, "danger")
        return render_template(
            "ticket_form.html",
            ticket=None,
            action="Créer",
            form_data=request.form,
        ), 400

    nouveau_ticket = Ticket(**champs)
    db.session.add(nouveau_ticket)
    db.session.commit()

    flash(f"Le ticket « {nouveau_ticket.titre} » a été créé.", "success")
    return redirect(url_for("liste_tickets"))


@app.route("/tickets/<int:ticket_id>/modifier", methods=["GET"])
def modifier_ticket_form(ticket_id):
    """Affiche le formulaire prérempli du ticket demandé."""
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash(f"Le ticket #{ticket_id} est introuvable.", "danger")
        return redirect(url_for("liste_tickets"))

    return render_template("ticket_form.html", ticket=ticket, action="Modifier")


@app.route("/tickets/<int:ticket_id>/modifier", methods=["POST"])
def modifier_ticket(ticket_id):
    """Valide les changements et met à jour le ticket demandé."""
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash(f"Le ticket #{ticket_id} est introuvable.", "danger")
        return redirect(url_for("liste_tickets"))

    champs, erreur = lire_champs_ticket()
    if erreur:
        flash(erreur, "danger")
        return render_template(
            "ticket_form.html",
            ticket=ticket,
            action="Modifier",
            form_data=request.form,
        ), 400

    ticket.titre = champs["titre"]
    ticket.description = champs["description"]
    ticket.statut = champs["statut"]
    ticket.priorite = champs["priorite"]
    db.session.commit()

    flash(f"Le ticket #{ticket_id} a été modifié.", "success")
    return redirect(url_for("liste_tickets"))


@app.route("/tickets/<int:ticket_id>/supprimer", methods=["POST"])
def supprimer_ticket(ticket_id):
    """Supprime le ticket demandé après confirmation dans l'interface."""
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash(f"Le ticket #{ticket_id} est introuvable.", "danger")
        return redirect(url_for("liste_tickets"))

    db.session.delete(ticket)
    db.session.commit()

    flash(f"Le ticket « {ticket.titre} » a été supprimé.", "success")
    return redirect(url_for("liste_tickets"))


# Ne démarre le serveur de développement que lorsque ce fichier est lancé directement.
if __name__ == "__main__":
    app.run(debug=True)

"""Configuration de la base de données SQLAlchemy."""

from flask_sqlalchemy import SQLAlchemy

# Instance SQLAlchemy partagée dans tout le projet
# Elle est initialisée dans app.py via db.init_app(app)
db = SQLAlchemy()
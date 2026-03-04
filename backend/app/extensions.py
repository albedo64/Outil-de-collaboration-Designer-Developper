from flask_bcrypt import Bcrypt
from flasgger import Swagger
from pymongo import MongoClient
from flask import g, current_app
from flask_cors import CORS
from werkzeug.local import LocalProxy

bcrypt = Bcrypt()
swagger = Swagger()
# NOUVEAU: Initialisation de l'objet CORS pour Angular
cors = CORS()

def get_db():
    """
    Fonction pour obtenir la connexion à la base de données pour la requête actuelle.
    La connexion est stockée dans le contexte 'g' de Flask.
    """
    return g.db

# db est un proxy qui appellera get_db() quand il sera utilisé.
db = LocalProxy(get_db)
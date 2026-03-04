from flask import Flask, jsonify, g, render_template
from asgiref.wsgi import WsgiToAsgi
from config import Config
from .extensions import bcrypt, swagger, cors, MongoClient
import os

def create_app(config_class=Config):
    """App Factory: crée et configure l'application Flask."""
    
    static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, static_folder=static_folder_path)
    app.config.from_object(config_class)

    # Initialiser les extensions avec l'application
    bcrypt.init_app(app)
    swagger.init_app(app)

    # NOUVEAU: Initialisation de CORS pour autoriser les requêtes de votre app Angular.
    # Pour le développement, on peut autoriser localhost:4200 (port par défaut d'Angular).
    cors.init_app(app, resources={r"/*": {"origins": "http://localhost:4200"}}) 
    # NOTE: Pour la production, remplacez l'URL par celle de votre frontend déployé.
    # Par exemple: "https://votre-domaine-frontend.com"

    # Créer une seule instance du client MongoDB
    mongo_client = MongoClient(app.config['MONGO_URI'])

    @app.before_request
    def before_request():
        """Avant chaque requête, stocke la connexion à la DB dans le contexte 'g'."""
        g.db = mongo_client.get_database()

    @app.teardown_appcontext
    def teardown_db(exception):
        """Ferme la connexion à la DB à la fin de la requête."""
        # Bien que MongoClient gère les pools, fermer le client est une bonne pratique
        # dans certains scénarios. Pour la simplicité, nous ne faisons rien ici,
        # car le client est conçu pour être persistant.
        pass

    # Enregistrer les Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .designs import designs_bp
    app.register_blueprint(designs_bp)

    @app.route('/')
    def index():
        # On retourne à une réponse JSON simple pour la racine de l'API.
        return jsonify({'message': 'Welcome to the Design/Developer Collaboration API!'})

    # Retourner l'application WSGI et sa version ASGI
    return app, WsgiToAsgi(app)

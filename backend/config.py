import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Classe de configuration de base."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'une_cle_secrete_par_defaut_tres_securisee')
    MONGO_URI = os.environ.get('DATABASE_URI', 'mongodb://localhost:27017/design_collab_db')
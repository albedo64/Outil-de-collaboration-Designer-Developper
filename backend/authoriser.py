from functools import wraps
from flask import jsonify, request, current_app
import jwt

def token_required(f):
    """Vérifie la validité du JWT et décode le token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Le token est généralement passé dans l'en-tête 'Authorization: Bearer <token>'
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Décode le token en utilisant la clé secrète
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.current_user = data # Ajoute les données du token (incluant le rôle) à l'objet requête
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            return jsonify({'message': 'Token is invalid or expired'}), 401

        return f(*args, **kwargs)
    return decorated

def roles_required(roles):
    """Vérifie si le rôle de l'utilisateur correspond aux rôles autorisés."""
    def wrapper(f):
        @wraps(f)
        @token_required # Doit vérifier le token avant de vérifier le rôle
        def decorated_function(*args, **kwargs):
            user_role = request.current_user.get('role')
            if user_role not in roles:
                # Réponse standard pour l'accès refusé (403 Forbidden)
                return jsonify({'message': 'Permission denied: Insufficient role'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
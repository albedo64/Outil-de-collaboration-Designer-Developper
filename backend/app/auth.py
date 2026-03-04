from flask import Blueprint, request, jsonify, current_app, render_template

from authoriser import token_required
from .extensions import bcrypt, db
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

ALLOWED_ROLES = {'designer', 'developer'}

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user
    This endpoint allows for the creation of a new user.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                example: newuser@example.com
              password:
                type: string
                example: a_strong_password
              role:
                type: string
                enum: [designer, developer]
                example: designer
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing data or invalid role
      409:
        description: User already exists
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body must be JSON'}), 400

    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if not all([email, password, role]):
        return jsonify({'message': 'Missing email, password, or role'}), 400

    if role not in ALLOWED_ROLES:
        return jsonify({'message': "Invalid role. Must be 'designer' or 'developer'"}), 400

    if db.users.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user_data = {
        'email': email,
        'password_hash': hashed_password,
        'role': role,
        'username': email.split('@')[0]
    }
    
    db.users.insert_one(user_data)
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Logs a user in
    Authenticates a user and returns a JWT token if successful.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                example: designer@example.com
              password:
                type: string
                example: password123
    responses:
      200:
        description: Login successful, token and role returned
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = db.users.find_one({'email': email})

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        token_payload = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token, 'role': user['role']}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logs a user out (client-side only for JWT)
    
    In a JWT system, this primarily confirms the token's validity
    and prompts the client to discard the token.
    """
    # Si nous utilisions une liste noire de tokens (token blacklist), 
    # la logique serait ici d'ajouter le token actuel à cette liste.
    
    # Pour l'approche MVP simple, on confirme la déconnexion.
    return jsonify({'message': 'Logout successful (Token invalidated client-side)'}), 200
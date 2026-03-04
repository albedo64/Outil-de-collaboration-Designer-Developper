from flask import Blueprint, request, jsonify
from .extensions import db
from authoriser import roles_required
from bson.objectid import ObjectId
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Configuration pour l'upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

designs_bp = Blueprint('designs', __name__)


@designs_bp.route('/designs/import', methods=['POST'])
@roles_required(['designer'])
def import_design():
    # Les données sont maintenant envoyées en multipart/form-data
    if 'designData' not in request.form:
        return jsonify({'message': 'Missing designData part in the form'}), 400
    
    import json
    data = json.loads(request.form['designData'])
    files = request.files.getlist('images')

    if not files:
        return jsonify({'message': 'At least one image is required'}), 400

    image_urls = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Pour éviter les conflits, on peut préfixer avec un timestamp ou un UUID
            unique_filename = f"{datetime.utcnow().timestamp()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            # NOUVEAU : Construire une URL complète
            # request.host_url donnera "http://127.0.0.1:8000/"
            image_urls.append(f'{request.host_url}static/uploads/{unique_filename}')

    # Le modèle de données est maintenant beaucoup plus riche
    design_doc = {
        'project_id': 'proj-abc',
        'designer_id': request.current_user['user_id'],
        'name': data.get('name', 'Untitled Design'),
        'version': data.get('version', '1.0'),
        'description': data.get('description', ''),
        'created_at': datetime.utcnow(),
        'status': 'Draft',
        'imageUrls': image_urls,
        'tokens': data.get('tokens', []), # Stocke les IDs des tokens
        'codeSnippets': data.get('codeSnippets', {}),
        'layers': data.get('layers', [])
    }
    
    result = db.designs.insert_one(design_doc)
    
    return jsonify({
        'message': 'Design imported successfully', 
        'id': str(result.inserted_id)
    }), 201


@designs_bp.route('/designs/<design_id>', methods=['GET'])
@roles_required(['designer', 'developer'])
def get_design(design_id):
    try:
        design_doc = db.designs.find_one({'_id': ObjectId(design_id)})
    except Exception:
        return jsonify({'message': 'Invalid design ID format'}), 400
    
    if not design_doc:
        return jsonify({'message': 'Design not found'}), 404

    design_doc['_id'] = str(design_doc['_id'])
    # Ensure created_at is ISO formatted with Z
    if 'created_at' in design_doc and isinstance(design_doc['created_at'], datetime):
        design_doc['created_at'] = design_doc['created_at'].isoformat() + "Z"

    # Pour la vue détaillée, on doit "hydrater" les tokens avec leurs vraies données
    # On suppose que les tokens sont stockés dans une collection 'design_tokens'
    # MODIFICATION : On utilise directement les IDs de type string
    token_ids = design_doc.get('tokens', [])
    if token_ids:
        # MODIFICATION : On recherche sur le champ 'id' au lieu de '_id'
        # Assurez-vous que votre collection 'design_tokens' a bien un champ 'id'
        token_cursor = db.design_tokens.find({'id': {'$in': token_ids}})
        full_tokens = []
        for token in token_cursor:
            token['_id'] = str(token['_id'])
            full_tokens.append(token)
        design_doc['tokens'] = full_tokens
    else:
        design_doc['tokens'] = []

    # Renommer _id en id pour le frontend
    design_doc['id'] = str(design_doc.pop('_id'))
    
    return jsonify(design_doc), 200


@designs_bp.route('/designs/<design_id>', methods=['PUT'])
@roles_required(['designer'])
def update_design(design_id):
    data = request.get_json()
    user_id = request.current_user['user_id']
    
    # 1. Optionnel: Récupérer les données de la maquette à partir de l'API de design (comme dans l'import)
    # 2. Mettre à jour le document MongoDB
    try:
        # Vérification si le designer est bien celui qui a créé le design ou a les droits sur le projet
        result = db.designs.update_one(
            {'_id': ObjectId(design_id), 'designer_id': user_id}, # Cible le design par ID ET par designer_id
            {'$set': {
                'data': data.get('data', {}),  # Permet de mettre à jour le JSON de structure
                'status': data.get('status', 'Draft'),
                'updated_at': datetime.utcnow()
            }}
        )
        if result.matched_count == 0:
            return jsonify({'message': 'Design not found or you do not have permission to update'}), 404

    except Exception:
        return jsonify({'message': 'Invalid design ID format'}), 400
        
    return jsonify({'message': f'Design {design_id} updated successfully'}), 200


@designs_bp.route('/designs/<design_id>/specs', methods=['GET'])
@roles_required(['designer', 'developer'])
def get_design_specs(design_id):
    # ... (Copiez le code de la fonction get_design_specs ici)
    return jsonify({'specs': f'Technical specs for design {design_id}'}), 200


@designs_bp.route('/designs/<design_id>/assets', methods=['GET'])
@roles_required(['developer'])
def export_assets(design_id):
    # ... (Copiez le code de la fonction export_assets ici)
    return jsonify({'message': f'Assets exported for design {design_id} by Developer'}), 200


@designs_bp.route('/designs/<design_id>/comments', methods=['POST'])
@roles_required(['designer', 'developer'])
def add_comment(design_id):
    data = request.get_json()
    content = data.get('text')
    element_id = data.get('element_id', None)

    if not content:
        return jsonify({'message': 'Comment text is required'}), 400

    try:
        design_object_id = ObjectId(design_id)
    except Exception:
        return jsonify({'message': 'Invalid design ID format'}), 400

    comment_doc = {
        'design_id': design_object_id,
        'user_id': request.current_user['user_id'],
        'username': request.current_user['email'],
        'role': request.current_user['role'],
        'content': content,
        'element_id': element_id,
        'created_at': datetime.utcnow(),
        'resolved': False
    }
    
    result = db.comments.insert_one(comment_doc)
    
    new_comment = db.comments.find_one({'_id': result.inserted_id})
    new_comment['_id'] = str(new_comment['_id'])
    new_comment['created_at'] = new_comment['created_at'].isoformat() + "Z"
    new_comment['design_id'] = str(new_comment['design_id'])
    
    return jsonify(new_comment), 201


@designs_bp.route('/designs/<design_id>/comments', methods=['GET'])
@roles_required(['designer', 'developer'])
def get_comments(design_id):
    try:
        comments_cursor = db.comments.find({'design_id': ObjectId(design_id)}).sort('created_at', 1)
    except Exception:
        return jsonify({'message': 'Invalid design ID format'}), 400
    
    comments_list = []
    for comment in comments_cursor:
        comment['_id'] = str(comment['_id'])
        comment['created_at'] = comment['created_at'].isoformat() + "Z" 
        comment['design_id'] = str(comment['design_id'])
        comments_list.append(comment)

    return jsonify(comments_list), 200


@designs_bp.route('/designs/<design_id>/status', methods=['PUT'])
@roles_required(['designer', 'developer'])
def update_design_status(design_id):
    data = request.get_json()
    new_status = data.get('status')
    
    ALLOWED_STATUSES = {
        'Draft': ['designer'],
        'Ready for Dev': ['designer'],
        'In Progress': ['developer'],
        'Done': ['developer', 'designer'],
        'Needs Review': ['developer', 'designer']
    }

    if new_status not in ALLOWED_STATUSES:
        return jsonify({'message': f'Invalid status: {new_status}'}), 400
    
    user_role = request.current_user['role']
    if user_role not in ALLOWED_STATUSES.get(new_status, []):
        return jsonify({'message': f'Role {user_role} cannot set status to {new_status}'}), 403

    try:
        result = db.designs.update_one(
            {'_id': ObjectId(design_id)},
            {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
        )
        if result.matched_count == 0:
            return jsonify({'message': 'Design not found'}), 404

    except Exception:
        return jsonify({'message': 'Invalid design ID format'}), 400
    
    return jsonify({'message': f'Design {design_id} status updated to {new_status}'}), 200


@designs_bp.route('/designs', methods=['GET'])
@roles_required(['designer', 'developer'])
def list_designs():
    designs_cursor = db.designs.find({}) # Filter by project_id in production
    
    designs_list = []
    for design in designs_cursor:
        designs_list.append({
            'id': str(design['_id']), # Garder la cohérence
            'name': design.get('name', 'Untitled Design'),
            'status': design.get('status', 'Draft'),
            'version': design.get('version', '1.0'),
            'created_at': design.get('created_at').isoformat() + "Z" if design.get('created_at') else None,
            # NOUVEAU : S'assurer que la miniature a aussi une URL complète
            'imageUrl': design.get('imageUrls', ['https://via.placeholder.com/300x200?text=No+Image'])[0]
        })

    return jsonify(designs_list), 200

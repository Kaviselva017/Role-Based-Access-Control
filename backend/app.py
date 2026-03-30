from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os
from models import User, AccessKey, Document, ChatHistory, QueryMetrics, Role

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_EXPIRATION = 24  # hours

# Middleware
def token_required(f):
    """Decorator to check JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def role_required(*roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user['role'] not in roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator


def permission_required(permission):
    """Decorator to check user permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if not Role.has_permission(current_user['role'], permission):
                return jsonify({'message': 'Permission denied'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator


# ==================== AUTHENTICATION ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user (admin only)"""
    data = request.get_json()
    
    try:
        user = User.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'employee'),
            department=data.get('department', '')
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user['role']
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    user = User.get_user_by_username(data.get('username'))
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    import hashlib
    password_hash = hashlib.sha256(data.get('password', '').encode()).hexdigest()
    
    if user['password'] != password_hash:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Update last login
    User.update_user(str(user['_id']), last_login=datetime.utcnow())
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': str(user['_id']),
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'department': user['department']
        }
    }), 200


@app.route('/api/auth/apikey', methods=['POST'])
def login_with_apikey():
    """Login using access key"""
    data = request.get_json()
    key = data.get('key')
    
    if not key:
        return jsonify({'message': 'Access key is required'}), 400
    
    # Verify the access key
    access_key_doc = AccessKey.verify_key(key)
    
    if not access_key_doc:
        return jsonify({'message': 'Invalid or expired access key'}), 401
    
    # Get the user associated with this key
    user = User.get_user_by_id(str(access_key_doc['user_id']))
    
    if not user or not user.get('is_active'):
        return jsonify({'message': 'User not found or inactive'}), 401
    
    # Update last login
    User.update_user(str(user['_id']), last_login=datetime.utcnow())
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': str(user['_id']),
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'department': user['department']
        }
    }), 200


# ==================== USER MANAGEMENT ====================

@app.route('/api/users', methods=['GET'])
@token_required
@permission_required('manage_users')
def get_users(current_user):
    """Get all users (admin only)"""
    users = User.get_all_users()
    return jsonify({
        'users': [
            {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'department': user.get('department', ''),
                'last_login': user.get('last_login').isoformat() if user.get('last_login') else None,
                'created_at': user['created_at'].isoformat()
            }
            for user in users
        ]
    }), 200


@app.route('/api/users/<user_id>', methods=['PUT'])
@token_required
@permission_required('manage_users')
def update_user(current_user, user_id):
    """Update user (admin only)"""
    data = request.get_json()
    
    # Prevent admin from removing their own admin status
    if user_id == current_user['_id'] and data.get('role') != 'admin':
        return jsonify({'message': 'Cannot change your own role'}), 400
    
    success = User.update_user(user_id, **data)
    
    if success:
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/users/<user_id>', methods=['DELETE'])
@token_required
@permission_required('manage_users')
def delete_user(current_user, user_id):
    """Delete user (admin only)"""
    
    # Prevent admin from deleting themselves
    if user_id == str(current_user['_id']):
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    success = User.delete_user(user_id)
    
    if success:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# ==================== ACCESS KEYS ====================

@app.route('/api/access-keys', methods=['POST'])
@token_required
@permission_required('generate_keys')
def create_access_key(current_user):
    """Create new access key (admin only)"""
    data = request.get_json()
    
    key_data = AccessKey.generate_key(
        user_id=data.get('user_id', str(current_user['_id'])),
        key_name=data.get('key_name', ''),
        expiry_days=data.get('expiry_days', 365)
    )
    
    return jsonify({
        'message': 'Access key created successfully',
        'key': key_data
    }), 201


@app.route('/api/access-keys', methods=['GET'])
@token_required
def get_access_keys(current_user):
    """Get user's access keys"""
    # Users can only see their own keys unless they're admin
    if current_user['role'] != 'admin':
        user_id = current_user['_id']
    else:
        user_id = request.args.get('user_id', current_user['_id'])
    
    keys = AccessKey.get_user_keys(str(user_id))
    return jsonify({
        'keys': [
            {
                'id': str(key['_id']),
                'name': key['name'],
                'created_at': key['created_at'].isoformat(),
                'expires_at': key['expires_at'].isoformat(),
                'last_used': key['last_used'].isoformat() if key.get('last_used') else None,
                'is_active': key['is_active']
            }
            for key in keys
        ]
    }), 200


@app.route('/api/access-keys/<key_id>', methods=['DELETE'])
@token_required
def revoke_access_key(current_user, key_id):
    """Revoke access key"""
    success = AccessKey.revoke_key(key_id)
    
    if success:
        return jsonify({'message': 'Access key revoked successfully'}), 200
    else:
        return jsonify({'message': 'Access key not found'}), 404


# ==================== DOCUMENTS ====================

@app.route('/api/documents/upload', methods=['POST'])
@token_required
@permission_required('upload_docs')
def upload_document(current_user):
    """Upload document (admin only)"""
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    department = request.form.get('department', '')
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    try:
        content = file.read().decode('utf-8')
        
        doc_data = Document.upload_document(
            filename=file.filename,
            content=content,
            file_type=file.filename.split('.')[-1],
            uploaded_by_user_id=str(current_user['_id']),
            department=department
        )
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': doc_data
        }), 201
    except Exception as e:
        return jsonify({'message': f'Upload failed: {str(e)}'}), 400


@app.route('/api/documents', methods=['GET'])
@token_required
def get_documents(current_user):
    """Get documents (filtered by department for non-admins)"""
    
    if current_user['role'] == 'admin':
        documents = Document.get_all_documents()
    else:
        # Non-admin users only see documents from their department
        documents = Document.get_documents_by_department(current_user.get('department', ''))
    
    return jsonify({
        'documents': [
            {
                'id': str(doc['_id']),
                'filename': doc['filename'],
                'file_type': doc['file_type'],
                'department': doc['department'],
                'uploaded_at': doc['uploaded_at'].isoformat(),
                'is_indexed': doc['is_indexed']
            }
            for doc in documents
        ]
    }), 200


@app.route('/api/documents/<doc_id>', methods=['DELETE'])
@token_required
@permission_required('upload_docs')
def delete_document(current_user, doc_id):
    """Delete document (admin only)"""
    success = Document.delete_document(doc_id)
    
    if success:
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'message': 'Document not found'}), 404


# ==================== CHAT ====================

@app.route('/api/chat', methods=['POST'])
@token_required
@permission_required('chat')
def chat(current_user):
    """Send chat query"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'message': 'Query cannot be empty'}), 400
    
    # TODO: Integrate with RAG system
    # For now, return a placeholder response
    response = f"Response to query from {current_user['role']}: {query}"
    referenced_docs = []
    
    # Log chat
    chat_id = ChatHistory.save_chat(
        user_id=str(current_user['_id']),
        query=query,
        response=response,
        referenced_docs=referenced_docs
    )
    
    # Log metrics
    QueryMetrics.log_query(
        user_id=str(current_user['_id']),
        query=query,
        role=current_user['role']
    )
    
    return jsonify({
        'chat_id': chat_id,
        'query': query,
        'response': response,
        'referenced_docs': referenced_docs
    }), 200


@app.route('/api/chat/history', methods=['GET'])
@token_required
@permission_required('view_history')
def get_chat_history(current_user):
    """Get user's chat history"""
    limit = request.args.get('limit', 50, type=int)
    history = ChatHistory.get_user_chat_history(str(current_user['_id']), limit=limit)
    
    return jsonify({
        'history': [
            {
                'id': str(chat['_id']),
                'query': chat['query'],
                'response': chat['response'],
                'timestamp': chat['timestamp'].isoformat(),
                'referenced_docs': chat.get('referenced_docs', [])
            }
            for chat in history
        ]
    }), 200


# ==================== DASHBOARD ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@token_required
@permission_required('view_dashboard')
def get_dashboard_stats(current_user):
    """Get dashboard statistics (admin only)"""
    stats = QueryMetrics.get_dashboard_stats()
    activity = QueryMetrics.get_user_activity(days=7)
    
    return jsonify({
        'stats': {
            'total_queries': stats['total_queries'],
            'total_users': stats['total_users'],
            'access_denied': stats['access_denied'],
            'queries_by_role': [
                {
                    'role': item['_id'],
                    'count': item['count']
                }
                for item in stats['queries_by_role']
            ]
        },
        'activity': activity
    }), 200


@app.route('/api/dashboard/queries', methods=['GET'])
@token_required
@permission_required('view_dashboard')
def get_all_queries(current_user):
    """Get all queries (admin only)"""
    limit = request.args.get('limit', 100, type=int)
    history = ChatHistory.get_all_chat_history(limit=limit)
    
    return jsonify({
        'queries': [
            {
                'id': str(chat['_id']),
                'user_id': str(chat['user_id']),
                'query': chat['query'],
                'response': chat['response'],
                'timestamp': chat['timestamp'].isoformat()
            }
            for chat in history
        ]
    }), 200


# ==================== ROLES ====================

@app.route('/api/roles', methods=['GET'])
def get_all_roles():
    """Get all available roles"""
    roles = Role.get_all_roles()
    return jsonify({
        'roles': [
            {
                'key': key,
                'name': role['name'],
                'level': role['level'],
                'permissions': role['permissions']
            }
            for key, role in roles.items()
        ]
    }), 200


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os
try:
    from .models import User, AccessKey, Document, ChatHistory, QueryMetrics, Role, users_collection
    from .rag_system import search_relevant_documents, generate_rag_response, get_role_based_response, process_document_for_rag
except ImportError:
    from models import User, AccessKey, Document, ChatHistory, QueryMetrics, Role, users_collection
    from rag_system import search_relevant_documents, generate_rag_response, get_role_based_response, process_document_for_rag

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": ["*", "https://role-based-access-control-kaviselva017s-projects.vercel.app"]
}})

@app.after_request
def after_request(response):
    # Support multiple origins including the user's specific vercel domain
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_EXPIRATION = 24  # hours

# Health Check / Root Index
@app.route('/')
def home():
    return jsonify({
        "status": "ONLINE",
        "platform": "Dragon Intelligence Platform",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/login",
            "chat": "/api/chat",
            "stats": "/api/dashboard/stats"
        }
    }), 200

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


# The actual get_role_based_response is perfectly imported from rag_system.py



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
    username_or_email = data.get('username')
    
    # Try to find user by username first, then by email
    user = User.get_user_by_username(username_or_email)
    if not user:
        user = users_collection.find_one({'email': username_or_email})
    
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


@app.route('/api/auth/verify-key', methods=['POST'])
def verify_key():
    """Verify access key for user (Step 2 of login flow)"""
    # Get Bearer token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Missing authorization token'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # Verify and decode the token
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    
    # Get the access key from request
    data = request.get_json()
    access_key = data.get('accessKey')
    
    if not access_key:
        return jsonify({'message': 'Access key is required'}), 400
    
    # Verify the access key
    access_key_doc = AccessKey.verify_key(access_key)
    
    if not access_key_doc:
        return jsonify({'message': 'Invalid or expired access key'}), 401
    # Check if the access key belongs to the authenticated user
    if str(access_key_doc.get('user_id')) != user_id:
        # User Feature Request: If key used by new user, automatically allocate it to them!
        from models import access_keys_collection
        from bson import ObjectId
        access_keys_collection.update_one(
            {'_id': access_key_doc['_id']},
            {'$set': {'user_id': ObjectId(user_id)}}
        )
        access_key_doc['user_id'] = ObjectId(user_id)
    
    return jsonify({
        'message': 'Access key verified',
        'authorized': True
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
        raw_bytes = file.read()
        try:
            content = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = raw_bytes.decode('cp1252')
            except UnicodeDecodeError:
                content = raw_bytes.decode('utf-8', errors='replace')
        
        doc_data = Document.upload_document(
            filename=file.filename,
            content=content,
            file_type=file.filename.split('.')[-1],
            uploaded_by_user_id=str(current_user['_id']),
            department=department
        )
        
        # Index document for RAG search
        from rag_system import process_document_for_rag
        process_document_for_rag(doc_data['id'], content, file.filename, department)
        
        return jsonify({
            'message': 'Document uploaded and indexed successfully',
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
    """Send chat query with RAG (Retrieval-Augmented Generation)"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'message': 'Query cannot be empty'}), 400
    
    # First check role-based restrictions to instantly deny unauthorized queries
    role_response = get_role_based_response(query, current_user['role'])
    if role_response.get('access_denied'):
        # Log metrics (track access denials)
        QueryMetrics.log_query(
            user_id=str(current_user['_id']),
            query=query,
            role=current_user['role'],
            access_denied=True
        )
        return jsonify({
            'chat_id': None,
            'query': query,
            'response': role_response['response'],
            'access_denied': True,
            'role_info': role_response.get('role_info', {}),
            'referenced_docs': [],
            'source': 'Role-based'
        }), 200

    # Try to search for relevant documents first (RAG)
    user_department = current_user.get('department', '')
    search_dept = None if current_user['role'] in ['admin', 'c-level'] else user_department
    retrieved_docs = search_relevant_documents(query, department=search_dept, limit=3)
    
    # Generate response based on documents or role-based fallback
    if retrieved_docs and any(doc['similarity'] > 0.1 for doc in retrieved_docs):
        # Use RAG for document-based answer
        rag_result = generate_rag_response(query, current_user['role'], search_dept, retrieved_docs)
        response = rag_result['response']
        referenced_docs = rag_result['referenced_docs']
        access_denied = False
        role_info = role_response.get('role_info', {})
    else:
        # Fall back to role-based response
        role_response = get_role_based_response(query, current_user['role'])
        response = role_response['response']
        access_denied = role_response['access_denied']
        role_info = role_response.get('role_info', {})
        referenced_docs = []
    
    # Log chat
    chat_id = ChatHistory.save_chat(
        user_id=str(current_user['_id']),
        query=query,
        response=response,
        referenced_docs=referenced_docs
    )
    
    # Log metrics (track access denials)
    QueryMetrics.log_query(
        user_id=str(current_user['_id']),
        query=query,
        role=current_user['role'],
        access_denied=access_denied
    )
    
    return jsonify({
        'chat_id': chat_id,
        'query': query,
        'response': response,
        'access_denied': access_denied,
        'role_info': role_info,
        'referenced_docs': referenced_docs,
        'source': 'RAG' if retrieved_docs else 'Role-based'
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
    """Get comprehensive dashboard statistics (admin only)"""
    try:
        from models import users_collection, queries_collection, documents_collection, chat_history_collection, access_keys_collection
        
        stats = QueryMetrics.get_dashboard_stats()
        
        # Total counts
        total_queries = stats.get('total_queries', 0)
        total_users = stats.get('total_users', 0)
        access_denied_count = stats.get('access_denied', 0)
        total_documents = documents_collection.count_documents({})
        total_keys = access_keys_collection.count_documents({'is_active': True})
        
        # Active today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_today = len(queries_collection.distinct('user_id', {'timestamp': {'$gte': today_start}}))
        
        # Resolution / denial rate
        denial_rate = round((access_denied_count / total_queries * 100), 1) if total_queries > 0 else 0
        resolution_rate = round(100 - denial_rate, 1)
        
        # Queries by role
        queries_by_role = [
            {'role': item['_id'] or 'unknown', 'count': item['count']}
            for item in stats.get('queries_by_role', [])
        ]
        
        # Daily activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_pipeline = [
            {'$match': {'timestamp': {'$gte': seven_days_ago}}},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
                'count': {'$sum': 1},
                'denied': {'$sum': {'$cond': ['$access_denied', 1, 0]}}
            }},
            {'$sort': {'_id': 1}}
        ]
        daily_activity_raw = list(queries_collection.aggregate(daily_pipeline))
        
        # Fill in missing days
        daily_activity = []
        for i in range(7):
            day = (datetime.utcnow() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            found = next((d for d in daily_activity_raw if d['_id'] == day), None)
            daily_activity.append({
                'date': day,
                'count': found['count'] if found else 0,
                'denied': found['denied'] if found else 0
            })

        # Top queries
        top_queries_pipeline = [
            {'$group': {'_id': '$query', 'count': {'$sum': 1}, 'last_used': {'$max': '$timestamp'}}},
            {'$sort': {'count': -1}},
            {'$limit': 8}
        ]
        top_queries = [
            {'query': item['_id'], 'count': item['count'], 'last_used': item['last_used'].isoformat() if item.get('last_used') else None}
            for item in chat_history_collection.aggregate(top_queries_pipeline)
        ]
        
        # Top denied queries
        denied_pipeline = [
            {'$match': {'access_denied': True}},
            {'$group': {
                '_id': '$query',
                'count': {'$sum': 1},
                'roles': {'$addToSet': '$role'},
                'last_attempt': {'$max': '$timestamp'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 6}
        ]
        top_denied = [
            {
                'query': item['_id'],
                'count': item['count'],
                'roles': item['roles'],
                'last_attempt': item['last_attempt'].isoformat() if item.get('last_attempt') else None
            }
            for item in queries_collection.aggregate(denied_pipeline)
        ]
        
        # All users with full details
        all_users = list(users_collection.find({}, {'password': 0}))
        users_detail = []
        for u in all_users:
            uid = u['_id']
            user_query_count = queries_collection.count_documents({'user_id': uid})
            user_denied_count = queries_collection.count_documents({'user_id': uid, 'access_denied': True})
            user_chat_count = chat_history_collection.count_documents({'user_id': uid})
            active_keys = access_keys_collection.count_documents({'user_id': uid, 'is_active': True})
            
            first_query = queries_collection.find_one({'user_id': uid}, sort=[('timestamp', 1)])
            last_query = queries_collection.find_one({'user_id': uid}, sort=[('timestamp', -1)])
            
            users_detail.append({
                'id': str(uid),
                'username': u.get('username', ''),
                'email': u.get('email', ''),
                'role': u.get('role', 'employee'),
                'department': u.get('department', ''),
                'is_active': u.get('is_active', True),
                'created_at': u['created_at'].isoformat() if u.get('created_at') else None,
                'last_login': u['last_login'].isoformat() if u.get('last_login') else None,
                'total_queries': user_query_count,
                'denied_queries': user_denied_count,
                'chat_messages': user_chat_count,
                'active_keys': active_keys,
                'first_seen': first_query['timestamp'].isoformat() if first_query else None,
                'last_active': last_query['timestamp'].isoformat() if last_query else None,
            })
        
        # Documents breakdown
        docs_by_dept_pipeline = [
            {'$group': {'_id': '$department', 'count': {'$sum': 1}, 'indexed': {'$sum': {'$cond': ['$is_indexed', 1, 0]}}}},
            {'$sort': {'count': -1}}
        ]
        docs_by_dept = [
            {'department': item['_id'] or 'Unassigned', 'count': item['count'], 'indexed': item['indexed']}
            for item in documents_collection.aggregate(docs_by_dept_pipeline)
        ]
        
        # Role distribution
        role_dist_pipeline = [
            {'$group': {'_id': '$role', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        role_distribution = [
            {'role': item['_id'] or 'unknown', 'count': item['count']}
            for item in users_collection.aggregate(role_dist_pipeline)
        ]
        
        # Security issues / alerts
        security_issues = []
        never_logged_in = users_collection.count_documents({'last_login': None})
        if never_logged_in > 0:
            security_issues.append({
                'severity': 'warning', 'type': 'inactive_users', 'count': never_logged_in,
                'message': f'{never_logged_in} user(s) have never logged in'
            })
        
        if denial_rate > 20:
            security_issues.append({
                'severity': 'high', 'type': 'high_denial_rate', 'count': access_denied_count,
                'message': f'High access denial rate: {denial_rate}% of all queries'
            })

        for ud in users_detail:
            if ud['total_queries'] >= 3 and ud['denied_queries'] / ud['total_queries'] > 0.5:
                security_issues.append({
                    'severity': 'medium', 'type': 'user_high_denial', 'count': ud['denied_queries'],
                    'message': f"User '{ud['username']}' has {ud['denied_queries']}/{ud['total_queries']} queries denied"
                })
        
        # Average response time
        avg_time_pipeline = [
            {'$match': {'response_time': {'$gt': 0}}},
            {'$group': {'_id': None, 'avg': {'$avg': '$response_time'}}}
        ]
        avg_time_result = list(queries_collection.aggregate(avg_time_pipeline))
        avg_response_time = round(avg_time_result[0]['avg'], 2) if avg_time_result else 0
        
        # Peak hours
        peak_pipeline = [
            {'$group': {'_id': {'$hour': '$timestamp'}, 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}, {'$limit': 5}
        ]
        peak_hours = [{'hour': item['_id'], 'count': item['count']} for item in queries_collection.aggregate(peak_pipeline)]
        
        return jsonify({
            'stats': {
                'total_queries': total_queries, 'total_users': total_users, 'access_denied': access_denied_count,
                'active_today': active_today, 'total_documents': total_documents, 'total_active_keys': total_keys,
                'denial_rate': denial_rate, 'resolution_rate': resolution_rate, 'avg_response_time': avg_response_time,
                'queries_by_role': queries_by_role, 'role_distribution': role_distribution,
            },
            'daily_activity': daily_activity, 'top_queries': top_queries, 'top_denied': top_denied, 'users': users_detail,
            'documents': {'total': total_documents, 'by_department': docs_by_dept},
            'security_issues': security_issues, 'peak_hours': peak_hours, 'server_time': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"Dashboard Stats Error: {str(e)}")
        return jsonify({
            'message': 'Failed to retrieve dashboard data',
            'error': str(e), 'status': 'error'
        }), 500


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import secrets
import hashlib

# MongoDB Connection
MONGODB_URL = 'mongodb://localhost:27017'
client = MongoClient(MONGODB_URL)
db = client['company_chatbot_rbac']

# Collections
users_collection = db['users']
roles_collection = db['roles']
documents_collection = db['documents']
access_keys_collection = db['access_keys']
chat_history_collection = db['chat_history']
queries_collection = db['queries']

# Create indexes
users_collection.create_index('username', unique=True)
users_collection.create_index('email', unique=True)
access_keys_collection.create_index('key', unique=True)
access_keys_collection.create_index('user_id')
documents_collection.create_index('user_id')
chat_history_collection.create_index('user_id')
queries_collection.create_index('user_id')


class Role:
    """Role model for RBAC"""
    
    ROLES = {
        'admin': {
            'name': 'Admin',
            'permissions': ['view_dashboard', 'upload_docs', 'manage_users', 'generate_keys', 'chat', 'view_history'],
            'level': 5
        },
        'c-level': {
            'name': 'C-Level',
            'permissions': ['view_dashboard', 'chat', 'view_history'],
            'level': 4
        },
        'finance': {
            'name': 'Finance',
            'permissions': ['chat', 'view_history'],
            'level': 2
        },
        'hr': {
            'name': 'HR',
            'permissions': ['chat', 'view_history'],
            'level': 2
        },
        'marketing': {
            'name': 'Marketing',
            'permissions': ['chat', 'view_history'],
            'level': 2
        },
        'engineering': {
            'name': 'Engineering',
            'permissions': ['chat', 'view_history'],
            'level': 2
        },
        'employee': {
            'name': 'Employee',
            'permissions': ['chat', 'view_history'],
            'level': 1
        }
    }
    
    @classmethod
    def get_role(cls, role_name):
        return cls.ROLES.get(role_name)
    
    @classmethod
    def has_permission(cls, role_name, permission):
        role = cls.get_role(role_name)
        return role and permission in role['permissions']
    
    @classmethod
    def get_all_roles(cls):
        return cls.ROLES


class User:
    """User model"""
    
    @staticmethod
    def create_user(username, email, password, role='employee', department=''):
        """Create a new user"""
        user = {
            '_id': ObjectId(),
            'username': username,
            'email': email,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'role': role,
            'department': department,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'last_login': None
        }
        result = users_collection.insert_one(user)
        return user
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        return users_collection.find_one({'username': username})
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return users_collection.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user fields"""
        kwargs['updated_at'] = datetime.utcnow()
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': kwargs}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_all_users():
        """Get all users (excluding passwords)"""
        return list(users_collection.find({}, {'password': 0}))
    
    @staticmethod
    def get_users_by_role(role):
        """Get all users with a specific role"""
        return list(users_collection.find({'role': role}, {'password': 0}))
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0


class AccessKey:
    """Access key model for API authentication"""
    
    @staticmethod
    def generate_key(user_id, key_name='', expiry_days=365):
        """Generate a new access key for a user"""
        key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        access_key = {
            '_id': ObjectId(),
            'user_id': ObjectId(user_id),
            'key': key_hash,
            'plain_key': key,  # Store plain key once, return it to user
            'name': key_name or f"Key-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=expiry_days),
            'last_used': None,
            'is_active': True
        }
        
        result = access_keys_collection.insert_one(access_key)
        return {
            'id': str(access_key['_id']),
            'key': key,  # Return the plain key only once
            'name': access_key['name'],
            'expires_at': access_key['expires_at'].isoformat(),
            'created_at': access_key['created_at'].isoformat()
        }
    
    @staticmethod
    def verify_key(key):
        """Verify an access key by hash, plain_key, or name"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        access_key = access_keys_collection.find_one_and_update(
            {
                '$or': [{'key': key_hash}, {'name': key}, {'plain_key': key}],
                'is_active': True, 
                'expires_at': {'$gt': datetime.utcnow()}
            },
            {'$set': {'last_used': datetime.utcnow()}},
            return_document=True
        )
        return access_key
    
    @staticmethod
    def get_user_keys(user_id):
        """Get all access keys for a user"""
        keys = list(access_keys_collection.find(
            {'user_id': ObjectId(user_id)},
            {'key': 0, 'plain_key': 0}
        ))
        return keys
    
    @staticmethod
    def revoke_key(key_id):
        """Revoke an access key"""
        result = access_keys_collection.update_one(
            {'_id': ObjectId(key_id)},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0


class Document:
    """Document model for RAG"""
    
    @staticmethod
    def upload_document(filename, content, file_type, uploaded_by_user_id, department=''):
        """Store uploaded document"""
        doc = {
            '_id': ObjectId(),
            'filename': filename,
            'content': content,
            'file_type': file_type,  # pdf, txt, md, csv
            'uploaded_by': ObjectId(uploaded_by_user_id),
            'department': department,
            'uploaded_at': datetime.utcnow(),
            'is_indexed': False,
            'embedding_id': None,
            'summary': ''
        }
        result = documents_collection.insert_one(doc)
        return {
            'id': str(doc['_id']),
            'filename': doc['filename'],
            'uploaded_at': doc['uploaded_at'].isoformat()
        }
    
    @staticmethod
    def get_document(doc_id):
        """Get document by ID"""
        return documents_collection.find_one({'_id': ObjectId(doc_id)})
    
    @staticmethod
    def get_all_documents(department=None):
        """Get all documents, optionally filtered by department"""
        query = {}
        if department:
            query['department'] = department
        return list(documents_collection.find(query))
    
    @staticmethod
    def get_documents_by_department(department):
        """Get documents specific to a department AND the General department (case-insensitive)"""
        if not department:
            return list(documents_collection.find())
            
        import re
        escaped_dept = re.escape(str(department))
        escaped_general = re.escape('General')
        
        # Find docs matching either their specific department OR 'General'
        return list(documents_collection.find({
            '$or': [
                {'department': {'$regex': f"^{escaped_dept}$", '$options': 'i'}},
                {'department': {'$regex': f"^{escaped_general}$", '$options': 'i'}}
            ]
        }))
    
    @staticmethod
    def mark_indexed(doc_id, embedding_id):
        """Mark document as indexed in vector DB"""
        result = documents_collection.update_one(
            {'_id': ObjectId(doc_id)},
            {'$set': {'is_indexed': True, 'embedding_id': embedding_id}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_document(doc_id):
        """Delete a document"""
        result = documents_collection.delete_one({'_id': ObjectId(doc_id)})
        return result.deleted_count > 0


class ChatHistory:
    """Chat history model"""
    
    @staticmethod
    def save_chat(user_id, query, response, referenced_docs=None):
        """Save chat message"""
        chat = {
            '_id': ObjectId(),
            'user_id': ObjectId(user_id),
            'query': query,
            'response': response,
            'referenced_docs': referenced_docs or [],
            'timestamp': datetime.utcnow()
        }
        result = chat_history_collection.insert_one(chat)
        return str(chat['_id'])
    
    @staticmethod
    def get_user_chat_history(user_id, limit=50):
        """Get chat history for a user"""
        return list(chat_history_collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def get_all_chat_history(limit=100):
        """Get all chat history"""
        return list(chat_history_collection.find().sort('timestamp', -1).limit(limit))


class QueryMetrics:
    """Query metrics for analytics"""
    
    @staticmethod
    def log_query(user_id, query, response_time=0, role='', access_denied=False):
        """Log a query for analytics"""
        query_log = {
            '_id': ObjectId(),
            'user_id': ObjectId(user_id),
            'query': query,
            'response_time': response_time,
            'role': role,
            'access_denied': access_denied,
            'timestamp': datetime.utcnow()
        }
        result = queries_collection.insert_one(query_log)
        return str(query_log['_id'])
    
    @staticmethod
    def get_dashboard_stats():
        """Get stats for admin dashboard"""
        total_queries = queries_collection.count_documents({})
        total_users = users_collection.count_documents({})
        access_denied = queries_collection.count_documents({'access_denied': True})
        
        # Queries by role (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        queries_by_role = list(queries_collection.aggregate([
            {'$match': {'timestamp': {'$gte': seven_days_ago}}},
            {'$group': {'_id': '$role', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        return {
            'total_queries': total_queries,
            'total_users': total_users,
            'access_denied': access_denied,
            'queries_by_role': queries_by_role
        }
    
    @staticmethod
    def get_user_activity(days=7):
        """Get user activity for the last N days"""
        since = datetime.utcnow() - timedelta(days=days)
        activity = list(queries_collection.aggregate([
            {'$match': {'timestamp': {'$gte': since}}},
            {'$group': {'_id': '$user_id', 'query_count': {'$sum': 1}}},
            {'$sort': {'query_count': -1}},
            {'$limit': 20}
        ]))
        return activity

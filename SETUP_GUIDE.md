# Dragon Intelligence Platform - Role-Based Access Control

A complete AI-powered company chatbot with comprehensive Role-Based Access Control (RBAC). This application provides secure, role-based access to company documents and information with department-specific access controls.

## Features

### 🔐 Role-Based Access Control (RBAC)
- **Admin**: Full platform access including dashboard, user management, document uploads, and access key generation
- **C-Level**: Executive access to analytics dashboard and chat
- **Department Roles** (Finance, HR, Marketing, Engineering): Department-specific chat access
- **Employee**: Basic chat access within permission scope

### 📊 Admin Features
- **Analytics Dashboard**: View total queries, users, access attempts, and activity trends
- **User Management**: Add, edit, and delete users with role assignment
- **Document Upload**: Upload and manage company documents (TXT, MD, CSV) per department
- **Access Key Generation**: Create and manage API access keys with custom expiry dates
- **Query Monitoring**: Track and analyze all user queries

### 💬 Chat Interface
- Role-based query responses
- Document reference tracking
- Query history with timestamps
- Department-specific document access

### 🔑 Security Features
- JWT-based authentication
- Password hashing with SHA-256
- Access key management for API authentication
- Permission-based route protection
- Department-based document access control

## Technology Stack

### Backend
- **Framework**: Flask with Flask-CORS
- **Database**: MongoDB
- **Authentication**: JWT (PyJWT)
- **API Style**: RESTful

### Frontend
- **Framework**: React 18+
- **Routing**: React Router v6
- **State Management**: Context API
- **Styling**: CSS3 with modern design patterns

## Project Structure

```
company-chatbot-rbac/
├── backend/
│   ├── app.py                 # Flask application and routes
│   ├── models.py              # Database models (User, Role, Document, etc.)
│   ├── requirements.txt        # Python dependencies
│   └── users.db              # SQLite user database (generated)
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main app with routing
│   │   ├── context/
│   │   │   └── AuthContext.jsx # Authentication context
│   │   ├── components/
│   │   │   ├── Layout.jsx     # Main layout with sidebar
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── Chat.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── UserManagement.jsx
│   │   │   ├── AccessKeys.jsx
│   │   │   ├── ChatHistory.jsx
│   │   │   └── ...
│   │   └── styles/
│   │       ├── App.css
│   │       ├── Layout.css
│   │       ├── Chat.css
│   │       ├── Dashboard.css
│   │       └── ...
│   ├── package.json
│   └── public/index.html
├── data/
│   └── uploads/               # Document uploads directory
├── chroma_storage/            # Vector database storage
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn
- MongoDB (local or Atlas)

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
# backend/.env
SECRET_KEY=your-super-secret-key-change-this-in-production
MONGODB_URL=mongodb://localhost:27017/company_chatbot_rbac
FLASK_ENV=development
FLASK_DEBUG=True
```

5. **Initialize database**
```bash
python
>>> from models import User, Role
>>> User.create_user('admin', 'admin@company.com', 'admin123', role='admin')
>>> User.create_user('finance_user', 'finance@company.com', 'pass123', role='finance', department='Finance')
>>> User.create_user('employee_user', 'emp@company.com', 'pass123', role='employee')
>>> exit()
```

6. **Run backend server**
```bash
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Create .env file**
```bash
# frontend/.env
REACT_APP_API_BASE_URL=http://localhost:5000
```

4. **Start development server**
```bash
npm start
# or
yarn start
# Application runs on http://localhost:3000
```

## API Documentation

### Authentication Endpoints

#### Register User (Admin only)
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "admin|c-level|finance|hr|marketing|engineering|employee",
  "department": "string"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response:
{
  "token": "jwt_token_here",
  "user": {
    "id": "user_id",
    "username": "string",
    "email": "string",
    "role": "string",
    "department": "string"
  }
}
```

### User Management (Admin only)

#### Get All Users
```
GET /api/users
Authorization: Bearer {token}
```

#### Update User
```
PUT /api/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "role": "string",
  "department": "string"
}
```

#### Delete User
```
DELETE /api/users/{user_id}
Authorization: Bearer {token}
```

### Documents

#### Upload Document (Admin only)
```
POST /api/documents/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <file>
department: "Finance|HR|Marketing|Engineering"
```

#### Get Documents
```
GET /api/documents
Authorization: Bearer {token}
```

#### Delete Document (Admin only)
```
DELETE /api/documents/{doc_id}
Authorization: Bearer {token}
```

### Access Keys

#### Generate Access Key (Admin only)
```
POST /api/access-keys
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "string",
  "key_name": "string",
  "expiry_days": 365
}
```

#### Get Access Keys
```
GET /api/access-keys
Authorization: Bearer {token}
```

#### Revoke Access Key
```
DELETE /api/access-keys/{key_id}
Authorization: Bearer {token}
```

### Chat & History

#### Send Chat Message
```
POST /api/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "string"
}
```

#### Get Chat History
```
GET /api/chat/history?limit=50
Authorization: Bearer {token}
```

### Dashboard (Admin only)

#### Get Dashboard Statistics
```
GET /api/dashboard/stats
Authorization: Bearer {token}
```

#### Get All Queries
```
GET /api/dashboard/queries?limit=100
Authorization: Bearer {token}
```

## Role Permissions Matrix

| Feature | Admin | C-Level | Department | Employee |
|---------|-------|---------|------------|----------|
| Chat | ✅ | ✅ | ✅ | ✅ |
| View History | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ❌ | ❌ |
| Upload Docs | ✅ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Generate Keys | ✅ | ❌ | ❌ | ❌ |

## Default Users

### Demo Credentials
```
Admin:
  Username: admin
  Password: admin123
  
Finance User:
  Username: finance_user
  Password: pass123
  
Employee:
  Username: employee_user
  Password: pass123
```

## Environment Configuration

### Backend (.env)
```
SECRET_KEY=your-secret-key-here
MONGODB_URL=mongodb://localhost:27017/company_chatbot_rbac
FLASK_ENV=development
FLASK_DEBUG=True
```

### Frontend (.env)
```
REACT_APP_API_BASE_URL=http://localhost:5000
```

## Deployment

### Production Deployment

1. **Backend (Gunicorn + Nginx)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Frontend (Build)**
```bash
npm run build
# Deploy build/ directory to static hosting
```

3. **MongoDB Atlas**
- Replace local MongoDB URL with Atlas connection string
- Update MONGODB_URL in .env

## Troubleshooting

### Database Connection Issues
- Ensure MongoDB is running: `mongod`
- Check MONGODB_URL in backend/.env
- Verify MongoDB credentials if using Atlas

### CORS Errors
- Ensure Flask-CORS is installed
- Check frontend API_BASE_URL matches backend URL

### JWT Token Errors
- Token may be expired (24-hour expiry)
- Clear localStorage and login again
- Check SECRET_KEY in backend/.env

### Port Already in Use
```bash
# Kill process on port
lsof -i :5000       # macOS/Linux
netstat -ano | findstr :5000  # Windows
```

## Security Considerations

1. **Change SECRET_KEY in production**
2. **Update default passwords**
3. **Use HTTPS in production**
4. **Set CORS properly for production domain**
5. **Enable MongoDB authentication**
6. **Regular backups of MongoDB**
7. **API rate limiting recommended**

## Future Enhancements

- [ ] RAG (Retrieval Augmented Generation) integration with Chroma/Pinecone
- [ ] Advanced analytics and reporting
- [ ] Audit logging for all operations
- [ ] Two-factor authentication (2FA)
- [ ] LDAP/Active Directory integration
- [ ] SSO (Single Sign-On) support
- [ ] Document preview and search
- [ ] Real-time notifications
- [ ] Mobile app support

## Contributing

1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Create pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue in the repository.

---

**Built with ❤️ for secure, role-based access to company intelligence**

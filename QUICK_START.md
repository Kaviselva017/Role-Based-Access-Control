# 🐉 Dragon Intelligence Platform - Quick Start Guide

## Current Status

✅ **Completed:**
- Full RBAC system architecture with 5 roles
- React frontend with updated login interface matching your design
- Flask backend with JWT authentication
- All CSS styling with monospace fonts and cyan/blue theme
- Demo user credentials built into the login page
- GitHub repository with all code pushed

⏳ **Next Steps:**
1. Install MongoDB
2. Start MongoDB
3. Create demo users
4. Run the application

---

## Prerequisites

- Git (installed)
- Python 3.9+ (installed)
- Node.js 16+ (installed)
- npm (installed with Node.js)
- MongoDB Community Edition (need to install)

---

## Step-by-Step Setup

### Step 1: Install MongoDB

**Option A: Windows Installer (Recommended)**

1. Visit: https://www.mongodb.com/try/download/community
2. Select "Windows" and download the **MSI installer**
3. Run the installer
4. Choose "Complete" installation
5. **Important:** Check "Install MongoDB as a Service" and "Install MongoDB Compass" (optional)
6. Complete the installation

**Option B: Using WSL2 (if you have it)**

```bash
# In WSL2 terminal
sudo apt-get update
sudo apt-get install mongodb-org
sudo systemctl start mongod
```

**Option C: Using Docker (if Docker Desktop is running)**

```powershell
# Ensure Docker Desktop is running first
docker run -d -p 27017:27017 --name company-chatbot-mongo mongo
```

### Step 2: Verify MongoDB is Running

```powershell
# Check if MongoDB is listening on port 27017
netstat -an | findstr 27017

# You should see a line with "LISTENING" status
```

### Step 3: Install Python Backend Dependencies

```powershell
cd d:\python\company-chatbot-rbac\backend
pip install -r requirements.txt
```

### Step 4: Start the Flask Backend

```powershell
cd d:\python\company-chatbot-rbac\backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

**Leave this terminal running** - don't close it!

### Step 5: Create Demo Users (New Terminal)

```powershell
# Open a NEW terminal window
cd d:\python\company-chatbot-rbac

# First, install requests if not already installed
pip install requests

# Run the setup script
python setup_demo_users_api.py
```

You should see:
```
✓ Created admin (admin)
✓ Created clevel_user (c-level)
✓ Created finance_user (finance)
✓ Created hr_user (hr)
✓ Created employee_user (employee)
```

### Step 6: Start the React Frontend (Another New Terminal)

```powershell
# Open ANOTHER new terminal window
cd d:\python\company-chatbot-rbac\frontend
npm start
```

The browser should automatically open to `http://localhost:3000`

### Step 7: Test the Login

You now have **3 terminals running:**
1. Flask backend on localhost:5000
2. React frontend dev server on localhost:3000
3. Your command terminal

**Test Login with Demo Credentials:**

In the login page, try:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| C-Level | `clevel_user` | `pass123` |
| Finance | `finance_user` | `pass123` |
| HR | `hr_user` | `pass123` |
| Employee | `employee_user` | `pass123` |

### Step 8: Verify Features by Role

- **Admin**: Should see Dashboard, User Management, Document Upload, Access Keys
- **C-Level**: Should see Dashboard and Chat
- **Finance/HR/Employee**: Should see only Chat and History

---

## Troubleshooting

### MongoDB Not Connecting

**Error:**
```
MongoServerSelectionError: connect ECONNREFUSED 127.0.0.1:27017
```

**Solution:**
1. Verify MongoDB is running:
   ```powershell
   netstat -an | findstr 27017
   ```
2. If not listed, start MongoDB:
   ```powershell
   Start-Service MongoDB
   ```
3. If service doesn't exist, install MongoDB using the installer above

### Backend Won't Start

**Error:**
```
ModuleNotFoundError: No module named 'pymongo'
```

**Solution:**
```powershell
cd d:\python\company-chatbot-rbac\backend
pip install -r requirements.txt
python app.py
```

### Frontend npm Issues

**Error:**
```
npm: command not found
```

**Solution:**
- Reinstall Node.js from https://nodejs.org/
- Make sure to restart terminal after installation

**Error:**
```
npm ERR! code ERESOLVE
```

**Solution:**
```powershell
cd d:\python\company-chatbot-rbac\frontend
npm install --force
npm start
```

### Login Failed

**Error:**
```
Invalid username or password
```

**Solution:**
1. Make sure Flask backend is running (check terminal for "Running on http://127.0.0.1:5000")
2. Make sure demo users were created (`python setup_demo_users_api.py`)
3. Check browser console (F12) for detailed error messages
4. Try `admin` / `admin123` first

### Port Already in Use

**Port 3000 or 5000 in use:**

```powershell
# Find what's using the port (example for 3000)
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

---

## Using the Convenience Scripts

Instead of running three terminals manually, you can use these one-click scripts:

### Windows Batch Script (start.bat)
```powershell
# From project root
.\start.bat
```

### PowerShell Script (start.ps1)
```powershell
# From project root
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start.ps1
```

---

## Project Structure

```
dragon-intelligence-rbac/
├── backend/
│   ├── app.py                    # Flask routes and API
│   ├── models.py                 # Database models
│   ├── requirements.txt           # Python dependencies
│   └── setup_demo_users.py       # Direct DB user setup (if MongoDB not in Docker)
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx     # Updated login with 5 roles
│   │   │   ├── Chat.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── ...
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # Auth state management
│   │   ├── styles/
│   │   │   └── LoginPage.css     # Updated design
│   │   └── App.jsx               # Main app with routing
│   ├── package.json
│   └── .gitignore
├── setup_demo_users_api.py       # API-based user creation
├── start.bat                      # Windows batch starter
├── start.ps1                      # PowerShell starter
├── MONGODB_SETUP.md              # Detailed MongoDB guide
├── SETUP_GUIDE.md                # Full setup instructions
└── README.md
```

---

## Environment Variables

**Backend (.env in backend/ directory):**
```
SECRET_KEY=your-secret-key-change-in-production
MONGODB_URL=mongodb://localhost:27017/company_chatbot_rbac
FLASK_ENV=development
FLASK_DEBUG=True
```

**Frontend (.env in frontend/ directory):**
```
REACT_APP_API_BASE_URL=http://localhost:5000
```

---

## Available API Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/apikey` - Login with access key

**Protected Routes (require JWT token):**
- `GET /api/users` - List all users
- `POST /api/chat` - Send chat query
- `GET /api/documents` - List documents
- `POST /api/documents/upload` - Upload document
- `GET /api/dashboard` - Get dashboard stats

---

## Next Steps After Getting It Running

1. **Explore the Admin Dashboard:**
   - Login as `admin` / `admin123`
   - Explore User Management
   - Create custom users with different roles
   - Upload documents

2. **Test Role-Based Access Control:**
   - Login with different users
   - Observe which features are available
   - Verify chat queries are restricted by role

3. **Customize the Application:**
   - Modify roles and permissions in `backend/models.py`
   - Update the UI in `frontend/src/pages/`
   - Add more features to the Dashboard

4. **Deploy to Production:**
   - Set up MongoDB Atlas (cloud)
   - Update connection string
   - Deploy backend (Heroku, AWS, etc.)
   - Deploy frontend (Vercel, Netlify, etc.)

---

## Support & Resources

- **MongoDB Setup Issues**: See `MONGODB_SETUP.md`
- **Full Setup Instructions**: See `SETUP_GUIDE.md`
- **GitHub Repository**: https://github.com/Kaviselva017/Role-Based-Access-Control

---

## Quick Commands Reference

```powershell
# Start Everything (from project root)
.\start.ps1

# Start Backend Only
cd backend && python app.py

# Start Frontend Only
cd frontend && npm start

# Create Demo Users
python setup_demo_users_api.py

# Check MongoDB Status
netstat -an | findstr 27017

# Stop All Services
# → Ctrl+C in each terminal
```

---

## Version Information

- **React**: 18.2.0
- **Flask**: 2.3.2
- **MongoDB**: Latest Community Edition
- **Python**: 3.9+
- **Node.js**: 16+

---

## Success Indicators

✅ All systems functioning when you see:
- Flask terminal shows "Running on http://127.0.0.1:5000"
- React terminal shows "Compiled successfully! You can now view the app in your browser."
- Browser opens to http://localhost:3000
- Login page displays with Dragon Intelligence branding
- Can login with demo credentials

---

**You're all set! 🚀**

If you encounter any issues, check the Troubleshooting section or the detailed guides (MONGODB_SETUP.md, SETUP_GUIDE.md).

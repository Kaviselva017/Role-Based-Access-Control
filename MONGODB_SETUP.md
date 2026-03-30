# MongoDB Setup for Dragon Intelligence Platform

This guide will help you set up MongoDB locally for the company chatbot RBAC application.

## Option 1: MongoDB Community (Recommended)

### Windows Installation

1. **Download MongoDB Community Edition**
   - Visit: https://www.mongodb.com/try/download/community
   - Select Windows
   - Choose the latest MSI installer
   - Download and run the installer

2. **Installation Steps**
   - Run the MongoDB installer
   - Choose "Complete" installation
   - Select "Install MongoDB as a Service"
   - Uncheck "Install MongoDB Compass" if you don't need the GUI

3. **Start MongoDB**
   ```powershell
   # MongoDB should start automatically as a Windows service
   # To verify it's running:
   Get-Service MongoDB | Select-Object Status, Name
   
   # If not running, start it:
   Start-Service MongoDB
   ```

4. **Verify MongoDB is Running**
   ```powershell
   # Check if port 27017 is listening
   netstat -an | findstr 27017
   ```

## Option 2: MongoDB Community via WSL2 (If you have WSL2)

```bash
# In your WSL2 terminal
sudo apt-get update
sudo apt-get install mongodb-org

# Start MongoDB
sudo systemctl start mongod

# Verify it's running
sudo systemctl status mongod
```

## Option 3: Docker (If Docker Desktop is running)

```powershell
# Ensure Docker Desktop is running first

# Start MongoDB container
docker run -d -p 27017:27017 --name company-chatbot-mongo mongo

# Verify it's running
docker ps | Select-String mongo
```

## After MongoDB is Running

### 1. Create Demo Users

Navigate to the project root and run:

```powershell
cd d:\python\company-chatbot-rbac

# First, start the Flask backend in a separate terminal
cd backend
python app.py

# In another terminal, create demo users
cd d:\python\company-chatbot-rbac
python setup_demo_users_api.py
```

### 2. Start Frontend

In another terminal:

```powershell
cd d:\python\company-chatbot-rbac\frontend
npm start
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Login with demo credentials (see setup_demo_users_api.py output)

## Troubleshooting

### MongoDB Not Connecting

**Error**: `MongoServerSelectionError: connect ECONNREFUSED 127.0.0.1:27017`

**Solution**:
1. Check if MongoDB is running: `netstat -an | findstr 27017`
2. Restart MongoDB service: `Start-Service MongoDB`
3. Try connecting with mongosh client:
   ```powershell
   mongosh --host localhost --port 27017
   ```

### Port Already in Use

If port 27017 is already in use:

```powershell
# Find what's using the port
netstat -ano | findstr :27017

# Kill the process (replace PID with the actual Process ID)
taskkill /PID <PID> /F
```

### Backend Can't Connect to MongoDB

1. Ensure MongoDB is running before starting Flask
2. Check the MongoDB connection string in `backend/models.py`:
   - Should be: `mongodb://localhost:27017/`
   - Could also use MongoDB Atlas (cloud) with connection string in `.env`

### Docker Issues

If Docker fails to start:

```powershell
# Check Docker Desktop status
docker ps

# If Docker isn't responding, restart Docker Desktop application

# Check logs
docker logs company-chatbot-mongo

# Remove and recreate container if needed
docker stop company-chatbot-mongo
docker rm company-chatbot-mongo
docker run -d -p 27017:27017 --name company-chatbot-mongo mongo
```

## Verify Everything is Running

```powershell
# Check all services
Write-Host "MongoDB: $(if (netstat -an | Select-String '27017') { 'Running' } else { 'Not Found' })"
Write-Host "Flask backend: $(curl -s http://localhost:5000/api/health -ErrorAction SilentlyContinue | Select-String 'ok' | Measure-Object | Select-Object -ExpandProperty Count)"
Write-Host "React frontend: $(curl -s http://localhost:3000 -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count)"
```

## Next Steps

Once MongoDB is running and the backend is started:

1. Run the demo user setup script
2. Start the React frontend
3. Navigate to http://localhost:3000
4. Login with demo credentials:
   - Admin: `admin` / `admin123`
   - C-Level: `clevel_user` / `pass123`
   - Finance: `finance_user` / `pass123`
   - HR: `hr_user` / `pass123`
   - Employee: `employee_user` / `pass123`

## Support

If you encounter issues:

1. Check the backend logs in the Flask terminal
2. Check browser console (F12 in Chrome/Firefox)
3. Verify MongoDB is accepting connections:
   ```powershell
   mongosh --host localhost --port 27017
   ```

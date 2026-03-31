# Login System - Testing Guide

## Status

✅ **All systems ready for testing**

- Backend Flask server: Running on http://localhost:5000
- Frontend React server: Running on http://localhost:3000
- MongoDB: Connected to localhost:27017 (database: company_chatbot_rbac)
- Demo users: All 5 users created with access keys

## Authentication Flow (3 Steps)

### Step 1: Username/Password Login
- **Endpoint**: `POST /api/auth/login`
- **Request**: `{"username": "admin", "password": "admin123"}`
- **Response**: 
  ```json
  {
    "token": "eyJ...",
    "user": {
      "id": "...",
      "username": "admin",
      "email": "admin@test.com",
      "role": "admin",
      "department": "Administration"
    }
  }
  ```
- **Supports**: Both username and email for login

### Step 2: Access Key Authorization
- **Endpoint**: `POST /api/auth/verify-key`
- **Headers**: `Authorization: Bearer <token_from_step1>`
- **Request**: `{"accessKey": "ADM-2030"}`
- **Response**: `{"authorized": true}`
- **Validation**: Key must belong to the authenticated user

### Step 3: Confirmation & Enter System
- **Display**: User details from Step 1
- **Action**: Click "Enter System" button
- **Effect**: Store token and user in localStorage, navigate to `/chat`

## Test Credentials

### Admin User
```
Username: admin
Password: admin123
Email: admin@test.com
Access Key: ADM-2030
Role: admin
```

### C-Level User
```
Username: clevel_user
Password: pass123
Email: clevel@test.com
Access Key: CLV-2030
Role: c-level
```

### Finance User
```
Username: finance_user
Password: pass123
Email: finance@test.com
Access Key: FIN-2030
Role: finance
```

### HR User
```
Username: hr_user
Password: pass123
Email: hr@test.com
Access Key: HR-2030
Role: hr
```

### Employee User
```
Username: employee_user
Password: pass123
Email: emp@test.com
Access Key: EMP-2030
Role: employee
```

## Testing Steps

1. **Open browser**: Navigate to http://localhost:3000

2. **Step 1 - Login**:
   - Enter: `admin` (or `admin@test.com`)
   - Enter: `admin123`
   - Click: Login button
   - Expected: Proceed to Step 2 with no errors

3. **Step 2 - Access Key**:
   - Enter: `ADM-2030`
   - Click: Verify Key button
   - Expected: Proceed to Step 3 with success message

4. **Step 3 - Confirmation**:
   - Review: User details (admin, admin@test.com, Administration, admin role)
   - Click: "Enter System" button
   - Expected: Navigate to `/chat` route (dashboard)

## Troubleshooting

### "Invalid credentials" on Step 1
- Verify you're using correct username/password combinations above
- Check browser console (F12) for error details
- Check backend logs for authentication failures

### "Invalid or expired access key" on Step 2
- Verify access key matches the user's role (e.g., admin uses ADM-2030)
- Confirm the token from Step 1 is valid
- Check that user is still authenticated

### Token-related errors
- Clear browser localStorage and try again
- Verify backend is running (check port 5000)
- Check for JWT configuration issues

## Recent Fixes Applied

1. ✅ Updated `/api/auth/login` to support both username and email login
2. ✅ Created new `/api/auth/verify-key` endpoint for Step 2 authorization
3. ✅ Verified database contains all demo users with correct password hashes
4. ✅ Restarted backend server to load updated endpoints

## Database Information

- **Database Name**: `company_chatbot_rbac`
- **Collections**: users, access_keys, documents, chat_history, queries, roles
- **Users Collection**: Contains 6 users (5 demo + MARAN from previous session)
- **Access Keys Collection**: Contains 5 access keys (one per demo user)

## API Endpoints

- `POST /api/auth/login` - Username/password authentication
- `POST /api/auth/verify-key` - Access key verification (requires Bearer token)
- `POST /api/auth/apikey` - Direct login with access key (alternative flow)
- `POST /api/auth/register` - User registration
- `GET /api/user/profile` - Get user profile (requires auth)
- `GET /api/chat/history` - Chat history (requires auth)

## Frontend Components

- **LoginPage.jsx**: Main 3-step login component
  - State: username, password, accessKey, currentStep, userDetails, authToken
  - Handlers: handleLoginSubmit, handleAccessKeySubmit, handleProceedToChat
  - Routes to: /chat on successful step 3

- **AuthContext.jsx**: Stores authenticated user and token
- **localStorage**: Stores 'token' and 'user' for session persistence

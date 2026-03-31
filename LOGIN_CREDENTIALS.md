# 🔐 DRAGON INTEL - Complete Login Credentials

## System Details
- **Platform URL**: http://localhost:3000
- **Database**: MongoDB (company_chatbot_rbac)
- **Authentication**: 3-Step Login (Username/Password → Access Key → Confirmation)
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:3000
- **Total Users**: 8 accounts active and ready

---

## 📋 Quick Reference - All Users

| Username | Password | Email | Access Key | Role | Department |
|----------|----------|-------|-----------|------|-----------|
| admin | admin123 | admin@test.com | ADM-2030 | Admin | Administration |
| clevel_user | pass123 | clevel@test.com | CLV-2030 | C-Level | Executive |
| finance_user | pass123 | finance@test.com | FIN-2030 | Finance | Finance |
| hr_user | pass123 | hr@test.com | HR-2030 | HR | Human Resources |
| marketing_user | pass123 | marketing@test.com | MKT-2030 | Marketing | Marketing |
| engineering_user | pass123 | engineering@test.com | ENG-2030 | Engineering | Engineering |
| employee_user | pass123 | emp@test.com | EMP-2030 | Employee | General |
| MARAN | maran123 | maran@gmail.com | MAR-2030 | Marketing | Marketing |

---

## 👤 ALL USER ACCOUNTS (8 Total)

### 1️⃣ ADMIN USER
| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |
| **Email** | `admin@test.com` |
| **Access Key** | `ADM-2030` |
| **Role** | Admin |
| **Department** | Administration |
| **Access Level** | FULL_SYSTEM_ACCESS |

**Permissions**: System configuration, user management, security audit logs, all department data, financial reports, HR records, strategic documents, API management

---

### 2️⃣ C-LEVEL EXECUTIVE USER
| Field | Value |
|-------|-------|
| **Username** | `clevel_user` |
| **Password** | `pass123` |
| **Email** | `clevel@test.com` |
| **Access Key** | `CLV-2030` |
| **Role** | C-Level |
| **Department** | Executive |
| **Access Level** | STRATEGIC_ACCESS |

**Permissions**: Strategic documents, financial summaries, executive reports, board materials, high-level metrics, cross-department overview

---

### 3️⃣ FINANCE USER
| Field | Value |
|-------|-------|
| **Username** | `finance_user` |
| **Password** | `pass123` |
| **Email** | `finance@test.com` |
| **Access Key** | `FIN-2030` |
| **Role** | Finance |
| **Department** | Finance |
| **Access Level** | DEPARTMENTAL_ACCESS |

**Permissions**: Financial documents, budgets, expense reports, revenue data, financial analysis, audit trails

---

### 4️⃣ HR USER
| Field | Value |
|-------|-------|
| **Username** | `hr_user` |
| **Password** | `pass123` |
| **Email** | `hr@test.com` |
| **Access Key** | `HR-2030` |
| **Role** | HR |
| **Department** | Human Resources |
| **Access Level** | DEPARTMENTAL_ACCESS |

**Permissions**: Employee records, payroll information, benefits data, training materials, organizational structure, HR policies

---

### 5️⃣ MARKETING USER
| Field | Value |
|-------|-------|
| **Username** | `marketing_user` |
| **Password** | `pass123` |
| **Email** | `marketing@test.com` |
| **Access Key** | `MKT-2030` |
| **Role** | Marketing |
| **Department** | Marketing |
| **Access Level** | DEPARTMENTAL_ACCESS |

**Permissions**: Marketing materials, campaign data, market research, customer insights, brand guidelines, analytics reports

---

### 6️⃣ ENGINEERING USER
| Field | Value |
|-------|-------|
| **Username** | `engineering_user` |
| **Password** | `pass123` |
| **Email** | `engineering@test.com` |
| **Access Key** | `ENG-2030` |
| **Role** | Engineering |
| **Department** | Engineering |
| **Access Level** | DEPARTMENTAL_ACCESS |

**Permissions**: Technical documentation, system architecture, code standards, API documentation, development guidelines, tool configurations

---

### 7️⃣ EMPLOYEE USER
| Field | Value |
|-------|-------|
| **Username** | `employee_user` |
| **Password** | `pass123` |
| **Email** | `emp@test.com` |
| **Access Key** | `EMP-2030` |
| **Role** | Employee |
| **Department** | General |
| **Access Level** | LIMITED_ACCESS |

**Permissions**: Personal records, public company info, general guidelines, training materials, own department overview

---

### 8️⃣ MARAN USER (Now with Password!)
| Field | Value |
|-------|-------|
| **Username** | `MARAN` |
| **Password** | `maran123` |
| **Email** | `maran@gmail.com` |
| **Access Key** | `MAR-2030` |
| **Role** | Marketing |
| **Department** | Marketing |
| **Access Level** | DEPARTMENTAL_ACCESS |

**Permissions**: Marketing materials, campaign data, market research, customer insights, brand guidelines, analytics reports

## 🔄 3-STEP LOGIN FLOW

### Step 1: Username/Password Authentication
```
Enter Username: admin
Enter Password: admin123
```
**Expected Result**: Advance to Step 2, receive JWT Token

### Step 2: Access Key Authorization
```
Enter Access Key: ADM-2030
```
**Expected Result**: Key verified, advance to Step 3

### Step 3: Confirmation & System Access
```
Review authorized user details
Click: "Enter System"
```
**Expected Result**: Enter Dashboard (http://localhost:3000/chat)

---

## 🎯 Quick Login Guide

### For Testing Admin Features
```
1. Username: admin
2. Password: admin123
3. Access Key: ADM-2030
```

### For Testing Executive Dashboard
```
1. Username: clevel_user
2. Password: pass123
3. Access Key: CLV-2030
```

### For Testing Finance Reports
```
1. Username: finance_user
2. Password: pass123
3. Access Key: FIN-2030
```

### For Testing HR Functions
```
1. Username: hr_user
2. Password: pass123
3. Access Key: HR-2030
```

### For Testing Marketing Capabilities
```
1. Username: marketing_user
2. Password: pass123
3. Access Key: MKT-2030
```

### For Testing Engineering/Technical Access
```
1. Username: engineering_user
2. Password: pass123
3. Access Key: ENG-2030
```

### For Testing Employee Access
```
1. Username: employee_user
2. Password: pass123
3. Access Key: EMP-2030
```

### For Testing MARAN User (Marketing Role)
```
1. Username: MARAN
2. Password: maran123
3. Access Key: MAR-2030
```

---

## 📊 Role-Based Access Control

### ✅ Authorized Query Examples

**Marketing User**: "What are our latest campaign metrics?"
→ ✓ AUTHORIZED: Campaign data available

**Engineering User**: "Show me the API documentation"
→ ✓ AUTHORIZED: Technical docs accessible

**Finance User**: "What is the Q1 budget?"
→ ✓ AUTHORIZED: Budget data available

### ❌ Access Denied Examples

**C-Level User trying**: "Show me employee payroll"
→ ❌ DENIED: "Employee records not available for Executive role"

**Finance User trying**: "Configure system settings"
→ ❌ DENIED: "System configuration restricted to Admin role"

**Employee trying**: "Show financial forecasts"
→ ❌ DENIED: "Financial data not available for Employee role"

**Engineering User trying**: "Show me HR employee data"
→ ❌ DENIED: "HR records restricted to HR role only"

**Marketing User trying**: "Show me technical API secrets"
→ ❌ DENIED: "Technical deep dives restricted to Engineering role"

---

## 🔑 Access Keys Reference

| Role | Access Key | Used In Step |
|------|-----------|--------------|
| Admin | ADM-2030 | Step 2 |
| C-Level | CLV-2030 | Step 2 |
| Finance | FIN-2030 | Step 2 |
| HR | HR-2030 | Step 2 |
| Marketing | MKT-2030 | Step 2 |
| Engineering | ENG-2030 | Step 2 |
| Employee | EMP-2030 | Step 2 |
| MARAN (Marketing) | MAR-2030 | Step 2 |

**All Keys Expire**: 365 days from creation

---

## 🛡️ Security Notes

- ✅ Passwords are SHA256 hashed in database
- ✅ JWT tokens expire after 24 hours
- ✅ Access keys are hashed and validated on each request
- ✅ Role-based access control enforced at backend
- ✅ Session stored in browser localStorage
- ✅ Bearer token required for all API requests

---

## 🚀 Testing Checklist

- [ ] Login with admin credentials
- [ ] Try accessing restricted data (should be denied)
- [ ] Login with different role (clevel_user)
- [ ] Verify role-specific information shown
- [ ] Test chat queries within role scope
- [ ] Try chat query outside role scope (should deny)
- [ ] Logout and verify token cleared
- [ ] Test session persistence (refresh page)

---

## 📍 Important URLs

| Feature | URL |
|---------|-----|
| Login Page | http://localhost:3000/login |
| Chat Interface | http://localhost:3000/chat |
| Dashboard | http://localhost:3000/dashboard |
| Chat History | http://localhost:3000/history |
| User Management | http://localhost:3000/users |
| Document Upload | http://localhost:3000/upload |
| Access Keys | http://localhost:3000/access-keys |

---

## 🔧 Backend API Endpoints

### Authentication
- `POST /api/auth/login` - Username/Password auth (Step 1)
- `POST /api/auth/verify-key` - Access Key validation (Step 2)
- `POST /api/auth/apikey` - Direct API key login (alternative)

### Chat & Query
- `POST /api/chat` - Send message (requires auth)
- `GET /api/chat/history` - Retrieve chat history (requires auth)

### User Info
- `GET /api/user/profile` - Get current user profile (requires auth)

### Administration (Admin Only)
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

---

## ❓ Troubleshooting

**Q: "Invalid credentials" error on login**
- A: Verify you're using the correct username and password from table above
- A: Remember passwords are case-sensitive
- A: Try using email instead of username

**Q: Access key verification fails**
- A: Ensure you're entering the correct access key for your role
- A: Check that token from Step 1 was successfully received
- A: Try refreshing and logging in again

**Q: Cannot access chat after login**
- A: Make sure you completed both Step 1 and Step 2
- A: Clear browser cache and try again
- A: Check that both backend and frontend are running

**Q: "Access Denied" on role-based queries**
- A: This is expected behavior - you don't have permission for that data
- A: Login with appropriate role (admin for system config, finance for budgets, etc.)

---

**Last Updated**: March 31, 2026  
**System Version**: Dragon Intel v2.0  
**Status**: ✅ All Users Active and Authorized

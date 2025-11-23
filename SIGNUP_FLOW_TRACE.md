# User Signup Flow - Complete Trace

This document traces the complete flow of user registration from the frontend to the database.

## 📋 Flow Overview

```
Frontend Form → Validation → API Call → Backend Endpoint → Database Transaction → Response
```

---

## 1️⃣ **Frontend: User Input** 
**File:** `Frontend/src/routes/sign-in-up/+page.svelte`

### Step 1.1: User fills out the form
- User enters: `name`, `email`, `password`, `confirmPassword`
- Form data stored in: `formData` state variable (lines 21-25, 34-39)

### Step 1.2: Form submission
**Line 60:** `handleSubmit(event)` function is called when form is submitted

**Line 69-70:** Validation check
```typescript
if (formState.isSignUp) {
    validationErrors = validateSignUpCredentials(formData as SignUpCredentials);
}
```

**Line 82-84:** Call auth service
```typescript
const response = formState.isSignUp 
    ? await authService.signUp(formData as SignUpCredentials)
    : await authService.signIn(formData as LoginCredentials);
```

---

## 2️⃣ **Frontend: Auth Service**
**File:** `Frontend/src/lib/services/authService.ts`

### Step 2.1: signUp() method called
**Line 276:** `async signUp(credentials: SignUpCredentials)`

### Step 2.2: API Request to Backend
**Lines 278-282:** HTTP POST request to backend
```typescript
const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        name: credentials.name, 
        email: credentials.email, 
        password: credentials.password 
    })
});
```

**API Endpoint:** `http://localhost:9000/auth/signup` (from `Frontend/src/lib/config/api.ts`)

**Request Payload:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "userpassword123"
}
```

---

## 3️⃣ **Backend: API Endpoint**
**File:** `Backend/app/routers/auth.py`

### Step 3.1: Signup endpoint receives request
**Line 13:** `@router.post("/signup")`
**Line 14:** `def signup(payload: dict, db: Session = Depends(get_db))`

### Step 3.2: Check for existing user
**Lines 16-18:** Email uniqueness check
```python
existing = db.query(models.User.id).filter(models.User.email == payload["email"]).first()
if existing:
    raise HTTPException(status_code=400, detail="Email already registered")
```

### Step 3.3: Create User object
**Lines 19-25:** Create new User model instance
```python
user = models.User(
    id=str(uuid4()),                    # Generate UUID
    name=payload["name"],                # From request
    email=payload["email"],              # From request
    password_hash=hash_password(payload["password"]),  # Hash password
    role='user'                          # Default role
)
```

**Password Hashing:** 
- Function: `hash_password()` from `Backend/app/security.py`
- Uses: `passlib` with `bcrypt` algorithm

### Step 3.4: Save to Database
**Line 26:** `db.add(user)` - Add user to session
**Line 27:** `db.commit()` - **COMMIT TRANSACTION TO DATABASE**

**⚠️ IMPORTANT:** This is where the user is saved to the database!

### Step 3.5: Query user back (verify save)
**Lines 30-34:** Query the saved user
```python
user_data = db.query(
    models.User.id,
    models.User.name,
    models.User.email
).filter(models.User.id == user.id).first()
```

### Step 3.6: Generate JWT token
**Line 35:** `token = create_access_token(user.id)`

### Step 3.7: Return response
**Line 36:** Return user data and token
```python
return {
    "user": {
        "id": user_data.id, 
        "name": user_data.name, 
        "email": user_data.email
    }, 
    "token": token
}
```

---

## 4️⃣ **Backend: Database Layer**
**File:** `Backend/app/database.py`

### Step 4.1: Database Connection
**Line 34:** Engine created from `DATABASE_URL`
```python
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
```

**Database URL Source:** `Backend/app/config.py`
- Default: `mysql+pymysql://root:@127.0.0.1:3306/bayanihan_exchange`
- Can be overridden via `.env` file with `DATABASE_URL` variable

### Step 4.2: Session Management
**Line 35:** `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
**Line 42-47:** `get_db()` function provides database session

### Step 4.3: User Model
**File:** `Backend/app/models.py`

**Lines 7-18:** User table structure
```python
class User(Base):
    __tablename__ = "users"  # Table name in database
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum('user', 'admin', 'moderator'), default='user')
    location = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime)
```

### Step 4.4: Database Transaction
When `db.commit()` is called (line 27 in auth.py):
1. SQLAlchemy generates SQL INSERT statement
2. Executes: `INSERT INTO users (id, name, email, password_hash, role, created_at) VALUES (...)`
3. Transaction is committed to MySQL database
4. Data is permanently saved in the `users` table

---

## 5️⃣ **Backend: Response to Frontend**
**File:** `Backend/app/routers/auth.py` → `Frontend/src/lib/services/authService.ts`

### Step 5.1: Backend returns JSON
```json
{
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "email": "john@example.com"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Step 5.2: Frontend receives response
**Lines 299-316:** Process successful signup
```typescript
const data = await res.json();
const { user: apiUser, token } = data;

const user = {
    id: apiUser.id,
    email: apiUser.email,
    name: apiUser.name,
    isVerified: true,
    role: 'user' as const,
    createdAt: new Date()
};

localStorage.setItem('bayanihan_token', token);  // Save token
```

### Step 5.3: Update auth store
**File:** `Frontend/src/routes/sign-in-up/+page.svelte`
**Line 88:** `authStore.setUser(response.user)`

### Step 5.4: Redirect user
**Line 91:** `await goto('/discovery')` - Navigate to discovery page

---

## 🔍 **Database Storage Details**

### Where is the user saved?
- **Database Type:** MySQL (via Aiven or local)
- **Database Name:** From `DATABASE_URL` (default: `bayanihan_exchange`)
- **Table Name:** `users`
- **Database Location:** 
  - Aiven: Remote MySQL instance
  - Local: `127.0.0.1:3306` (if using local MySQL)

### What data is saved?
```sql
INSERT INTO users (
    id,                    -- UUID string (36 chars)
    name,                  -- User's full name
    email,                 -- User's email (unique)
    password_hash,         -- Bcrypt hashed password
    role,                  -- 'user' (default)
    is_verified,           -- false (default)
    created_at,            -- Current timestamp
    location,              -- NULL (optional)
    last_login_at          -- NULL (set on first login)
) VALUES (...)
```

---

## 🐛 **Debugging: Verify User in Database**

### Method 1: Use Debug Endpoint
**Endpoint:** `GET http://localhost:9000/debug/db-info`

This will show:
- Current database name
- User count
- List of all users (first 10)

### Method 2: Check Database Directly
1. Connect to your Aiven MySQL database
2. Run: `USE bayanihan_exchange;` (or your database name)
3. Run: `SELECT * FROM users;`
4. Verify the user exists with the registered email

### Method 3: Check Backend Logs
- Look for any database connection errors
- Check for transaction commit errors
- Verify `DATABASE_URL` is correct

---

## 📝 **Key Files in the Flow**

1. **Frontend Form:** `Frontend/src/routes/sign-in-up/+page.svelte`
2. **Frontend Service:** `Frontend/src/lib/services/authService.ts`
3. **API Config:** `Frontend/src/lib/config/api.ts`
4. **Backend Endpoint:** `Backend/app/routers/auth.py`
5. **User Model:** `Backend/app/models.py`
6. **Database Config:** `Backend/app/database.py`
7. **Settings:** `Backend/app/config.py`
8. **Security:** `Backend/app/security.py` (password hashing)

---

## ⚠️ **Common Issues**

### Issue 1: User not visible in Aiven
- **Check:** Database name in connection string matches Aiven database
- **Check:** `.env` file has correct `DATABASE_URL`
- **Check:** You're looking at the correct database in Aiven console

### Issue 2: Transaction not committed
- **Check:** No exceptions thrown before `db.commit()`
- **Check:** Database connection is active
- **Check:** Backend logs for errors

### Issue 3: Wrong database
- **Verify:** Use `/debug/db-info` endpoint to see actual database name
- **Verify:** Connection string points to correct Aiven instance

---

## ✅ **Verification Checklist**

- [ ] Frontend form submits successfully
- [ ] API request reaches backend (check network tab)
- [ ] Backend receives payload correctly
- [ ] Email uniqueness check passes
- [ ] User object created successfully
- [ ] `db.commit()` executes without errors
- [ ] Response returned to frontend
- [ ] Token saved in localStorage
- [ ] User visible in database via `/debug/db-info`
- [ ] User visible in Aiven database console



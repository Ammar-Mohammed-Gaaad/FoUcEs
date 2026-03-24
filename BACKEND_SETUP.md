# Backend Setup Documentation

## 🏗️ Backend Structure

The backend is organized in the `src/` folder with the following architecture:

```
src/
├── main.py              # FastAPI application entry point
├── config.py            # Environment configuration & settings
├── database.py          # SQLAlchemy database setup
├── models.py            # ORM models (User, LearningProfile, Goal, Task, FocusSession)
├── schemas.py           # Pydantic request/response schemas
├── utils.py             # Utilities (JWT, password hashing, validation)
├── auth.py              # Authentication endpoints (/api/auth/*)
├── learning.py          # Learning profile endpoints (/api/learning/*)
├── tasks.py             # Task management endpoints (/api/tasks/*)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
└── fakarni.db           # SQLite database (auto-created)
```

---

## 🔌 Core Backend Components

### 1. **Database Setup** (`database.py`)
- **Engine**: SQLAlchemy with SQLite (default) / PostgreSQL (configurable)
- **Session Management**: Dependency injection for FastAPI routes
- **Database URL**: Configured via `.env` file

### 2. **Data Models** (`models.py`)
```python
- User           # Email, password (hashed), full_name
- LearningProfile # User profile with learning style & interview status
- Goal          # User goals with progress tracking
- Task          # Daily tasks with CRUD operations
- FocusSession  # Focus session tracking for productivity
```

### 3. **API Routes** (Split into routers)

#### Authentication (`auth.py` → `/api/auth/`)
```
POST   /api/auth/signup      # Create account (no auth required)
POST   /api/auth/login       # Login (returns JWT token)
```

#### Learning Profile (`learning.py` → `/api/learning/`)
```
GET    /api/learning/profile-status      # Check if interview completed
GET    /api/learning/my-profile          # Get user's learning profile
PUT    /api/learning/my-profile          # Update profile & mark interview done
GET    /api/learning/learning-styles     # Get learning style percentages
```

#### Tasks (`tasks.py` → `/api/tasks/`)
```
GET    /api/tasks/                       # List all user tasks
POST   /api/tasks/                       # Create new task
GET    /api/tasks/{task_id}              # Get specific task
PUT    /api/tasks/{task_id}              # Update task
DELETE /api/tasks/{task_id}              # Delete task
```

---

## 🔐 Authentication Flow

1. **User Signup** (Frontend → Backend)
   ```
   POST /api/auth/signup
   {
     "email": "user@example.com",
     "full_name": "محمد علي",
     "password": "securepass123"
   }
   ```
   Response:
   ```json
   {
     "access_token": "eyJ...",
     "token_type": "bearer",
     "user_id": 1,
     "name": "محمد علي",
     "email": "user@example.com"
   }
   ```

2. **User Login** (Frontend → Backend)
   ```
   POST /api/auth/login?email=user@example.com&password=securepass123
   ```
   Response: Same as signup

3. **Store Token** (Frontend)
   ```javascript
   localStorage.setItem('access_token', data.access_token);
   localStorage.setItem('token', data.access_token);
   ```

4. **Protected Route Access** (Frontend)
   ```javascript
   fetch('/api/learning/my-profile', {
     headers: {
       'Authorization': `Bearer ${localStorage.getItem('access_token')}`
     }
   })
   ```

---

## 🚀 Running the Backend

### Start Development Server
```bash
cd src/
uvicorn main.py --reload --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Verify Server
```bash
curl http://127.0.0.1:8000/health
# Response: {"status":"healthy"}
```

---

## 📝 Environment Variables (`.env`)

```
DATABASE_URL=sqlite:///./fakarni.db
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_HOST=127.0.0.1
API_PORT=8000
```

---

## 🔗 Frontend-Backend Integration

### API Base URL (in frontend)
All frontend files use the base URL: `http://127.0.0.1:8000`

### Frontend Pages & Related APIs

| Page | Purpose | Backend APIs Used |
|------|---------|------------------|
| `login.html` | Authentication | POST `/api/auth/login`, POST `/api/auth/signup` |
| `home.html` | Dashboard | GET `/api/learning/my-profile` (protected) |
| `learning-interview.html` | Learning profile setup | PUT `/api/learning/my-profile` (protected) |
| `tasks.html` | Task management | CRUD `/api/tasks/*` (protected) |
| `profile.html` | User profile view | GET `/api/learning/my-profile` (protected) |
| `index.html` | Landing page | No APIs (static content) |

---

## ✅ Database Initialization

The database is automatically created on first run with these tables:

1. **users** - User accounts with hashed passwords
2. **learning_profiles** - Learning style & interview status
3. **goals** - User goals tracking
4. **tasks** - Daily tasks
5. **focus_sessions** - Productivity tracking

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: pydantic_settings` | Run `pip install -r requirements.txt` |
| `404 on /api/health` | Use `/health` or check route registration in main.py |
| `CORS errors` | CORS is enabled for all origins (`allow_origins=["*"]`) |
| `Database not found` | Auto-created on first run; check write permissions to `src/` |
| `401 Unauthorized on protected routes` | Token missing or invalid; verify Bearer token format |

---

## 📦 Dependencies

See `requirements.txt` for full list. Key packages:
- **FastAPI** 0.104.1 - Web framework
- **SQLAlchemy** 2.0.23 - ORM
- **Pydantic** 2.5.0 - Data validation
- **python-jose** - JWT tokens
- **bcrypt** - Password hashing
- **uvicorn** 0.24.0 - ASGI server

---

## 🎯 Next Steps

1. ✅ Backend running on `http://127.0.0.1:8000`
2. ✅ Frontend pages created and linked
3. ⚙️ Test signup → login → redirect flow
4. ⚙️ Test protected routes with Bearer token
5. ⚙️ Deploy to production (update CORS, database, JWT secret)


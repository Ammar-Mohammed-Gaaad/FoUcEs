# 🚀 Fakarni - Complete Backend & Frontend Setup

## 📦 Project Structure

```
FoUcEs/
├── src/                          # Backend (Python/FastAPI)
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment configuration
│   ├── database.py              # SQLAlchemy database setup
│   ├── models.py                # ORM models (User, Task, etc)
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── utils.py                 # Auth utilities (JWT, password hashing)
│   ├── auth.py                  # Auth endpoints (/api/auth/*)
│   ├── learning.py              # Learning profile endpoints
│   ├── tasks.py                 # Task management endpoints
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables
│   ├── fakarni.db               # SQLite database (auto-created)
│   └── [legacy files]           # app_dashboard.py, monitor.py, etc
│
├── front/                        # Frontend (HTML/CSS/JavaScript)
│   ├── html/
│   │   ├── index.html           # Landing page
│   │   ├── login.html           # Auth page (signup + login)
│   │   ├── home.html            # Dashboard
│   │   ├── learning-interview.html  # Learning quiz
│   │   ├── tasks.html           # Task management
│   │   ├── profile.html         # User profile
│   │   └── 404.html             # Error page
│   ├── css/
│   │   └── style.css            # Main stylesheet
│   ├── js/
│   │   ├── api-client.js        # API communication layer
│   │   ├── app.js               # Global app logic
│   │   ├── auth_interview_integration.js
│   │   ├── learning_interview.js
│   │   └── learning_snippets.js
│   └── img/                      # Images and icons
│
├── docs/
│   ├── BACKEND_SETUP.md         # Backend architecture docs
│   ├── API_REFERENCE.md         # Complete API endpoint reference
│   └── FRONTEND_INTEGRATION.md  # Frontend-backend integration guide
│
└── README.md (this file)
```

---

## ⚙️ Backend Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Running

1. **Install dependencies:**
   ```bash
   cd src/
   pip install -r requirements.txt
   ```

2. **Create .env file** (if not exists):
   ```bash
   # src/.env
   DATABASE_URL=sqlite:///./fakarni.db
   JWT_SECRET_KEY=your-secret-key-change-in-production
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   API_HOST=127.0.0.1
   API_PORT=8000
   ```

3. **Start development server:**
   ```bash
   uvicorn main.py --reload --host 127.0.0.1 --port 8000
   ```

   **Expected output:**
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Application startup complete
   ```

4. **Verify server is running:**
   ```bash
   # Open browser or terminal
   curl http://127.0.0.1:8000/health
   # Response: {"status":"healthy"}
   ```

### Database

- **Type:** SQLite (default) / PostgreSQL (configurable)
- **Location:** `src/fakarni.db`
- **Auto-initialization:** Tables created on first run

### Backend Stack
- **Framework:** FastAPI 0.104.1
- **ORM:** SQLAlchemy 2.0.23
- **Validation:** Pydantic 2.5.0
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Server:** Uvicorn 0.24.0

---

## 🎨 Frontend Setup

### File Structure
- **HTML Pages:** `front/html/*.html`
- **Stylesheets:** `front/css/style.css`
- **JavaScript:** `front/js/*.js`
- **Images:** `front/img/`

### Running Frontend
1. Backend server must be running on `http://127.0.0.1:8000`
2. Open `http://127.0.0.1:8000/index.html` in browser
3. Or access `http://127.0.0.1:8000/login.html` directly

### Frontend Pages

| Page | Purpose | Public/Auth | Backend APIs |
|------|---------|-----------|--------------|
| `index.html` | Landing page | Public | None |
| `login.html` | Signup/Login | Public | POST /api/auth/* |
| `home.html` | Dashboard | Authenticated | GET /api/learning/*, GET /api/tasks/* |
| `learning-interview.html` | Learning quiz | Authenticated | PUT /api/learning/* |
| `tasks.html` | Task management | Authenticated | CRUD /api/tasks/* |
| `profile.html` | User settings | Authenticated | GET/PUT /api/learning/* |
| `404.html` | Error page | Public | None |

### Frontend Stack
- **Language:** HTML5, CSS3, JavaScript (ES6+)
- **Fonts:** Cairo (Arabic), Poppins (English)
- **RTL Support:** Yes (Arabic interface)
- **HTTP Client:** Fetch API

---

## 🔗 Frontend-Backend Integration

### Authentication Flow

```
User Browser                Backend Server
    |                            |
    | 1. Fill signup form         |
    |---> POST /api/auth/signup ---|
    |                            |
    |<-- Return JWT token --------|
    |                            |
    | 2. Store token in          |
    |    localStorage            |
    |                            |
    | 3. Visit protected page     |
    | 4. Include Bearer token    |
    |---> GET /api/learning/* ---|
    |    Authorization: Bearer ...|
    |                            |
    |<-- Return user data --------|
```

### Using API Client (Recommended)

Frontend includes `front/js/api-client.js` - a JavaScript library for communicating with backend.

**Include in HTML:**
```html
<script src="/js/api-client.js"></script>
```

**Usage Examples:**

```javascript
// 1. Authentication
const user = await authService.signup('user@example.com', 'محمد', 'password123');
authService.storeAuth(user);
// or
const user = await authService.login('user@example.com', 'password123');

// 2. Get user profile
const profile = await learningService.getProfile();
console.log(profile.learning_style); // 'visual'

// 3. Update learning style
await learningService.updateProfile('auditory', true);

// 4. Task management
const tasks = await taskService.getAllTasks();
const newTask = await taskService.createTask('New task', 'Description', 'high');
await taskService.updateTaskStatus(newTask.id, 'completed');
await taskService.deleteTask(newTask.id);

// 5. Helper functions
UIHelper.showError('خطأ', 'حدث خطأ ما');
UIHelper.showSuccess('نجاح', 'تم الحفظ');
const userName = UIHelper.getUserName(); // 'محمد'
```

### Manual Fetch Calls (Alternative)

```javascript
// Get token from localStorage
const token = localStorage.getItem('access_token');

// Include in Authorization header
const response = await fetch('http://127.0.0.1:8000/api/learning/my-profile', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```

---

## 📡 API Endpoints

All endpoints: `http://127.0.0.1:8000`

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login user (query params: email, password)

### Learning Profile
- `GET /api/learning/profile-status` - Check interview status (requires auth)
- `GET /api/learning/my-profile` - Get user profile (requires auth)
- `PUT /api/learning/my-profile` - Update profile (requires auth)
- `GET /api/learning/learning-styles` - Get style percentages

### Tasks
- `GET /api/tasks/` - List all tasks (requires auth)
- `POST /api/tasks/` - Create task (requires auth)
- `GET /api/tasks/{id}` - Get task (requires auth)
- `PUT /api/tasks/{id}` - Update task (requires auth)
- `DELETE /api/tasks/{id}` - Delete task (requires auth)

### Health Check
- `GET /health` - Server health status
- `GET /api/health` - API health status

---

## 🔐 Authentication Details

### Registration
```json
POST /api/auth/signup
{
    "email": "user@example.com",
    "full_name": "محمد علي",
    "password": "SecurePass123!"
}
```

### Login
```
POST /api/auth/login?email=user@example.com&password=SecurePass123!
```

### Token Storage
```javascript
localStorage.setItem('access_token', token);
localStorage.setItem('token', token);  // Fallback compatibility
```

### Protected Routes
All routes except `/api/auth/signup` and `/api/auth/login` require Bearer token:
```
Authorization: Bearer <access_token>
```

---

## 🧪 Testing

### Browser Console Testing

```javascript
// Test signup
fetch('http://127.0.0.1:8000/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        email: 'test@example.com',
        full_name: 'Test',
        password: 'Test123!'
    })
}).then(r => r.json()).then(console.log);

// Test protected endpoint
const token = localStorage.getItem('access_token');
fetch('http://127.0.0.1:8000/api/learning/my-profile', {
    headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);
```

### End-to-End Flow
1. ✅ Open `http://127.0.0.1:8000/index.html`
2. ✅ Click "إنشاء حساب" → Fill signup form
3. ✅ Should redirect to `/learning-interview.html`
4. ✅ Complete learning quiz → Redirect to `/home.html`
5. ✅ View dashboard with user data
6. ✅ Create/edit tasks
7. ✅ Click logout → Back to login page

---

## 🐛 Troubleshooting

### Issue: 404 on /api/auth/login
**Solution:** Check backend is running. Endpoints must include `/api/` prefix.

### Issue: CORS errors
**Solution:** Already handled - CORS enabled for all origins in development. For production, update in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["yourdomain.com"],  # Restrict to your domain
    # ...
)
```

### Issue: 401 Unauthorized
**Solution:** Token is missing or expired. 
- Verify token stored in localStorage
- Check Authorization header format: `Bearer <token>`
- Verify token is passed correctly in API calls

### Issue: Database not found
**Solution:** Delete `src/fakarni.db` and restart server. Database auto-created.

### Issue: Module not found errors
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📋 Checklist

- [x] Backend created and running on port 8000
- [x] Database initialized with all tables
- [x] Authentication endpoints working (signup/login)
- [x] Learning profile endpoints functional
- [x] Task CRUD endpoints implemented
- [x] Frontend pages created and styled
- [x] Frontend-backend API integration code ready
- [x] Token-based authentication implemented
- [x] CORS enabled for development
- [ ] Error handling improved across frontend
- [ ] Loading states added to all API calls
- [ ] Testing suite created
- [ ] Production deployment docs created

---

## 📚 Documentation

- **[BACKEND_SETUP.md](./BACKEND_SETUP.md)** - Backend architecture and setup
- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API endpoint reference
- **[FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)** - Frontend integration guide

---

## 🎯 Quick Start

```bash
# 1. Terminal 1: Start backend
cd src
uvicorn main.py --reload

# 2. Terminal 2: Open frontend (any browser)
http://127.0.0.1:8000/
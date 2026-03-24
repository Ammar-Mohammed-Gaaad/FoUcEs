# 📋 API Reference & Frontend Integration Map

## 🔗 Complete API Endpoint List

### Base URL: `http://127.0.0.1:8000`

---

## 🔐 Authentication Endpoints (`/api/auth/`)

### 1. Signup (User Registration)
**Endpoint:** `POST /api/auth/signup`

**Frontend Call Location:** `login.html` (Lines 249-275)
```javascript
fetch('http://127.0.0.1:8000/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        email, 
        full_name: name, 
        password 
    })
})
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "full_name": "محمد علي",
    "password": "MyPassword123!"
}
```

**Response (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "name": "محمد علي",
    "email": "user@example.com"
}
```

**Frontend Actions After Success:**
```javascript
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('token', data.access_token);
localStorage.setItem('user_id', data.user_id);
localStorage.setItem('user_name', data.name);
localStorage.setItem('user_email', data.email);
// Redirect to learning-interview.html after 2 seconds
window.location.href = '/learning-interview.html';
```

---

### 2. Login
**Endpoint:** `POST /api/auth/login`

**Frontend Call Location:** `login.html` (Lines 229-245)
```javascript
fetch('http://127.0.0.1:8000/api/auth/login?email=' + encodeURIComponent(email) + '&password=' + encodeURIComponent(password), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
})
```

**Request Parameters:** (Query string)
- `email` - User email
- `password` - User password

**Response (200 OK):**
Same as signup response

**Frontend Actions After Success:**
```javascript
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('token', data.access_token);
// ... store other user info ...
// Redirect to home.html after 2 seconds
window.location.href = '/home.html';
```

---

## 📚 Learning Profile Endpoints (`/api/learning/`)

### 1. Get Profile Status
**Endpoint:** `GET /api/learning/profile-status`

**Frontend Call Location:** `home.html` (on page load)
```javascript
fetch('/api/learning/profile-status', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
```

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "redirect_to_interview": true,  // If interview not completed
    "completed": false               // Interview completion status
}
```

**Frontend Logic:**
- If `redirect_to_interview` is true → Redirect to `/learning-interview.html`
- If false → Show dashboard

---

### 2. Get User Profile
**Endpoint:** `GET /api/learning/my-profile`

**Frontend Call Locations:**
- `home.html` - Display user profile
- `profile.html` - Edit profile page
- `learning-interview.html` - Learning style selection

**Request:**
```javascript
fetch('/api/learning/my-profile', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
```

**Response (200 OK):**
```json
{
    "id": 1,
    "user_id": 1,
    "learning_style": "visual",        // Options: visual, auditory, kinesthetic, reading_writing
    "learning_percentage": {
        "visual": 45,
        "auditory": 30,
        "kinesthetic": 15,
        "reading_writing": 10
    },
    "completed_interview": false,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
}
```

---

### 3. Update Profile
**Endpoint:** `PUT /api/learning/my-profile`

**Frontend Call Location:** `learning-interview.html` (on form submit)
```javascript
fetch('/api/learning/my-profile', {
    method: 'PUT',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
        learning_style: selectedStyle,
        completed_interview: true
    })
})
```

**Request Body:**
```json
{
    "learning_style": "visual",
    "completed_interview": true
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "user_id": 1,
    "learning_style": "visual",
    "learning_percentage": {...},
    "completed_interview": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T15:45:22"
}
```

---

### 4. Get Learning Styles
**Endpoint:** `GET /api/learning/learning-styles`

**Response (200 OK):**
```json
{
    "visual": 45,
    "auditory": 30,
    "kinesthetic": 15,
    "reading_writing": 10
}
```

---

## ✅ Task Management Endpoints (`/api/tasks/`)

### 1. Get All Tasks
**Endpoint:** `GET /api/tasks/`

**Frontend Call Location:** `tasks.html`
```javascript
fetch('/api/tasks/', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "title": "اكمل المشروع",
        "description": "انهي الجزء الأول من المشروع",
        "status": "pending",  // pending, in_progress, completed
        "priority": "high",   // low, medium, high
        "created_at": "2024-01-15T10:00:00",
        "due_date": "2024-01-20T23:59:59"
    }
]
```

---

### 2. Create Task
**Endpoint:** `POST /api/tasks/`

**Frontend Call Location:** `tasks.html` (Add task form)
```javascript
fetch('/api/tasks/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
        title, 
        description, 
        priority,
        due_date
    })
})
```

**Request Body:**
```json
{
    "title": "اكمل المشروع",
    "description": "انهي الجزء الأول",
    "priority": "high",
    "due_date": "2024-01-20T23:59:59"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "user_id": 1,
    "title": "اكمل المشروع",
    "description": "انهي الجزء الأول",
    "status": "pending",
    "priority": "high",
    "created_at": "2024-01-15T10:00:00",
    "due_date": "2024-01-20T23:59:59"
}
```

---

### 3. Get Task by ID
**Endpoint:** `GET /api/tasks/{task_id}`

**Request:**
```javascript
fetch(`/api/tasks/${taskId}`, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
```

**Response (200 OK):** Single task object (same structure as above)

---

### 4. Update Task
**Endpoint:** `PUT /api/tasks/{task_id}`

**Frontend Call Location:** `tasks.html` (Edit task)
```javascript
fetch(`/api/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
        status: 'completed',
        // ... other fields to update
    })
})
```

**Response (200 OK):** Updated task object

---

### 5. Delete Task
**Endpoint:** `DELETE /api/tasks/{task_id}`

**Frontend Call Location:** `tasks.html` (Delete button)
```javascript
fetch(`/api/tasks/${taskId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
```

**Response (200 OK):**
```json
{ "message": "Task deleted successfully" }
```

---

## 🔒 Authentication Pattern

All protected endpoints require the `Authorization` header with Bearer token:

```javascript
// Get token from localStorage
const token = localStorage.getItem('access_token');

// Use in all protected API calls
fetch('/api/learning/my-profile', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
})
```

---

## ✔️ Error Responses

### Invalid Credentials (401)
```json
{
    "detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة"
}
```

### Missing Token (401)
```json
{
    "detail": "Not authenticated"
}
```

### Invalid Token (401)
```json
{
    "detail": "Invalid token"
}
```

### Validation Error (422)
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "invalid email format",
            "type": "value_error.email"
        }
    ]
}
```

### Not Found (404)
```json
{
    "detail": "Task not found"
}
```

---

## 📊 Frontend-Backend Connection Checklist

- [x] **Login Page** - Connects to `/api/auth/login` & `/api/auth/signup`
- [x] **Token Storage** - Stores in `localStorage` with keys: `access_token`, `token`
- [x] **Protected Routes** - Include Bearer token in Authorization header  
- [x] **Home Page** - Redirects based on `profile-status` response
- [x] **Learning Interview** - Updates profile with learning style
- [x] **Tasks Page** - CRUD operations on `/api/tasks/`
- [x] **Profile Page** - Reads user profile from `/api/learning/my-profile`
- [ ] **Error Handling** - Display backend error messages to user
- [ ] **Loading States** - Show loading indicators during API calls
- [ ] **Offline Handling** - Graceful fallback when backend unavailable


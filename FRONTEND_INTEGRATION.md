# 🔗 Frontend-Backend Integration Guide

## 📍 Frontend Files & Their Backend Connections

### 🏠 1. **index.html** (Landing Page)
**Path:** `front/html/index.html`
**Purpose:** Static landing page with product features
**Backend APIs Used:** None (no authentication needed)
**Status:** ✅ Ready

**Features:**
- Hero section with call-to-action buttons
- Feature grid (6 features)
- Links to login.html and signup.html

---

### 🔐 2. **login.html** (Authentication Page)
**Path:** `front/html/login.html`
**Purpose:** User signup and login interface
**Backend APIs Used:**
- `POST /api/auth/signup`
- `POST /api/auth/login`
**Status:** ✅ Complete Integration (Lines 229-290)

**Connection Details:**

**Signup Flow:**
1. User fills name, email, password, confirm password
2. Validates password match
3. Sends: `POST /api/auth/signup`
```javascript
fetch('http://127.0.0.1:8000/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        email: email, 
        full_name: name, 
        password: password 
    })
})
```
4. Stores token to localStorage (dual keys for compatibility)
5. Redirects to `/learning-interview.html`

**Login Flow:**
1. User enters email and password
2. Sends: `POST /api/auth/login?email=X&password=Y`
3. Stores token and user info to localStorage
4. Redirects to `/home.html`

**Error Handling:**
- Shows popup with backend error message
- Validates: empty fields, email format, password match

---

### 📚 3. **learning-interview.html** (Learning Profile Setup)
**Path:** `front/html/learning-interview.html`
**Purpose:** Quiz to determine user's learning style
**Backend APIs Used:**
- `PUT /api/learning/my-profile` (on submit)
**Status:** ⚠️ Needs Verification

**Expected Connection:**
```javascript
// On quiz completion
const selectedStyle = getSelectedLearningStyle(); // visual, auditory, etc.

fetch('http://127.0.0.1:8000/api/learning/my-profile', {
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
.then(response => response.json())
.then(data => {
    // Mark interview as completed
    // Redirect to home.html
    window.location.href = '/home.html';
})
```

**TODO:** Add actual API call to learning-interview.html

---

### 🏠 4. **home.html** (Dashboard)
**Path:** `front/html/home.html`
**Purpose:** Main user dashboard with sidebar and sections
**Backend APIs Used:**
- `GET /api/learning/profile-status` (on page load)
- `GET /api/learning/my-profile` (fetch user profile)
**Status:** ⚠️ Incomplete Integration (has token check, missing API calls)

**Current Implementation:**
```javascript
// Only checks token presence (Lines 424-435)
const token = localStorage.getItem('access_token') || localStorage.getItem('token');
if (!token) window.location.href = 'login.html';
```

**Missing Implementation:**
1. Fetch and display user profile data
2. Fetch and display learning style
3. Fetch tasks list
4. Load chat history (if applicable)

**TODO: Add These Features:**
```javascript
// On page load, fetch user profile
async function loadUserProfile() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/learning/my-profile', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const profile = await response.json();
    document.getElementById('learningStyle').textContent = profile.learning_style;
    // Update other profile fields
}

// Fetch tasks from backend
async function loadTasks() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/tasks/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const tasks = await response.json();
    // Render tasks in the UI
    renderTasks(tasks);
}

// Call on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    loadTasks();
});
```

**Sections in Dashboard:**
- Dashboard (main overview)
- Tasks (CRUD operations)
- Chat (AI assistant)
- Profile (user settings)

Each section needs backend API integration.

---

### ✅ 5. **tasks.html** (Task Management)
**Path:** `front/html/tasks.html`
**Purpose:** Create, read, update, delete tasks
**Backend APIs Used:**
- `GET /api/tasks/` (list all tasks)
- `POST /api/tasks/` (create new task)
- `GET /api/tasks/{id}` (fetch single task)
- `PUT /api/tasks/{id}` (update task)
- `DELETE /api/tasks/{id}` (delete task)
**Status:** ⚠️ Needs Verification

**Expected Implementation:**
```javascript
// Load all tasks
async function loadTasks() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/tasks/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const tasks = await response.json();
    renderTaskList(tasks);
}

// Create new task
async function createTask(taskData) {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/tasks/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
    });
    return await response.json();
}

// Update task status
async function updateTask(taskId, updates) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://127.0.0.1:8000/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
    });
    return await response.json();
}

// Delete task
async function deleteTask(taskId) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://127.0.0.1:8000/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return await response.json();
}
```

---

### 👤 6. **profile.html** (User Profile)
**Path:** `front/html/profile.html`
**Purpose:** Display and edit user profile
**Backend APIs Used:**
- `GET /api/learning/my-profile`
- `PUT /api/learning/my-profile`
**Status:** ⚠️ Needs Verification

**Expected Implementation:**
```javascript
// Fetch and display profile
async function loadProfile() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/learning/my-profile', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const profile = await response.json();
    
    // Display profile data
    document.getElementById('profileName').value = localStorage.getItem('user_name');
    document.getElementById('learningStyle').textContent = profile.learning_style;
    // ... display other fields
}

// Update profile
async function updateProfile(updates) {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/learning/my-profile', {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
    });
    return await response.json();
}
```

---

## ⚡ Quick Integration Checklist

### Pages Ready for Production ✅
- [x] login.html - Complete backend integration for auth
- [x] index.html - Static landing page

### Pages Need Backend Integration ⚠️
- [ ] learning-interview.html - Add API call to PUT profile
- [ ] home.html - Add profile fetch and task list fetch
- [ ] tasks.html - Add CRUD operations for tasks
- [ ] profile.html - Add profile fetch and update
- [ ] 404.html - Error page (static, no APIs needed)

---

## 🔐 Global Helper Functions (Add to main JavaScript)

Create `front/js/api-client.js`:

```javascript
// Global API client with automatic token handling
const API_BASE_URL = 'http://127.0.0.1:8000';

async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            localStorage.removeItem('token');
            window.location.href = '/login.html';
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showError('خطأ اتصال 🌐 تأكد من تشغيل الخادم');
        return null;
    }
}

// Usage examples:
// const profile = await apiCall('/api/learning/my-profile');
// const tasks = await apiCall('/api/tasks/');
// await apiCall('/api/tasks/', { method: 'POST', body: JSON.stringify(taskData) });
```

Then import in all HTML files:
```html
<script src="/js/api-client.js"></script>
```

---

## 📡 Testing from Browser Console

```javascript
// Test login
fetch('http://127.0.0.1:8000/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        email: 'test@example.com',
        full_name: 'اختبار',
        password: 'TestPass123!'
    })
}).then(r => r.json()).then(console.log);

// Test protected endpoint
fetch('http://127.0.0.1:8000/api/learning/my-profile', {
    headers: { 'Authorization': 'Bearer YOUR_TOKEN_HERE' }
}).then(r => r.json()).then(console.log);
```

---

## 🚀 Integration Priority

### Phase 1 (Critical) 🔴
- [x] Auth endpoints (login/signup)
- [ ] Profile status check (prevent auth bypass)

### Phase 2 (Important) 🟠
- [ ] Load user profile on home.html
- [ ] Load tasks list
- [ ] Update profile (learning-interview)

### Phase 3 (Enhancement) 🟡
- [ ] Task CRUD operations
- [ ] Chat functionality (backend might be AI-based)
- [ ] Profile editing

### Phase 4 (Polish) 🟢
- [ ] Error handling and user feedback
- [ ] Loading states
- [ ] Offline detection
- [ ] Auto-save functionality


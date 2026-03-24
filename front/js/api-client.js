/**
 * 🔗 API Client for Fakarni Frontend
 * 
 * This client handles all API communication between frontend and backend
 * Automatically includes authentication headers for protected routes
 * 
 * Usage Examples:
 * - const data = await apiClient.get('/api/learning/my-profile');
 * - const result = await apiClient.post('/api/tasks', { title: 'Task' });
 * - const updated = await apiClient.put('/api/tasks/1', { status: 'completed' });
 * - await apiClient.delete('/api/tasks/1');
 */

class APIClient {
    constructor(baseURL = 'http://127.0.0.1:8000') {
        this.baseURL = baseURL;
        this.tokenKey = 'access_token';
        this.fallbackTokenKey = 'token';
    }

    /**
     * Get stored authentication token
     * Tries primary key first, then fallback
     */
    getToken() {
        return localStorage.getItem(this.tokenKey) || localStorage.getItem(this.fallbackTokenKey);
    }

    /**
     * Build headers with authorization token
     */
    buildHeaders(customHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, method = 'GET', body = null, customHeaders = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = this.buildHeaders(customHeaders);

        const options = {
            method,
            headers
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, options);

            // Handle 401 - unauthorized (token expired or invalid)
            if (response.status === 401) {
                console.warn('[APIClient] Unauthorized - clearing tokens and redirecting to login');
                localStorage.removeItem(this.tokenKey);
                localStorage.removeItem(this.fallbackTokenKey);
                localStorage.removeItem('user_name');
                localStorage.removeItem('user_email');
                localStorage.removeItem('user_id');
                // Redirect to login page
                if (!window.location.pathname.includes('login.html')) {
                    window.location.href = '/login.html';
                }
                return null;
            }

            // Handle errors
            if (!response.ok) {
                const errorData = await response.json();
                const errorMessage = errorData.detail || response.statusText;
                console.error(`[APIClient] Error ${response.status}: ${errorMessage}`);
                throw new Error(errorMessage);
            }

            // Parse and return response
            const data = await response.json();
            return data;

        } catch (error) {
            console.error('[APIClient] Request failed:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, customHeaders = {}) {
        return this.request(endpoint, 'GET', null, customHeaders);
    }

    /**
     * POST request
     */
    async post(endpoint, body = {}, customHeaders = {}) {
        return this.request(endpoint, 'POST', body, customHeaders);
    }

    /**
     * PUT request
     */
    async put(endpoint, body = {}, customHeaders = {}) {
        return this.request(endpoint, 'PUT', body, customHeaders);
    }

    /**
     * PATCH request
     */
    async patch(endpoint, body = {}, customHeaders = {}) {
        return this.request(endpoint, 'PATCH', body, customHeaders);
    }

    /**
     * DELETE request
     */
    async delete(endpoint, customHeaders = {}) {
        return this.request(endpoint, 'DELETE', null, customHeaders);
    }
}

/**
 * 🔐 Authentication Service
 */
class AuthService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Signup new user
     */
    async signup(email, fullName, password) {
        return this.api.post('/api/auth/signup', {
            email,
            full_name: fullName,
            password
        });
    }

    /**
     * Login existing user
     */
    async login(email, password) {
        const endpoint = `/api/auth/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;
        return this.api.post(endpoint);
    }

    /**
     * Store auth tokens and user info
     */
    storeAuth(authData) {
        localStorage.setItem(this.api.tokenKey, authData.access_token);
        localStorage.setItem(this.api.fallbackTokenKey, authData.access_token);
        localStorage.setItem('user_id', authData.user_id);
        localStorage.setItem('user_name', authData.name);
        localStorage.setItem('user_email', authData.email);
    }

    /**
     * Check if user is logged in
     */
    isLoggedIn() {
        return !!this.api.getToken();
    }

    /**
     * Logout and clear stored data
     */
    logout() {
        localStorage.removeItem(this.api.tokenKey);
        localStorage.removeItem(this.api.fallbackTokenKey);
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_email');
    }
}

/**
 * 📚 Learning Profile Service
 */
class LearningService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Get user's profile status (check if interview completed)
     */
    async getProfileStatus() {
        return this.api.get('/api/learning/profile-status');
    }

    /**
     * Get current user's learning profile
     */
    async getProfile() {
        return this.api.get('/api/learning/my-profile');
    }

    /**
     * Update user's learning profile
     */
    async updateProfile(learningStyle, completedInterview = false) {
        return this.api.put('/api/learning/my-profile', {
            learning_style: learningStyle,
            completed_interview: completedInterview
        });
    }

    /**
     * Get learning style percentages
     */
    async getLearningStyles() {
        return this.api.get('/api/learning/learning-styles');
    }
}

/**
 * ✅ Task Service
 */
class TaskService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Get all tasks for current user
     */
    async getAllTasks() {
        return this.api.get('/api/tasks/');
    }

    /**
     * Get specific task by ID
     */
    async getTask(taskId) {
        return this.api.get(`/api/tasks/${taskId}`);
    }

    /**
     * Create new task
     */
    async createTask(title, description = '', priority = 'medium', dueDate = null) {
        return this.api.post('/api/tasks/', {
            title,
            description,
            priority,
            due_date: dueDate
        });
    }

    /**
     * Update existing task
     */
    async updateTask(taskId, updates) {
        return this.api.put(`/api/tasks/${taskId}`, updates);
    }

    /**
     * Update task status
     */
    async updateTaskStatus(taskId, status) {
        return this.api.put(`/api/tasks/${taskId}`, { status });
    }

    /**
     * Delete task
     */
    async deleteTask(taskId) {
        return this.api.delete(`/api/tasks/${taskId}`);
    }
}

/**
 * 🎯 UI Helper Functions
 */
class UIHelper {
    /**
     * Show error popup
     */
    static showError(title, message) {
        const popup = document.getElementById('customPopup');
        if (popup) {
            document.getElementById('popupTitle').textContent = title;
            document.getElementById('popupMessage').textContent = message;
            popup.classList.add('active');
        } else {
            alert(`${title}: ${message}`);
        }
    }

    /**
     * Show success popup
     */
    static showSuccess(title, message) {
        this.showError(title, message); // Same popup styling
    }

    /**
     * Show loading indicator
     */
    static showLoading(elementId, show = true) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.opacity = show ? '0.6' : '1';
            element.style.pointerEvents = show ? 'none' : 'auto';
        }
    }

    /**
     * Require authentication
     */
    static requireAuth() {
        const apiClient = new APIClient();
        if (!apiClient.getToken()) {
            window.location.href = '/login.html';
        }
    }

    /**
     * Get user name from localStorage
     */
    static getUserName() {
        return localStorage.getItem('user_name') || 'يا صاحبي';
    }

    /**
     * Get user email from localStorage
     */
    static getUserEmail() {
        return localStorage.getItem('user_email') || '';
    }

    /**
     * Get user ID from localStorage
     */
    static getUserId() {
        return localStorage.getItem('user_id') || 0;
    }
}

// ============================================
// Initialize Global Instances
// ============================================

const apiClient = new APIClient();
const authService = new AuthService(apiClient);
const learningService = new LearningService(apiClient);
const taskService = new TaskService(apiClient);

// Export for use globally
window.apiClient = apiClient;
window.authService = authService;
window.learningService = learningService;
window.taskService = taskService;
window.UIHelper = UIHelper;

console.log('[APIClient] Initialized - Global services ready');

// Usage in HTML:
// <script src="/js/api-client.js"></script>
// <script>
//   // Example: Load user's tasks
//   taskService.getAllTasks().then(tasks => console.log(tasks));
// </script>

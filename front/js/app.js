/**
 * Fakarni AI - Frontend Logic
 * Handles global custom popups, real-time form validation, and Auth API calls.
 * Customized for Fakarni's playful and friendly vibe.
 */

const API_BASE = "http://localhost:8000/api";

function authToken() {
    return localStorage.getItem('access_token') || localStorage.getItem('token') || null;
}

function setAuth(data) {
    if (!data) return;
    if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token', data.access_token);
    }
    if (data.user_name) localStorage.setItem('user_name', data.user_name);
    if (data.full_name) localStorage.setItem('user_name', data.full_name);
    if (data.user_id) localStorage.setItem('user_id', data.user_id);
    if (data.email) localStorage.setItem('user_email', data.email);
}

function clearAuth() {
    ['access_token','token','user_name','user_email','user_id','userProfile'].forEach(k => localStorage.removeItem(k));
}

function requireAuth(redirect = '/') {
    const token = authToken();
    if (!token) {
        window.location.href = redirect;
        return false;
    }
    return true;
}

window.appAuth = {
    authToken,
    setAuth,
    clearAuth,
    requireAuth,
    showPopup: null,
    closePopup: null,
    logout: null
};

// ================= GLOBAL POPUP SYSTEM =================

// Override default alert
window.alert = function (message) {
    showPopup("فكرني بيقولك 🤖", message);
};

// Custom confirm (Basic override)
window.confirm = function (message) {
    return true; // Non-blocking, simple pass-through for now
};

function showPopup(title, message, callback = null) {
    const overlay = document.getElementById('customPopup');
    if (!overlay) return;

    document.getElementById('popupTitle').innerText = title;
    document.getElementById('popupMessage').innerText = message;

    overlay.classList.add('active');

    // Store callback on the OK button
    const btn = overlay.querySelector('button');
    // Remove old listeners to prevent duplicate clicks
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);
    
    newBtn.onclick = function () {
        closePopup();
        if (callback) callback();
    };
}

function closePopup() {
    const overlay = document.getElementById('customPopup');
    if (overlay) overlay.classList.remove('active');
}

window.appAuth.showPopup = showPopup;
window.appAuth.closePopup = closePopup;

// ================= MAIN LOGIC =================

document.addEventListener("DOMContentLoaded", () => {
    
    // --- Dark Mode Logic ---
    const themeToggle = document.getElementById("checkbox");
    const body = document.body;
    const html = document.documentElement;

    // Load saved preference
    if (localStorage.getItem("theme") === "light-mode") {
        html.classList.add("light-mode");
        body.classList.add("light-mode");
        if (themeToggle) themeToggle.checked = true;
    }

    if (themeToggle) {
        themeToggle.addEventListener("change", () => {
            if (themeToggle.checked) {
                html.classList.add("light-mode");
                body.classList.add("light-mode");
                localStorage.setItem("theme", "light-mode");
            } else {
                html.classList.remove("light-mode");
                body.classList.remove("light-mode");
                localStorage.setItem("theme", "dark-mode");
            }
        });
    }

    // --- Input Validation Logic ---
    const inputs = document.querySelectorAll(".field input");

    inputs.forEach(input => {
        // Validate strictly on blur
        input.addEventListener("blur", () => {
            validateInput(input);
        });

        // Clear error as soon as user types
        input.addEventListener("input", () => {
            const field = input.parentElement;
            if (field.classList.contains("error")) {
                field.classList.remove("error");
            }
        });
    });

    // --- 1. LOGIN FORM HANDLING ---
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            if (validateForm(loginForm)) {
                const submitBtn = loginForm.querySelector('input[type="submit"]');
                const originalText = submitBtn.value;
                
                // UI Feedback (Fakarni Style)
                submitBtn.value = "ثواني بفتكرك... ⏳";
                submitBtn.disabled = true;
                submitBtn.style.cursor = "not-allowed";

                // Get values (Using robust selectors)
                const emailInput = loginForm.querySelector('input[type="text"]');
                const passInput = loginForm.querySelector('input[type="password"]');
                
                const email = emailInput.value.trim();
                const password = passInput.value.trim();

                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Success: Save Token/User info and redirect
                        appAuth.setAuth({
                            full_name: data.name || data.full_name || "يا حبيب",
                            user_name: data.name || data.full_name || "يا حبيب",
                            user_id: data.user_id,
                            email: data.email || '',
                            access_token: data.access_token || data.token,
                        });
                        window.location.href = "/home";
                    } else {
                        showPopup("مش عارف ألاقيك! 🕵️‍♂️", data.detail || "الإيميل أو الباسورد فيهم حاجة غلط، ركز كده!");
                    }
                } catch (error) {
                    console.error("Login Error:", error);
                    showPopup("فصلت شحن! 🔌", "مش قادر أوصل للسيرفر، اتأكد من النت وجرب تاني.");
                } finally {
                    // Reset Button
                    submitBtn.value = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.cursor = "pointer";
                }
            }
        });
    }

    // --- 2. SIGNUP FORM HANDLING (FIXED) ---
    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (validateForm(signupForm)) {
                const submitBtn = signupForm.querySelector('input[type="submit"]');
                const originalText = submitBtn.value;

                // UI Feedback (Fakarni Style)
                submitBtn.value = "بجهزلك مكان... 🚀";
                submitBtn.disabled = true;
                submitBtn.style.cursor = "not-allowed";

                // Get Values using IDs (Robust method)
                const nameInput = document.getElementById("signupName") || signupForm.querySelector('input[placeholder="Full Name"]');
                const emailInput = document.getElementById("signupEmail") || signupForm.querySelector('input[placeholder="Email Address"]');
                const passInput = document.getElementById("signupPass") || signupForm.querySelector('input[placeholder="Password"]');

                const fullName = nameInput.value.trim();
                const email = emailInput.value.trim();
                const password = passInput.value.trim();

                try {
                    // CRITICAL FIX: Sending "full_name" instead of "name"
                    const payload = {
                        full_name: fullName, 
                        email: email, 
                        password: password 
                    };

                    const response = await fetch('/api/auth/signup', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    const data = await response.json();

                    if (response.ok) {
                        showPopup("عاش يا بطل! 🎉", "حسابك جاهز يا صاحبي، يالا اعمل تسجيل دخول وخلينا نبدأ نظبط الدنيا.", () => {
                            // Switch to login tab automatically
                            const loginTab = document.querySelector("label.login");
                            if(loginTab) loginTab.click();
                        });
                    } else {
                        // Show specific error from backend
                        let errorMsg = data.detail;
                        if (Array.isArray(data.detail)) {
                             errorMsg = data.detail[0].msg; 
                        }
                        showPopup("في حاجة غلط! ⚠️", errorMsg || "مقدرتش أعمل الحساب، جرب بإيميل تاني.");
                    }
                } catch (error) {
                    console.error("Signup Error:", error);
                    showPopup("فصلت شحن! 🔌", "مش قادر أوصل للسيرفر، اتأكد من النت وجرب تاني.");
                } finally {
                    // Reset Button
                    submitBtn.value = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.cursor = "pointer";
                }
            }
        });
    }

}); // End DOMContentLoaded


// ================= HELPER FUNCTIONS =================

function logout() {
    clearAuth();
    window.location.href = '/';
}

window.appAuth.logout = logout;

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll("input:not([type='submit'])");

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateInput(input) {
    const field = input.parentElement;
    const value = input.value.trim();
    // Use ID if available, otherwise placeholder for type detection
    const typeIdentifier = (input.id + input.placeholder).toLowerCase(); 
    let errorMsg = field.querySelector(".error-text");
    let isError = false;

    // 1. Check Empty
    if (value === "") {
        isError = true;
        if (errorMsg) errorMsg.innerText = "أومال هسجل إيه؟ الخانة دي فاضية! 😅";
    }
    // 2. Check Email
    else if (typeIdentifier.includes("email") && !validateEmail(value)) {
        isError = true;
        if (errorMsg) errorMsg.innerText = "ده مش شكل إيميل يا صديقي! ✉️";
    }
    // 3. Check Password Length (Exclude Confirm Password field)
    else if (typeIdentifier.includes("pass") && !typeIdentifier.includes("confirm") && value.length < 6) {
        isError = true;
        if (errorMsg) errorMsg.innerText = "الباسورد لازم 6 حروف أو أكتر عشان الأمان 🔒";
    }
    // 4. Check Confirm Password
    else if (typeIdentifier.includes("confirm")) {
        // Find the main password field (try ID first, then generic selector)
        const mainPassInput = document.getElementById("signupPass") || 
                              input.closest("form").querySelector("input[placeholder='Password']");
        
        if (mainPassInput && value !== mainPassInput.value) {
            isError = true;
            if (errorMsg) errorMsg.innerText = "الباسوردين مش زي بعض، ركز معايا! 👀";
        }
    }

    // Apply Styles
    if (isError) {
        field.classList.add("error");
        return false;
    } else {
        field.classList.remove("error");
        return true;
    }
}

function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}
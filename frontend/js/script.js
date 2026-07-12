// API Base URL - Update the placeholder with your actual deployed backend URL (e.g. Render)
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api'
    : 'https://YOUR-BACKEND-URL.onrender.com/api';

// --- UTILITIES ---

function getToken() {
    return localStorage.getItem('token');
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    const user = getUser();
    return user && user.role === 'admin';
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// --- API CALLS ---

async function fetchAPI(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Remove Content-Type if FormData (browser sets it automatically with boundary)
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                if (!window.location.pathname.includes('login.html')) {
                    window.location.href = 'login.html';
                }
            }
            throw new Error(data.error || 'Something went wrong');
        }
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// --- UI UPDATES ---

function updateNav() {
    const user = getUser();
    const guestLinks = document.querySelectorAll('.guest-only');
    const authLinks = document.querySelectorAll('.auth-only');
    const adminLinks = document.querySelectorAll('.admin-only');
    const userNames = document.querySelectorAll('.user-name');
    
    if (user) {
        guestLinks.forEach(el => el.classList.add('hidden'));
        authLinks.forEach(el => el.classList.remove('hidden'));
        userNames.forEach(el => el.textContent = user.name);
        
        if (user.role === 'admin') {
            adminLinks.forEach(el => el.classList.remove('hidden'));
        } else {
            adminLinks.forEach(el => el.classList.add('hidden'));
        }
        updateCartBadge();
    } else {
        guestLinks.forEach(el => el.classList.remove('hidden'));
        authLinks.forEach(el => el.classList.add('hidden'));
        adminLinks.forEach(el => el.classList.add('hidden'));
    }
}

async function updateCartBadge() {
    if (!isLoggedIn()) return;
    try {
        const cart = await fetchAPI('/cart');
        const badge = document.getElementById('cart-badge');
        if (badge) {
            const count = cart.items ? cart.items.reduce((acc, item) => acc + item.quantity, 0) : 0;
            badge.textContent = count;
            badge.classList.toggle('hidden', count === 0);
        }
    } catch (e) {
        console.error('Error updating cart badge', e);
    }
}

function handleLogout() {
    fetchAPI('/logout', { method: 'POST' }).finally(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    });
}

// --- PAGE SPECIFIC LOGIC ---

document.addEventListener('DOMContentLoaded', () => {
    updateNav();
    
    // Bind Logout
    const logoutBtns = document.querySelectorAll('.logout-btn');
    logoutBtns.forEach(btn => btn.addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
    }));
    
    // Load pages based on URL
    const path = window.location.pathname;
    
    if (path.includes('register.html')) initRegister();
    if (path.includes('login.html')) initLogin();
    if (path.includes('medicines.html')) initMedicines();
    if (path.includes('medicine-details.html')) initMedicineDetails();
    if (path.includes('cart.html')) initCart();
    if (path.includes('checkout.html')) initCheckout();
    if (path.includes('orders.html')) initOrders();
    if (path.includes('admin-dashboard.html')) initAdminDashboard();
    if (path.includes('admin-medicines.html')) initAdminMedicines();
});

// Implement page functions...
function initRegister() {
    const form = document.getElementById('register-form');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(form));
        if (data.password !== data.confirmPassword) {
            return showToast('Passwords do not match', 'error');
        }
        try {
            await fetchAPI('/register', { method: 'POST', body: JSON.stringify(data) });
            showToast('Registration successful. Please log in.');
            setTimeout(() => window.location.href = 'login.html', 1500);
        } catch (e) {}
    });
}

function initLogin() {
    const form = document.getElementById('login-form');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(form));
        try {
            const res = await fetchAPI('/login', { method: 'POST', body: JSON.stringify(data) });
            localStorage.setItem('token', res.token);
            localStorage.setItem('user', JSON.stringify(res.user));
            showToast('Login successful');
            setTimeout(() => {
                window.location.href = res.user.role === 'admin' ? 'admin-dashboard.html' : 'index.html';
            }, 1000);
        } catch (e) {}
    });
}

async function initMedicines() {
    const container = document.getElementById('medicines-grid');
    if (!container) return;
    
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    const sortFilter = document.getElementById('sort-filter');
    const applyBtn = document.getElementById('apply-filters-btn');
    
    let allMeds = [];
    
    // Load Categories for filter dropdown
    try {
        const cats = await fetchAPI('/categories');
        if(categoryFilter) {
            cats.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.categoryName;
                opt.textContent = c.categoryName;
                categoryFilter.appendChild(opt);
            });
        }
    } catch (e) {}

    const renderMeds = () => {
        let filtered = [...allMeds];
        
        // Search
        if(searchInput && searchInput.value) {
            const q = searchInput.value.toLowerCase();
            filtered = filtered.filter(m => m.medicineName.toLowerCase().includes(q) || m.brand.toLowerCase().includes(q));
        }
        
        // Category
        if(categoryFilter && categoryFilter.value) {
            filtered = filtered.filter(m => m.category === categoryFilter.value);
        }
        
        // Sort
        if(sortFilter && sortFilter.value) {
            const s = sortFilter.value;
            if(s === 'name_asc') filtered.sort((a,b) => a.medicineName.localeCompare(b.medicineName));
            if(s === 'name_desc') filtered.sort((a,b) => b.medicineName.localeCompare(a.medicineName));
            if(s === 'price_asc') filtered.sort((a,b) => a.price - b.price);
            if(s === 'price_desc') filtered.sort((a,b) => b.price - a.price);
        }
        
        if(filtered.length === 0) {
            container.innerHTML = '<p>No medicines found.</p>';
            return;
        }
        
        container.innerHTML = filtered.map(med => `
            <div class="card medicine-card">
                <img src="${med.image || 'https://via.placeholder.com/200'}" alt="${med.medicineName}" class="medicine-img">
                <h3 class="medicine-title">${med.medicineName}</h3>
                <p class="medicine-category">${med.category}</p>
                <div class="medicine-price">₹${med.price.toFixed(2)}</div>
                <button class="btn btn-primary" onclick="addToCart('${med._id}')">Add to Cart</button>
                <a href="medicine-details.html?id=${med._id}" class="btn btn-outline mt-1">View Details</a>
            </div>
        `).join('');
    };

    try {
        allMeds = await fetchAPI('/medicines');
        renderMeds();
    } catch (e) {
        container.innerHTML = '<p>Error loading medicines.</p>';
    }
    
    if(applyBtn) applyBtn.addEventListener('click', renderMeds);
    if(searchInput) searchInput.addEventListener('keypress', e => e.key === 'Enter' && renderMeds());
}

async function addToCart(medicineId, quantity = 1) {
    if (!isLoggedIn()) {
        showToast('Please login to add to cart', 'error');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return;
    }
    try {
        await fetchAPI('/cart/add', {
            method: 'POST',
            body: JSON.stringify({ medicineId, quantity })
        });
        showToast('Added to cart');
        updateCartBadge();
    } catch (e) {}
}

async function initCart() {
    const container = document.getElementById('cart-items');
    if (!container) return;
    try {
        const cart = await fetchAPI('/cart');
        const totalEl = document.getElementById('cart-total');
        if (!cart.items || cart.items.length === 0) {
            container.innerHTML = '<p>Your cart is empty.</p>';
            if(totalEl) totalEl.textContent = '₹0.00';
            return;
        }
        
        container.innerHTML = cart.items.map(item => `
            <div class="card d-flex align-items-center justify-content-between mb-2">
                <div class="d-flex align-items-center gap-2">
                    <img src="${item.medicine?.image || 'https://via.placeholder.com/50'}" style="width: 50px; height: 50px; object-fit: cover;">
                    <div>
                        <h4>${item.medicine?.medicineName || 'Unknown'}</h4>
                        <p>₹${item.price.toFixed(2)}</p>
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <button class="btn btn-outline" onclick="updateCart('${item.medicineId}', ${item.quantity - 1})">-</button>
                    <span>${item.quantity}</span>
                    <button class="btn btn-outline" onclick="updateCart('${item.medicineId}', ${item.quantity + 1})">+</button>
                    <button class="btn btn-danger" onclick="removeFromCart('${item.medicineId}')">Remove</button>
                </div>
            </div>
        `).join('');
        if(totalEl) totalEl.textContent = '₹' + cart.total.toFixed(2);
    } catch (e) {}
}

async function updateCart(medicineId, quantity) {
    if (quantity < 1) return removeFromCart(medicineId);
    try {
        await fetchAPI('/cart/update', {
            method: 'PUT',
            body: JSON.stringify({ medicineId, quantity })
        });
        initCart();
        updateCartBadge();
    } catch (e) {}
}

async function removeFromCart(medicineId) {
    try {
        await fetchAPI(`/cart/remove/${medicineId}`, { method: 'DELETE' });
        initCart();
        updateCartBadge();
        showToast('Item removed');
    } catch (e) {}
}

// Global functions for inline handlers
window.addToCart = addToCart;
window.updateCart = updateCart;
window.removeFromCart = removeFromCart;

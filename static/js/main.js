// Dhofar University Student Management System JavaScript

// Global utility functions
function showLoading(element) {
    const spinner = '<i class="fas fa-spinner fa-spin"></i>';
    const originalContent = element.innerHTML;
    element.innerHTML = spinner + ' Loading...';
    element.disabled = true;
    return originalContent;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// API helper functions
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Theme Toggle (Dark / Light Mode)
function initThemeToggle() {
    const toggleBtn = document.getElementById('duThemeToggleBtn');
    const themeIcon = document.getElementById('duThemeIcon');
    const themeLabel = document.getElementById('duThemeLabel');

    function updateToggleUI(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.className = 'fas fa-sun text-warning';
            if (themeLabel) themeLabel.textContent = 'Light';
            if (toggleBtn) toggleBtn.setAttribute('title', 'Switch to Light Mode');
        } else {
            themeIcon.className = 'fas fa-moon text-light';
            if (themeLabel) themeLabel.textContent = 'Dark';
            if (toggleBtn) toggleBtn.setAttribute('title', 'Switch to Dark Mode');
        }
    }

    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    updateToggleUI(currentTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const activeTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('du_theme', newTheme);
            updateToggleUI(newTheme);

            if (themeIcon) {
                themeIcon.style.transform = 'rotate(360deg)';
                setTimeout(() => { themeIcon.style.transform = ''; }, 350);
            }

            window.dispatchEvent(new CustomEvent('duThemeChanged', { detail: { theme: newTheme } }));
        });
    }

    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            if (!localStorage.getItem('du_theme')) {
                const sysTheme = e.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', sysTheme);
                updateToggleUI(sysTheme);
                window.dispatchEvent(new CustomEvent('duThemeChanged', { detail: { theme: sysTheme } }));
            }
        });
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dhofar University Student Management System initialized');
    initThemeToggle();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
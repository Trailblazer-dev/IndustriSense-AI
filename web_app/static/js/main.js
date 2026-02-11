/* Main JavaScript file for IndustriSense AI */

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', () => {
    console.log('IndustriSense AI Dashboard Initialized');
    initializeEventListeners();
});

function initializeEventListeners() {
    // Hamburger menu toggle
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Close menu when navigating to a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navbar-container')) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
    
    // Close alerts
    const closeButtons = document.querySelectorAll('.alert .close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
}

// API Helper Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert('An error occurred. Please try again.', 'danger');
        throw error;
    }
}

function showAlert(message, type = 'info') {
    const alertHTML = `
        <div class="alert alert-${type}">
            ${message}
            <button type="button" class="close" data-dismiss="alert">&times;</button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    const alertElement = document.createElement('div');
    alertElement.innerHTML = alertHTML;
    
    const firstAlert = container.querySelector('.alert');
    if (firstAlert) {
        firstAlert.parentElement.insertBefore(alertElement.firstElementChild, firstAlert);
    } else {
        container.insertBefore(alertElement.firstElementChild, container.firstChild);
    }
}

// Utility Functions
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getStatusColor(status) {
    const colors = {
        'CRITICAL': '#f5576c',
        'WARNING': '#ffc107',
        'NORMAL': '#4CAF50'
    };
    return colors[status] || '#667eea';
}

// Chart Helper (if needed for future enhancements)
function createChart(canvasId, type, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Export utilities for reuse
window.IndustriSense = {
    apiCall,
    showAlert,
    formatNumber,
    formatDate,
    getStatusColor,
    createChart
};

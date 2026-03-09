/* Main JavaScript file for IndustriSense AI */

// Initialize Bootstrap tooltips and popovers
document.addEventListener('DOMContentLoaded', () => {
    console.log('IndustriSense AI Dashboard Initialized');
    
    // Initialize Bootstrap components
    initializeBootstrap();
    initializeEventListeners();
});

function initializeBootstrap() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeEventListeners() {
    // Close alerts automatically (Bootstrap dismiss still works with btn-close)
    const alertElements = document.querySelectorAll('.alert');
    alertElements.forEach(alert => {
        // Auto-dismiss non-permanent alerts after 5 seconds
        if (!alert.classList.contains('alert-persistent')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
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

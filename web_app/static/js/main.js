/**
 * IndustriSense AI - Main Interface Logic
 * Optimized for professional industrial monitoring
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('IndustriSense AI Interface Initialized');
    
    initializeBootstrap();
    setupNavigation();
    initializeBot();
});

/**
 * Initialize Assistant Bot Logic
 */
function initializeBot() {
    const botToggle = document.getElementById('bot-toggle');
    const botWindow = document.getElementById('bot-window');
    const botClose = document.getElementById('bot-close');
    const botSend = document.getElementById('bot-send');
    const botInput = document.getElementById('bot-input');
    const botMessages = document.getElementById('bot-messages');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    if (!botToggle) return;

    // --- Bot Knowledge Base ---
    const BOT_KNOWLEDGE = {
        metrics: {
            keywords: ['rul', 'minute', 'measure', 'wear', 'time', 'remaining'],
            response: "<strong>📊 Metrics Explanation:</strong><br><br>" +
                      "• <strong>Why Minutes?</strong> Industrial metrics use 'operating minutes' to track usage intensity rather than calendar hours.<br>" +
                      "• <strong>RUL (Remaining Useful Life):</strong> Operational minutes left before reaching the 254-min critical threshold.<br>" +
                      "• <strong>Wear:</strong> Predicted tool degradation based on real-time sensor streams."
        },
        technology: {
            keywords: ['tech', 'xgboost', 'ml', 'ai', 'algorithm', 'stack', 'flask', 'python'],
            response: "<strong>💻 Technical Architecture:</strong><br><br>" +
                      "• <strong>Core:</strong> Python 3.13 & Flask 3.0.<br>" +
                      "• <strong>ML Models:</strong> Dual XGBoost 3.2.0 engines (Vectorized for high speed).<br>" +
                      "• <strong>Persistence:</strong> SQLite with SQLAlchemy.<br>" +
                      "• <strong>Security:</strong> CSRF protection, Rate Limiting, and CSP headers."
        },
        security: {
            keywords: ['safe', 'security', 'secure', 'private', 'csrf', 'data', 'isolation', 'tenancy'],
            response: "<strong>🛡️ Security Protocols:</strong><br><br>" +
                      "• <strong>Multi-Tenancy:</strong> Strict data isolation ensures users only see their assigned fleet.<br>" +
                      "• <strong>Authentication:</strong> Secure session management via Flask-Login.<br>" +
                      "• <strong>Defense:</strong> CSRF tokens on all POST requests and brute-force rate limiting."
        },
        pricing: {
            keywords: ['price', 'cost', 'pay', 'plan', 'starter', 'pro', 'enterprise', 'money', 'subscription'],
            response: "<strong>💳 Subscription Tiers:</strong><br><br>" +
                      "• <strong>Starter:</strong> 5 machines + Advanced Analytics.<br>" +
                      "• <strong>Professional:</strong> 50 machines + Manual Diagnostics API.<br>" +
                      "• <strong>Enterprise:</strong> Unlimited machines + System Calibration.<br>" +
                      "• <strong>Payments:</strong> Secure processing via PayHero (M-Pesa/Card)."
        },
        project: {
            keywords: ['about', 'project', 'ktda', 'tea', 'origin', 'purpose', 'downtime'],
            response: "<strong>🏭 Project IndustriSense:</strong><br><br>" +
                      "Originally tailored for the <strong>Kenya Tea Development Agency (KTDA)</strong>, this platform aims to reduce unplanned industrial downtime by up to <strong>35%</strong> using predictive failure signals."
        },
        help: {
            keywords: ['help', 'support', 'contact', 'human', 'email', 'engineer'],
            response: "<strong>🆘 Need Human Assistance?</strong><br><br>" +
                      "You can reach our engineering support team directly at <strong>support@industrisense.ai</strong>. We typically respond within 2 business hours."
        }
    };

    // Toggle Window
    botToggle.addEventListener('click', () => {
        botWindow.classList.toggle('d-none');
        if (!botWindow.classList.contains('d-none')) {
            botInput.focus();
        }
    });

    botClose.addEventListener('click', () => {
        botWindow.classList.add('d-none');
    });

    // Handle Suggestions
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-btn')) {
            const query = e.target.getAttribute('data-query');
            handleBotQuery(query);
        }
    });

    // Send Message
    const sendMessage = () => {
        const query = botInput.value.trim();
        if (query) {
            handleBotQuery(query);
            botInput.value = '';
        }
    };

    botSend.addEventListener('click', sendMessage);
    botInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function handleBotQuery(query) {
        appendMessage(query, 'user');
        showTypingIndicator();

        setTimeout(() => {
            hideTypingIndicator();
            let bestMatch = null;
            const q = query.toLowerCase();

            // Keyword Matching Engine
            for (const category in BOT_KNOWLEDGE) {
                const keywords = BOT_KNOWLEDGE[category].keywords;
                if (keywords.some(k => q.includes(k))) {
                    bestMatch = BOT_KNOWLEDGE[category].response;
                    break;
                }
            }

            const response = bestMatch || "I'm not exactly sure about that. Try asking about <strong>security</strong>, <strong>pricing</strong>, <strong>technology</strong>, or <strong>RUL metrics</strong>.";
            appendMessage(response, 'bot');
        }, 800);
    }

    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message mb-2`;
        msgDiv.innerHTML = text;
        botMessages.appendChild(msgDiv);
        botMessages.scrollTop = botMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'bot-typing';
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        botMessages.appendChild(indicator);
        botMessages.scrollTop = botMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById('bot-typing');
        if (indicator) indicator.remove();
    }
}


/**
 * Initialize Bootstrap 5 tooltips, popovers, and alerts
 */
function initializeBootstrap() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (el) {
        return new bootstrap.Popover(el);
    });

    // Auto-dismiss alerts after 8 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 8000);
    });
}

/**
 * Enhanced navigation feedback
 */
function setupNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Utility: Format large numbers for industrial display
 */
window.formatValue = (val, decimals = 2) => {
    if (typeof val !== 'number') return val;
    return val.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
};

/**
 * Global IndustriSense UI Object
 */
window.IndustriSense = {
    showFeedback: (message, type = 'info') => {
        const container = document.querySelector('.content-wrapper');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show border-0 shadow-sm mx-4 mt-3`;
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-info-circle me-3"></i>
                <div>${message}</div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.prepend(alertDiv);
    }
};

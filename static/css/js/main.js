// Payment handling
function initializePayment(method) {
    const paymentMethods = document.querySelectorAll('.payment-method-card');
    paymentMethods.forEach(card => card.classList.remove('selected'));
    
    const selectedCard = document.querySelector(`[data-method="${method}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    document.getElementById('payment-method').value = method;
}

// Task completion verification
async function verifyTask(taskId) {
    showLoading();
    
    try {
        const response = await fetch(`/api/verify-task/${taskId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            updatePoints(data.points);
            showSuccess('Task completed successfully!');
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
    } finally {
        hideLoading();
    }
}

// Loading overlay
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    document.querySelector('main').prepend(alert);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    document.querySelector('main').prepend(alert);
}

function updatePoints(points) {
    const pointsDisplay = document.querySelector('.nav-link[href="/profile/"] span');
    if (pointsDisplay) {
        pointsDisplay.textContent = points;
    }
}
const selectedPackage = document.querySelector(`.package-card[data-package="${packageId}"]`);
/**
 * Expense Tracker System - Master Frontend JS
 * Company: Monarch Softwares | Final Round Task
 */

// Modal Window Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Close modals when clicking outside
window.addEventListener('click', function (event) {
    if (event.target.classList.contains('modal-backdrop')) {
        event.target.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Mobile Sidebar Toggle
document.addEventListener('DOMContentLoaded', function () {
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('sidebar');

    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });
    }

    // Auto-dismiss Toast Notifications after 5 seconds
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    });

    // Display formatted local date in header
    const dateStrElem = document.getElementById('currentDateStr');
    if (dateStrElem) {
        const today = new Date();
        const options = { day: 'numeric', month: 'short', year: 'numeric' };
        dateStrElem.innerText = today.toLocaleDateString('en-GB', options);
    }
});

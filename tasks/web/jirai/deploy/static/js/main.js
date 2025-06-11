// Main JS file for Jirai Application

// Add HTMX extensions and boost
document.addEventListener('DOMContentLoaded', function() {
    // Handle toast messages
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Hide and remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // Listen for HTMX events
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'search-results') {
            showToast('Search results updated', 'success');
        }
    });
    
    document.body.addEventListener('htmx:responseError', function() {
        showToast('An error occurred while processing your request', 'error');
    });
    
    // Handle form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Highlight invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('is-invalid');
                    
                    // Add error message if not present
                    const parent = field.parentElement;
                    if (!parent.querySelector('.error-message')) {
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'error-message';
                        errorMessage.textContent = field.validationMessage;
                        parent.appendChild(errorMessage);
                    }
                });
                
                showToast('Please fix the errors in the form', 'warning');
            }
        });
        
        // Clear validation on input
        form.addEventListener('input', function(event) {
            if (event.target.classList.contains('is-invalid')) {
                event.target.classList.remove('is-invalid');
                
                // Remove error message if present
                const parent = event.target.parentElement;
                const errorMessage = parent.querySelector('.error-message');
                if (errorMessage) {
                    parent.removeChild(errorMessage);
                }
            }
        });
    });
});

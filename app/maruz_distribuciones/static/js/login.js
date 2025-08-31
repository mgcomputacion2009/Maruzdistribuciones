// Modern Login Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Modal functionality
    const modal = document.getElementById('developmentModal');
    const modalClose = document.querySelector('.modal-close');
    const modalButton = document.querySelector('.modal-button');
    
    // Function to show modal
    function showModal() {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    // Function to hide modal
    function hideModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    // Social button event listeners
    const socialButtons = document.querySelectorAll('.social-button');
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            showModal();
        });
    });
    
    // Login form submission
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        showModal();
    });
    
    // Modal close events
    modalClose.addEventListener('click', hideModal);
    modalButton.addEventListener('click', hideModal);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            hideModal();
        }
    });
    
    // Form input animations
    const formInputs = document.querySelectorAll('.form-input');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Check if input has value on page load
        if (input.value !== '') {
            input.parentElement.classList.add('focused');
        }
    });
    
    // Add smooth hover effects
    const buttons = document.querySelectorAll('button, .social-button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = '#ea4335';
                this.style.boxShadow = '0 0 0 3px rgba(234, 67, 53, 0.1)';
            } else {
                this.style.borderColor = '#e1e5e9';
                this.style.boxShadow = 'none';
            }
        });
    }
    
    // Password visibility toggle (optional feature)
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = getPasswordStrength(password);
            updatePasswordStrength(strength);
        });
    }
    
    function getPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        return strength;
    }
    
    function updatePasswordStrength(strength) {
        // This function can be expanded to show password strength indicator
        // For now, we'll just apply visual feedback
        const passwordInput = document.getElementById('password');
        if (strength >= 3) {
            passwordInput.style.borderColor = '#34a853';
        } else if (strength >= 2) {
            passwordInput.style.borderColor = '#fbbc04';
        } else if (strength >= 1) {
            passwordInput.style.borderColor = '#ea4335';
        }
    }
    
    // Animate elements on page load
    setTimeout(() => {
        const loginContainer = document.querySelector('.login-container');
        if (loginContainer) {
            loginContainer.style.opacity = '0';
            loginContainer.style.transform = 'translateY(20px)';
            loginContainer.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                loginContainer.style.opacity = '1';
                loginContainer.style.transform = 'translateY(0)';
            }, 100);
        }
    }, 100);
    
});

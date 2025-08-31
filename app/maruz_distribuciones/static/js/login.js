// Modern Login Page JavaScript - Maruz Distribuciones
document.addEventListener('DOMContentLoaded', function() {
    
    // Elementos del DOM
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const registerModal = document.getElementById('registerModal');
    const successModal = document.getElementById('successModal');
    const errorModal = document.getElementById('errorModal');
    
    // Botones de modal
    const showRegisterBtn = document.getElementById('showRegister');
    const showLoginBtn = document.getElementById('showLogin');
    const closeRegisterBtn = document.getElementById('closeRegister');
    const successButton = document.getElementById('successButton');
    const errorButton = document.getElementById('errorButton');
    
    // Botones de login social
    const googleLoginBtn = document.getElementById('googleLogin');
    const appleLoginBtn = document.getElementById('appleLogin');
    const facebookLoginBtn = document.getElementById('facebookLogin');
    
    // Toggle de contraseñas
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    // Estado de la aplicación
    let isAuthenticated = false;
    let currentUser = null;
    
    // Inicializar la aplicación
    init();
    
    function init() {
        setupEventListeners();
        setupPasswordToggles();
        checkAuthStatus();
        setupFormValidation();
    }
    
    function setupEventListeners() {
        // Login form
        loginForm.addEventListener('submit', handleLogin);
        
        // Register form
        registerForm.addEventListener('submit', handleRegister);
        
        // Modal controls
        showRegisterBtn.addEventListener('click', showRegisterModal);
        showLoginBtn.addEventListener('click', hideRegisterModal);
        closeRegisterBtn.addEventListener('click', hideRegisterModal);
        successButton.addEventListener('click', hideSuccessModal);
        errorButton.addEventListener('click', hideErrorModal);
        
        // Social login
        googleLoginBtn.addEventListener('click', handleGoogleLogin);
        appleLoginBtn.addEventListener('click', handleAppleLogin);
        facebookLoginBtn.addEventListener('click', handleFacebookLogin);
        
        // Cerrar modales al hacer clic fuera
        window.addEventListener('click', function(e) {
            if (e.target === registerModal) hideRegisterModal();
            if (e.target === successModal) hideSuccessModal();
            if (e.target === errorModal) hideErrorModal();
        });
        
        // Cerrar modales con Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hideRegisterModal();
                hideSuccessModal();
                hideErrorModal();
            }
        });
    }
    
    function setupPasswordToggles() {
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const input = this.previousElementSibling;
                const icon = this.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.className = 'fas fa-eye-slash';
                } else {
                    input.type = 'password';
                    icon.className = 'fas fa-eye';
                }
            });
        });
    }
    
    function setupFormValidation() {
        // Validación en tiempo real para email
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', validateEmail);
        }
        
        // Validación en tiempo real para contraseña
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', validatePassword);
        }
        
        // Validación para registro
        const regEmailInput = document.getElementById('regEmail');
        if (regEmailInput) {
            regEmailInput.addEventListener('blur', validateRegEmail);
        }
        
        const regPasswordInput = document.getElementById('regPassword');
        if (regPasswordInput) {
            regPasswordInput.addEventListener('input', validateRegPassword);
        }
        
        const regConfirmPasswordInput = document.getElementById('regConfirmPassword');
        if (regConfirmPasswordInput) {
            regConfirmPasswordInput.addEventListener('blur', validateConfirmPassword);
        }
    }
    
    // Validaciones
    function validateEmail() {
        const email = this.value.trim();
        const emailError = document.getElementById('emailError');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            showFieldError(emailError, 'El email es obligatorio');
            this.classList.add('error');
        } else if (!emailRegex.test(email)) {
            showFieldError(emailError, 'Formato de email inválido');
            this.classList.add('error');
        } else {
            hideFieldError(emailError);
            this.classList.remove('error');
        }
    }
    
    function validatePassword() {
        const password = this.value;
        const passwordError = document.getElementById('passwordError');
        
        if (password.length < 6) {
            showFieldError(passwordError, 'La contraseña debe tener al menos 6 caracteres');
            this.classList.add('error');
        } else {
            hideFieldError(passwordError);
            this.classList.remove('error');
        }
    }
    
    function validateRegEmail() {
        const email = this.value.trim();
        const emailError = document.getElementById('regEmailError');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            showFieldError(emailError, 'El email es obligatorio');
            this.classList.add('error');
        } else if (!emailRegex.test(email)) {
            showFieldError(emailError, 'Formato de email inválido');
            this.classList.add('error');
        } else {
            hideFieldError(emailError);
            this.classList.remove('error');
        }
    }
    
    function validateRegPassword() {
        const password = this.value;
        const passwordError = document.getElementById('regPasswordError');
        
        if (password.length < 6) {
            showFieldError(passwordError, 'La contraseña debe tener al menos 6 caracteres');
            this.classList.add('error');
        } else {
            hideFieldError(passwordError);
            this.classList.remove('error');
        }
    }
    
    function validateConfirmPassword() {
        const password = document.getElementById('regPassword').value;
        const confirmPassword = this.value;
        const confirmError = document.getElementById('regConfirmPasswordError');
        
        if (password !== confirmPassword) {
            showFieldError(confirmError, 'Las contraseñas no coinciden');
            this.classList.add('error');
        } else {
            hideFieldError(confirmError);
            this.classList.remove('error');
        }
    }
    
    function showFieldError(errorElement, message) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
    
    function hideFieldError(errorElement) {
        errorElement.classList.remove('show');
    }
    
    // Handlers principales
    async function handleLogin(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        // Validaciones
        if (!email || !password) {
            showError('Por favor completa todos los campos');
            return;
        }
        
        // Mostrar loading
        setLoginButtonLoading(true);
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember_me: rememberMe
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Guardar token
                localStorage.setItem('authToken', data.token);
                if (rememberMe) {
                    localStorage.setItem('rememberMe', 'true');
                }
                
                // Actualizar estado
                isAuthenticated = true;
                currentUser = data.user;
                
                // Mostrar éxito y redirigir
                showSuccess('Login exitoso', 'Redirigiendo al dashboard...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
                
            } else {
                showError(data.error || 'Error en el login');
            }
            
        } catch (error) {
            console.error('Error en login:', error);
            showError('Error de conexión. Intenta nuevamente.');
        } finally {
            setLoginButtonLoading(false);
        }
    }
    
    async function handleRegister(e) {
        e.preventDefault();
        
        const nombre = document.getElementById('regNombre').value.trim();
        const apellido = document.getElementById('regApellido').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        
        // Validaciones
        if (!nombre || !email || !password || !confirmPassword) {
            showError('Por favor completa todos los campos obligatorios');
            return;
        }
        
        if (password !== confirmPassword) {
            showError('Las contraseñas no coinciden');
            return;
        }
        
        if (password.length < 6) {
            showError('La contraseña debe tener al menos 6 caracteres');
            return;
        }
        
        // Mostrar loading
        setRegisterButtonLoading(true);
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre: nombre,
                    apellido: apellido,
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Guardar token
                localStorage.setItem('authToken', data.token);
                
                // Actualizar estado
                isAuthenticated = true;
                currentUser = data.user;
                
                // Mostrar éxito y cerrar modal
                hideRegisterModal();
                showSuccess('Registro exitoso', 'Tu cuenta ha sido creada correctamente');
                
                // Redirigir al dashboard
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
                
            } else {
                showError(data.error || 'Error en el registro');
            }
            
        } catch (error) {
            console.error('Error en registro:', error);
            showError('Error de conexión. Intenta nuevamente.');
        } finally {
            setRegisterButtonLoading(false);
        }
    }
    
    // Handlers de login social
    function handleGoogleLogin() {
        // Por ahora mostrar modal de desarrollo
        showError('Login con Google en desarrollo');
    }
    
    function handleAppleLogin() {
        showError('Login con Apple en desarrollo');
    }
    
    function handleFacebookLogin() {
        showError('Login con Facebook en desarrollo');
    }
    
    // Funciones de UI
    function showRegisterModal() {
        registerModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    function hideRegisterModal() {
        registerModal.style.display = 'none';
        document.body.style.overflow = 'auto';
        // Limpiar formulario
        registerForm.reset();
        // Limpiar errores
        document.querySelectorAll('.error-message').forEach(el => el.classList.remove('show'));
        document.querySelectorAll('.form-input').forEach(el => el.classList.remove('error'));
    }
    
    function showSuccessModal() {
        successModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    function hideSuccessModal() {
        successModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    function showErrorModal() {
        errorModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    function hideErrorModal() {
        errorModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    function showSuccess(title, message) {
        document.getElementById('successTitle').textContent = title;
        document.getElementById('successMessage').textContent = message;
        showSuccessModal();
    }
    
    function showError(message) {
        document.getElementById('errorMessage').textContent = message;
        showErrorModal();
    }
    
    function setLoginButtonLoading(loading) {
        const button = document.getElementById('loginButton');
        const buttonText = button.querySelector('.button-text');
        const spinner = button.querySelector('.spinner');
        
        if (loading) {
            button.disabled = true;
            buttonText.style.display = 'none';
            spinner.style.display = 'block';
        } else {
            button.disabled = false;
            buttonText.style.display = 'inline-block';
            spinner.style.display = 'none';
        }
    }
    
    function setRegisterButtonLoading(loading) {
        const button = document.getElementById('registerButton');
        const buttonText = button.querySelector('.button-text');
        const spinner = button.querySelector('.spinner');
        
        if (loading) {
            button.disabled = true;
            buttonText.style.display = 'none';
            spinner.style.display = 'block';
        } else {
            button.disabled = false;
            buttonText.style.display = 'inline-block';
            spinner.style.display = 'none';
        }
    }
    
    // Verificar estado de autenticación
    function checkAuthStatus() {
        const token = localStorage.getItem('authToken');
        if (token) {
            // Verificar si el token es válido
            verifyToken(token);
        }
    }
    
    async function verifyToken(token) {
        try {
            const response = await fetch('/api/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: token })
            });
            
            const data = await response.json();
            
            if (data.success && data.valid) {
                isAuthenticated = true;
                currentUser = data.user;
                
                // Si ya está autenticado y está en login, redirigir
                if (window.location.pathname === '/login') {
                    window.location.href = '/dashboard';
                }
            } else {
                // Token inválido, limpiar
                localStorage.removeItem('authToken');
                isAuthenticated = false;
                currentUser = null;
            }
            
        } catch (error) {
            console.error('Error verificando token:', error);
            localStorage.removeItem('authToken');
            isAuthenticated = false;
            currentUser = null;
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

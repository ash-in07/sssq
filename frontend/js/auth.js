function initAuthPage() {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const forgotForm = document.getElementById('forgot-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = loginForm.email.value.trim();
      const password = loginForm.password.value.trim();
      const role = loginForm.role.value;
      const messageBox = document.getElementById('auth-message');
      if (!email || !password) {
        messageBox.textContent = 'Email and password are required.';
        messageBox.className = 'auth-error';
        return;
      }
      const response = await apiRequest('/auth/login', 'POST', { email, password, role });
      if (response.token) {
        localStorage.setItem('sqlMigratorToken', response.token);
        setUserInfo(response.user);
        window.location.href = role === 'Admin' ? '../pages/admin_dashboard.html' : '../pages/user_dashboard.html';
      } else {
        messageBox.textContent = response.message || 'Login failed.';
        messageBox.className = 'auth-error';
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fullname = registerForm.fullname.value.trim();
      const email = registerForm.email.value.trim();
      const password = registerForm.password.value.trim();
      const confirmPassword = registerForm.confirmPassword.value.trim();
      const role = registerForm.role.value;
      const messageBox = document.getElementById('auth-message');
      if (!fullname || !email || !password) {
        messageBox.textContent = 'All fields are required.';
        messageBox.className = 'auth-error';
        return;
      }
      if (password !== confirmPassword) {
        messageBox.textContent = 'Passwords do not match.';
        messageBox.className = 'auth-error';
        return;
      }
      const response = await apiRequest('/auth/register', 'POST', { fullname, email, password, role });
      messageBox.textContent = response.message || 'Registration complete.';
      messageBox.className = 'auth-success';
      registerForm.reset();
    });
  }

  if (forgotForm) {
    forgotForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = forgotForm.email.value.trim();
      const messageBox = document.getElementById('auth-message');
      if (!email) {
        messageBox.textContent = 'Email is required.';
        messageBox.className = 'auth-error';
        return;
      }
      const response = await apiRequest('/auth/forgot-password', 'POST', { email });
      messageBox.textContent = response.message || 'Password reset link sent.';
      messageBox.className = 'auth-success';
      forgotForm.reset();
    });
  }
}

function loadSharedComponent(componentName, callback) {
  return fetch(`../components/${componentName}.html`)
    .then((response) => response.text())
    .then((html) => {
      const container = document.getElementById(`${componentName}-container`);
      if (container) {
        container.innerHTML = html;
        if (typeof callback === 'function') callback();
      }
    })
    .catch(() => {
      console.warn(`Unable to load ${componentName} component.`);
    });
}

function showNotification(message, type = 'success') {
  const notice = document.createElement('div');
  notice.className = `notification notification-${type}`;
  notice.textContent = message;
  document.body.appendChild(notice);
  setTimeout(() => notice.classList.add('visible'), 10);
  setTimeout(() => notice.classList.remove('visible'), 3200);
  setTimeout(() => notice.remove(), 3600);
}

function navigateToPage(path) {
  window.location.href = path;
}

function isLoggedIn() {
  return Boolean(getAuthToken());
}

function requireAuth(role = null) {
  const user = getUserInfo();
  if (!isLoggedIn() || !user) {
    window.location.href = '../pages/login.html';
    return false;
  }
  if (role && user.role !== role) {
    if (user.role === 'Admin') window.location.href = '../pages/admin_dashboard.html';
    else window.location.href = '../pages/user_dashboard.html';
    return false;
  }
  return true;
}

function buildSidebarLinks(role) {
  const nav = document.querySelector('.sidebar-nav');
  if (!nav) return;
  const adminLinks = [
    { label: 'Dashboard', path: '../pages/admin_dashboard.html', icon: '🏠' },
    { label: 'Users', path: '../pages/users.html', icon: '👥' },
    { label: 'Migration History', path: '../pages/migration_history.html', icon: '📜' },
    { label: 'Reports', path: '../pages/reports.html', icon: '📊' },
    { label: 'Settings', path: '../pages/settings.html', icon: '⚙️' },
  ];
  const userLinks = [
    { label: 'Dashboard', path: '../pages/user_dashboard.html', icon: '🏠' },
    { label: 'Migration', path: '../pages/migration.html', icon: '🔄' },
    { label: 'Migration History', path: '../pages/migration_history.html', icon: '📜' },
    { label: 'Reports', path: '../pages/reports.html', icon: '📊' },
    { label: 'About', path: '../pages/about.html', icon: 'ℹ️' },
    { label: 'Settings', path: '../pages/settings.html', icon: '⚙️' },
  ];
  const links = role === 'Admin' ? adminLinks : userLinks;
  nav.innerHTML = links
    .map((item) => `
      <a href="${item.path}" class="sidebar-link" data-path="${item.path}">
        <span class="icon">${item.icon}</span>
        <span class="link-text">${item.label}</span>
      </a>
    `)
    .join('');

  highlightSidebarLink();
}

function highlightSidebarLink() {
  const currentPath = location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach((link) => {
    const targetPath = link.dataset.path;
    if (currentPath.endsWith(targetPath)) {
      link.classList.add('active');
    }
  });
}

function bindHeaderActions() {
  const profileButton = document.getElementById('profile-button');
  const profileMenu = document.getElementById('profile-menu');
  const themeToggle = document.getElementById('theme-toggle');
  const menuButton = document.getElementById('mobile-menu-button');
  const sidebar = document.querySelector('.sidebar');
  if (profileButton && profileMenu) {
    profileButton.addEventListener('click', () => profileMenu.classList.toggle('open'));
    document.addEventListener('click', (event) => {
      if (!profileButton.contains(event.target) && !profileMenu.contains(event.target)) {
        profileMenu.classList.remove('open');
      }
    });
  }
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      showNotification('Theme updated', 'success');
    });
  }
  if (menuButton && sidebar) {
    menuButton.addEventListener('click', () => sidebar.classList.toggle('open'));
  }
}

function bindLogout() {
  const logout = document.getElementById('logout-link');
  if (!logout) return;
  logout.addEventListener('click', (event) => {
    event.preventDefault();
    clearAuth();
    window.location.href = '../pages/login.html';
  });
}

function setProfileSummary() {
  const user = getUserInfo();
  if (!user) return;
  const profileName = document.querySelector('.profile-name');
  const profileRole = document.querySelector('.profile-role');
  if (profileName) profileName.textContent = user.name || 'Guest';
  if (profileRole) profileRole.textContent = user.role || 'User';
}

function mapDatabaseOptions() {
  return [
    { value: 'mysql', label: 'MySQL' },
    { value: 'postgres', label: 'PostgreSQL' },
    { value: 'oracle', label: 'Oracle' },
    { value: 'sqlite', label: 'SQLite' },
    { value: 'sqlserver', label: 'SQL Server' },
  ];
}

function injectDatabaseOptions(elementId) {
  const select = document.getElementById(elementId);
  if (!select) return;
  select.innerHTML = mapDatabaseOptions()
    .map((item) => `<option value="${item.value}">${item.label}</option>`)
    .join('');
}

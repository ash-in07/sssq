function initUsersPage() {
  if (!requireAuth('Admin')) return;
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();
  const headerTitle = document.getElementById('page-title');
  if (headerTitle) headerTitle.textContent = 'Users';
  renderUserMetrics();
  renderUserTable();
}

async function renderUserTable() {
  const response = await apiRequest('/users', 'GET');
  const rows = response.users || [];
  const tableBody = document.getElementById('users-table-body');
  if (!tableBody) return;
  tableBody.innerHTML = rows
    .map((user) => `
      <tr>
        <td>${user.name}</td>
        <td>${user.email}</td>
        <td>${user.role}</td>
        <td>${user.status}</td>
        <td>${user.migrations}</td>
        <td>${user.lastLogin}</td>
        <td><button class="button-secondary">View</button></td>
      </tr>
    `)
    .join('');
}

function renderUserMetrics() {
  const stats = {
    totalUsers: 241,
    activeUsers: 187,
    adminUsers: 25,
    inactiveUsers: 12,
  };
  const container = document.getElementById('users-metrics');
  if (!container) return;
  container.innerHTML = `
    <div class="card metric-card"><h3>Total Users</h3><strong>${stats.totalUsers}</strong></div>
    <div class="card metric-card"><h3>Active Users</h3><strong>${stats.activeUsers}</strong></div>
    <div class="card metric-card"><h3>Admin Users</h3><strong>${stats.adminUsers}</strong></div>
    <div class="card metric-card"><h3>Inactive Users</h3><strong>${stats.inactiveUsers}</strong></div>
  `;
}

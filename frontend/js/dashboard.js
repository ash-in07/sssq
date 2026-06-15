function initDashboardPage() {
  if (!requireAuth()) return;
  const user = getUserInfo();
  document.title = user.role === 'Admin' ? 'Admin Dashboard | SQL Migrator' : 'Dashboard | SQL Migrator';
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();
  const headerTitle = document.getElementById('page-title');
  if (headerTitle) {
    headerTitle.textContent = user.role === 'Admin' ? 'Admin Dashboard' : 'User Dashboard';
  }

  const stats = {
    totalUsers: 241,
    activeUsers: 187,
    totalMigrations: 814,
    systemHealth: 'Stable',
    successful: 728,
    failed: 17,
    reports: 52,
  };

  const summaryContainer = document.getElementById('dashboard-summary');
  if (summaryContainer) {
    summaryContainer.innerHTML = `
      <div class="card metric-card"><h3>Total Migrations</h3><strong>${stats.totalMigrations}</strong></div>
      <div class="card metric-card"><h3>Successful</h3><strong>${stats.successful}</strong></div>
      <div class="card metric-card"><h3>Failed</h3><strong>${stats.failed}</strong></div>
      <div class="card metric-card"><h3>Reports Generated</h3><strong>${stats.reports}</strong></div>
    `;
  }

  const activityContainer = document.getElementById('recent-activity');
  if (activityContainer) {
    activityContainer.innerHTML = [
      { user: 'Daniel Park', action: 'Completed SQL to SQL migration', time: '2 hours ago' },
      { user: 'Priya Nair', action: 'Exported database to CSV', time: '4 hours ago' },
      { user: 'Sara Blake', action: 'Imported file to PostgreSQL', time: 'Yesterday' },
    ]
      .map((item) => `
      <div class="activity-item">
        <div>
          <strong>${item.user}</strong>
          <p class="small-text">${item.action}</p>
        </div>
        <span class="small-text">${item.time}</span>
      </div>
    `)
      .join('');
  }

  injectQuickActions();
  renderDashboardCharts();
}

function injectQuickActions() {
  const quickActions = document.getElementById('quick-actions');
  if (!quickActions) return;
  quickActions.innerHTML = `
    <button class="button-primary" onclick="window.location.href='../pages/migration.html'">New Migration</button>
    <button class="button-secondary" onclick="window.location.href='../pages/migration_history.html'">View History</button>
    <button class="button-secondary" onclick="window.location.href='../pages/reports.html'">Generate Report</button>
  `;
}

function renderDashboardCharts() {
  const trends = document.getElementById('migration-trends-chart');
  const activity = document.getElementById('user-activity-chart');
  const usage = document.getElementById('database-usage-chart');
  if (window.Chart) {
    if (trends) {
      new Chart(trends, {
        type: 'line',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Migrations',
            data: [45, 58, 52, 67, 53, 72, 68],
            borderColor: '#8B7CFF',
            backgroundColor: 'rgba(139,124,255,0.14)',
            tension: 0.35,
            fill: true,
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#9CA3AF' } },
            y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: '#9CA3AF' } },
          },
        },
      });
    }
    if (activity) {
      new Chart(activity, {
        type: 'bar',
        data: {
          labels: ['Users', 'Migrations', 'Reports'],
          datasets: [{
            label: 'This Week',
            data: [132, 94, 48],
            backgroundColor: ['#6366F1', '#22C55E', '#F59E0B'],
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#9CA3AF' } },
            y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: '#9CA3AF' } },
          },
        },
      });
    }
    if (usage) {
      new Chart(usage, {
        type: 'doughnut',
        data: {
          labels: ['MySQL', 'PostgreSQL', 'Oracle', 'SQLite'],
          datasets: [{
            data: [28, 34, 18, 20],
            backgroundColor: ['#8B7CFF', '#22C55E', '#F59E0B', '#EF4444'],
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom', labels: { color: '#9CA3AF' } } },
        },
      });
    }
  }
}

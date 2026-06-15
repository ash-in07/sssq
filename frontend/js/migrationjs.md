#frontend/js/migration.js
function initMigrationPage() {
  if (!requireAuth()) return;
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();
  const headerTitle = document.getElementById('page-title');
  if (headerTitle) headerTitle.textContent = 'Migration';

  const tabs = document.querySelectorAll('.migration-tab');
  const panels = document.querySelectorAll('.migration-panel');
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((item) => item.classList.remove('active'));
      panels.forEach((panel) => panel.classList.add('hidden'));
      tab.classList.add('active');
      document.getElementById(tab.dataset.target).classList.remove('hidden');
    });
  });

  injectDatabaseOptions('source-db-type');
  injectDatabaseOptions('target-db-type');
  injectDatabaseOptions('file-target-db-type');

  const sqlToSqlForm = document.getElementById('sql-to-sql-form');
  const sqlToFileForm = document.getElementById('sql-to-file-form');
  const fileToSqlForm = document.getElementById('file-to-sql-form');

  [sqlToSqlForm, sqlToFileForm, fileToSqlForm].forEach((form) => {
    if (!form) return;
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const action = form.dataset.action;
      const progress = document.getElementById('migration-progress-fill');
      const progressText = document.getElementById('migration-progress-status');
      const logs = document.getElementById('migration-logs');
      if (progress) progress.style.width = '0%';
      if (progressText) progressText.textContent = 'Pending';
      if (logs) logs.innerHTML = '<p class="log-line">Initializing migration...</p>';

      const endpointMap = {
  'sql-to-sql': '/migration/sql-to-sql',
  'sql-to-file': '/export/sql-to-file',
  'file-to-sql': '/import/file-to-sql',
};
      const response = await apiRequest(endpointMap[action], 'POST', { action });
      if (response.message) {
        if (logs) logs.innerHTML += `<p class="log-line">${response.message}</p>`;
      }
      simulateMigrationProgress();
    });
  });

  const uploadInput = document.getElementById('source-file');
  const filePreview = document.getElementById('file-preview');
  if (uploadInput && filePreview) {
    uploadInput.addEventListener('change', () => {
      const file = uploadInput.files[0];
      if (!file) return;
      filePreview.textContent = `Selected file: ${file.name}`;
    });
  }
}

function simulateMigrationProgress() {
  const progress = document.getElementById('migration-progress-fill');
  const progressText = document.getElementById('migration-progress-status');
  const logs = document.getElementById('migration-logs');
  let percentage = 0;
  const interval = setInterval(() => {
    percentage += Math.floor(Math.random() * 12) + 8;
    if (percentage > 100) percentage = 100;
    if (progress) progress.style.width = `${percentage}%`;
    if (progressText) progressText.textContent = percentage < 100 ? 'Running' : 'Completed';
    const progressNumber = document.getElementById('migration-progress-percentage');
    if (progressNumber) progressNumber.textContent = `${percentage}%`;
    if (logs) {
      logs.innerHTML += `<p class="log-line">${percentage}% completed... checking connection and migrating rows.</p>`;
      logs.scrollTop = logs.scrollHeight;
    }
    if (percentage >= 100) {
      clearInterval(interval);
      if (logs) logs.innerHTML += '<p class="log-line status-success">Migration completed successfully.</p>';
    }
  }, 700);
}

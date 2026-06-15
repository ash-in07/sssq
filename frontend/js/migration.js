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

  // NOTE: Do NOT call injectDatabaseOptions here — the HTML already has
  // the correct <option> values (mysql, postgres, sqlite, etc.) that match
  // what the backend connection_manager expects.

  const sqlToSqlForm = document.getElementById('sql-to-sql-form');
  const sqlToFileForm = document.getElementById('sql-to-file-form');
  const fileToSqlForm = document.getElementById('file-to-sql-form');

  // --- SQL to SQL ---
  if (sqlToSqlForm) {
    sqlToSqlForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      resetProgress();
      appendLog('Collecting connection details...');

      const payload = {
        source_db_type: getVal('source-db-type'),
        source_host: getVal('source-host'),
        source_port: getVal('source-port'),
        source_username: getVal('source-username'),
        source_password: getVal('source-password'),
        source_database: getVal('source-db-name'),
        target_db_type: getVal('target-db-type'),
        target_host: getVal('target-host'),
        target_port: getVal('target-port'),
        target_username: getVal('target-username'),
        target_password: getVal('target-password'),
        target_database: getVal('target-db-name'),
        tables: getVal('sql-tables') ? getVal('sql-tables').split(',').map(s => s.trim()) : [],
      };

      appendLog(`Connecting to source (${payload.source_db_type}://${payload.source_host})...`);
      const response = await apiRequest('/migration/sql-to-sql', 'POST', payload);
      handleMigrationResponse(response);
    });
  }

  // --- SQL to File ---
  if (sqlToFileForm) {
    sqlToFileForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      resetProgress();
      appendLog('Preparing export...');

      const payload = {
        source_db_type: getVal('export-db-type'),
        source_host: getVal('export-host'),
        source_port: getVal('export-port'),
        source_username: getVal('export-username'),
        source_password: getVal('export-password'),
        source_database: getVal('export-db-name'),
        source_table: getVal('export-table-name'),
        export_format: getVal('export-format'),
        columns: getVal('export-columns') ? getVal('export-columns').split(',').map(s => s.trim()) : [],
      };

      appendLog(`Exporting from ${payload.source_db_type}...`);
      const response = await apiRequest('/export/sql-to-file', 'POST', payload);
      handleMigrationResponse(response);
    });
  }

  // --- File to SQL ---
  if (fileToSqlForm) {
    fileToSqlForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      resetProgress();
      appendLog('Preparing file import...');

      const fileInput = document.getElementById('source-file');
      const file = fileInput ? fileInput.files[0] : null;

      if (!file) {
        appendLog('<span class="status-error">Please select a file to import.</span>');
        return;
      }

      const ext = file.name.split('.').pop().toLowerCase();
      const isSqlDump = ext === 'sql';

      appendLog(`Detected file type: <strong>.${ext}</strong>${isSqlDump ? ' (SQL dump — executing directly)' : ' (tabular — importing via pandas)'}`);

      const payload = new FormData();
      payload.append('file', file);
      payload.append('target_db_type', getVal('file-target-db-type'));
      payload.append('target_host', getVal('file-target-host'));
      payload.append('target_port', getVal('file-target-port'));
      payload.append('target_username', getVal('file-target-username'));
      payload.append('target_password', getVal('file-target-password'));
      payload.append('target_database', getVal('file-target-db-name'));

      if (!isSqlDump) {
        payload.append('target_table', getVal('file-target-table'));
      }
      payload.append('if_exists', getVal('file-if-exists'));

      appendLog(`Importing to ${payload.get('target_db_type')}...`);
      const response = await apiRequest('/import/file-to-sql', 'POST', payload);
      handleMigrationResponse(response);
    });
  }

  // File upload preview + drag-and-drop
  bindFileUploader();

  // Test Connection buttons
  bindTestConnections();
}

/* ---------- File Uploader ---------- */
function bindFileUploader() {
  const uploadInput = document.getElementById('source-file');
  const filePreview = document.getElementById('file-preview');
  const dropZone = document.getElementById('drop-zone');

  if (!uploadInput) return;

  uploadInput.addEventListener('change', () => {
    const file = uploadInput.files[0];
    updateFilePreview(file, filePreview);
  });

  if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });

    ['dragleave', 'dragend'].forEach(evt =>
      dropZone.addEventListener(evt, () => dropZone.classList.remove('drag-over'))
    );

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file) {
        // Transfer the dropped file to the file input
        const dt = new DataTransfer();
        dt.items.add(file);
        uploadInput.files = dt.files;
        updateFilePreview(file, filePreview);
      }
    });
  }
}

function updateFilePreview(file, previewEl) {
  if (!file || !previewEl) return;
  const ext = file.name.split('.').pop().toLowerCase();
  const sizeKB = (file.size / 1024).toFixed(1);
  const typeLabel = ext === 'sql' ? '🗄 SQL Dump' : ext === 'csv' ? '📄 CSV' : ext === 'json' ? '📋 JSON' : '📊 Excel';
  previewEl.innerHTML = `${typeLabel} &nbsp;·&nbsp; <strong>${file.name}</strong> &nbsp;·&nbsp; ${sizeKB} KB`;
}

/* ---------- Test Connection ---------- */

/**
 * Configuration map: button id → {statusId, fields to read}
 */
const _TEST_CONN_CONFIGS = [
  {
    btnId: 'test-conn-source',
    statusId: 'conn-status-source',
    fields: {
      db_type: 'source-db-type',
      host: 'source-host',
      port: 'source-port',
      username: 'source-username',
      password: 'source-password',
      database: 'source-db-name',
    },
  },
  {
    btnId: 'test-conn-target',
    statusId: 'conn-status-target',
    fields: {
      db_type: 'target-db-type',
      host: 'target-host',
      port: 'target-port',
      username: 'target-username',
      password: 'target-password',
      database: 'target-db-name',
    },
  },
  {
    btnId: 'test-conn-export',
    statusId: 'conn-status-export',
    fields: {
      db_type: 'export-db-type',
      host: 'export-host',
      port: 'export-port',
      username: 'export-username',
      password: 'export-password',
      database: 'export-db-name',
    },
  },
  {
    btnId: 'test-conn-file-target',
    statusId: 'conn-status-file-target',
    fields: {
      db_type: 'file-target-db-type',
      host: 'file-target-host',
      port: 'file-target-port',
      username: 'file-target-username',
      password: 'file-target-password',
      database: 'file-target-db-name',
    },
  },
];

function bindTestConnections() {
  _TEST_CONN_CONFIGS.forEach(({ btnId, statusId, fields }) => {
    const btn = document.getElementById(btnId);
    const statusEl = document.getElementById(statusId);
    if (!btn || !statusEl) return;

    btn.addEventListener('click', async () => {
      // Build payload from the card's fields
      const payload = {};
      for (const [key, fieldId] of Object.entries(fields)) {
        payload[key] = getVal(fieldId);
      }

      // Show spinner
      setConnStatus(statusEl, 'loading', 'Testing…');
      btn.disabled = true;

      try {
        const response = await apiRequest('/test-connection', 'POST', payload);
        if (response && response.status === 'ok') {
          setConnStatus(statusEl, 'ok', `✅ Connected`);
        } else {
          const msg = (response && response.message) ? response.message : 'Connection failed.';
          setConnStatus(statusEl, 'error', `❌ ${truncate(msg, 80)}`);
        }
      } catch (err) {
        setConnStatus(statusEl, 'error', '❌ Network error');
      } finally {
        btn.disabled = false;
      }
    });
  });
}

function setConnStatus(el, state, message) {
  el.className = 'conn-status' + (state ? ` conn-status--${state}` : '');
  el.innerHTML = message;
}

/* ---------- Helpers ---------- */

function getVal(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

function truncate(str, max) {
  return str.length > max ? str.slice(0, max) + '…' : str;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function resetProgress() {
  const progress = document.getElementById('migration-progress-fill');
  const progressText = document.getElementById('migration-progress-status');
  const logs = document.getElementById('migration-logs');
  if (progress) { progress.style.width = '0%'; progress.style.background = ''; }
  if (progressText) progressText.textContent = 'Pending';
  const pct = document.getElementById('migration-progress-percentage');
  if (pct) pct.textContent = '0%';
  if (logs) logs.innerHTML = '<p class="log-line">Initializing migration...</p>';
}

function appendLog(message) {
  const logs = document.getElementById('migration-logs');
  if (logs) {
    logs.innerHTML += `<p class="log-line">${message}</p>`;
    logs.scrollTop = logs.scrollHeight;
  }
}

function handleMigrationResponse(response) {
  // Backend error responses come in two forms:
  // 1. { "message": "Migration failed.", "error": "..." } (500 errors)
  // 2. { "message": "source_table is required." } (400 errors — no `error` key)
  const isError = response.error
    || (!response.report && !response.result && response.message &&
        /required|failed|error|not found|invalid|denied|placeholder/i.test(response.message));

  if (isError) {
    const errorDetail = response.error || response.message || 'Unknown error';
    appendLog(`<span class="status-error">Error: ${escapeHtml(errorDetail)}</span>`);
    const progressText = document.getElementById('migration-progress-status');
    if (progressText) progressText.textContent = 'Failed';
    const progress = document.getElementById('migration-progress-fill');
    if (progress) { progress.style.width = '100%'; progress.style.background = '#ef4444'; }
    const pct = document.getElementById('migration-progress-percentage');
    if (pct) pct.textContent = '100%';
  } else {
    if (response.message) appendLog(response.message);
    simulateMigrationProgress(response);
  }
}

function simulateMigrationProgress(response) {
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
      if (logs) {
        const isImport = response && response.result && (response.result.import_type === 'sql_dump' || response.result.rows_imported != null);
        const isExport = response && response.result && response.result.filename != null && response.result.rows_exported != null;
        const actionWord = isImport ? 'Import' : (isExport ? 'Export' : 'Migration');
        logs.innerHTML += `<p class="log-line status-success">${actionWord} completed successfully.</p>`;
      }
      // Show extra details for successful imports or exports
      if (response && response.result) {
        const r = response.result;
        if (r.import_type === 'sql_dump') {
          appendLog(`✅ SQL dump executed: <strong>${r.statements_executed}</strong> statements, <strong>${r.statements_skipped}</strong> skipped.`);
          if (r.target_database) {
            appendLog(`Target Database: <code>${escapeHtml(r.target_database)}</code>`);
          }
        } else if (r.rows_imported != null) {
          appendLog(`✅ Imported <strong>${r.rows_imported}</strong> rows into <code>${r.table_name}</code>.`);
          if (r.target_database) {
            appendLog(`Target Database: <code>${escapeHtml(r.target_database)}</code>`);
          }
          if (r.schema_sql) {
            appendLog(`<details><summary style="cursor:pointer;color:var(--accent)">View generated schema SQL</summary><pre style="margin-top:8px;overflow:auto">${escapeHtml(r.schema_sql)}</pre></details>`);
          }
        } else if (r.filename != null && r.rows_exported != null) {
          appendLog(`✅ Exported <strong>${r.rows_exported}</strong> rows from <code>${r.table_name}</code> to <strong>${r.export_format.toUpperCase()}</strong>.`);
          appendLog(`📥 Starting download: <code>${escapeHtml(r.filename)}</code>...`);
          
          // Programmatic download trigger
          const downloadUrl = `${API_BASE_URL}/export/download/${encodeURIComponent(r.filename)}`;
          const a = document.createElement('a');
          a.href = downloadUrl;
          a.download = r.filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      }
    }
  }, 700);
}

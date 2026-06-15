#frontend/pages/migration.html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Migration | SQL Migrator</title>
  <link rel="stylesheet" href="../css/global.css" />
  <link rel="stylesheet" href="../css/sidebar.css" />
  <link rel="stylesheet" href="../css/migration.css" />
</head>
<body>
  <!-- Dynamic Sidebar Container -->
  <div id="sidebar-container"></div>

  <!-- PAGE CONTENT -->
  <div class="page-content">
    <header class="page-header">
      <div class="header-content">
        <h1>SQL Migrator</h1>
        <p>Database Migration & Management Platform</p>
      </div>
    </header>
    <main class="content-inner migration-shell">

      <!-- TABS -->
      <div class="migration-tabs" role="tablist" aria-label="Migration modes">
        <button class="migration-tab active" data-target="sql-to-sql-panel" role="tab">SQL to SQL</button>
        <button class="migration-tab" data-target="sql-to-file-panel" role="tab">SQL to File</button>
        <button class="migration-tab" data-target="file-to-sql-panel" role="tab">File to SQL</button>
      </div>

      <!-- SQL TO SQL -->
      <div id="sql-to-sql-panel" class="migration-panel">
        <div class="panel-grid">
          <div class="connection-card">
            <h3>Source SQL Connection</h3>
            <div class="input-group">
              <label for="source-db-type">Database Type</label>
              <select id="source-db-type">
                <option value="mysql">MySQL</option>
                <option value="postgres">PostgreSQL</option>
                <option value="sqlite">SQLite</option>
                <option value="sqlserver">SQL Server</option>
                <option value="oracle">Oracle</option>
                <option value="other">Other / Generic</option>
              </select>
            </div>
            <div class="input-group">
              <label for="source-host">Host</label>
              <input id="source-host" type="text" placeholder="127.0.0.1" />
            </div>
            <div class="input-group">
              <label for="source-port">Port</label>
              <input id="source-port" type="text" placeholder="3306" />
            </div>
            <div class="input-group">
              <label for="source-db-name">Database Name</label>
              <input id="source-db-name" type="text" placeholder="example_db" />
            </div>
            <div class="input-group">
              <label for="source-username">Username</label>
              <input id="source-username" type="text" placeholder="db_user" />
            </div>
            <div class="input-group">
              <label for="source-password">Password</label>
              <input id="source-password" type="password" placeholder="••••••••" />
            </div>
            <button class="button-secondary">Test Connection</button>
          </div>

          <div class="connection-card">
            <h3>Target SQL Connection</h3>
            <div class="input-group">
              <label for="target-db-type">Database Type</label>
              <select id="target-db-type">
                <option value="postgres">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="sqlite">SQLite</option>
                <option value="sqlserver">SQL Server</option>
                <option value="oracle">Oracle</option>
                <option value="other">Other / Generic</option>
              </select>
            </div>
            <div class="input-group">
              <label for="target-host">Host</label>
              <input id="target-host" type="text" placeholder="127.0.0.1" />
            </div>
            <div class="input-group">
              <label for="target-port">Port</label>
              <input id="target-port" type="text" placeholder="5432" />
            </div>
            <div class="input-group">
              <label for="target-db-name">Database Name</label>
              <input id="target-db-name" type="text" placeholder="example_db" />
            </div>
            <div class="input-group">
              <label for="target-username">Username</label>
              <input id="target-username" type="text" placeholder="db_user" />
            </div>
            <div class="input-group">
              <label for="target-password">Password</label>
              <input id="target-password" type="password" placeholder="••••••••" />
            </div>
            <button class="button-secondary">Test Connection</button>
          </div>
        </div>
        <form id="sql-to-sql-form" data-action="sql-to-sql" class="action-row">
          <button type="submit" class="button-primary">Run Migration</button>
        </form>
      </div>

      <!-- SQL TO FILE -->
      <div id="sql-to-file-panel" class="migration-panel hidden">
        <div class="panel-grid">
          <div class="connection-card">
            <h3>Source Database</h3>
            <div class="input-group">
              <label for="export-db-type">Database Type</label>
              <select id="export-db-type">
                <option value="mysql">MySQL</option>
                <option value="postgres">PostgreSQL</option>
                <option value="sqlite">SQLite</option>
                <option value="sqlserver">SQL Server</option>
                <option value="oracle">Oracle</option>
                <option value="other">Other / Generic</option>
              </select>
            </div>
            <div class="input-group">
              <label for="export-host">Host</label>
              <input id="export-host" type="text" />
            </div>
            <div class="input-group">
              <label for="export-port">Port</label>
              <input id="export-port" type="text" />
            </div>
            <div class="input-group">
              <label for="export-db-name">Database Name</label>
              <input id="export-db-name" type="text" />
            </div>
            <div class="input-group">
              <label for="export-username">Username</label>
              <input id="export-username" type="text" />
            </div>
            <div class="input-group">
              <label for="export-password">Password</label>
              <input id="export-password" type="password" />
            </div>
            <button class="button-secondary">Test Connection</button>
          </div>

          <div class="connection-card">
            <h3>Output Format</h3>
            <div class="input-group">
              <label for="export-format">Format</label>
              <select id="export-format">
                <option>CSV</option>
                <option>JSON</option>
                <option>Excel</option>
              </select>
            </div>
            <p class="small-text">Select the target export format and run the export.</p>
          </div>
        </div>
        <form id="sql-to-file-form" data-action="sql-to-file" class="action-row">
          <button type="submit" class="button-primary">Export Data</button>
        </form>
      </div>

      <!-- FILE TO SQL -->
      <div id="file-to-sql-panel" class="migration-panel hidden">
        <div class="panel-grid">
          <div class="connection-card file-uploader">
            <h3>File Upload</h3>
            <div class="uploader-box" aria-label="File drop zone">
              <p>Drag and drop your CSV, JSON or Excel file here</p>
              <p>or</p>
              <input id="source-file" type="file" accept=".csv,.json,.xlsx,.xls" />
            </div>
            <p id="file-preview" class="small-text">No file selected.</p>
          </div>

          <div class="connection-card">
            <h3>Target Database</h3>
            <div class="input-group">
              <label for="file-target-db-type">Database Type</label>
              <select id="file-target-db-type">
                <option value="mysql">MySQL</option>
                <option value="postgres">PostgreSQL</option>
                <option value="sqlite">SQLite</option>
                <option value="sqlserver">SQL Server</option>
                <option value="oracle">Oracle</option>
                <option value="other">Other / Generic</option>
              </select>
            </div>
            <div class="input-group">
              <label for="file-target-host">Host</label>
              <input id="file-target-host" type="text" />
            </div>
            <div class="input-group">
              <label for="file-target-port">Port</label>
              <input id="file-target-port" type="text" />
            </div>
            <div class="input-group">
              <label for="file-target-db-name">Database Name</label>
              <input id="file-target-db-name" type="text" />
            </div>
            <div class="input-group">
              <label for="file-target-username">Username</label>
              <input id="file-target-username" type="text" />
            </div>
            <div class="input-group">
              <label for="file-target-password">Password</label>
              <input id="file-target-password" type="password" />
            </div>
            <button class="button-secondary">Test Connection</button>
          </div>
        </div>
        <form id="file-to-sql-form" data-action="file-to-sql" class="action-row">
          <button type="submit" class="button-primary">Import To Database</button>
        </form>
      </div>

      <!-- PROGRESS -->
      <section class="progress-panel">
        <h3>Migration Progress</h3>
        <p class="small-text">Track live status and view logs in real time.</p>
        <div class="progress-bar">
          <div id="migration-progress-fill" class="progress-fill"></div>
        </div>
        <div class="progress-meta">
          <span id="migration-progress-status">Pending</span>
          <span id="migration-progress-percentage">0%</span>
        </div>
        <div id="migration-logs" class="log-console" aria-live="polite"></div>
      </section>

    </main>
  </div>

  <script src="../js/api.js"></script>
  <script src="../js/utils.js"></script>
  <script src="../js/sidebar.js"></script>
  <script src="../js/migration.js"></script>
  <script>
    // Initialize page with common components
    if (typeof initSidebar === 'function') initSidebar();
    if (typeof loadSharedComponent === 'function') {
      loadSharedComponent('header', () => {
        if (typeof setProfileSummary === 'function') setProfileSummary();
      });
    }
    if (typeof initMigrationPage === 'function') initMigrationPage();

    // Tab switching
    document.querySelectorAll('.migration-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.migration-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.migration-panel').forEach(p => p.classList.add('hidden'));
        tab.classList.add('active');
        const target = document.getElementById(tab.dataset.target);
        if (target) target.classList.remove('hidden');
      });
    });
  </script>
</body>
</html>

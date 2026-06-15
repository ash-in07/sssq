/* reports.js - Updated to fetch real data, handle loading, errors, and CRUD operations */

function initReportsPage() {
  if (!requireAuth()) return;
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();

  const headerTitle = document.getElementById('page-title');
  if (headerTitle) headerTitle.textContent = 'Reports';

  // Bind action buttons
  document.querySelector('.report-actions')?.addEventListener('click', (e) => {
    if (e.target.matches('.button-primary')) {
      openCreateReportModal();
    } else if (e.target.matches('.button-secondary')) {
      // Assuming the second button is Refresh
      refreshReports();
    }
  });

  // Initial load
  refreshReports();
}

/** Fetch reports and update both summary stats and table */
async function refreshReports() {
  const container = document.getElementById('report-summary');
  const tableBody = document.getElementById('reports-table-body');
  if (!container || !tableBody) return;

  // Show loading placeholders
  container.innerHTML = `<div class="spinner">Loading...</div>`;
  tableBody.innerHTML = `<tr><td colspan="6" class="loading-cell">Loading reports...</td></tr>`;

  try {
    const response = await apiRequest('/reports', 'GET');
    const reports = response.reports || [];
    renderReportSummary(reports);
    renderReportTable(reports);
  } catch (err) {
    console.error('Failed to load reports:', err);
    container.innerHTML = `<p class="error">Unable to load report statistics.</p>`;
    tableBody.innerHTML = `<tr><td colspan="6" class="error">Failed to load reports.</td></tr>`;
    showNotification('Failed to load reports', 'error');
  }
}

/** Compute and render the dashboard statistics based on the reports list */
function renderReportSummary(reports) {
  const totalReports = reports.length;
  const today = new Date().toISOString().split('T')[0];
  const generatedToday = reports.filter(r => r.date === today).length;
  const pdfReports = reports.filter(r => r.type?.toUpperCase() === 'PDF').length;
  const jsonReports = reports.filter(r => r.type?.toUpperCase() === 'JSON').length;

  const container = document.getElementById('report-summary');
  if (!container) return;
  container.innerHTML = `
    <div class="card metric-card"><h3>Total Reports</h3><strong>${totalReports}</strong></div>
    <div class="card metric-card"><h3>Generated Today</h3><strong>${generatedToday}</strong></div>
    <div class="card metric-card"><h3>PDF Reports</h3><strong>${pdfReports}</strong></div>
    <div class="card metric-card"><h3>JSON Reports</h3><strong>${jsonReports}</strong></div>
  `;
}

/** Render the reports table; show empty-state if none */
function renderReportTable(reports) {
  const tableBody = document.getElementById('reports-table-body');
  if (!tableBody) return;

  if (!reports || reports.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="6" class="empty-state">No reports found.</td></tr>`;
    return;
  }

  tableBody.innerHTML = reports
    .map((report) => `
      <tr>
        <td>${report.name}</td>
        <td>${report.type}</td>
        <td>${report.generatedBy}</td>
        <td>${report.date}</td>
        <td><span class="status-pill status-success">${report.status}</span></td>
        <td>
          <button class="button-secondary" data-id="${report.id}" data-action="view">View</button>
          <button class="button-secondary" data-id="${report.id}" data-action="download">Download</button>
        </td>
      </tr>
    `)
    .join('');

  // Attach row action listeners
  tableBody.querySelectorAll('button').forEach((btn) => {
    btn.addEventListener('click', handleReportAction);
  });
}

/** Handle view/download actions from the table */
function handleReportAction(event) {
  const btn = event.currentTarget;
  const reportId = btn.dataset.id;
  const action = btn.dataset.action;
  if (action === 'view') {
    // Placeholder: implement view logic (e.g., open modal with details)
    showNotification(`Viewing report #${reportId}`);
  } else if (action === 'download') {
    // Placeholder: implement download logic (e.g., fetch file blob)
    showNotification(`Downloading report #${reportId}`);
  }
}

/** Open a simple modal/form to create a new report */
function openCreateReportModal() {
  // For simplicity, use a prompt. In production, replace with proper modal UI.
  const name = prompt('Report Name:');
  if (!name) return;
  const type = prompt('Report Type (PDF/JSON):', 'PDF');
  if (!type) return;
  const generatedBy = getUserInfo()?.name || 'Unknown';

  const payload = {
    name,
    type: type.toUpperCase(),
    generatedBy,
  };

  // Send to backend (assumes POST /reports creates a report)
  apiRequest('/reports', 'POST', payload)
    .then((resp) => {
      if (resp.message) {
        showNotification('Report created successfully');
      }
      // Refresh list to reflect new entry
      refreshReports();
    })
    .catch((err) => {
      console.error('Create report failed:', err);
      showNotification('Failed to create report', 'error');
    });
}

/* End of reports.js */

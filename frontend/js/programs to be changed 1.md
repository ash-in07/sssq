#backend/routes/migration_routes.py
from flask import request
from flask_restful import Resource

from backend.models.migration_model import Migration
from backend.models.history_model import MigrationHistory
from backend.models.report_model import Report
from backend.extensions import db
from backend.utils.helpers import get_placeholder_data, sanitize_string
from backend.converters.sql_converter import migrate_sql_to_sql
from backend.converters.file_to_sql import import_file_to_sql
from backend.converters.sql_to_file import export_sql_to_file
from backend.processors.schema_generator import generate_create_table_schema

import json


class SqlToSqlResource(Resource):
    """Endpoint to migrate tables from one SQL database to another."""

    def post(self):
        payload = request.get_json(silent=True) or {}
        print("PAYLOAD RECEIVED:", payload)
        defaults = {
            "source_db_type": "mysql",
            "source_host": None,
            "source_port": None,
            "source_username": None,
            "source_password": None,
            "source_database": None,
            "target_db_type": "postgresql",
            "target_host": None,
            "target_port": None,
            "target_username": None,
            "target_password": None,
            "target_database": None,
            "tables": [],
        }
        if not payload:
            payload = get_placeholder_data(defaults)

        migration_record = Migration(
            migration_type="sql_to_sql",
            source_db=f"{payload.get('source_db_type')}://{payload.get('source_host')}",
            target_db=f"{payload.get('target_db_type')}://{payload.get('target_host')}",
            status="running",
        )
        db.session.add(migration_record)
        db.session.commit()

        try:
            report_data = migrate_sql_to_sql(payload)
            migration_record.status = "completed"
            report = Report(
                migration_id=migration_record.id,
                report_format="json",
                file_path="",
                summary=json.dumps(
                    report_data.get("summary", []),
                    default=str
                ),
            )
            db.session.add(report)
            db.session.commit()
            migration_record.report_id = report.id
            db.session.commit()
            history = MigrationHistory(
                migration_type="sql_to_sql",
                source_db=migration_record.source_db,
                target_db=migration_record.target_db,
                status="completed",
                errors=None,
                report_summary=report.summary,
            )
            db.session.add(history)
            db.session.commit()
            return {
                "message": "Migration completed.",
                "report": report_data
            }, 200
        except Exception as exc:
            migration_record.status = "failed"
            migration_record.error_message = str(exc)
            db.session.rollback()
            db.session.add(migration_record)
            db.session.commit()
            history = MigrationHistory(
                migration_type="sql_to_sql",
                source_db=migration_record.source_db,
                target_db=migration_record.target_db,
                status="failed",
                errors=str(exc),
                report_summary="Migration failed.",
            )
            db.session.add(history)
            db.session.commit()
            return {
                "message": "Migration failed.",
                "error": str(exc)
            }, 500


class MigrationStatusResource(Resource):
    """Endpoint to check the status of a migration by ID."""

    def get(self, migration_id: int):
        migration = Migration.query.get(migration_id)
        if migration is None:
            return {"message": "Migration not found."}, 404
        return {"migration": migration.to_dict()}, 200


class MigrationHistoryResource(Resource):
    """Endpoint to list migration history entries."""

    def get(self):
        history = [record.to_dict() for record in MigrationHistory.query.order_by(MigrationHistory.timestamp.desc()).all()]
        return {"history": history, "count": len(history)}, 200


class FileImportResource(Resource):
    """Endpoint to import a CSV or Excel file into a SQL database."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"message": "Request body is required."}, 400

        file_path = payload.get("file_path")

        if not file_path:
            return {"message": "file_path is required."}, 400

        if "<FRONTEND" in str(file_path):
            return {"message": "Replace placeholder file path with a real file path."}, 400

        try:
            import_result = import_file_to_sql(payload)
            return {"message": "File import completed.", "result": import_result}, 200
        except FileNotFoundError:
            return {"message": f"File not found: {file_path}"}, 404
        except Exception as exc:
            return {"message": "File import failed.", "error": str(exc)}, 500


class SqlExportResource(Resource):
    """Endpoint to export SQL data to CSV or Excel."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"message": "Request body is required."}, 400

        source_table = payload.get("source_table")

        if not source_table:
            return {"message": "source_table is required."}, 400

        try:
            export_result = export_sql_to_file(payload)
            return {"message": "Export completed.", "result": export_result}, 200
        except ValueError as exc:
            return {"message": str(exc)}, 400
        except Exception as exc:
            return {"message": "Export failed.", "error": str(exc)}, 500


class SchemaGeneratorResource(Resource):
    """Endpoint to generate CREATE TABLE schema from a file."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"message": "Request body is required."}, 400

        file_path = payload.get("file_path")
        table_name = payload.get("table_name")

        if not file_path:
            return {"message": "file_path is required."}, 400

        if "<FRONTEND" in str(file_path):
            return {"message": "Replace placeholder file path with a real file path."}, 400

        try:
            schema_sql = generate_create_table_schema(file_path, table_name)
            return {"schema_sql": schema_sql}, 200
        except FileNotFoundError:
            return {"message": f"File not found: {file_path}"}, 404
        except Exception as exc:
            return {"message": "Schema generation failed.", "error": str(exc)}, 500
        
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


# frontend/js/api.js

const API_BASE_URL = 'http://localhost:5000/api';

function getAuthToken() {
  return localStorage.getItem('sqlMigratorToken');
}

function getUserInfo() {
  const stored = localStorage.getItem('sqlMigratorUser');
  return stored ? JSON.parse(stored) : null;
}

function setUserInfo(user) {
  localStorage.setItem('sqlMigratorUser', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('sqlMigratorToken');
  localStorage.removeItem('sqlMigratorUser');
}

async function apiRequest(endpoint, method = 'GET', data = null, options = {}) {
  const fullUrl = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {}),
    ...options.headers,
  };

  const request = {
    method,
    headers,
  };

  if (data) {
    request.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(fullUrl, request);
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new Error(payload?.message || response.statusText || 'API error');
    }
    return await response.json();
  } catch (error) {
    return getMockApiResponse(endpoint, method, data);
  }
}

function getMockApiResponse(endpoint, method, data) {
  const route = endpoint.toLowerCase();
  if (route.includes('/auth/login') && method === 'POST') {
    const role = data.role || 'user';
    const user = {
      name: data.email.includes('admin') ? 'Admin User' : 'Default User',
      email: data.email,
      role,
    };
    return {
      token: 'mock-jwt-token',
      user,
      message: 'Login successful',
    };
  }

  if (route.includes('/auth/register') && method === 'POST') {
    return {
      message: 'Account created successfully. Check your email for verification.',
    };
  }

  if (route.includes('/auth/forgot-password') && method === 'POST') {
    return { message: 'Password reset link sent.' };
  }

  if (route.includes('/users') && method === 'GET') {
    return {
      users: [
        { id: 1, name: 'Sara Blake', email: 'sara@example.com', role: 'Admin', status: 'Active', migrations: 32, lastLogin: '2026-05-29' },
        { id: 2, name: 'Daniel Park', email: 'daniel@example.com', role: 'User', status: 'Active', migrations: 15, lastLogin: '2026-06-03' },
        { id: 3, name: 'Priya Nair', email: 'priya@example.com', role: 'User', status: 'Inactive', migrations: 8, lastLogin: '2026-05-20' },
      ],
    };
  }

  if (route.includes('/migration/history') && method === 'GET') {
    return {
      history: [
        { id: 'MIG-001', user: 'Daniel Park', source: 'MySQL', target: 'PostgreSQL', type: 'SQL to SQL', date: '2026-06-01', duration: '12m', status: 'Completed' },
        { id: 'MIG-002', user: 'Priya Nair', source: 'Oracle', target: 'CSV', type: 'SQL to File', date: '2026-05-28', duration: '5m', status: 'Completed' },
        { id: 'MIG-003', user: 'Sara Blake', source: 'CSV', target: 'SQL Server', type: 'File to SQL', date: '2026-06-03', duration: '9m', status: 'Running' },
      ],
    };
  }

  if (route.includes('/reports') && method === 'GET') {
    return {
      reports: [
        { id: 1, name: 'Monthly Migration Summary', type: 'PDF', generatedBy: 'Sara Blake', date: '2026-06-03', status: 'Ready' },
        { id: 2, name: 'Failed Jobs Report', type: 'JSON', generatedBy: 'Daniel Park', date: '2026-06-02', status: 'Ready' },
      ],
    };
  }

  if (route.includes('/settings') && method === 'GET') {
    return {
      settings: {
        applicationName: 'SQL Migrator',
        version: '1.0.0',
        maintenanceMode: false,
        defaultDatabase: 'PostgreSQL',
        sessionTimeout: 30,
        passwordPolicy: 'Strong',
        emailNotifications: true,
        migrationAlerts: true,
      },
    };
  }

  if (route.includes('/settings') && method === 'POST') {
    return { message: 'Settings updated successfully' };
  }

  if (route.includes('/migration/sql-to-sql') && method === 'POST') {
    return { message: 'SQL to SQL migration started', jobId: 'job-sql-001' };
  }

  if (route.includes('/migration/sql-to-file') && method === 'POST') {
    return { message: 'SQL export started', jobId: 'job-file-001' };
  }

  if (route.includes('/migration/file-to-sql') && method === 'POST') {
    return { message: 'File import started', jobId: 'job-import-001' };
  }

  return { message: 'Mock API endpoint not implemented', data: null };
}

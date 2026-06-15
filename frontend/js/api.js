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
  const isFormData = data instanceof FormData;

  const headers = {
    ...(getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {}),
    ...options.headers,
  };

  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  const request = {
    method,
    headers,
  };

  if (data) {
    request.body = isFormData ? data : JSON.stringify(data);
  }

  try {
    const response = await fetch(fullUrl, request);
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      return payload || { message: response.statusText || 'API error' };
    }
    return payload;
  } catch (error) {
    console.error('API request failed:', error);
    return { message: 'Cannot connect to server. Make sure the backend is running on ' + API_BASE_URL };
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

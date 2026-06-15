const S = {
  strictMode: false,
  autoEnum: false,
  backtick: false,
  autoMap: false,
  maxUpload: 250,
  timeout: 600,
  concurrent: 4,
  batchSize: 1000,
  allowSql: true,
  allowXlsx: true,
  allowCsv: true,
  users: [
    { id: 1, name: 'Sara Blake', email: 'sara@example.com', role: 'Admin' },
    { id: 2, name: 'Daniel Park', email: 'daniel@example.com', role: 'User' },
    { id: 3, name: 'Priya Nair', email: 'priya@example.com', role: 'Viewer' }
  ],
  _uid: 0,
  UPOOL: [
    { name: 'Aisha Khan', email: 'aisha@example.com', role: 'User' },
    { name: 'Tom Reed', email: 'tom@example.com', role: 'Viewer' },
    { name: 'Lina Wu', email: 'lina@example.com', role: 'Admin' }
  ],
  logFilter: 'All',
  logs: [
    { ts: '10:22:03', lv: 'INFO', m: 'Scheduled migration queue polled' },
    { ts: '10:23:17', lv: 'SUCCESS', m: 'Backup archive created' },
    { ts: '10:24:08', lv: 'WARN', m: 'Slow response from analytics DB' },
    { ts: '10:25:09', lv: 'ERROR', m: 'Failed to connect to remote host' }
  ],
  minPw: 8,
  pwExpiry: 90,
  twoFactor: true,
  deviceAlerts: true,
  reqUpper: true,
  reqNum: true,
  reqSym: false,
  sessionTO: 30,
  maxFail: 5,
  enforce2fa: true,
  ipAllow: false,
  sso: false,
  autoDownload: true,
  includeDiff: true,
  fileFormat: '.sql',
  theme: 'Light',
  autoDelete: true,
  retention: 30,
  notifEmail: 'admin@example.com',
  emailNotifications: true,
  successAlerts: true,
  failureAlerts: true
};

function toast(message) {
  showNotification(message, 'success');
}

function tog(key) {
  S[key] = !S[key];
  renderSettings();
}

function sv(key, value) {
  const parsed = Number(value);
  S[key] = Number.isNaN(parsed) ? value : parsed;
  renderSettings();
}

function renderSettings() {
  const activeTab = document.querySelector('.tab-pill.active');
  const activePage = document.querySelector('#settings-subnav .subnav-item.active');
  if (activeTab && activePage) {
    renderSubpage(activeTab.dataset.tab, activePage.dataset.key, getCurrentRole());
  }
}

function TR(label, desc, key) {
  return `
    <div class="toggle-row">
      <div style="max-width:72%;">
        <strong>${label}</strong>
        <div class="small-text">${desc}</div>
      </div>
      <label class="switch"><input type="checkbox" onchange="tog('${key}')" ${S[key] ? 'checked' : ''} /><span class="slider"></span></label>
    </div>
  `;
}

function FL(label, key, type = 'number') {
  return `
    <div class="input-group">
      <label>${label}</label>
      <input type="${type}" value="${S[key] !== undefined ? S[key] : ''}" onchange="sv('${key}', this.value)" />
    </div>
  `;
}

function SEL(label, key, options) {
  return `
    <div class="input-group">
      <label>${label}</label>
      <select onchange="sv('${key}', this.value)" style="background:#ffffff; color:#111111; border:1px solid rgba(0,0,0,0.16); box-shadow:none;">
        ${options.map((value) => `<option value="${value}" ${S[key] === value ? 'selected' : ''}>${value}</option>`).join('')}
      </select>
    </div>
  `;
}

function rb(role) {
  const cls = role === 'Admin' ? 'rb-admin' : role === 'User' ? 'rb-user' : 'rb-viewer';
  return `<span class="${cls}">${role}</span>`;
}

function addUser() {
  const next = S.UPOOL[S._uid % S.UPOOL.length];
  const id = Date.now();
  S.users.push({ id, name: next.name, email: next.email, role: next.role });
  S._uid += 1;
  toast('User added');
  renderSettings();
}

function delUser(id) {
  S.users = S.users.filter((user) => user.id !== id);
  toast('User removed');
  renderSettings();
}

function filterU(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('#utbl tbody tr').forEach((row) => {
    const name = row.dataset.name.toLowerCase();
    const email = row.dataset.email.toLowerCase();
    row.style.display = name.includes(q) || email.includes(q) ? '' : 'none';
  });
}

function addLog() {
  const now = new Date();
  const ts = now.toTimeString().slice(0, 8);
  S.logs.push({ ts, lv: 'INFO', m: ' Log refresh by arun@company.io' });
  renderSettings();
}

function pgProfile() {
  const user = getUserInfo() || { name: 'User', email: '' };
  const [firstName, ...rest] = (user.name || '').split(' ');
  return `
    <h3 class="subpage-heading">Profile</h3>
    <p class="subpage-sub">Manage your account details and contact email.</p>
    <div class="grid-two">
      <div style="display:flex; gap:12px; align-items:center;">
        <div class="avatar-circle" style="background:linear-gradient(135deg,#5B6CF7,#7E8CFF);">${(user.name || 'SM').split(' ').map((s) => s[0]).slice(0,2).join('')}</div>
        <div>
          <div style="font-weight:700;">${user.name || 'User'}</div>
          <div class="small-text">${user.email || 'No email available'}</div>
        </div>
      </div>
      <div></div>
    </div>
    <form onsubmit="event.preventDefault(); toast('Profile saved');">
      <div class="grid-two">
        <div class="input-group"><label>First name</label><input value="${firstName || ''}" /></div>
        <div class="input-group"><label>Last name</label><input value="${rest.join(' ') || ''}" /></div>
      </div>
      <div class="input-group"><label>Email</label><input type="email" value="${user.email || ''}" /></div>
      <div style="display:flex; gap:12px; margin-top:12px;"><button type="button" class="button-outline" onclick="toast('Password reset email sent')">Change Password</button><button type="submit" class="button-primary">Save</button></div>
    </form>
  `;
}

function pgSecurity() {
  return `
    <h3 class="subpage-heading">Security</h3>
    <p class="subpage-sub">Configure two-factor authentication and device alerts.</p>
    ${TR('Two-factor authentication (2FA)', 'Require a second factor to sign in.', 'twoFactor')}
    ${TR('New device login alerts', 'Notify you when a new device signs in.', 'deviceAlerts')}
    <div style="margin-top:12px;"><button class="button-secondary" style="background:#FCEBEB; color:#A32D2D; border:1px solid rgba(163,45,45,0.12);" onclick="toast('Logged out from all devices')">Logout from all devices</button></div>
  `;
}

function pgNotifications() {
  return `
    <h3 class="subpage-heading">Notifications</h3>
    <p class="subpage-sub">Control email alerts for migration events.</p>
    ${TR('Email notifications', 'Receive migration update emails.', 'emailNotifications')}
    <div id="notif-subgroup" style="opacity:${S.emailNotifications ? '1' : '0.45'}; pointer-events:${S.emailNotifications ? 'auto' : 'none'}; margin-top:12px;">
      ${TR('Migration success alerts', 'Notify when a migration completes successfully.', 'successAlerts')}
      ${TR('Migration failure alerts', 'Notify when a migration fails.', 'failureAlerts')}
      ${FL('Notification email', 'notifEmail', 'email')}
    </div>
    <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('Notifications saved')">Save</button></div>
  `;
}

function pgPreferences() {
  return `
    <h3 class="subpage-heading">Preferences</h3>
    <p class="subpage-sub">Select your preferred display and export settings.</p>
    ${SEL('Theme', 'theme', ['Light','Dark','System'])}
    <div style="display:flex; gap:8px; margin-top:8px;">
      ${['Light','Dark','System'].map((theme) => `<div class="theme-pill" onclick="sv('theme','${theme}')" style="padding:8px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.06); cursor:pointer; ${S.theme===theme?'border-color:#185FA5;':''}">${theme}</div>`).join('')}
    </div>
    <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('Preferences saved')">Save</button></div>
  `;
}

function pgReports() {
  return `
    <h3 class="subpage-heading">Reports & downloads</h3>
    <p class="subpage-sub">Configure report delivery and export format.</p>
    ${TR('Auto-download reports', 'Save reports to your device automatically.', 'autoDownload')}
    ${TR('Include row diff', 'Include row difference details in report exports.', 'includeDiff')}
    ${SEL('Default file format', 'fileFormat', ['.sql','.xlsx','.csv','.json'])}
    <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('Reports settings saved')">Save</button></div>
  `;
}

function pgFiles() {
  return `
    <h3 class="subpage-heading">File handling</h3>
    <p class="subpage-sub">Choose how uploaded files are managed and retained.</p>
    ${TR('Auto-delete uploaded files', 'Remove uploaded files after retention expires.', 'autoDelete')}
    <div style="margin-top:12px; opacity:${S.autoDelete ? '1' : '0.4'}; pointer-events:${S.autoDelete ? 'auto' : 'none'};">
      ${FL('Retention period (days)', 'retention')}
    </div>
    <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('File handling saved')">Save</button></div>
  `;
}

function pgConversion() {
  return `
    <h3 class="subpage-heading">Conversion rules</h3>
    <p class="subpage-sub">Adjust conversion behavior for migration jobs.</p>
    ${TR('Strict mode', 'Fail the entire migration if any warnings are detected', 'strictMode')}
    ${TR('Auto-convert ENUM types', 'Replace MySQL ENUMs with PostgreSQL CHECK constraints', 'autoEnum')}
    ${TR('Convert backtick identifiers', 'Replace backticks with double quotes on target', 'backtick')}
    ${TR('Auto-map data types', 'Match source types to nearest target equivalent', 'autoMap')}
    <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('Conversion rules saved')">Save</button></div>
  `;
}

function pgSystem() {
  return `
    <h3 class="subpage-heading">System configuration</h3>
    <p class="subpage-sub">Control upload limits and allowed file types.</p>
    <div class="fr2" style="display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap:16px;">
      ${FL('Max upload size (MB)', 'maxUpload')}
      ${FL('Migration timeout (s)', 'timeout')}
      ${FL('Max concurrent migrations', 'concurrent')}
      ${FL('Default batch size (rows)', 'batchSize')}
    </div>
    <div style="margin:18px 0 8px; font-weight:600;">Allowed file types</div>
    <div style="display:flex; gap:16px; flex-wrap:wrap;">
      <label><input type="checkbox" onchange="tog('allowSql')" ${S.allowSql ? 'checked' : ''} /> .sql</label>
      <label><input type="checkbox" onchange="tog('allowXlsx')" ${S.allowXlsx ? 'checked' : ''} /> .xlsx</label>
      <label><input type="checkbox" onchange="tog('allowCsv')" ${S.allowCsv ? 'checked' : ''} /> .csv</label>
    </div>
    <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('System configuration saved')">Save</button></div>
  `;
}

function pgUserMgmt() {
  return `
    <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px;">
      <div>
        <h3 class="subpage-heading" style="margin:0;">All users</h3>
        <p class="subpage-sub">Manage application user accounts and roles.</p>
      </div>
      <button class="button-primary" onclick="addUser()">Add user</button>
    </div>
    <div style="margin-bottom:12px;"><input id="user-search" oninput="filterU(this.value)" placeholder="Search by name or email" style="width:100%; padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.04); color:var(--text);" /></div>
    <div style="overflow-x:auto;">
      <table id="utbl" style="width:100%; table-layout:fixed; border-collapse:collapse;">
        <thead>
          <tr>
            <th style="padding:12px 10px; text-align:left; width:56px;">Avatar</th>
            <th style="padding:12px 10px; text-align:left;">Name</th>
            <th style="padding:12px 10px; text-align:left;">Email</th>
            <th style="padding:12px 10px; text-align:left;">Role</th>
            <th style="padding:12px 10px; text-align:left;">Actions</th>
          </tr>
        </thead>
        <tbody>
          ${S.users.map((u) => `
            <tr data-name="${u.name}" data-email="${u.email}" style="border-bottom:1px solid rgba(255,255,255,0.06);">
              <td style="padding:10px;"><div class="avatar-circle" style="background:linear-gradient(135deg,#5B6CF7,#7E8CFF);">${u.name.split(' ').map((s) => s[0]).slice(0,2).join('')}</div></td>
              <td style="padding:10px;">${u.name}</td>
              <td style="padding:10px;">${u.email}</td>
              <td style="padding:10px;">${rb(u.role)}</td>
              <td style="padding:10px;"><button class="btn xs" style="margin-right:8px;" onclick="toast('Edit user not implemented')">Edit</button><button class="btn xs dng" onclick="delUser(${u.id})">Delete</button></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function pgLogs() {
  const filtered = S.logFilter === 'All' ? S.logs : S.logs.filter((log) => log.lv.includes(S.logFilter));
  return `
    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:12px;">
      <div>
        <h3 class="subpage-heading" style="margin:0;">System logs</h3>
        <p class="subpage-sub">Live output from the migration engine.</p>
      </div>
      <div style="display:flex; gap:8px; align-items:center;">
        <select onchange="sv('logFilter', this.value); renderSettings()" style="padding:10px; border-radius:8px; border:1px solid rgba(0,0,0,0.16); background:#ffffff; color:#111111; box-shadow:none;">
          ${['All','INFO','SUCCESS','WARN','ERROR'].map((level) => `<option value="${level}" ${S.logFilter===level?'selected':''}>${level}</option>`).join('')}
        </select>
        <button class="button-secondary" onclick="toast('Logs downloaded')">Download Logs</button>
        <button class="button-secondary" style="background:#FCEBEB; color:#A32D2D; border:1px solid rgba(163,45,45,0.12);" onclick="S.logs=[]; renderSettings();">Clear Logs</button>
      </div>
    </div>
    <div style="background:#1a1d2e; border-radius:8px; padding:10px 13px; font-family:monospace; font-size:11px; line-height:1.8; max-height:160px; overflow-y:auto;">
      ${filtered.map((log) => `
        <div style="display:flex; gap:8px; align-items:center; padding:4px 0;">
          <span style="color:#5b6280; width:72px;">${log.ts}</span>
          <span style="color:${log.lv==='INFO'?'#60a5fa':log.lv==='SUCCESS'?'#34d399':log.lv==='WARN'?'#fbbf24':'#f87171'}; width:72px;">${log.lv}</span>
          <span style="color:#c4c9e0;">${log.m}</span>
        </div>
      `).join('')}
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
      <div class="small-text">${filtered.length} entries</div>
      <button class="button-secondary" onclick="addLog()">Refresh</button>
    </div>
  `;
}

function pgSecpol() {
  return `
    <div style="display:grid; gap:16px;">
      <div class="card" style="padding:18px;">
        <h4 style="margin:0 0 8px;">Password policy</h4>
        <div class="fr2" style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px;">
          ${FL('Minimum password length', 'minPw')}
          ${FL('Expiry days', 'pwExpiry')}
        </div>
        <div style="margin-top:12px; display:flex; gap:16px; flex-wrap:wrap;">
          <label><input type="checkbox" onchange="tog('reqUpper')" ${S.reqUpper ? 'checked' : ''} /> Require uppercase</label>
          <label><input type="checkbox" onchange="tog('reqNum')" ${S.reqNum ? 'checked' : ''} /> Require numbers</label>
          <label><input type="checkbox" onchange="tog('reqSym')" ${S.reqSym ? 'checked' : ''} /> Require symbols</label>
        </div>
        <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('Password policy saved')">Save</button></div>
      </div>
      <div class="card" style="padding:18px;">
        <h4 style="margin:0 0 8px;">Session & access control</h4>
        <div class="fr2" style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px;">
          ${FL('Session timeout (mins)', 'sessionTO')}
          ${FL('Max failed login attempts', 'maxFail')}
        </div>
        ${TR('Enforce 2FA for all users', '', 'enforce2fa')}
        ${TR('IP allowlist', '', 'ipAllow')}
        ${TR('Single sign-on (SSO)', '', 'sso')}
        <div style="margin-top:12px; text-align:right;"><button class="button-primary" onclick="toast('Session & access control saved')">Save</button></div>
      </div>
    </div>
  `;
}

const pageMap = {
  profile: pgProfile,
  security: pgSecurity,
  notifications: pgNotifications,
  preferences: pgPreferences,
  reports: pgReports,
  files: pgFiles,
  conversion: pgConversion,
  system: pgSystem,
  usermgmt: pgUserMgmt,
  logs: pgLogs,
  secpol: pgSecpol
};

function initSettingsPage() {
  if (!requireAuth()) return;
  loadSharedComponent('header', () => {
    setProfileSummary();
    bindHeaderActions();
  });
  initSidebar();
  const headerTitle = document.getElementById('page-title');
  if (headerTitle) headerTitle.textContent = 'Settings';
  setTimeout(() => {
    renderRoleUI();
    const adminPill = document.getElementById('role-pill-admin');
    const userPill = document.getElementById('role-pill-user');
    if (adminPill) adminPill.addEventListener('click', () => setCurrentRole('Admin'));
    if (userPill) userPill.addEventListener('click', () => setCurrentRole('User'));
  }, 120);
}

function getCurrentRole() {
  const user = getUserInfo();
  return user ? user.role || 'User' : 'User';
}

function setCurrentRole(role) {
  const user = getUserInfo() || { name: 'Guest', email: '', role };
  user.role = role;
  setUserInfo(user);
  renderRoleUI();
}

function renderRoleUI() {
  const role = getCurrentRole();
  buildSidebarLinks(role);
  renderTabs(role);
  const adminPill = document.getElementById('role-pill-admin');
  const userPill = document.getElementById('role-pill-user');
  if (adminPill && userPill) {
    adminPill.classList.toggle('active', role === 'Admin');
    userPill.classList.toggle('active', role === 'User');
    adminPill.style.background = role === 'Admin' ? '#185FA5' : 'transparent';
    adminPill.style.color = role === 'Admin' ? 'white' : 'inherit';
    userPill.style.background = role === 'User' ? '#185FA5' : 'transparent';
    userPill.style.color = role === 'User' ? 'white' : 'inherit';
    const avatar = document.getElementById('avatar-circle');
    const u = getUserInfo();
    if (avatar) avatar.textContent = (u && u.name) ? u.name.split(' ').map((s) => s[0]).slice(0, 2).join('') : 'SM';
  }
}

function renderTabs(role) {
  const tabsBar = document.querySelector('.tabs-bar');
  if (!tabsBar) return;
  const tabs = [{ key: 'my-account', label: 'My Account' }];
  if (role === 'User') tabs.push({ key: 'user-settings', label: 'User Settings' });
  if (role === 'Admin') tabs.push({ key: 'admin-settings', label: 'Admin Settings <span class="badge-amber">Admin only</span>' });
  tabsBar.innerHTML = tabs.map((t) => `<button class="tab-pill" data-tab="${t.key}">${t.label}</button>`).join('');
  const defaultTab = document.querySelector('.tab-pill[data-tab="my-account"]');
  if (defaultTab) {
    defaultTab.classList.add('active');
    renderSubnavFor('my-account', role);
  }
  document.querySelectorAll('.tab-pill').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-pill').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      renderSubnavFor(btn.dataset.tab, role);
    });
  });
}

function renderSubnavFor(tabKey, role) {
  const subnav = document.getElementById('settings-subnav');
  const content = document.getElementById('settings-content');
  if (!subnav || !content) return;
  subnav.innerHTML = '';
  content.innerHTML = '';
  let items = [];
  if (tabKey === 'my-account') {
    items = [
      { label: 'Profile', key: 'profile' },
      { label: 'Security', key: 'security' },
      { label: 'Notifications', key: 'notifications' },
      { label: 'Preferences', key: 'preferences' }
    ];
  } else if (tabKey === 'user-settings') {
    items = [
      { label: 'Reports & Downloads', key: 'reports' },
      { label: 'File handling', key: 'files' }
    ];
  } else if (tabKey === 'admin-settings') {
    items = [
      { label: 'Conversion rules', key: 'conversion' },
      { label: 'System configuration', key: 'system' },
      { label: 'User management', key: 'usermgmt' },
      { label: 'Logs & monitoring', key: 'logs' },
      { label: 'Security policies', key: 'secpol' }
    ];
  }
  items.forEach((item, idx) => {
    const el = document.createElement('div');
    el.className = 'subnav-item';
    el.dataset.key = item.key;
    el.innerHTML = `<span>${item.label}</span>`;
    if (idx === 0) el.classList.add('active');
    el.addEventListener('click', () => {
      subnav.querySelectorAll('.subnav-item').forEach((s) => s.classList.remove('active'));
      el.classList.add('active');
      renderSubpage(tabKey, item.key, role);
    });
    subnav.appendChild(el);
  });
  if (items.length) renderSubpage(tabKey, items[0].key, role);
}

function renderSubpage(tabKey, pageKey, role) {
  const content = document.getElementById('settings-content');
  if (!content) return;
  const pageFn = pageMap[pageKey];
  content.innerHTML = pageFn ? pageFn() : '';
}


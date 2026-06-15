function renderSidebar() {
  const user = getUserInfo();
  if (!user) return;
  buildSidebarLinks(user.role);
}

function initSidebar() {
  const sidebarContainer = document.getElementById('sidebar-container');
  if (!sidebarContainer) return;
  loadSharedComponent('sidebar', () => {
    renderSidebar();
    bindLogout();
  });
}

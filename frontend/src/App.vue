<style scoped>
.loading-screen {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--parchment);
}
.loader-wrap { text-align: center; }
.loader-wrap .logo-icon { font-size: 48px; }
.loader-wrap p { margin-top: 12px; color: var(--warm-brown); font-family: 'Playfair Display', serif; }

.app-shell { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: var(--sidebar-w); background: var(--warm-brown); color: #f5ece0;
  display: flex; flex-direction: column; padding: 28px 0; flex-shrink: 0; z-index: 200;
}
.sidebar-logo {
  display: flex; align-items: center; gap: 12px;
  padding: 0 20px 28px; border-bottom: 1px solid rgba(255,255,255,.12); margin-bottom: 16px;
}
.logo-icon { font-size: 28px; }
.logo-name { font-size: 22px; color: var(--amber-light); line-height: 1; }
.logo-sub { font-size: 11px; color: rgba(245,236,224,.55); letter-spacing: .5px; margin-top: 2px; }

.sidebar-nav { flex: 1; padding: 0 12px; display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  display: flex; align-items: center; gap: 11px; padding: 11px 14px;
  border-radius: 10px; font-size: 14.5px; color: rgba(245,236,224,.75); transition: all .16s; position: relative;
}
.nav-item:hover { background: rgba(255,255,255,.08); color: #fff; }
.nav-item.active { background: rgba(201,136,42,.25); color: var(--amber-light); font-weight: 500; }
.nav-icon { font-size: 18px; width: 22px; text-align: center; }
.nav-badge {
  margin-left: auto; background: #e55; color: #fff;
  font-size: 11px; font-weight: 700; padding: 1px 7px; border-radius: 99px;
}

.sidebar-user {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px; margin: 0 12px 12px;
  border-radius: 10px; background: rgba(255,255,255,.08);
}
.user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--amber); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px; flex-shrink: 0;
}
.user-info { flex: 1; min-width: 0; }
.user-name { font-size: 13px; font-weight: 600; color: #f5ece0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 11px; color: rgba(245,236,224,.5); text-transform: capitalize; }
.logout-btn {
  background: none; border: none; color: rgba(245,236,224,.5); font-size: 18px;
  cursor: pointer; padding: 2px; transition: color .15s;
}
.logout-btn:hover { color: #f5ece0; }

.sidebar-footer {
  padding: 24px 20px 0; border-top: 1px solid rgba(255,255,255,.1); margin-top: 8px;
}
.sidebar-quote { font-size: 12px; color: rgba(245,236,224,.5); font-style: italic; line-height: 1.5; }
.sidebar-quote-author { font-size: 11px; color: rgba(245,236,224,.3); margin-top: 4px; }

.main-content { flex: 1; overflow-y: auto; padding: 36px 40px; background: var(--parchment); }

/* hidden on desktop */
.mobile-topbar { display: none; }
.sidebar-overlay { display: none; }
.bottom-nav { display: none; }
.hamburger { display: none; }

@media (max-width: 768px) {
  .app-shell { flex-direction: column; height: 100dvh; }

  .mobile-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 18px; background: var(--warm-brown); flex-shrink: 0; z-index: 300;
  }
  .mobile-logo { display: flex; align-items: center; gap: 10px; color: #f5ece0; }
  .hamburger {
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,.15); border: none; border-radius: 8px;
    color: #f5ece0; font-size: 20px; width: 38px; height: 38px; cursor: pointer;
  }

  .sidebar {
    position: fixed; top: 0; left: 0; height: 100%; width: 260px;
    transform: translateX(-100%); transition: transform .25s ease; padding-top: 60px;
  }
  .sidebar.open { transform: translateX(0); box-shadow: 4px 0 24px rgba(0,0,0,.3); }

  .sidebar-overlay {
    display: block; position: fixed; inset: 0;
    background: rgba(0,0,0,.4); z-index: 199;
  }

  .main-content { flex: 1; overflow-y: auto; padding: 20px 16px 80px; }

  .bottom-nav {
    display: flex; position: fixed; bottom: 0; left: 0; right: 0;
    background: var(--warm-brown); border-top: 1px solid rgba(255,255,255,.12);
    z-index: 300; padding-bottom: env(safe-area-inset-bottom);
  }
  .bnav-item {
    flex: 1; display: flex; flex-direction: column; align-items: center;
    justify-content: center; gap: 3px; padding: 8px 4px;
    color: rgba(245,236,224,.6); font-size: 10px; text-decoration: none;
    transition: color .15s; position: relative;
  }
  .bnav-item span:first-child { font-size: 20px; }
  .bnav-item.active { color: var(--amber-light); }
  .bnav-badge {
    position: absolute; top: 4px; right: calc(50% - 18px);
    background: #e55; color: #fff; font-size: 9px;
    font-weight: 700; padding: 1px 5px; border-radius: 99px;
  }
}
</style>

<template>
  <div v-if="!auth.loaded" class="loading-screen">
    <div class="loader-wrap"><span class="logo-icon">📚</span><p>Loading Biblios…</p></div>
  </div>

  <div v-else-if="!auth.user">
    <router-view />
  </div>

  <div v-else class="app-shell">
    <!-- Mobile topbar -->
    <header class="mobile-topbar">
      <div class="mobile-logo">
        <span>📚</span>
        <span class="serif" style="color:var(--amber-light);font-size:18px">Biblios</span>
      </div>
      <button class="hamburger" @click="menuOpen = !menuOpen">
        {{ menuOpen ? '✕' : '☰' }}
      </button>
    </header>

    <!-- Sidebar overlay on mobile -->
    <div class="sidebar-overlay" v-if="menuOpen" @click="menuOpen = false" />

    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="sidebar-logo">
        <span class="logo-icon">📚</span>
        <div>
          <div class="logo-name serif">Biblios</div>
          <div class="logo-sub">Library System</div>
        </div>
      </div>

      <nav class="sidebar-nav" v-if="auth.isLibrarian">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }" @click="menuOpen = false">
          <span class="nav-icon">🏛️</span> Dashboard
        </router-link>
        <router-link to="/books" class="nav-item" :class="{ active: $route.path === '/books' }" @click="menuOpen = false">
          <span class="nav-icon">📖</span> Books
        </router-link>
        <router-link to="/members" class="nav-item" :class="{ active: $route.path === '/members' }" @click="menuOpen = false">
          <span class="nav-icon">👥</span> Members
        </router-link>
        <router-link to="/borrows" class="nav-item" :class="{ active: $route.path === '/borrows' }" @click="menuOpen = false">
          <span class="nav-icon">🔖</span> Borrows
        </router-link>
        <router-link to="/students" class="nav-item" :class="{ active: $route.path === '/students' }" @click="menuOpen = false">
          <span class="nav-icon">🎓</span> Students
          <span v-if="pendingCount > 0" class="nav-badge">{{ pendingCount }}</span>
        </router-link>
      </nav>

      <nav class="sidebar-nav" v-else>
        <router-link to="/my" class="nav-item" :class="{ active: $route.path === '/my' }" @click="menuOpen = false">
          <span class="nav-icon">🏠</span> My Library
        </router-link>
        <router-link to="/books" class="nav-item" :class="{ active: $route.path === '/books' }" @click="menuOpen = false">
          <span class="nav-icon">📖</span> Browse Books
        </router-link>
      </nav>

      <div class="sidebar-user">
        <div class="user-avatar">{{ auth.user.username[0].toUpperCase() }}</div>
        <div class="user-info">
          <div class="user-name">{{ auth.user.username }}</div>
          <div class="user-role">{{ auth.user.role }}</div>
        </div>
        <button class="logout-btn" @click="doLogout" title="Logout">⏏</button>
      </div>

      <div class="sidebar-footer">
        <div class="sidebar-quote serif">"A reader lives a thousand lives."</div>
        <div class="sidebar-quote-author">— George R.R. Martin</div>
      </div>
    </aside>

    <!-- Mobile bottom nav -->
    <nav class="bottom-nav" v-if="auth.isLibrarian">
      <router-link to="/" class="bnav-item" :class="{ active: $route.path === '/' }">
        <span>🏛️</span><span>Home</span>
      </router-link>
      <router-link to="/books" class="bnav-item" :class="{ active: $route.path === '/books' }">
        <span>📖</span><span>Books</span>
      </router-link>
      <router-link to="/members" class="bnav-item" :class="{ active: $route.path === '/members' }">
        <span>👥</span><span>Members</span>
      </router-link>
      <router-link to="/borrows" class="bnav-item" :class="{ active: $route.path === '/borrows' }">
        <span>🔖</span><span>Borrows</span>
      </router-link>
      <router-link to="/students" class="bnav-item" :class="{ active: $route.path === '/students' }">
        <span>🎓</span><span>Students</span>
        <span v-if="pendingCount > 0" class="bnav-badge">{{ pendingCount }}</span>
      </router-link>
    </nav>
    <nav class="bottom-nav" v-else>
      <router-link to="/my" class="bnav-item" :class="{ active: $route.path === '/my' }">
        <span>🏠</span><span>My Library</span>
      </router-link>
      <router-link to="/books" class="bnav-item" :class="{ active: $route.path === '/books' }">
        <span>📖</span><span>Books</span>
      </router-link>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from './store/auth.js'
import { logout, getPendingStudents } from './store/api.js'

const router = useRouter()
const pendingCount = ref(0)
const menuOpen = ref(false)

const doLogout = async () => {
  await logout()
  auth.user = null
  auth.loaded = false
  menuOpen.value = false
  router.push('/login')
}

onMounted(async () => {
  if (auth.isLibrarian) {
    try {
      const r = await getPendingStudents()
      pendingCount.value = r.data.length
    } catch {}
  }
})
</script>

<style scoped>
.loading-screen {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--parchment);
}
.loader-wrap { text-align: center; }
.loader-wrap .logo-icon { font-size: 48px; }
.loader-wrap p { margin-top: 12px; color: var(--warm-brown); font-family: 'Playfair Display', serif; }

.app-shell { display: flex; height: 100vh; overflow: hidden; }

/* ── SIDEBAR ─────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-w); background: var(--warm-brown); color: #f5ece0;
  display: flex; flex-direction: column; padding: 28px 0; flex-shrink: 0;
  z-index: 200;
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
  border-radius: 10px; font-size: 14.5px; font-weight: 400;
  color: rgba(245,236,224,.75); transition: all .16s; position: relative;
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

/* ── MAIN ────────────────────────────────────────── */
.main-content { flex: 1; overflow-y: auto; padding: 36px 40px; background: var(--parchment); }

/* ── MOBILE ELEMENTS (hidden on desktop) ─────────── */
.mobile-topbar { display: none; }
.sidebar-overlay { display: none; }
.bottom-nav { display: none; }
.hamburger { display: none; }

/* ── MOBILE BREAKPOINT ───────────────────────────── */
@media (max-width: 768px) {
  .app-shell { flex-direction: column; height: 100dvh; }

  /* topbar */
  .mobile-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 18px; background: var(--warm-brown);
    flex-shrink: 0; z-index: 300;
  }
  .mobile-logo { display: flex; align-items: center; gap: 10px; color: #f5ece0; }
  .hamburger {
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,.15); border: none; border-radius: 8px;
    color: #f5ece0; font-size: 20px; width: 38px; height: 38px; cursor: pointer;
  }

  /* sidebar slides in as drawer */
  .sidebar {
    position: fixed; top: 0; left: 0; height: 100%; width: 260px;
    transform: translateX(-100%); transition: transform .25s ease;
    padding-top: 60px;
  }
  .sidebar.open { transform: translateX(0); box-shadow: 4px 0 24px rgba(0,0,0,.3); }

  /* dark overlay behind drawer */
  .sidebar-overlay {
    display: block; position: fixed; inset: 0;
    background: rgba(0,0,0,.4); z-index: 199;
  }

  /* main content area */
  .main-content {
    flex: 1; overflow-y: auto;
    padding: 20px 16px 80px; /* bottom padding for bottom nav */
  }

  /* bottom navigation bar */
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

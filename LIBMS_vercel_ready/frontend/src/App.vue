<template>
  <div v-if="!auth.loaded" class="loading-screen">
    <div class="loader-wrap"><span class="logo-icon">📚</span><p>Loading Biblios…</p></div>
  </div>

  <!-- Not logged in: just show the page (login) -->
  <div v-else-if="!auth.user">
    <router-view />
  </div>

  <!-- Logged in: full shell -->
  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-icon">📚</span>
        <div>
          <div class="logo-name serif">Biblios</div>
          <div class="logo-sub">Library System</div>
        </div>
      </div>

      <!-- LIBRARIAN NAV -->
      <nav class="sidebar-nav" v-if="auth.isLibrarian">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <span class="nav-icon">🏛️</span> Dashboard
        </router-link>
        <router-link to="/books" class="nav-item" :class="{ active: $route.path === '/books' }">
          <span class="nav-icon">📖</span> Books
        </router-link>
        <router-link to="/members" class="nav-item" :class="{ active: $route.path === '/members' }">
          <span class="nav-icon">👥</span> Members
        </router-link>
        <router-link to="/borrows" class="nav-item" :class="{ active: $route.path === '/borrows' }">
          <span class="nav-icon">🔖</span> Borrows
        </router-link>
        <router-link to="/students" class="nav-item" :class="{ active: $route.path === '/students' }">
          <span class="nav-icon">🎓</span> Students
          <span v-if="pendingCount > 0" class="nav-badge">{{ pendingCount }}</span>
        </router-link>
      </nav>

      <!-- STUDENT NAV -->
      <nav class="sidebar-nav" v-else>
        <router-link to="/my" class="nav-item" :class="{ active: $route.path === '/my' }">
          <span class="nav-icon">🏠</span> My Library
        </router-link>
        <router-link to="/books" class="nav-item" :class="{ active: $route.path === '/books' }">
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

const doLogout = async () => {
  await logout()
  auth.user = null
  auth.loaded = false
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

.sidebar {
  width: var(--sidebar-w); background: var(--warm-brown); color: #f5ece0;
  display: flex; flex-direction: column; padding: 28px 0; flex-shrink: 0;
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
  border-radius: 10px; font-size: 14.5px; font-weight: 400; color: rgba(245,236,224,.75); transition: all .16s;
  position: relative;
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
</style>

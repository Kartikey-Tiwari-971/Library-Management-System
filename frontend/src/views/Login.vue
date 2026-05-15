<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <span>📚</span>
        <div>
          <div class="serif" style="font-size:28px;color:var(--warm-brown)">Biblios</div>
          <div style="font-size:13px;color:#9a8a7a;letter-spacing:.5px">Library Management System</div>
        </div>
      </div>

      <!-- Tab switcher -->
      <div class="tab-bar">
        <button :class="['tab', { active: tab === 'login' }]" @click="tab = 'login'">Sign In</button>
        <button :class="['tab', { active: tab === 'register' }]" @click="tab = 'register'">Request Access</button>
      </div>

      <!-- LOGIN FORM -->
      <div v-if="tab === 'login'">
        <div class="form-group">
          <label>Username</label>
          <input v-model="lForm.username" placeholder="Enter username" @keyup.enter="doLogin" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="lForm.password" type="password" placeholder="Enter password" @keyup.enter="doLogin" />
        </div>
        <button class="btn btn-primary btn-full" @click="doLogin" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign In' }}
        </button>
        
      </div>

      <!-- REGISTER FORM -->
      <div v-else>
        <p style="font-size:13px;color:#7a6a5a;margin-bottom:16px">
          Submit a request to join the library. The librarian will review and approve your account.
        </p>
        <div class="form-group">
          <label>Full Name *</label>
          <input v-model="rForm.name" placeholder="e.g. Priya Sharma" />
        </div>
        <div class="form-group">
          <label>Email *</label>
          <input v-model="rForm.email" type="email" placeholder="priya@example.com" />
        </div>
        <div class="form-group">
          <label>Phone</label>
          <input v-model="rForm.phone" placeholder="+91 98765 43210 (optional)" />
        </div>
        <div class="form-group">
          <label>Username *</label>
          <input v-model="rForm.username" placeholder="Choose a username" />
        </div>
        <div class="form-group">
          <label>Password *</label>
          <input v-model="rForm.password" type="password" placeholder="Choose a password" />
        </div>
        <button class="btn btn-primary btn-full" @click="doRegister" :disabled="loading">
          {{ loading ? 'Submitting…' : 'Submit Request' }}
        </button>
      </div>

      <div class="error-box" v-if="error">{{ error }}</div>
      <div class="success-box" v-if="success">{{ success }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, registerStudent } from '../store/api.js'
import { auth } from '../store/auth.js'

const router = useRouter()
const tab = ref('login')
const loading = ref(false)
const error = ref('')
const success = ref('')

const lForm = ref({ username: '', password: '' })
const rForm = ref({ name: '', email: '', phone: '', username: '', password: '' })

const doLogin = async () => {
  error.value = ''; loading.value = true
  try {
    const r = await login(lForm.value)
    auth.user = r.data.user; auth.loaded = true
    router.push(auth.isLibrarian ? '/' : '/my')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed.'
  } finally { loading.value = false }
}

const doRegister = async () => {
  error.value = ''; success.value = ''; loading.value = true
  try {
    const r = await registerStudent(rForm.value)
    success.value = r.data.message
    rForm.value = { name: '', email: '', phone: '', username: '', password: '' }
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed.'
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--parchment) 0%, var(--cream) 100%);
}
.login-card {
  background: #fff; border: 1px solid var(--border); border-radius: 18px;
  padding: 40px; width: 420px; box-shadow: 0 8px 40px rgba(106,76,53,.12);
}
.login-logo { display: flex; align-items: center; gap: 16px; margin-bottom: 28px; }
.login-logo span { font-size: 44px; }

.tab-bar { display: flex; gap: 4px; background: var(--cream); border-radius: 10px; padding: 4px; margin-bottom: 24px; }
.tab {
  flex: 1; padding: 9px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 500; cursor: pointer;
  background: transparent; color: #7a6a5a; transition: all .15s;
}
.tab.active { background: #fff; color: var(--warm-brown); box-shadow: 0 1px 6px var(--shadow); }

.btn-full { width: 100%; justify-content: center; padding: 12px; font-size: 15px; }
.btn-full:disabled { opacity: .6; cursor: not-allowed; }

.hint-box {
  margin-top: 14px; padding: 10px 14px; background: var(--cream);
  border-radius: 8px; font-size: 13px; color: #7a6a5a;
}
.hint-box code { background: rgba(106,76,53,.1); padding: 1px 6px; border-radius: 4px; font-size: 12px; }

.error-box {
  margin-top: 14px; padding: 10px 14px; background: #fde8e8;
  border-radius: 8px; font-size: 13px; color: #9b2020;
}
.success-box {
  margin-top: 14px; padding: 10px 14px; background: #dff0e0;
  border-radius: 8px; font-size: 13px; color: #2d6a3f;
}
</style>

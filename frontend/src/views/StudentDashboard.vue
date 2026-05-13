<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="serif">My Library</h1>
        <p>Welcome, {{ auth.user?.username }}! Manage your books here.</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon">🔖</div>
        <div class="stat-val">{{ stats.active_borrows ?? '—' }}</div>
        <div class="stat-label">Currently Borrowed</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-val">{{ stats.total_borrows ?? '—' }}</div>
        <div class="stat-label">Total Borrowed</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📌</div>
        <div class="stat-val">{{ stats.reservations ?? '—' }}</div>
        <div class="stat-label">Active Reservations</div>
      </div>
      <div class="stat-card" :class="{ danger: stats.overdue > 0 }">
        <div class="stat-icon">⚠️</div>
        <div class="stat-val">{{ stats.overdue ?? '—' }}</div>
        <div class="stat-label">Overdue</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar" style="margin-top:28px">
      <button :class="['tab', { active: tab === 'active' }]" @click="tab = 'active'">📖 Currently Borrowed</button>
      <button :class="['tab', { active: tab === 'history' }]" @click="tab = 'history'">🕑 Borrow History</button>
      <button :class="['tab', { active: tab === 'reservations' }]" @click="tab = 'reservations'">📌 My Reservations</button>
    </div>

    <!-- Currently Borrowed -->
    <div class="card" v-if="tab === 'active'" style="margin-top:16px">
      <table v-if="activeBorrows.length">
        <thead>
          <tr><th>Book</th><th>Issued On</th><th>Due Date</th><th>Reissues</th><th>Fine</th><th>Status</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in activeBorrows" :key="r.id" :class="{ 'row-overdue': r.overdue }">
            <td>
              <strong>{{ r.book_title }}</strong><br>
              <small style="color:#9a8a7a">{{ r.book_author }}</small>
            </td>
            <td class="ts">{{ fmt(r.borrow_date) }}</td>
            <td class="ts" :style="{ color: r.overdue ? '#9b2020' : '#2d6a3f', fontWeight: r.overdue ? 600 : 400 }">
              {{ fmt(r.due_date) }}
            </td>
            <td style="text-align:center">
              <span class="badge" :class="r.reissue_count >= 2 ? 'badge-overdue' : 'badge-available'">
                {{ r.reissue_count }}/2
              </span>
            </td>
            <td>
              <span v-if="r.fine_amount > 0" style="color:#a04020;font-weight:600">₹{{ r.fine_amount }}</span>
              <span v-else style="color:#9a8a7a">—</span>
            </td>
            <td>
              <span class="badge" :class="r.overdue ? 'badge-overdue' : 'badge-available'">
                {{ r.overdue ? 'Overdue' : 'Active' }}
              </span>
            </td>
            <td>
              <button v-if="r.reissue_count < 2" class="btn btn-primary btn-sm" @click="doReissue(r)">
                🔄 Reissue
              </button>
              <span v-else style="font-size:12px;color:#9a8a7a">Max reissues</span>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-else>
        <div class="icon">📭</div>
        <p>You have no books currently borrowed.</p>
      </div>
    </div>

    <!-- History -->
    <div class="card" v-if="tab === 'history'" style="margin-top:16px">
      <table v-if="allBorrows.length">
        <thead>
          <tr><th>Book</th><th>Issued On</th><th>Due Date</th><th>Returned On</th><th>Fine</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in allBorrows" :key="r.id">
            <td>
              <strong>{{ r.book_title }}</strong><br>
              <small style="color:#9a8a7a">{{ r.book_author }}</small>
            </td>
            <td class="ts">{{ fmt(r.borrow_date) }}</td>
            <td class="ts">{{ fmt(r.due_date) }}</td>
            <td class="ts">{{ r.return_date ? fmt(r.return_date) : '—' }}</td>
            <td>
              <span v-if="r.fine_amount > 0" style="color:#a04020;font-weight:600">₹{{ r.fine_amount }}</span>
              <span v-else style="color:#9a8a7a">—</span>
            </td>
            <td>
              <span class="badge" :class="r.returned ? 'badge-returned' : r.overdue ? 'badge-overdue' : 'badge-available'">
                {{ r.returned ? 'Returned' : r.overdue ? 'Overdue' : 'Active' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-else>
        <div class="icon">🕑</div><p>No borrow history yet.</p>
      </div>
    </div>

    <!-- Reservations -->
    <div class="card" v-if="tab === 'reservations'" style="margin-top:16px">
      <table v-if="reservations.length">
        <thead>
          <tr><th>Book</th><th>Reserved On</th><th>Status</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in reservations" :key="r.id">
            <td><strong>{{ r.book_title }}</strong><br><small style="color:#9a8a7a">{{ r.book_author }}</small></td>
            <td class="ts">{{ fmt(r.reserved_on) }}</td>
            <td>
              <span class="badge" :class="{ 'badge-available': r.status === 'active', 'badge-returned': r.status === 'fulfilled', 'badge-overdue': r.status === 'cancelled' }">
                {{ r.status }}
              </span>
            </td>
            <td>
              <button v-if="r.status === 'active'" class="btn btn-danger btn-sm" @click="cancelRes(r)">Cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-else>
        <div class="icon">📌</div><p>No reservations. Browse books to reserve!</p>
      </div>
    </div>

    <div class="toast" :class="toast.type" v-if="toast.msg">{{ toast.msg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStats, getBorrows, getReservations, reissueBook, cancelReservation } from '../store/api.js'
import { auth } from '../store/auth.js'

const stats = ref({})
const allBorrows = ref([])
const reservations = ref([])
const tab = ref('active')
const toast = ref({ msg: '', type: '' })

const activeBorrows = computed(() => allBorrows.value.filter(r => !r.returned))

const fmt = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'

const showToast = (msg, type = 'toast-success') => {
  toast.value = { msg, type }; setTimeout(() => toast.value = { msg: '', type: '' }, 3000)
}

const load = async () => {
  const [s, b, r] = await Promise.all([getStats(), getBorrows(), getReservations()])
  stats.value = s.data; allBorrows.value = b.data; reservations.value = r.data
}

const doReissue = async (r) => {
  try { await reissueBook(r.id); showToast('Due date extended!'); await load() }
  catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

const cancelRes = async (r) => {
  try { await cancelReservation(r.id); showToast('Reservation cancelled.'); await load() }
  catch { showToast('Error', 'toast-error') }
}

onMounted(load)
</script>

<style scoped>
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card {
  background: #fff; border: 1px solid var(--border); border-radius: 14px;
  padding: 22px 20px; text-align: center; box-shadow: 0 2px 10px var(--shadow);
}
.stat-card.danger { border-color: #f9cccc; background: #fff8f8; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-val { font-size: 36px; font-weight: 700; color: var(--warm-brown); font-family: 'Playfair Display', serif; }
.stat-label { font-size: 13px; color: #9a8a7a; margin-top: 4px; }

.tab-bar { display: flex; gap: 4px; background: var(--cream); border-radius: 10px; padding: 4px; }
.tab { flex: 1; padding: 9px; border-radius: 8px; border: none; font-size: 13.5px; font-weight: 500; cursor: pointer; background: transparent; color: #7a6a5a; transition: all .15s; }
.tab.active { background: #fff; color: var(--warm-brown); box-shadow: 0 1px 6px var(--shadow); }

.ts { font-size: 12px; color: #7a6a5a; }
.row-overdue { background: #fff8f5; }
</style>

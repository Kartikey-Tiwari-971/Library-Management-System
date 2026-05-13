<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="serif">Dashboard</h1>
        <p>Welcome back, {{ auth.user?.username }}! Here's your library at a glance.</p>
      </div>
      <div style="display:flex;gap:10px">
        <button class="btn btn-ghost" @click="openIssue">📖 Issue Book</button>
        <button class="btn btn-primary" @click="scrollToReservations" v-if="pendingReservations.length">
          ✅ Approve Reservations
          <span class="notif-badge">{{ pendingReservations.length }}</span>
        </button>
      </div>
    </div>

    <!-- Stats grid -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-val">{{ stats.total_books ?? '—' }}</div>
        <div class="stat-label">Total Books</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-val">{{ stats.total_members ?? '—' }}</div>
        <div class="stat-label">Members</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔖</div>
        <div class="stat-val">{{ stats.active_borrows ?? '—' }}</div>
        <div class="stat-label">Currently Issued</div>
      </div>
      <div class="stat-card" :class="{ danger: stats.overdue > 0 }">
        <div class="stat-icon">⚠️</div>
        <div class="stat-val">{{ stats.overdue ?? '—' }}</div>
        <div class="stat-label">Overdue</div>
      </div>
      <div class="stat-card" :class="{ warn: stats.pending_students > 0 }">
        <div class="stat-icon">🎓</div>
        <div class="stat-val">{{ stats.pending_students ?? '—' }}</div>
        <div class="stat-label">Pending Approvals</div>
      </div>
      <div class="stat-card" :class="{ warn: stats.active_reservations > 0 }">
        <div class="stat-icon">📌</div>
        <div class="stat-val">{{ stats.active_reservations ?? '—' }}</div>
        <div class="stat-label">Reservations</div>
      </div>
    </div>

    <!-- Pending Reservations panel -->
    <div class="card" style="margin-top:28px" ref="reservationsSection" v-if="pendingReservations.length">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
        <h3 class="serif" style="margin:0">Pending Reservations</h3>
        <span class="badge badge-warn" style="font-size:13px;padding:4px 12px">{{ pendingReservations.length }} waiting</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Book</th>
            <th>Member</th>
            <th>Reserved On</th>
            <th>Availability</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in pendingReservations" :key="r.id">
            <td><strong>{{ r.book_title }}</strong><br><small style="color:#9a8a7a">{{ r.book_author }}</small></td>
            <td>{{ r.member_name }}</td>
            <td style="font-size:13px;color:#7a6a5a">{{ fmt(r.reserved_on) }}</td>
            <td>
              <span class="badge" :class="r.book_available > 0 ? 'badge-available' : 'badge-unavailable'">
                {{ r.book_available > 0 ? `${r.book_available} available` : 'Unavailable' }}
              </span>
            </td>
            <td>
              <div style="display:flex;gap:6px">
                <button
                  class="btn btn-primary btn-sm"
                  :disabled="r.book_available <= 0"
                  :title="r.book_available <= 0 ? 'No copies available' : 'Approve & issue this book'"
                  @click="approveReservation(r)"
                >✅ Approve &amp; Issue</button>
                <button class="btn btn-danger btn-sm" @click="cancelRes(r)">✕ Cancel</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Currently Issued Books -->
    <div class="card" style="margin-top:28px">
      <h3 class="serif" style="margin-bottom:16px">Currently Issued Books</h3>
      <table v-if="borrows.length">
        <thead>
          <tr>
            <th>Book</th>
            <th>Member</th>
            <th>Issued On</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in borrows" :key="b.id">
            <td><strong>{{ b.book_title }}</strong><br><small style="color:#9a8a7a">{{ b.book_author }}</small></td>
            <td>{{ b.member_name }}</td>
            <td style="font-size:13px;color:#7a6a5a">{{ fmt(b.borrow_date) }}</td>
            <td style="font-size:13px" :style="{ color: b.overdue ? '#9b2020' : '#2d6a3f' }">{{ fmt(b.due_date) }}</td>
            <td>
              <span class="badge" :class="b.overdue ? 'badge-overdue' : 'badge-available'">
                {{ b.overdue ? `Overdue • ₹${b.fine_amount}` : 'Active' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-else><div class="icon">📭</div><p>No active borrows.</p></div>
    </div>

    <!-- Issue Book Modal -->
    <div class="modal-overlay" v-if="showIssue" @click.self="showIssue = false">
      <div class="modal" style="width:480px">
        <h2>📖 Issue a Book</h2>
        <div class="form-group">
          <label>Member *</label>
          <select v-model="issueForm.member_id">
            <option value="">— Select member —</option>
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }} ({{ m.email }})</option>
          </select>
        </div>
        <div class="form-group">
          <label>Book *</label>
          <select v-model="issueForm.book_id" @change="onBookSelect">
            <option value="">— Select book —</option>
            <option v-for="b in availableBooks" :key="b.id" :value="b.id">
              {{ b.title }} — {{ b.author }} ({{ b.available }} available)
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Issue Period (days)</label>
          <input v-model.number="issueForm.issue_days" type="number" min="1" />
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:8px">
          <button class="btn btn-ghost" @click="showIssue = false">Cancel</button>
          <button class="btn btn-primary" @click="doIssue">Issue Book</button>
        </div>
      </div>
    </div>

    <div class="toast" :class="toast.type" v-if="toast.msg">{{ toast.msg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  getStats, getBorrows, getMembers, getBooks,
  getReservations, borrowBook, cancelReservation
} from '../store/api.js'
import { auth } from '../store/auth.js'

const stats = ref({})
const borrows = ref([])
const members = ref([])
const allBooks = ref([])
const reservations = ref([])
const showIssue = ref(false)
const reservationsSection = ref(null)
const toast = ref({ msg: '', type: '' })
const issueForm = ref({ member_id: '', book_id: '', issue_days: 14 })

const fmt = (d) => d
  ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  : '—'

const availableBooks = computed(() => allBooks.value.filter(b => b.available > 0))

const pendingReservations = computed(() =>
  reservations.value.filter(r => r.status === 'active')
)

const showToast = (msg, type = 'toast-success') => {
  toast.value = { msg, type }
  setTimeout(() => toast.value = { msg: '', type: '' }, 3000)
}

const load = async () => {
  const [s, b, m, bk, res] = await Promise.all([
    getStats(), getBorrows({ active: 'true' }),
    getMembers(), getBooks(), getReservations()
  ])
  stats.value = s.data
  borrows.value = b.data.slice(0, 10)
  members.value = m.data
  allBooks.value = bk.data
  reservations.value = res.data
}

const openIssue = () => {
  issueForm.value = { member_id: '', book_id: '', issue_days: 14 }
  showIssue.value = true
}

const onBookSelect = () => {
  const b = allBooks.value.find(x => x.id === issueForm.value.book_id)
  if (b) issueForm.value.issue_days = b.issue_days
}

const doIssue = async () => {
  if (!issueForm.value.member_id || !issueForm.value.book_id)
    return showToast('Please select a member and a book.', 'toast-error')
  try {
    await borrowBook(issueForm.value)
    showToast('Book issued successfully!')
    showIssue.value = false
    await load()
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed to issue book.', 'toast-error')
  }
}

const approveReservation = async (r) => {
  try {
    // borrowBook auto-fulfils the matching active reservation on the backend
    await borrowBook({ member_id: r.member_id, book_id: r.book_id, issue_days: 14 })
    showToast(`Approved — "${r.book_title}" issued to ${r.member_name}!`)
    await load()
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed to approve reservation.', 'toast-error')
  }
}

const cancelRes = async (r) => {
  try {
    await cancelReservation(r.id)
    showToast('Reservation cancelled.')
    await load()
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed to cancel.', 'toast-error')
  }
}

const scrollToReservations = () => {
  reservationsSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(load)
</script>

<style scoped>
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-card {
  background: #fff; border: 1px solid var(--border); border-radius: 14px;
  padding: 22px 20px; text-align: center; box-shadow: 0 2px 10px var(--shadow);
  transition: transform .18s;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-card.danger { border-color: #f9cccc; background: #fff8f8; }
.stat-card.warn { border-color: #ffe4b3; background: #fffbf0; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-val { font-size: 36px; font-weight: 700; color: var(--warm-brown); font-family: 'Playfair Display', serif; }
.stat-label { font-size: 13px; color: #9a8a7a; margin-top: 4px; }

.notif-badge {
  display: inline-flex; align-items: center; justify-content: center;
  background: #fff; color: var(--warm-brown);
  border-radius: 999px; font-size: 11px; font-weight: 700;
  min-width: 18px; height: 18px; padding: 0 5px; margin-left: 6px;
}

.badge-warn { background: #ffe4b3; color: #a06020; }

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none !important;
}
</style>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="serif">Dashboard</h1>
        <p>Welcome back, {{ auth.user?.username }}! Here's your library at a glance.</p>
      </div>
    </div>

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
      <div class="stat-card">
        <div class="stat-icon">📌</div>
        <div class="stat-val">{{ stats.active_reservations ?? '—' }}</div>
        <div class="stat-label">Reservations</div>
      </div>
    </div>

    <!-- Recent borrows -->
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStats, getBorrows } from '../store/api.js'
import { auth } from '../store/auth.js'

const stats = ref({})
const borrows = ref([])
const fmt = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'

onMounted(async () => {
  const [s, b] = await Promise.all([getStats(), getBorrows({ active: 'true' })])
  stats.value = s.data
  borrows.value = b.data.slice(0, 10)
})
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
</style>

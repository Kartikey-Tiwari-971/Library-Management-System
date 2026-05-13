<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="serif">Borrows</h1>
        <p>Issue & return books, track fines</p>
      </div>
      <button class="btn btn-primary" @click="openIssue">＋ Issue Book</button>
    </div>

    <!-- Filters -->
    <div class="card" style="margin-bottom:20px;padding:14px 18px;display:flex;gap:12px;align-items:center">
      <input v-model="search" placeholder="🔍  Search member or book…" style="flex:1;padding:9px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;background:var(--parchment);color:var(--ink)" />
      <select v-model="filterStatus" style="padding:9px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;background:var(--parchment);color:var(--ink)">
        <option value="">All Records</option>
        <option value="active">Active</option>
        <option value="overdue">Overdue</option>
        <option value="returned">Returned</option>
      </select>
    </div>

    <div class="card" v-if="filtered.length">
      <table>
        <thead>
          <tr>
            <th>Book</th>
            <th>Member</th>
            <th>Issue Date</th>
            <th>Due Date</th>
            <th>Return Date</th>
            <th>Reissues</th>
            <th>Fine</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filtered" :key="r.id" :class="{ 'row-overdue': r.overdue }">
            <td><strong>{{ r.book_title }}</strong></td>
            <td>{{ r.member_name }}</td>
            <td class="ts">{{ fmt(r.borrow_date) }}</td>
            <td class="ts" :style="{ color: r.overdue ? '#9b2020' : '' }">{{ fmt(r.due_date) }}</td>
            <td class="ts">{{ r.return_date ? fmt(r.return_date) : '—' }}</td>
            <td style="text-align:center">{{ r.reissue_count }}</td>
            <td>
              <span v-if="r.fine_amount > 0" style="color:#a04020;font-weight:600">₹{{ r.fine_amount }}</span>
              <span v-else style="color:#9a8a7a">—</span>
            </td>
            <td>
              <span class="badge" :class="statusClass(r)">{{ statusLabel(r) }}</span>
            </td>
            <td>
              <div style="display:flex;gap:6px">
                <button v-if="!r.returned" class="btn btn-sage btn-sm" @click="doReturn(r)">↩ Return</button>
                <button v-if="!r.returned && r.reissue_count < 2" class="btn btn-ghost btn-sm" @click="doReissue(r)">🔄 Reissue</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="empty-state" v-else><div class="icon">🔖</div><p>No borrow records.</p></div>

    <!-- Issue Modal -->
    <div class="modal-overlay" v-if="showIssue" @click.self="showIssue = false">
      <div class="modal" style="width:480px">
        <h2>Issue a Book</h2>
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
            <option v-for="b in availableBooks" :key="b.id" :value="b.id">{{ b.title }} ({{ b.available }} available)</option>
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
import { getBorrows, borrowBook, returnBook, reissueBook, getMembers, getBooks } from '../store/api.js'

const borrows = ref([])
const members = ref([])
const allBooks = ref([])
const search = ref('')
const filterStatus = ref('')
const showIssue = ref(false)
const toast = ref({ msg: '', type: '' })
const issueForm = ref({ member_id: '', book_id: '', issue_days: 14 })

const availableBooks = computed(() => allBooks.value.filter(b => b.available > 0))
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return borrows.value.filter(r => {
    const matchQ = !q || r.book_title.toLowerCase().includes(q) || r.member_name.toLowerCase().includes(q)
    const matchS = !filterStatus.value ||
      (filterStatus.value === 'active' && !r.returned && !r.overdue) ||
      (filterStatus.value === 'overdue' && r.overdue) ||
      (filterStatus.value === 'returned' && r.returned)
    return matchQ && matchS
  })
})

const fmt = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
const statusLabel = (r) => r.returned ? 'Returned' : r.overdue ? 'Overdue' : 'Active'
const statusClass = (r) => r.returned ? 'badge-returned' : r.overdue ? 'badge-overdue' : 'badge-available'

const showToast = (msg, type = 'toast-success') => {
  toast.value = { msg, type }; setTimeout(() => toast.value = { msg: '', type: '' }, 3000)
}

const load = async () => {
  const [b, m, bk] = await Promise.all([getBorrows(), getMembers(), getBooks()])
  borrows.value = b.data; members.value = m.data; allBooks.value = bk.data
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
  if (!issueForm.value.member_id || !issueForm.value.book_id) return showToast('Select member and book.', 'toast-error')
  try {
    await borrowBook(issueForm.value); showToast('Book issued!'); showIssue.value = false; await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

const doReturn = async (r) => {
  try {
    const res = await returnBook(r.id)
    const fine = res.data.fine_amount
    showToast(fine > 0 ? `Book returned. Fine: ₹${fine}` : 'Book returned!')
    await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

const doReissue = async (r) => {
  try {
    await reissueBook(r.id); showToast('Book reissued — due date extended!'); await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

onMounted(load)
</script>

<style scoped>
.ts { font-size: 12px; color: #7a6a5a; }
.row-overdue { background: #fff8f5; }
</style>

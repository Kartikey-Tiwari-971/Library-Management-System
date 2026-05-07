<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="serif">Students</h1>
        <p>Manage student accounts and pending approvals</p>
      </div>
      <button class="btn btn-primary" @click="openAdd">＋ Add Student</button>
    </div>

    <!-- Pending approvals -->
    <div v-if="pending.length" class="card pending-section">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
        <h3 class="serif" style="margin:0">⏳ Pending Approval</h3>
        <span class="badge badge-overdue">{{ pending.length }}</span>
      </div>
      <table>
        <thead><tr><th>Username</th><th>Email</th><th>Requested On</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="u in pending" :key="u.id">
            <td><strong>{{ u.username }}</strong></td>
            <td>{{ u.email }}</td>
            <td style="font-size:13px;color:#7a6a5a">{{ fmt(u.created_at) }}</td>
            <td>
              <div style="display:flex;gap:8px">
                <button class="btn btn-sage btn-sm" @click="approve(u)">✓ Approve</button>
                <button class="btn btn-danger btn-sm" @click="reject(u)">✗ Reject</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Members table -->
    <div class="card" style="margin-top:20px">
      <h3 class="serif" style="margin-bottom:16px">All Members</h3>
      <input v-model="search" placeholder="🔍  Search…" style="width:100%;margin-bottom:14px;padding:9px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;background:var(--parchment);color:var(--ink)" />
      <table v-if="filtered.length">
        <thead>
          <tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th><th>Joined</th><th>Active Borrows</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="m in filtered" :key="m.id">
            <td style="color:#9a8a7a;font-size:13px">{{ m.id }}</td>
            <td>
              <div style="display:flex;align-items:center;gap:10px">
                <div class="avatar">{{ m.name[0].toUpperCase() }}</div>
                <strong>{{ m.name }}</strong>
              </div>
            </td>
            <td style="color:#7a6a5a">{{ m.email }}</td>
            <td style="color:#7a6a5a">{{ m.phone || '—' }}</td>
            <td style="color:#9a8a7a;font-size:13px">{{ fmt(m.joined_on) }}</td>
            <td>
              <span class="badge" :class="m.active_borrows > 0 ? 'badge-overdue' : 'badge-available'">{{ m.active_borrows }}</span>
            </td>
            <td>
              <div style="display:flex;gap:8px">
                <button class="btn btn-ghost btn-sm" @click="openEdit(m)">✏️ Edit</button>
                <button class="btn btn-danger btn-sm" @click="confirmDel(m)">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="empty-state" v-else><div class="icon">👥</div><p>No members yet.</p></div>
    </div>

    <!-- Add Student Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal">
        <h2>{{ editing ? 'Edit Member' : 'Add Student Directly' }}</h2>
        <div class="form-group"><label>Full Name *</label><input v-model="form.name" placeholder="e.g. Priya Sharma" /></div>
        <div class="form-group"><label>Email *</label><input v-model="form.email" type="email" /></div>
        <div class="form-group"><label>Phone</label><input v-model="form.phone" /></div>
        <template v-if="!editing">
          <div class="form-group"><label>Username *</label><input v-model="form.username" /></div>
          <div class="form-group"><label>Password</label><input v-model="form.password" type="password" placeholder="Default: student123" /></div>
        </template>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:8px">
          <button class="btn btn-ghost" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="save">{{ editing ? 'Save' : 'Add Student' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div class="modal-overlay" v-if="delTarget" @click.self="delTarget = null">
      <div class="modal" style="width:380px">
        <h2>Remove Member?</h2>
        <p style="color:#7a6a5a;margin-bottom:20px">Remove <strong>{{ delTarget?.name }}</strong>?</p>
        <div style="display:flex;gap:10px;justify-content:flex-end">
          <button class="btn btn-ghost" @click="delTarget = null">Keep</button>
          <button class="btn btn-danger" @click="doDelete">Remove</button>
        </div>
      </div>
    </div>

    <div class="toast" :class="toast.type" v-if="toast.msg">{{ toast.msg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPendingStudents, approveStudent, rejectStudent, addStudentDirect, getMembers, updateMember, deleteMember } from '../store/api.js'

const pending = ref([])
const members = ref([])
const search = ref('')
const showModal = ref(false)
const editing = ref(null)
const delTarget = ref(null)
const toast = ref({ msg: '', type: '' })
const form = ref({ name: '', email: '', phone: '', username: '', password: '' })

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return members.value.filter(m => !q || m.name.toLowerCase().includes(q) || m.email.toLowerCase().includes(q))
})

const fmt = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
const showToast = (msg, type = 'toast-success') => {
  toast.value = { msg, type }; setTimeout(() => toast.value = { msg: '', type: '' }, 3000)
}

const load = async () => {
  const [p, m] = await Promise.all([getPendingStudents(), getMembers()])
  pending.value = p.data; members.value = m.data
}

const approve = async (u) => {
  try { await approveStudent(u.id); showToast(`${u.username} approved!`); await load() }
  catch { showToast('Error', 'toast-error') }
}
const reject = async (u) => {
  try { await rejectStudent(u.id); showToast(`${u.username} rejected.`); await load() }
  catch { showToast('Error', 'toast-error') }
}

const openAdd = () => {
  editing.value = null
  form.value = { name: '', email: '', phone: '', username: '', password: '' }
  showModal.value = true
}
const openEdit = (m) => {
  editing.value = m; form.value = { ...m }; showModal.value = true
}

const save = async () => {
  if (!form.value.name || !form.value.email) return showToast('Name and email required.', 'toast-error')
  try {
    if (editing.value) await updateMember(editing.value.id, form.value)
    else await addStudentDirect(form.value)
    showToast(editing.value ? 'Updated!' : 'Student added!'); showModal.value = false; await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

const confirmDel = (m) => delTarget.value = m
const doDelete = async () => {
  try { await deleteMember(delTarget.value.id); showToast('Removed.'); delTarget.value = null; await load() }
  catch { showToast('Error', 'toast-error') }
}

onMounted(load)
</script>

<style scoped>
.pending-section { border: 2px solid #ffe4b3; background: #fffbf0; }
.avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--amber); color: #fff;
  font-weight: 600; font-size: 14px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
</style>

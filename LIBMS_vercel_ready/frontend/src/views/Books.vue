<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="serif">Books</h1>
        <p>{{ books.length }} book{{ books.length !== 1 ? 's' : '' }} in the library</p>
      </div>
      <button v-if="auth.isLibrarian" class="btn btn-primary" @click="openAdd">＋ Add Book</button>
    </div>

    <div class="card" style="margin-bottom:20px;padding:14px 18px;display:flex;gap:12px;align-items:center">
      <input v-model="search" placeholder="🔍  Search by title or author…" style="flex:1;padding:9px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;background:var(--parchment);color:var(--ink)" />
      <select v-model="filterGenre" style="padding:9px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;background:var(--parchment);color:var(--ink)">
        <option value="">All Genres</option>
        <option v-for="g in genres" :key="g">{{ g }}</option>
      </select>
      <label style="display:flex;align-items:center;gap:6px;font-size:14px;color:#7a6a5a;white-space:nowrap">
        <input type="checkbox" v-model="onlyAvailable" /> Available only
      </label>
    </div>

    <div class="books-grid" v-if="filtered.length">
      <div class="book-card" v-for="b in filtered" :key="b.id">
        <div class="book-cover">
          <span class="cover-icon">{{ genreIcon(b.genre) }}</span>
          <span class="genre-tag">{{ b.genre }}</span>
        </div>
        <div class="book-info">
          <div class="book-title">{{ b.title }}</div>
          <div class="book-author">by {{ b.author }}</div>
          <div class="book-isbn" v-if="b.isbn">ISBN: {{ b.isbn }}</div>
          <div class="book-meta">
            <span class="badge" :class="b.available > 0 ? 'badge-available' : 'badge-unavailable'">
              {{ b.available > 0 ? `${b.available} available` : 'Unavailable' }}
            </span>
            <span style="font-size:12px;color:#9a8a7a">{{ b.copies }} total</span>
          </div>
          <div class="book-meta" style="font-size:12px;color:#9a8a7a;margin-top:4px" v-if="auth.isLibrarian">
            Issue: {{ b.issue_days }}d • Fine: ₹{{ b.fine_per_day }}/day
          </div>
        </div>
        <div class="book-actions">
          <!-- Librarian actions -->
          <template v-if="auth.isLibrarian">
            <div class="copies-ctrl">
              <button class="icon-btn" @click="changeCopies(b, -1)">−</button>
              <span>{{ b.copies }}</span>
              <button class="icon-btn" @click="changeCopies(b, 1)">＋</button>
            </div>
            <button class="btn btn-ghost btn-sm" @click="openEdit(b)">✏️ Edit</button>
            <button class="btn btn-danger btn-sm" @click="confirmDelete(b)">🗑️</button>
          </template>
          <!-- Student actions -->
          <template v-else>
            <button v-if="b.available > 0" class="btn btn-ghost btn-sm" disabled>Borrow via librarian</button>
            <button class="btn btn-primary btn-sm" @click="doReserve(b)" v-if="b.available === 0">📌 Reserve</button>
            <button class="btn btn-ghost btn-sm" @click="doReserve(b)" v-else>📌 Reserve</button>
          </template>
        </div>
      </div>
    </div>
    <div class="empty-state" v-else>
      <div class="icon">📚</div>
      <p>No books found.</p>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal" style="width:520px">
        <h2>{{ editing ? 'Edit Book' : 'Add New Book' }}</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="form-group" style="grid-column:1/-1">
            <label>Title *</label>
            <input v-model="form.title" placeholder="Book title" />
          </div>
          <div class="form-group">
            <label>Author *</label>
            <input v-model="form.author" placeholder="Author name" />
          </div>
          <div class="form-group">
            <label>Genre</label>
            <input v-model="form.genre" placeholder="e.g. Fiction" />
          </div>
          <div class="form-group">
            <label>ISBN</label>
            <input v-model="form.isbn" placeholder="978-..." />
          </div>
          <div class="form-group">
            <label>Total Copies</label>
            <input v-model.number="form.copies" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Issue Period (days)</label>
            <input v-model.number="form.issue_days" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Fine per day (₹)</label>
            <input v-model.number="form.fine_per_day" type="number" min="0" step="0.5" />
          </div>
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:8px">
          <button class="btn btn-ghost" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="save">{{ editing ? 'Save' : 'Add Book' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div class="modal-overlay" v-if="delTarget" @click.self="delTarget = null">
      <div class="modal" style="width:380px">
        <h2>Remove Book?</h2>
        <p style="color:#7a6a5a;margin-bottom:20px">Remove <strong>{{ delTarget?.title }}</strong>? All borrow records will be deleted.</p>
        <div style="display:flex;gap:10px;justify-content:flex-end">
          <button class="btn btn-ghost" @click="delTarget = null">Cancel</button>
          <button class="btn btn-danger" @click="doDelete">Yes, Remove</button>
        </div>
      </div>
    </div>

    <div class="toast" :class="toast.type" v-if="toast.msg">{{ toast.msg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getBooks, addBook, updateBook, deleteBook, adjustCopies, reserveBook } from '../store/api.js'
import { auth } from '../store/auth.js'

const books = ref([])
const search = ref('')
const filterGenre = ref('')
const onlyAvailable = ref(false)
const showModal = ref(false)
const editing = ref(null)
const delTarget = ref(null)
const toast = ref({ msg: '', type: '' })
const form = ref({ title: '', author: '', genre: '', isbn: '', copies: 1, issue_days: 14, fine_per_day: 2 })

const genres = computed(() => [...new Set(books.value.map(b => b.genre))].sort())
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return books.value.filter(b =>
    (!q || b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)) &&
    (!filterGenre.value || b.genre === filterGenre.value) &&
    (!onlyAvailable.value || b.available > 0)
  )
})

const genreIcon = (g) => ({ Fiction: '📖', 'Sci-Fi': '🚀', History: '🏛️', 'Self-Help': '💡', Finance: '💰', General: '📚' }[g] || '📚')

const showToast = (msg, type = 'toast-success') => {
  toast.value = { msg, type }
  setTimeout(() => toast.value = { msg: '', type: '' }, 3000)
}

const load = async () => {
  const r = await getBooks()
  books.value = r.data
}

const openAdd = () => {
  editing.value = null
  form.value = { title: '', author: '', genre: 'Fiction', isbn: '', copies: 1, issue_days: 14, fine_per_day: 2 }
  showModal.value = true
}
const openEdit = (b) => {
  editing.value = b
  form.value = { ...b }
  showModal.value = true
}

const save = async () => {
  if (!form.value.title || !form.value.author) return showToast('Title and author required.', 'toast-error')
  try {
    if (editing.value) await updateBook(editing.value.id, form.value)
    else await addBook(form.value)
    showToast(editing.value ? 'Book updated!' : 'Book added!')
    showModal.value = false; await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

const changeCopies = async (b, delta) => {
  try {
    await adjustCopies(b.id, delta)
    await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

const confirmDelete = (b) => delTarget.value = b
const doDelete = async () => {
  try {
    await deleteBook(delTarget.value.id)
    showToast('Book removed.'); delTarget.value = null; await load()
  } catch { showToast('Could not remove.', 'toast-error') }
}

const doReserve = async (b) => {
  try {
    await reserveBook({ book_id: b.id })
    showToast(`📌 Reserved "${b.title}"!`)
    await load()
  } catch (e) { showToast(e.response?.data?.error || 'Error', 'toast-error') }
}

onMounted(load)
</script>

<style scoped>
.books-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }
.book-card {
  background: #fff; border: 1px solid var(--border); border-radius: 14px;
  overflow: hidden; box-shadow: 0 2px 10px var(--shadow); display: flex; flex-direction: column;
  transition: transform .18s, box-shadow .18s;
}
.book-card:hover { transform: translateY(-4px); box-shadow: 0 8px 28px var(--shadow); }
.book-cover {
  background: linear-gradient(135deg, var(--warm-brown), #9b6a48);
  padding: 24px 20px; display: flex; align-items: center; justify-content: space-between;
}
.cover-icon { font-size: 36px; }
.genre-tag {
  font-size: 11px; background: rgba(255,255,255,.2); color: #f5ece0;
  padding: 3px 10px; border-radius: 99px; letter-spacing: .4px;
}
.book-info { padding: 16px 18px; flex: 1; }
.book-title { font-weight: 600; font-size: 15px; margin-bottom: 4px; line-height: 1.3; }
.book-author { font-size: 13px; color: #7a6a5a; margin-bottom: 6px; }
.book-isbn { font-size: 11px; color: #aaa; margin-bottom: 8px; }
.book-meta { display: flex; align-items: center; gap: 10px; }
.book-actions {
  padding: 12px 18px; border-top: 1px solid var(--border);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.copies-ctrl {
  display: flex; align-items: center; gap: 8px;
  background: var(--cream); border-radius: 8px; padding: 4px 12px;
  font-weight: 600; font-size: 15px; color: var(--warm-brown);
}
.icon-btn {
  background: none; border: none; font-size: 18px; color: var(--amber);
  cursor: pointer; padding: 0 2px; line-height: 1; transition: color .15s;
}
.icon-btn:hover { color: #b57820; }
</style>

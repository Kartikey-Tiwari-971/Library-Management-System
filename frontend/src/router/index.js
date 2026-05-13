import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../store/auth.js'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Books from '../views/Books.vue'
import Members from '../views/Members.vue'
import Borrows from '../views/Borrows.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import Students from '../views/Students.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Dashboard, meta: { role: 'librarian' } },
  { path: '/books', component: Books },
  { path: '/members', component: Members, meta: { role: 'librarian' } },
  { path: '/borrows', component: Borrows, meta: { role: 'librarian' } },
  { path: '/students', component: Students, meta: { role: 'librarian' } },
  { path: '/my', component: StudentDashboard, meta: { role: 'student' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  if (!auth.loaded) await auth.init()
  if (to.meta.public) return true
  if (!auth.user) return '/login'
  if (to.meta.role && auth.user.role !== to.meta.role) {
    return auth.isLibrarian ? '/' : '/my'
  }
  return true
})

export default router

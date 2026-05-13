import { reactive } from 'vue'
import { getMe } from './api.js'

export const auth = reactive({
  user: null,
  loaded: false,
  async init() {
    try {
      const r = await getMe()
      this.user = r.data.user
    } catch { this.user = null }
    this.loaded = true
  },
  get isLibrarian() { return this.user?.role === 'librarian' },
  get isStudent() { return this.user?.role === 'student' },
  get memberId() { return this.user?.member_id },
})

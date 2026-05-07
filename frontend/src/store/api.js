import axios from 'axios'

const api = axios.create({ baseURL: '/api', withCredentials: true })

// Auth
export const login = (data) => api.post('/auth/login', data)
export const logout = () => api.post('/auth/logout')
export const getMe = () => api.get('/auth/me')
export const registerStudent = (data) => api.post('/auth/register', data)

// Students management (librarian)
export const getPendingStudents = () => api.get('/students/pending')
export const approveStudent = (id) => api.post(`/students/${id}/approve`)
export const rejectStudent = (id) => api.post(`/students/${id}/reject`)
export const addStudentDirect = (data) => api.post('/students', data)

// Books
export const getBooks = (params) => api.get('/books', { params })
export const getBook = (id) => api.get(`/books/${id}`)
export const addBook = (data) => api.post('/books', data)
export const updateBook = (id, data) => api.put(`/books/${id}`, data)
export const adjustCopies = (id, delta) => api.patch(`/books/${id}/copies`, { delta })
export const deleteBook = (id) => api.delete(`/books/${id}`)

// Members
export const getMembers = () => api.get('/members')
export const getMember = (id) => api.get(`/members/${id}`)
export const addMember = (data) => api.post('/members', data)
export const updateMember = (id, data) => api.put(`/members/${id}`, data)
export const deleteMember = (id) => api.delete(`/members/${id}`)

// Borrows
export const getBorrows = (params) => api.get('/borrows', { params })
export const borrowBook = (data) => api.post('/borrow', data)
export const returnBook = (id) => api.post(`/return/${id}`)
export const reissueBook = (id) => api.post(`/reissue/${id}`)

// Reservations
export const reserveBook = (data) => api.post('/reserve', data)
export const getReservations = () => api.get('/reservations')
export const cancelReservation = (id) => api.post(`/reservations/${id}/cancel`)

// Stats
export const getStats = () => api.get('/stats')

# Biblios — Enhanced Library Management System

## What's New

### Login System
- **Librarian** login with username/password
- **Student** self-registration (sends a "pending" request)
- Librarian approves or rejects student requests
- Default librarian: `librarian / admin123`

### Librarian Features
- Dashboard with stats: total books, members, active borrows, overdue, pending approvals, reservations
- Add, edit, delete books with configurable **issue period (days)** and **fine per day (₹)**
- **Increase/decrease copies** available per book via +/− controls
- View all currently issued books with issue date and member name
- Issue books to members, set custom issue period per issuance
- Return books — fine is auto-calculated and frozen at return time
- Approve/reject student join requests, or add students directly
- View and manage all reservations

### Student Features
- **My Library dashboard**: active borrows, history, reservations — all in one place
- **Check availability** of any book (available count shown on Books page)
- **Reserve a book** in advance (from the Books page)
- **Reissue** a book up to 2 times (extends due date by issue_days each time)
- **Borrow history** with full timestamps: issued on, due date, returned on
- **Fine tracker**: see accruing fine for overdue books in real time
- Cancel active reservations

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Architecture
- **Backend**: Flask + SQLAlchemy + SQLite
- **Frontend**: Vue 3 + Vite + Axios
- **Auth**: Flask sessions (cookie-based)
- **Database**: SQLite (`library.db`) — 4 tables: users, books, members, borrow_records, reservations

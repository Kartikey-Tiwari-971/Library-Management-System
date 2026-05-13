from flask import Flask, jsonify, request, session
from flask_cors import CORS
from database import db, User, Book, Member, BorrowRecord, Reservation
from datetime import datetime, timedelta
import os
import functools

app = Flask(__name__)

# Secret key — set SECRET_KEY env var in Vercel dashboard
app.secret_key = os.environ.get("SECRET_KEY", "libms-dev-secret-change-me")

# Database — uses Neon PostgreSQL in production, SQLite locally
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    # Neon gives postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'library.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

# Sessions must work cross-origin when frontend is on Vercel
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True

CORS(app, supports_credentials=True, origins=[FRONTEND_URL, "http://localhost:5173"])

db.init_app(app)

with app.app_context():
    db.create_all()
    # Seed default librarian
    if User.query.count() == 0:
        lib = User(username="librarian", email="librarian@library.com", role="librarian", status="approved")
        lib.set_password("admin123")
        db.session.add(lib)
        db.session.commit()
    # Seed books if empty
    if Book.query.count() == 0:
        seeds = []
            
        db.session.bulk_save_objects(seeds)
        db.session.commit()


# ── AUTH HELPERS ────────────────────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required."}), 401
        return f(*args, **kwargs)
    return wrapper

def librarian_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required."}), 401
        u = User.query.get(session["user_id"])
        if not u or u.role != "librarian":
            return jsonify({"error": "Librarian access only."}), 403
        return f(*args, **kwargs)
    return wrapper

def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None


# ── AUTH ENDPOINTS ──────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    u = User.query.filter_by(username=data.get("username", "")).first()
    if not u or not u.check_password(data.get("password", "")):
        return jsonify({"error": "Invalid username or password."}), 401
    if u.status != "approved":
        return jsonify({"error": "Your account is pending librarian approval."}), 403
    session["user_id"] = u.id
    return jsonify({"user": u.to_dict()})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})


@app.route("/api/auth/me", methods=["GET"])
def me():
    u = current_user()
    if not u:
        return jsonify({"user": None})
    return jsonify({"user": u.to_dict()})


@app.route("/api/auth/register", methods=["POST"])
def register_student():
    """Student self-signup — creates a pending account."""
    data = request.json
    if User.query.filter_by(username=data.get("username", "")).first():
        return jsonify({"error": "Username already taken."}), 400
    if User.query.filter_by(email=data.get("email", "")).first():
        return jsonify({"error": "Email already registered."}), 400
    # Create member profile
    member = Member(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone", ""),
    )
    db.session.add(member)
    db.session.flush()
    u = User(
        username=data["username"],
        email=data["email"],
        role="student",
        member_id=member.id,
        status="pending",
    )
    u.set_password(data["password"])
    db.session.add(u)
    db.session.commit()
    return jsonify({"message": "Registration submitted! Please wait for librarian approval."}), 201


# ── STUDENT REQUESTS (pending approvals) ────────────────────────────────────

@app.route("/api/students/pending", methods=["GET"])
@librarian_required
def get_pending_students():
    users = User.query.filter_by(role="student", status="pending").all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/students/<int:user_id>/approve", methods=["POST"])
@librarian_required
def approve_student(user_id):
    u = User.query.get_or_404(user_id)
    u.status = "approved"
    db.session.commit()
    return jsonify(u.to_dict())


@app.route("/api/students/<int:user_id>/reject", methods=["POST"])
@librarian_required
def reject_student(user_id):
    u = User.query.get_or_404(user_id)
    u.status = "rejected"
    db.session.commit()
    return jsonify(u.to_dict())


# Librarian adds student directly (auto-approved)
@app.route("/api/students", methods=["POST"])
@librarian_required
def add_student_direct():
    data = request.json
    if User.query.filter_by(username=data.get("username", "")).first():
        return jsonify({"error": "Username already taken."}), 400
    if Member.query.filter_by(email=data.get("email", "")).first():
        return jsonify({"error": "Email already registered."}), 400
    member = Member(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone", ""),
    )
    db.session.add(member)
    db.session.flush()
    u = User(
        username=data["username"],
        email=data["email"],
        role="student",
        member_id=member.id,
        status="approved",
    )
    u.set_password(data.get("password", "student123"))
    db.session.add(u)
    db.session.commit()
    return jsonify({"user": u.to_dict(), "member": member.to_dict()}), 201


# ── BOOKS ──────────────────────────────────────────────────────────────────

@app.route("/api/books", methods=["GET"])
@login_required
def get_books():
    q = request.args.get("q", "").lower()
    genre = request.args.get("genre", "")
    books = Book.query.all()
    if q:
        books = [b for b in books if q in b.title.lower() or q in b.author.lower()]
    if genre:
        books = [b for b in books if b.genre == genre]
    return jsonify([b.to_dict() for b in books])


@app.route("/api/books/<int:book_id>", methods=["GET"])
@login_required
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@app.route("/api/books", methods=["POST"])
@librarian_required
def add_book():
    data = request.json
    book = Book(
        title=data["title"],
        author=data["author"],
        genre=data.get("genre", "General"),
        isbn=data.get("isbn", ""),
        copies=int(data.get("copies", 1)),
        issue_days=int(data.get("issue_days", 14)),
        fine_per_day=float(data.get("fine_per_day", 2.0)),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@app.route("/api/books/<int:book_id>", methods=["PUT"])
@librarian_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.json
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.genre = data.get("genre", book.genre)
    book.isbn = data.get("isbn", book.isbn)
    book.copies = int(data.get("copies", book.copies))
    book.issue_days = int(data.get("issue_days", book.issue_days))
    book.fine_per_day = float(data.get("fine_per_day", book.fine_per_day))
    db.session.commit()
    return jsonify(book.to_dict())


@app.route("/api/books/<int:book_id>/copies", methods=["PATCH"])
@librarian_required
def adjust_copies(book_id):
    """Increment or decrement available copies."""
    book = Book.query.get_or_404(book_id)
    delta = int(request.json.get("delta", 0))
    new_val = book.copies + delta
    if new_val < 0:
        return jsonify({"error": "Copies cannot go below 0."}), 400
    book.copies = new_val
    db.session.commit()
    return jsonify(book.to_dict())


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
@librarian_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book removed."})


# ── MEMBERS ────────────────────────────────────────────────────────────────

@app.route("/api/members", methods=["GET"])
@librarian_required
def get_members():
    members = Member.query.all()
    return jsonify([m.to_dict() for m in members])


@app.route("/api/members/<int:member_id>", methods=["GET"])
@login_required
def get_member(member_id):
    u = current_user()
    # Students can only view their own profile
    if u.role == "student" and u.member_id != member_id:
        return jsonify({"error": "Access denied."}), 403
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())


@app.route("/api/members", methods=["POST"])
@librarian_required
def add_member():
    data = request.json
    member = Member(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone", ""),
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@app.route("/api/members/<int:member_id>", methods=["PUT"])
@librarian_required
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.json
    member.name = data.get("name", member.name)
    member.email = data.get("email", member.email)
    member.phone = data.get("phone", member.phone)
    db.session.commit()
    return jsonify(member.to_dict())


@app.route("/api/members/<int:member_id>", methods=["DELETE"])
@librarian_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed."})


# ── BORROW / RETURN / REISSUE ───────────────────────────────────────────────

@app.route("/api/borrow", methods=["POST"])
@librarian_required
def borrow_book():
    data = request.json
    book = Book.query.get_or_404(data["book_id"])
    member = Member.query.get_or_404(data["member_id"])

    if book.available_copies() <= 0:
        return jsonify({"error": "No copies available right now."}), 400

    # Fulfill active reservation if exists
    res = Reservation.query.filter_by(book_id=book.id, member_id=member.id, status="active").first()
    if res:
        res.status = "fulfilled"

    issue_days = data.get("issue_days", book.issue_days)
    due = datetime.utcnow() + timedelta(days=int(issue_days))
    record = BorrowRecord(book_id=book.id, member_id=member.id, due_date=due)
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@app.route("/api/return/<int:record_id>", methods=["POST"])
@librarian_required
def return_book(record_id):
    record = BorrowRecord.query.get_or_404(record_id)
    if record.returned:
        return jsonify({"error": "Already returned."}), 400
    record.returned = True
    record.return_date = datetime.utcnow()
    # Freeze fine at return time
    record.fine_amount = record.calculated_fine()
    db.session.commit()
    return jsonify(record.to_dict())


@app.route("/api/reissue/<int:record_id>", methods=["POST"])
@login_required
def reissue_book(record_id):
    record = BorrowRecord.query.get_or_404(record_id)
    u = current_user()
    # Students can only reissue their own books
    if u.role == "student" and record.member_id != u.member_id:
        return jsonify({"error": "Access denied."}), 403
    if record.returned:
        return jsonify({"error": "Book already returned."}), 400
    if record.reissue_count >= 2:
        return jsonify({"error": "Maximum reissues (2) reached."}), 400
    extra_days = record.book.issue_days if record.book else 14
    record.due_date = record.due_date + timedelta(days=extra_days)
    record.reissue_count += 1
    db.session.commit()
    return jsonify(record.to_dict())


@app.route("/api/borrows", methods=["GET"])
@login_required
def get_borrows():
    u = current_user()
    active_only = request.args.get("active") == "true"
    member_id = request.args.get("member_id")

    records = BorrowRecord.query
    if u.role == "student":
        records = records.filter_by(member_id=u.member_id)
    elif member_id:
        records = records.filter_by(member_id=int(member_id))

    if active_only:
        records = records.filter_by(returned=False)

    records = records.order_by(BorrowRecord.borrow_date.desc()).all()
    return jsonify([r.to_dict() for r in records])


# ── RESERVATIONS ────────────────────────────────────────────────────────────

@app.route("/api/reserve", methods=["POST"])
@login_required
def reserve_book():
    data = request.json
    u = current_user()
    book_id = data.get("book_id")
    # Students can only reserve for themselves
    if u.role == "student":
        member_id = u.member_id
    else:
        member_id = data.get("member_id")

    book = Book.query.get_or_404(book_id)
    member = Member.query.get_or_404(member_id)

    existing = Reservation.query.filter_by(book_id=book_id, member_id=member_id, status="active").first()
    if existing:
        return jsonify({"error": "You already have an active reservation for this book."}), 400

    res = Reservation(book_id=book_id, member_id=member_id)
    db.session.add(res)
    db.session.commit()
    return jsonify(res.to_dict()), 201


@app.route("/api/reservations", methods=["GET"])
@login_required
def get_reservations():
    u = current_user()
    if u.role == "student":
        recs = Reservation.query.filter_by(member_id=u.member_id).order_by(Reservation.reserved_on.desc()).all()
    else:
        recs = Reservation.query.order_by(Reservation.reserved_on.desc()).all()
    return jsonify([r.to_dict() for r in recs])


@app.route("/api/reservations/<int:res_id>/cancel", methods=["POST"])
@login_required
def cancel_reservation(res_id):
    res = Reservation.query.get_or_404(res_id)
    u = current_user()
    if u.role == "student" and res.member_id != u.member_id:
        return jsonify({"error": "Access denied."}), 403
    res.status = "cancelled"
    db.session.commit()
    return jsonify(res.to_dict())


# ── STATS ──────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
@login_required
def get_stats():
    u = current_user()
    if u.role == "librarian":
        return jsonify({
            "total_books": Book.query.count(),
            "total_members": Member.query.count(),
            "active_borrows": BorrowRecord.query.filter_by(returned=False).count(),
            "overdue": BorrowRecord.query.filter(
                BorrowRecord.returned == False,
                BorrowRecord.due_date < datetime.utcnow()
            ).count(),
            "pending_students": User.query.filter_by(role="student", status="pending").count(),
            "active_reservations": Reservation.query.filter_by(status="active").count(),
        })
    else:
        mid = u.member_id
        return jsonify({
            "active_borrows": BorrowRecord.query.filter_by(member_id=mid, returned=False).count(),
            "total_borrows": BorrowRecord.query.filter_by(member_id=mid).count(),
            "reservations": Reservation.query.filter_by(member_id=mid, status="active").count(),
            "overdue": BorrowRecord.query.filter(
                BorrowRecord.member_id == mid,
                BorrowRecord.returned == False,
                BorrowRecord.due_date < datetime.utcnow()
            ).count(),
        })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

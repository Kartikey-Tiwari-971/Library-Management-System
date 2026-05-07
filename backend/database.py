from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Unified auth table for both librarians and students."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'librarian' | 'student'
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=True)
    status = db.Column(db.String(20), default="approved")  # 'pending' | 'approved' | 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    member = db.relationship("Member", backref="user", uselist=False, foreign_keys=[member_id])

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "member_id": self.member_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(80), default="General")
    isbn = db.Column(db.String(20), default="")
    copies = db.Column(db.Integer, default=1)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    issue_days = db.Column(db.Integer, default=14)
    fine_per_day = db.Column(db.Float, default=2.0)

    borrows = db.relationship("BorrowRecord", backref="book", lazy=True, cascade="all, delete-orphan")
    reservations = db.relationship("Reservation", backref="book", lazy=True, cascade="all, delete-orphan")

    def available_copies(self):
        active = BorrowRecord.query.filter_by(book_id=self.id, returned=False).count()
        reserved = Reservation.query.filter_by(book_id=self.id, status="active").count()
        return max(0, self.copies - active - reserved)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "isbn": self.isbn,
            "copies": self.copies,
            "available": self.available_copies(),
            "added_on": self.added_on.isoformat(),
            "issue_days": self.issue_days,
            "fine_per_day": self.fine_per_day,
        }


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    phone = db.Column(db.String(20), default="")
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

    borrows = db.relationship("BorrowRecord", backref="member", lazy=True, cascade="all, delete-orphan")
    reservations = db.relationship("Reservation", backref="member", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        active = BorrowRecord.query.filter_by(member_id=self.id, returned=False).count()
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "joined_on": self.joined_on.isoformat(),
            "active_borrows": active,
        }


class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime, nullable=True)
    returned = db.Column(db.Boolean, default=False)
    reissue_count = db.Column(db.Integer, default=0)
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)

    def is_overdue(self):
        if self.returned:
            return False
        return datetime.utcnow() > self.due_date

    def calculated_fine(self):
        if self.returned:
            return self.fine_amount
        if not self.is_overdue():
            return 0.0
        days_late = (datetime.utcnow() - self.due_date).days
        rate = self.book.fine_per_day if self.book else 2.0
        return round(days_late * rate, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else "",
            "book_author": self.book.author if self.book else "",
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else "",
            "member_email": self.member.email if self.member else "",
            "borrow_date": self.borrow_date.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "returned": self.returned,
            "overdue": self.is_overdue(),
            "reissue_count": self.reissue_count,
            "fine_amount": self.calculated_fine(),
            "fine_paid": self.fine_paid,
        }


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    reserved_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")  # 'active' | 'fulfilled' | 'cancelled'

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else "",
            "book_author": self.book.author if self.book else "",
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else "",
            "reserved_on": self.reserved_on.isoformat(),
            "status": self.status,
        }

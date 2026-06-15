from datetime import datetime
from typing import Optional
from backend.extensions import db


class User(db.Model):
    """Internal user model for authentication and role management."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="User", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "User",
    ) -> None:
        """Explicit constructor so type checkers recognize all column kwargs.

        SQLAlchemy generates this automatically at runtime; we declare it
        explicitly only to satisfy static analysis tools (Pyrefly / Pylance).
        """
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }

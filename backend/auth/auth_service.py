from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from backend.extensions import db
from backend.models.user_model import User
from backend.utils.encryption import hash_password, check_password


def register_user(username: str, email: str, password: str, role: str = "User") -> Optional[User]:
    """Register a new application user."""
    password_hash = hash_password(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except IntegrityError:
        db.session.rollback()
        return None


def authenticate_user(login_id: str, password: str) -> Optional[User]:
    """
    Authenticate a user using either username or email.
    """

    user = User.query.filter(
        or_(
            User.username == login_id,
            User.email == login_id
        )
    ).first()

    if user and check_password(password, user.password_hash):
        return user

    return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """Retrieve a user record by ID."""
    return User.query.get(user_id)
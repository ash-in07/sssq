import bcrypt


def hash_password(password: str) -> str:
    """Hash the password using bcrypt for secure storage."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a hashed value."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

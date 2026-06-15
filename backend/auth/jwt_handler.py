from flask_jwt_extended import create_access_token
from datetime import timedelta


def create_user_token(identity: int, role: str) -> str:
    """Create a JWT access token for a user identity and role."""

    additional_claims = {
        "user_id": identity,
        "role": role
    }

    return create_access_token(
        identity=str(identity),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=2),
    )
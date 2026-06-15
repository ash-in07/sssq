#backend/models/migration_model.py
from datetime import datetime
from backend.extensions import db


class Migration(db.Model):
    """Stores metadata for active migration jobs."""
    __tablename__ = "migrations"

    id = db.Column(db.Integer, primary_key=True)
    migration_type = db.Column(db.String(120), nullable=False)
    source_db = db.Column(db.String(255), nullable=False)
    target_db = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(80), nullable=False, default="pending")
    error_message = db.Column(db.Text, nullable=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "migration_type": self.migration_type,
            "source_db": self.source_db,
            "target_db": self.target_db,
            "status": self.status,
            "error_message": self.error_message,
            "report_id": self.report_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

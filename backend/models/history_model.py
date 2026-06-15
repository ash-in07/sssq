from datetime import datetime
from backend.extensions import db


class MigrationHistory(db.Model):
    """Stores migration history, validation results, and execution metadata."""
    __tablename__ = "migration_history"

    id = db.Column(db.Integer, primary_key=True)
    migration_type = db.Column(db.String(120), nullable=False)
    source_db = db.Column(db.String(255), nullable=False)
    target_db = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    errors = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    report_summary = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "migration_type": self.migration_type,
            "source_db": self.source_db,
            "target_db": self.target_db,
            "status": self.status,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
            "report_summary": self.report_summary,
        }

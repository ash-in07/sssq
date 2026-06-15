from datetime import datetime
from typing import Optional
from backend.extensions import db


class Report(db.Model):
    """Stores report metadata and exported file paths."""
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    migration_id = db.Column(db.Integer, db.ForeignKey("migrations.id"), nullable=True)
    name = db.Column(db.String(255), nullable=False, default='Unnamed Report')
    generated_by = db.Column(db.String(255), nullable=False, default='System')
    file_path = db.Column(db.String(512), nullable=True)
    report_format = db.Column(db.String(50), nullable=False, default='UNKNOWN')
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self,
        name: str,
        report_format: str,
        generated_by: str = 'System',
        migration_id: Optional[int] = None,
        file_path: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        """Explicit constructor for Report model.

        Parameters reflect database columns.
        """
        self.name = name
        self.report_format = report_format
        self.generated_by = generated_by
        self.migration_id = migration_id
        self.file_path = file_path
        self.summary = summary

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "migration_id": self.migration_id,
            "name": self.name,
            "generated_by": self.generated_by,
            "report_format": self.report_format,
            "file_path": self.file_path,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
        }

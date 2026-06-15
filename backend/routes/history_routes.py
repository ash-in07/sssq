from flask_restful import Resource
from flask_jwt_extended import jwt_required

from backend.models.history_model import MigrationHistory
from backend.extensions import db


class HistoryListResource(Resource):
    """Endpoint to list migration history records."""

    @jwt_required()
    def get(self):
        history = [
            record.to_dict()
            for record in MigrationHistory.query.order_by(
                MigrationHistory.timestamp.desc()
            ).all()
        ]

        return {
            "history": history,
            "count": len(history)
        }, 200


class HistoryDeleteResource(Resource):
    """Endpoint to delete a migration history record by ID."""

    @jwt_required()
    def delete(self, history_id: int):
        record = MigrationHistory.query.get(history_id)

        if record is None:
            return {
                "message": "History record not found."
            }, 404

        db.session.delete(record)
        db.session.commit()

        return {
            "message": "History record deleted successfully."
        }, 200

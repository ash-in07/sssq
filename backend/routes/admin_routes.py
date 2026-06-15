from flask_restful import Resource
from backend.models.report_model import Report
from backend.models.migration_model import Migration
from backend.models.history_model import MigrationHistory
from flask_jwt_extended import jwt_required, get_jwt


def is_admin_user() -> bool:
    claims = get_jwt()
    return claims.get("role") == "Admin"

class AdminResetResource(Resource):
    """Admin-only endpoint to reset reports, dashboard stats, and migration history."""

    @jwt_required()
    def post(self):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403
        # Delete all records from Report, Migration, MigrationHistory tables
        from backend.extensions import db
        try:
            db.session.query(Report).delete()
            db.session.query(Migration).delete()
            db.session.query(MigrationHistory).delete()
            db.session.commit()
            return {"message": "All reports, migrations, and history have been reset."}, 200
        except Exception as exc:
            db.session.rollback()
            return {"message": "Reset failed.", "error": str(exc)}, 500


from backend.models.user_model import User
from backend.models.migration_model import Migration
from backend.models.history_model import MigrationHistory





class AdminUserListResource(Resource):
    """Admin-only endpoint to list all registered users."""

    @jwt_required()
    def get(self):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403

        users = [user.to_dict() for user in User.query.all()]
        return {"users": users, "count": len(users)}, 200


class AdminUserDeleteResource(Resource):
    """Admin-only endpoint to delete a specific user."""

    @jwt_required()
    def delete(self, user_id: int):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403

        user = User.query.get(user_id)
        if user is None:
            return {"message": "User not found."}, 404

        User.query.filter_by(id=user.id).delete()
        from backend.extensions import db
        db.session.commit()
        return {"message": f"User {user.username} deleted."}, 200


class AdminStatsResource(Resource):
    """Admin-only endpoint for migration statistics and failed jobs."""

    @jwt_required()
    def get(self):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403

        total_migrations = Migration.query.count()
        history_count = MigrationHistory.query.count()
        failed_migrations = Migration.query.filter_by(status="failed").count()
        failed_history = MigrationHistory.query.filter(MigrationHistory.status.ilike("%failed%"))

        return {
            "total_migrations": total_migrations,
            "migration_history_count": history_count,
            "failed_migrations": failed_migrations,
            "failed_history_count": failed_history.count(),
        }, 200

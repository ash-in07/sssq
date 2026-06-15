import os
import sys

# Ensure the project root (parent of backend/) is on sys.path so that
# absolute imports like `from backend.config import ...` work when
# running directly with `python app.py` from inside the backend dir.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pyrefly: ignore [missing-import]
from flask import Flask, jsonify
# pyrefly: ignore [missing-import]
from flask_restful import Api

from backend.config import Config
from backend.extensions import db, jwt
from backend.auth.auth_routes import RegisterResource, LoginResource, LogoutResource
from backend.routes.migration_routes import SqlToSqlResource, MigrationStatusResource, MigrationHistoryResource, FileImportResource, SqlExportResource, SchemaGeneratorResource, TestConnectionResource, DownloadExportResource
from backend.routes.history_routes import HistoryListResource, HistoryDeleteResource
from backend.routes.admin_routes import AdminUserListResource, AdminUserDeleteResource, AdminStatsResource, AdminResetResource


from backend.routes.report_routes import ReportResource, ReportListResource
from backend.utils.logger import setup_logging

from flask_cors import CORS

def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    if os.getenv("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

    setup_logging(app)
    db.init_app(app)
    jwt.init_app(app)

    api = Api(app)

    # Authentication endpoints
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(LogoutResource, "/api/auth/logout")

    # Migration and conversion endpoints
    api.add_resource(SqlToSqlResource, "/api/migration/sql-to-sql")
    api.add_resource(MigrationStatusResource, "/api/migration/status/<int:migration_id>")
    api.add_resource(MigrationHistoryResource, "/api/migration/history")
    api.add_resource(FileImportResource, "/api/import/file-to-sql")
    api.add_resource(SqlExportResource, "/api/export/sql-to-file")
    api.add_resource(DownloadExportResource, "/api/export/download/<string:filename>")
    api.add_resource(SchemaGeneratorResource, "/api/schema/generate")
    api.add_resource(TestConnectionResource, "/api/test-connection")

    # History endpoints
    api.add_resource(HistoryListResource, "/api/history")
    api.add_resource(HistoryDeleteResource, "/api/history/<int:history_id>")

    # Admin endpoints
    api.add_resource(AdminUserListResource, "/api/admin/users")
    api.add_resource(AdminUserDeleteResource, "/api/admin/user/<int:user_id>")
    api.add_resource(AdminStatsResource, "/api/admin/stats")
    api.add_resource(AdminResetResource, "/api/admin/reset")

    # Reports endpoint
    api.add_resource(ReportResource, "/api/reports/<int:report_id>")
    api.add_resource(ReportListResource, "/api/reports")

    @app.route("/", methods=["GET"])
    def root() -> tuple[dict, int]:
        return {
            "message": "SQL Migrator Backend is running. Use /api endpoints for access."}, 200

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=True)

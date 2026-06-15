from flask_restful import Resource
from backend.models.report_model import Report
from flask import request
from backend.extensions import db
from datetime import datetime


class ReportResource(Resource):
    """Endpoint to retrieve report metadata by ID."""

    def get(self, report_id: int):
        report = Report.query.get(report_id)
        if report is None:
            return {"message": "Report not found."}, 404

        return {"report": report.to_dict()}, 200


class ReportListResource(Resource):
    """Endpoint to retrieve all reports and create new reports."""

    def get(self):
        reports = Report.query.order_by(Report.created_at.desc()).all()
        result = []
        for r in reports:
            result.append({
                "id": r.id,
                "name": r.name,
                "type": r.report_format.upper(),
                "generatedBy": r.generated_by,
                "date": r.created_at.strftime("%Y-%m-%d"),
                "status": "Ready"
            })
        return {"reports": result, "count": len(result)}, 200

    def post(self):
        data = request.get_json() or {}
        name = data.get('name') or f"Report {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        report_format = data.get('type', data.get('report_format', 'PDF')).upper()
        generated_by = data.get('generatedBy') or data.get('generated_by') or 'System'
        report = Report(name=name, report_format=report_format, generated_by=generated_by)
        db.session.add(report)
        db.session.commit()
        return {
            "message": "Report created",
            "report": {
                "id": report.id,
                "name": report.name,
                "type": report.report_format,
                "generatedBy": report.generated_by,
                "date": report.created_at.strftime("%Y-%m-%d"),
                "status": "Ready"
            }
        }, 201

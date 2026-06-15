from fpdf import FPDF
from typing import Dict
from backend.utils.file_handler import resolve_export_path
from backend.reports.report_templates import build_text_report, build_json_report


def generate_json_report(summary: Dict) -> Dict:
    """Generate a JSON formatted migration report."""
    return build_json_report(summary)


def generate_text_report(summary: Dict) -> str:
    """Generate a text formatted migration report."""
    return build_text_report(summary)


def generate_pdf_report(summary: Dict, filename: str = "migration_report.pdf") -> str:
    """Generate a PDF report file from a migration summary."""
    content = build_text_report(summary)
    pdf_path = resolve_export_path(filename)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.cell(0, 10, txt=line, ln=True)
    pdf.output(pdf_path)
    return pdf_path

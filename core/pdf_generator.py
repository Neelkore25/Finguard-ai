"""FinGuard AI - Executive Financial Intelligence PDF Report Generator"""

import io
import html
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_executive_pdf(kpis: Dict[str, Any], risk_data: Dict[str, Any], xray_findings: List[Dict[str, str]]) -> bytes:
    """
    Generates a professional executive PDF summary report using ReportLab.
    Returns: PDF file content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        "ReportHeader",
        parent=styles["Heading1"],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0A192F"),
        fontName="Helvetica-Bold",
        spaceAfter=4
    )

    subhead_style = ParagraphStyle(
        "SubHeader",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#5A6B82"),
        fontName="Helvetica",
        spaceAfter=15
    )

    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F3460"),
        fontName="Helvetica-Bold",
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2C3E50"),
        fontName="Helvetica"
    )

    story = []

    # Title & Branding
    story.append(Paragraph("FinGuard AI — Financial Intelligence Report", header_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Confidential &amp; Grounded Analysis", subhead_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#00D2FF"), spaceAfter=15))

    # 1. Executive KPIs Summary Table
    story.append(Paragraph("1. Executive Financial Overview", section_title))
    kpi_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Monthly Avg Income", f"INR {kpis.get('monthly_avg_income', 0):,.0f}", "Monthly Avg Expense", f"INR {kpis.get('monthly_avg_expense', 0):,.0f}"],
        ["Net Savings (YTD)", f"INR {kpis.get('net_savings', 0):,.0f}", "Savings Rate", f"{kpis.get('savings_rate', 0):.1f}%"],
        ["Financial Risk Score", f"{risk_data.get('score', 0)} / 100", "Risk Classification", f"{risk_data.get('status', 'Moderate')}"],
        ["Debt-to-Income (DTI)", f"{risk_data.get('dti_ratio', 0):.1f}%", "Emergency Buffer", f"{risk_data.get('runway_months', 0):.1f} Months"]
    ]

    t1 = Table(kpi_data, colWidths=[130, 135, 130, 135])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A2536")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    # 2. Financial Risk Engine Attribution Breakdown
    story.append(Paragraph("2. Financial Risk Factor Breakdown", section_title))
    risk_rows = [["Risk Factor / Measurable Indicator", "Score Contribution", "Benchmark Max", "Status"]]
    for f in risk_data.get("breakdown", []):
        risk_rows.append([f["factor"], f"{f['points']} pts", f"{f['max']} pts", f["status"]])

    t2 = Table(risk_rows, colWidths=[220, 110, 100, 100])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # 3. Financial X-Ray Diagnostics
    story.append(Paragraph("3. Financial X-Ray Diagnostics &amp; Prescriptions", section_title))
    if xray_findings:
        xray_rows = [["Risk Issue", "Evidence & Telemetry", "Actionable Prescription"]]
        for item in xray_findings[:4]:
            r_text = html.escape(str(item.get('risk', '')))
            e_text = html.escape(str(item.get('evidence', '')))
            a_text = html.escape(str(item.get('action', '')))
            xray_rows.append([
                Paragraph(f"<b>{r_text}</b>", body_style),
                Paragraph(e_text, body_style),
                Paragraph(a_text, body_style)
            ])

        t3 = Table(xray_rows, colWidths=[140, 200, 190])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("No severe anomalies or structural risks identified in the current reporting period.", body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceAfter=10))
    story.append(Paragraph("FinGuard AI Intelligence Engine • Powered by Machine Learning & Personal Finance Analytics", subhead_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

import io
import os
import pandas as pd
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.users import User
from app.models.datasets import Dataset
from app.auth.dependencies import get_current_user
from app.data_sources.service import DataInputService
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

router = APIRouter(prefix="/api/v1/export", tags=["Export"])

class PDFReportRequest(BaseModel):
    title: str
    dataset_name: str
    question: Optional[str] = ""
    short_answer: Optional[str] = ""
    key_insights: List[str] = []
    kpis: Dict[str, Any] = {}
    table_data: Optional[List[Dict[str, Any]]] = []

@router.get("/csv/{dataset_id}")
def export_csv(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")

    df = DataInputService.load_data(dataset.file_format, dataset.file_path)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dataset.name}.csv"}
    )

@router.post("/pdf")
def export_pdf_report(req: PDFReportRequest):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2563EB"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1F2937")
    )

    story = []
    # Title & Metadata
    story.append(Paragraph("AgentIQ Analytical Report", title_style))
    story.append(Paragraph(f"<b>Dataset:</b> {req.dataset_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Project:</b> AgentIQ (Batch 08)", body_style))
    story.append(Spacer(1, 15))

    # Analytical Question
    if req.question:
        story.append(Paragraph("Analytical Inquiry", h2_style))
        story.append(Paragraph(f"<i>\"{req.question}\"</i>", body_style))
        story.append(Spacer(1, 8))

    # Grounded Answer
    if req.short_answer:
        story.append(Paragraph("Executive Summary & Grounded Findings", h2_style))
        story.append(Paragraph(req.short_answer, body_style))
        story.append(Spacer(1, 10))

    # Key Insights
    if req.key_insights:
        story.append(Paragraph("Key Calculated Insights", h2_style))
        for ins in req.key_insights:
            story.append(Paragraph(f"• {ins}", body_style))
        story.append(Spacer(1, 10))

    # Key Performance Indicators Table
    if req.kpis:
        story.append(Paragraph("Summary Key Performance Indicators", h2_style))
        kpi_table_data = [["Metric", "Value"]]
        for k, v in req.kpis.items():
            kpi_table_data.append([str(k), str(v)])
        
        t = Table(kpi_table_data, colWidths=[260, 260])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F9FAFB"), colors.white])
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

    # Data sample table
    if req.table_data and len(req.table_data) > 0:
        story.append(Paragraph("Aggregated Result Sample", h2_style))
        headers = list(req.table_data[0].keys())[:6]
        table_rows = [headers]
        for row in req.table_data[:10]:
            table_rows.append([str(row.get(h, "")) for h in headers])

        col_w = max(520 / max(len(headers), 1), 60)
        dt = Table(table_rows, colWidths=[col_w] * len(headers))
        dt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")])
        ]))
        story.append(dt)

    doc.build(story)
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=AgentIQ_Analysis_Report.pdf"}
    )

import io
import hashlib
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_handover_receipt_pdf(
    receipt_no: str,
    lot_code: str,
    date_str: str,
    collector_name: str,
    buyer_name: str,
    buyer_license: str,
    items: list,
    agreed_inr: float,
    final_inr: float,
    upi_ref: Optional[str] = "N/A",
    hash_chain_summary: str = ""
) -> tuple[bytes, str]:
    """
    Generates a formal Handover Receipt PDF adhering to E-Waste (Management) Rules, 2022.
    Returns (pdf_bytes, sha256_hash).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0B3D2E'),
        alignment=1,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#5B6B62'),
        alignment=1,
        spaceAfter=15
    )
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#14201A'),
        fontName="Helvetica-Bold"
    )
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#14201A')
    )

    story.append(Paragraph("KABADIWALA CONNECT — E-WASTE HANDOVER RECEIPT", title_style))
    story.append(Paragraph("Compliant with E-Waste (Management) Rules, 2022 — Ministry of Environment, Forest and Climate Change", subtitle_style))
    story.append(Spacer(1, 10))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Receipt No:</b>", normal_style), Paragraph(receipt_no, bold_style), Paragraph("<b>Date & Time:</b>", normal_style), Paragraph(date_str, normal_style)],
        [Paragraph("<b>Lot Code:</b>", normal_style), Paragraph(lot_code, bold_style), Paragraph("<b>E-Payment Ref:</b>", normal_style), Paragraph(upi_ref or "N/A (Cash)", normal_style)],
        [Paragraph("<b>Collector:</b>", normal_style), Paragraph(collector_name, normal_style), Paragraph("<b>Authorized Buyer:</b>", normal_style), Paragraph(buyer_name, bold_style)],
        [Paragraph("<b>CPCB/SPCB Reg:</b>", normal_style), Paragraph(buyer_license, bold_style), Paragraph("<b>Custody Status:</b>", normal_style), Paragraph("VERIFIED FORMAL CHANNEL", bold_style)],
    ]
    meta_table = Table(meta_data, colWidths=[100, 170, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7F5EF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E3E0D5')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Items Table
    item_header = [Paragraph("<b>#</b>", bold_style), Paragraph("<b>Material</b>", bold_style), Paragraph("<b>Condition</b>", bold_style), Paragraph("<b>Est Wt (kg)</b>", bold_style), Paragraph("<b>Actual Wt (kg)</b>", bold_style), Paragraph("<b>Amount (INR)</b>", bold_style)]
    table_rows = [item_header]
    for idx, item in enumerate(items, 1):
        table_rows.append([
            Paragraph(str(idx), normal_style),
            Paragraph(item.get("name", "E-Waste"), normal_style),
            Paragraph(item.get("condition", "Normal"), normal_style),
            Paragraph(f"{item.get('est_kg', 0):.2f}", normal_style),
            Paragraph(f"{item.get('actual_kg', item.get('est_kg', 0)):.2f}", normal_style),
            Paragraph(f"₹{item.get('amount_inr', 0):,.2f}", normal_style),
        ])
    
    items_table = Table(table_rows, colWidths=[30, 180, 80, 80, 80, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E4F4EA')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0B3D2E')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E3E0D5')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))

    # Summary Table
    summary_data = [
        [Paragraph("<b>Agreed Quote Amount:</b>", normal_style), Paragraph(f"₹{agreed_inr:,.2f}", normal_style)],
        [Paragraph("<b>Final Settled Amount:</b>", bold_style), Paragraph(f"<b>₹{final_inr:,.2f}</b>", bold_style)],
        [Paragraph("<b>Platform Commission:</b>", normal_style), Paragraph("₹0.00 (Zero fee for Collector)", normal_style)],
    ]
    summary_table = Table(summary_data, colWidths=[200, 340])
    summary_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor('#E3E0D5')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Audit & Legal Footnote
    legal_text = (
        "<b>Statutory Traceability Note:</b> This document certifies that the aforementioned electronic waste items "
        "have been handed over to an authorized recycler in strict accordance with the E-Waste (Management) Rules, 2022. "
        f"Cryptographic Hash Audit: {hash_chain_summary[:32]}... | Verification URL: https://kabadiwala.gov.in/verify/{receipt_no}"
    )
    story.append(Paragraph(legal_text, ParagraphStyle('Legal', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#5B6B62'))))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    return pdf_bytes, sha256

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

GREEN = colors.HexColor("#2d6a4f")
DARK_GREEN = colors.HexColor("#1b4332")


def generate_plant_report(farmer_name, farm_name, result, image_path=None):
    """Plant Analysis result mathi PDF report banave. Returns bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Head", fontName="Helvetica-Bold", fontSize=16,
                               alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=11,
                               spaceBefore=10, spaceAfter=4, textColor=DARK_GREEN))
    styles.add(ParagraphStyle(name="Body9", fontName="Helvetica", fontSize=9.5, leading=13))

    story = []

    header = Table([[Paragraph("🌾 AgroAI — Crop Health Report", styles["Head"])]], colWidths=[17*cm])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))

    meta = [
        ["Farmer Name", farmer_name or "N/A"],
        ["Farm", farm_name or "N/A"],
        ["Crop", result.get("crop", "N/A")],
        ["Date", datetime.now().strftime("%d %B %Y, %I:%M %p")],
    ]
    meta_tbl = Table(meta, colWidths=[4.5*cm, 12.5*cm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef5f0")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("AI Analysis", styles["Section"]))
    top = result["top_prediction"]
    story.append(Paragraph(f"<b>Finding:</b> {top['label']} ({top['type'].replace('_',' ')})", styles["Body9"]))
    story.append(Paragraph(f"<b>Confidence:</b> {top['confidence']:.0%}", styles["Body9"]))
    story.append(Paragraph(f"<b>Severity:</b> {result.get('severity', 'Unknown')}", styles["Body9"]))
    story.append(Paragraph(f"<b>Message:</b> {result.get('message', '')}", styles["Body9"]))

    story.append(Paragraph("Disclaimer", styles["Section"]))
    story.append(Paragraph(
        "This is an AI-generated analysis, not an official diagnosis. Always confirm "
        "with a qualified agricultural expert before taking any action. Any treatment "
        "information shown separately in the application is subject to its own "
        "verification status and must not be used without confirming the real product "
        "label.", styles["Body9"]))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def generate_soil_report(farmer_name, farm_name, soil_inputs, soil_result):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Head", fontName="Helvetica-Bold", fontSize=16,
                               alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=11,
                               spaceBefore=10, spaceAfter=4, textColor=DARK_GREEN))
    styles.add(ParagraphStyle(name="Body9", fontName="Helvetica", fontSize=9.5, leading=13))

    story = []
    header = Table([[Paragraph("🧪 AgroAI — Soil Analysis Report", styles["Head"])]], colWidths=[17*cm])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))

    meta = [
        ["Farmer Name", farmer_name or "N/A"],
        ["Farm", farm_name or "N/A"],
        ["Date", datetime.now().strftime("%d %B %Y, %I:%M %p")],
    ]
    meta_tbl = Table(meta, colWidths=[4.5*cm, 12.5*cm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef5f0")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Soil Nutrient Status", styles["Section"]))
    for nutrient, level in soil_result["nutrient_status"].items():
        story.append(Paragraph(f"<b>{nutrient}:</b> {level}", styles["Body9"]))
    story.append(Paragraph(f"<b>pH:</b> {soil_inputs['ph']} ({soil_result['ph_label']})", styles["Body9"]))

    story.append(Paragraph("Summary", styles["Section"]))
    story.append(Paragraph(soil_result["summary"], styles["Body9"]))

    story.append(Paragraph("Disclaimer", styles["Section"]))
    story.append(Paragraph(
        "These thresholds are derived from general crop-recommendation data, not a "
        "certified soil-testing standard. Consult a certified soil test for precise "
        "nutrient management.", styles["Body9"]))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
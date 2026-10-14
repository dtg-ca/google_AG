"""
pdf_generator.py - Professional PDF Advisory Report Builder using ReportLab.
Converts the structured Smart Mentor advisory report into a beautifully styled,
multi-page PDF publication complete with headers, footers, callout boxes,
action tables, and verified citations.
"""

import html
import io
import re
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from mentor_engine import MentorAdvisoryReport
from search_engine import SearchResultItem


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and stamp total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(54, 11 * inch - 36, "Smart Mentor | Strategic Knowledge & Advisory System")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Running Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 36, "Confidential Advisory Brief — Designed for User Guidance & Self-Protection")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(8.5 * inch - 54, 36, page_str)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * inch - 54, 48)
        self.restoreState()


def clean_markdown_for_reportlab(text: str) -> str:
    """Sanitizes plain markdown text into safe ReportLab-compatible HTML tags."""
    if not text:
        return ""

    # Escape HTML special chars
    safe_text = html.escape(text)

    # Convert bold **text** or __text__ to <b>text</b>
    safe_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe_text)
    safe_text = re.sub(r"__(.+?)__", r"<b>\1</b>", safe_text)

    # Convert italics *text* or _text_ to <i>text</i>
    safe_text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", safe_text)
    safe_text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<i>\1</i>", safe_text)

    # Convert backticks `code` to <code>
    safe_text = re.sub(r"`(.+?)`", r'<font face="Courier" color="#334155">\1</font>', safe_text)

    return safe_text


def generate_mentor_pdf(report: MentorAdvisoryReport) -> bytes:
    """Generates an executive-grade PDF document from the MentorAdvisoryReport."""
    buffer = io.BytesIO()

    # Document Setup with 0.75 in (54 pt) margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Design Typography Palette
    primary_color = colors.HexColor("#0F172A")  # Slate 900
    accent_color = colors.HexColor("#1E40AF")   # Indigo/Blue 800
    teal_color = colors.HexColor("#0D9488")     # Teal 600
    body_color = colors.HexColor("#334155")     # Slate 700
    card_bg = colors.HexColor("#F8FAFC")        # Slate 50
    border_color = colors.HexColor("#CBD5E1")   # Slate 300

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=teal_color,
        spaceAfter=12,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=body_color,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=body_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    meta_label_style = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=primary_color,
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=body_color,
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("SMART MENTOR ADVISORY BRIEF", title_style))
    story.append(Paragraph("EVIDENCE-BACKED STRATEGIC INTELLIGENCE & ACTION ROADMAP", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=0, spaceAfter=10))

    # 2. Executive Metadata Box
    date_str = datetime.now().strftime("%B %d, %Y • %H:%M")
    meta_data = [
        [
            Paragraph("<b>Topic:</b>", meta_label_style),
            Paragraph(clean_markdown_for_reportlab(report.topic), meta_val_style),
            Paragraph("<b>Date:</b>", meta_label_style),
            Paragraph(date_str, meta_val_style),
        ],
        [
            Paragraph("<b>Category:</b>", meta_label_style),
            Paragraph(clean_markdown_for_reportlab(report.category), meta_val_style),
            Paragraph("<b>Mentor Stance:</b>", meta_label_style),
            Paragraph(clean_markdown_for_reportlab(report.mentor_tone), meta_val_style),
        ],
        [
            Paragraph("<b>Engine:</b>", meta_label_style),
            Paragraph(f"Google Gemini ({report.model_used})", meta_val_style),
            Paragraph("<b>Compliance:</b>", meta_label_style),
            Paragraph(
                f"Summary: {report.summary_word_count}w (&lt;1000) • Analysis: {report.analysis_word_count}w (&lt;500)",
                meta_val_style,
            ),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[65, 205, 80, 154])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), card_bg),
            ("BOX", (0, 0), (-1, -1), 0.75, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Section 1: The Question / Input from User
    story.append(Paragraph("1. THE QUESTION / INPUT FROM USER", section_heading))
    q_paragraphs = report.question_input_section.split("\n")
    for qp in q_paragraphs:
        qp = qp.strip()
        if not qp:
            continue
        cleaned = clean_markdown_for_reportlab(qp)
        if qp.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ")
            story.append(Paragraph(f"&bull; {cleaned}", bullet_style))
        else:
            story.append(Paragraph(cleaned, body_style))
    story.append(Spacer(1, 10))

    # 4. Section 2: Summary of Search Results (< 1000 words)
    story.append(
        Paragraph(
            f"2. SUMMARY OF SEARCH RESULTS <font size=8 color='#0D9488'>({report.summary_word_count} words • &lt;1000 word limit)</font>",
            section_heading,
        )
    )
    s_paragraphs = report.summary_results_section.split("\n")
    for sp in s_paragraphs:
        sp = sp.strip()
        if not sp:
            continue
        cleaned = clean_markdown_for_reportlab(sp)
        if sp.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ")
            story.append(Paragraph(f"&bull; {cleaned}", bullet_style))
        elif sp.startswith("###"):
            subheading = cleaned.lstrip("# ")
            story.append(Paragraph(f"<b>{subheading}</b>", body_style))
        else:
            story.append(Paragraph(cleaned, body_style))
    story.append(Spacer(1, 10))

    # 5. Section 3: Analysis & Insights (< 500 words)
    story.append(
        Paragraph(
            f"3. ANALYSIS & INSIGHTS FROM SEARCHED REFERENCES <font size=8 color='#0D9488'>({report.analysis_word_count} words • &lt;500 word limit)</font>",
            section_heading,
        )
    )
    a_paragraphs = report.analysis_insights_section.split("\n")
    for ap in a_paragraphs:
        ap = ap.strip()
        if not ap:
            continue
        cleaned = clean_markdown_for_reportlab(ap)
        if ap.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ")
            story.append(Paragraph(f"&bull; {cleaned}", bullet_style))
        elif re.match(r"^\d+\.", ap):
            story.append(Paragraph(cleaned, bullet_style))
        else:
            story.append(Paragraph(cleaned, body_style))
    story.append(Spacer(1, 10))

    # 6. Section 4: Action Plans / Next Steps
    story.append(Paragraph("4. ACTION PLANS & PROTECTIVE NEXT STEPS", section_heading))
    p_paragraphs = report.action_plans_section.split("\n")
    for pp in p_paragraphs:
        pp = pp.strip()
        if not pp:
            continue
        cleaned = clean_markdown_for_reportlab(pp)
        if pp.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ")
            story.append(Paragraph(f"&bull; {cleaned}", bullet_style))
        elif re.match(r"^\d+\.", pp):
            story.append(Paragraph(cleaned, bullet_style))
        elif pp.startswith("###") or pp.startswith("##"):
            subheading = cleaned.lstrip("# ")
            story.append(Paragraph(f"<b>{subheading}</b>", body_style))
        else:
            story.append(Paragraph(cleaned, body_style))
    story.append(Spacer(1, 14))

    # 7. References Consulted Table (if available)
    if report.sources_consulted:
        story.append(
            KeepTogether([
                Paragraph("5. VERIFIED REFERENCES & KNOWLEDGE REPOSITORIES CONSULTED", section_heading),
                HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=2, spaceAfter=8),
            ])
        )

        ref_rows = [
            [
                Paragraph("<b>#</b>", meta_label_style),
                Paragraph("<b>Repository Type</b>", meta_label_style),
                Paragraph("<b>Title / Finding</b>", meta_label_style),
                Paragraph("<b>Source / Date</b>", meta_label_style),
            ]
        ]

        for i, src in enumerate(report.sources_consulted[:8], 1):
            title_p = Paragraph(f"<b>{clean_markdown_for_reportlab(src.title[:80])}</b>", meta_val_style)
            source_p = Paragraph(clean_markdown_for_reportlab(src.author_or_journal or src.published or "Verified"), meta_val_style)
            ref_rows.append([
                Paragraph(str(i), meta_val_style),
                Paragraph(clean_markdown_for_reportlab(src.source_type), meta_val_style),
                title_p,
                source_p,
            ])

        ref_table = Table(ref_rows, colWidths=[20, 140, 240, 104])
        ref_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, border_color),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(ref_table)

    # Build PDF with two-pass canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

"""
pdf_exporter.py
Exports viral song idea blueprints to a styled PDF document using ReportLab.
Includes every required section:
- Item a: Suggested Name
- Item b: Storyline (< 400 chars) forming lyrics basis for TopMedia AI description box
- Item c: Suggested Style (in a separate box by itself)
- Item d: Rationale for 1M+ views virality
- Item e: Storyline for TikTok video promotion via Google Flow
- Item f: Google Flow scene-by-scene prompts & Screen Text Hook
- Item g: Viral Hashtags
- Bonus: Sample Lyrics Preview (Verse + Viral Hook)
"""

import io
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(song_ideas: List[Dict[str, Any]], user_instruction: str = "") -> bytes:
    """Generates a professional, comprehensive PDF report with all required sections."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    main_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )

    sub_title_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    song_header_style = ParagraphStyle(
        'SongHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#4338CA")
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story_box_style = ParagraphStyle(
        'StoryBoxText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0F172A")
    )

    lyrics_style = ParagraphStyle(
        'LyricsText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#312E81")
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("VIRAL SONG IDEA BLUEPRINT REPORT", main_title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y')} | Objective: Song concepts engineered for 1,000,000+ views",
        sub_title_style
    ))
    if user_instruction:
        elements.append(Spacer(1, 3))
        elements.append(Paragraph(f"<b>Search & Guidance Input:</b> {user_instruction}", sub_title_style))

    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4338CA"), spaceAfter=12))

    for idx, song in enumerate(song_ideas, 1):
        block = []
        name = song.get("name", "Untitled Song")

        # Item a: Suggested Name
        block.append(Paragraph(f"<b>a. Suggested Song Name #{idx}: {name}</b>", song_header_style))
        block.append(Spacer(1, 5))

        # Item b: Context/Theme/Storyline (< 400 chars) forming lyrics basis
        storyline = song.get("storyline_lyrics_basis", "")
        char_count = len(storyline)
        block.append(Paragraph(
            f"<b>b. Storyline Context (Basis for Lyrics & TopMedia AI Description)</b> "
            f"<font color='#059669'>[{char_count}/400 chars]</font>:",
            section_title_style
        ))
        block.append(Spacer(1, 2))

        story_table = Table([[Paragraph(storyline, story_box_style)]], colWidths=[540])
        story_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('PADDING', (0, 0), (-1, -1), 7),
        ]))
        block.append(story_table)
        block.append(Spacer(1, 6))

        # Bonus: Sample Lyrics Preview
        lyrics = song.get("lyrics_preview", {})
        if lyrics:
            lyrics_text = f"<b>Verse:</b> {lyrics.get('verse', '')}<br/><b>Chorus Hook:</b> {lyrics.get('chorus', '')}"
            lyrics_table = Table([[Paragraph(lyrics_text, lyrics_style)]], colWidths=[540])
            lyrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D2FE")),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            block.append(Paragraph("<b>Basis of Lyrics (Generated Sample Excerpt):</b>", section_title_style))
            block.append(Spacer(1, 2))
            block.append(lyrics_table)
            block.append(Spacer(1, 6))

        # Item c: Suggested Style in a Separate Box by Itself
        style = song.get("style", {})
        style_rows = [
            [Paragraph("<b>Genre & Sub-genre:</b>", body_style), Paragraph(style.get("genre", "N/A"), body_style)],
            [Paragraph("<b>Key Instruments:</b>", body_style), Paragraph(style.get("instruments", "N/A"), body_style)],
            [Paragraph("<b>Tempo & Key:</b>", body_style), Paragraph(f"{style.get('tempo', 'N/A')} | {style.get('key', 'N/A')}", body_style)],
            [Paragraph("<b>Mood & Atmosphere:</b>", body_style), Paragraph(style.get("mood", "N/A"), body_style)],
            [Paragraph("<b>Vocal Delivery:</b>", body_style), Paragraph(style.get("vocal_delivery", "N/A"), body_style)],
        ]
        style_table = Table(style_rows, colWidths=[130, 410])
        style_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#94A3B8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        block.append(Paragraph("<b>c. Suggested Musical Style (Standalone Production Box):</b>", section_title_style))
        block.append(Spacer(1, 2))
        block.append(style_table)
        block.append(Spacer(1, 6))

        # Item d: Rationale for Why This Song Might Go Viral
        block.append(Paragraph("<b>d. Rationale for 1M+ Views Virality:</b>", section_title_style))
        block.append(Spacer(1, 2))
        block.append(Paragraph(song.get("viral_rationale", "N/A"), body_style))
        block.append(Spacer(1, 6))

        # Item e: Storyline for TikTok Video via Google Flow
        block.append(Paragraph("<b>e. Storyline for Generating TikTok Video (Google Flow Concept):</b>", section_title_style))
        block.append(Spacer(1, 2))
        block.append(Paragraph(song.get("tiktok_video_storyline", "N/A"), body_style))
        block.append(Spacer(1, 6))

        # Item f: Google Flow Scene Prompts & Screen Hook
        block.append(Paragraph("<b>f. Google Flow / Veo Video Generation Prompts & Screen Hook:</b>", section_title_style))
        block.append(Spacer(1, 2))
        hook = song.get("screen_text_hook", "")
        if hook:
            block.append(Paragraph(f"<b>Screen Text Overlay Hook:</b> <i>\"{hook}\"</i>", body_style))
            block.append(Spacer(1, 2))
        for p in song.get("google_flow_prompts", []):
            block.append(Paragraph(f"• {p}", body_style))
        block.append(Spacer(1, 6))

        # Item g: Viral Hashtags
        hashtags = song.get("hashtags", [])
        tag_str = " ".join(hashtags) if isinstance(hashtags, list) else str(hashtags)
        block.append(Paragraph(f"<b>g. Viral Hashtags:</b> <font color='#4338CA'>{tag_str}</font>", section_title_style))
        block.append(Spacer(1, 10))
        block.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

        elements.append(KeepTogether(block))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

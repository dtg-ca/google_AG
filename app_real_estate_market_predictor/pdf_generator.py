"""
PDF Generator for Real Estate Market Prediction Reports.
Generates an executive-ready, publication-grade PDF report using ReportLab.
"""

import io
import re
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class RealEstatePDFGenerator:
    """
    Builds a professional multi-page PDF document containing property analysis,
    market health indicators, comps, predictions, and detailed reasoning.
    """

    def generate_pdf(
        self,
        property_info: Dict[str, Any],
        market_health: Dict[str, Any],
        prediction: Dict[str, Any],
        search_data: Dict[str, Any]
    ) -> bytes:
        """
        Creates the PDF report and returns the raw bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom styles
        primary_color = colors.HexColor("#1E3A8A")    # Deep Navy
        secondary_color = colors.HexColor("#0D9488")  # Teal Accent
        dark_neutral = colors.HexColor("#1F2937")     # Dark Slate
        light_bg = colors.HexColor("#F8FAFC")         # Very light slate/gray
        border_color = colors.HexColor("#E2E8F0")     # Subtle border

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=dark_neutral
        )
        bold_body = ParagraphStyle(
            "CustomBoldBody",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13.5,
            textColor=dark_neutral
        )
        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=dark_neutral
        )
        table_cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11.5,
            textColor=dark_neutral
        )
        table_cell_header = ParagraphStyle(
            "TableCellHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.white
        )

        story = []

        # 1. Header Banner
        curr_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        story.append(Paragraph("REAL ESTATE MARKET PREDICTION REPORT", title_style))
        story.append(Paragraph(
            f"<b>Role:</b> Real Estate Predictor &nbsp;|&nbsp; <b>Generated:</b> {curr_time} &nbsp;|&nbsp; <b>Horizon:</b> {search_data.get('time_horizon', 'Past 3 Months')}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=0, spaceAfter=10))

        # 2. Key Executive Summary Highlights (Cards)
        curr_sym = prediction.get("currency_symbol", "$")
        price_val = f"{curr_sym}{prediction.get('expected_price', 0):,}"
        price_rng = f"{curr_sym}{prediction.get('price_range_low', 0):,} – {curr_sym}{prediction.get('price_range_high', 0):,}"
        dom_val = f"{prediction.get('expected_dom', 0)} Days"
        dom_rng = f"{prediction.get('dom_range_low', 0)} – {prediction.get('dom_range_high', 0)} Days"
        market_type = market_health.get("market_state", "Balanced Market")
        health_score = f"{market_health.get('health_score', 70)} / 100"

        summary_data = [
            [
                Paragraph("<b>EXPECTED SELLING PRICE</b>", table_cell_header),
                Paragraph("<b>EXPECTED DAYS ON MARKET</b>", table_cell_header),
                Paragraph("<b>MARKET CLIMATE</b>", table_cell_header),
                Paragraph("<b>CONFIDENCE SCORE</b>", table_cell_header)
            ],
            [
                Paragraph(f"<font size=13 color='#1E3A8A'><b>{price_val}</b></font><br/><font size=7.5 color='#4B5563'>Range: {price_rng}</font>", table_cell_style),
                Paragraph(f"<font size=13 color='#0D9488'><b>{dom_val}</b></font><br/><font size=7.5 color='#4B5563'>Range: {dom_rng}</font>", table_cell_style),
                Paragraph(f"<font size=11 color='#1F2937'><b>{market_type}</b></font><br/><font size=7.5 color='#4B5563'>Health: {health_score}</font>", table_cell_style),
                Paragraph(f"<font size=13 color='#10B981'><b>{prediction.get('confidence_score', 85)}%</b></font><br/><font size=7.5 color='#4B5563'>{prediction.get('velocity_tag', 'Standard')[:22]}</font>", table_cell_style)
            ]
        ]
        summary_table = Table(summary_data, colWidths=[135, 135, 135, 135])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('BACKGROUND', (0, 1), (-1, 1), light_bg),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

        # 3. Property Information & Web Scope
        story.append(Paragraph("1. Subject Property & Search Scope", section_heading))
        prop_rows = [
            [
                Paragraph("<b>Street Address:</b>", table_cell_bold),
                Paragraph(str(property_info.get("street", "N/A")), table_cell_style),
                Paragraph("<b>Property Type:</b>", table_cell_bold),
                Paragraph(str(property_info.get("property_type", "N/A")), table_cell_style)
            ],
            [
                Paragraph("<b>City, State/Province:</b>", table_cell_bold),
                Paragraph(f"{property_info.get('city', '')}, {property_info.get('province_state', '')}", table_cell_style),
                Paragraph("<b>Bedrooms / Bathrooms:</b>", table_cell_bold),
                Paragraph(f"{property_info.get('bedrooms', 3)} Beds / {property_info.get('bathrooms', 2.0)} Baths", table_cell_style)
            ],
            [
                Paragraph("<b>Country & Postal/Zip:</b>", table_cell_bold),
                Paragraph(f"{property_info.get('country', '')} &nbsp; ({property_info.get('postal_code', '')})", table_cell_style),
                Paragraph("<b>Interior Size & Lot:</b>", table_cell_bold),
                Paragraph(f"{property_info.get('sqft', 0):,} sq.ft. (Lot: {property_info.get('lot_size', 'N/A')})", table_cell_style)
            ],
            [
                Paragraph("<b>Year Built & Condition:</b>", table_cell_bold),
                Paragraph(f"{property_info.get('year_built', 'N/A')} &bull; {property_info.get('condition', 'Good')}", table_cell_style),
                Paragraph("<b>Target Websites Searched:</b>", table_cell_bold),
                Paragraph(", ".join(search_data.get("target_websites", ["realtor.ca", "zillow.com"])), table_cell_style)
            ]
        ]
        prop_table = Table(prop_rows, colWidths=[125, 145, 130, 140])
        prop_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('BOX', (0, 0), (-1, -1), 0.75, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(prop_table)
        story.append(Spacer(1, 10))

        # 4. Market Health & Absorption Analysis
        story.append(Paragraph("2. Neighborhood Market Health & Absorption Dynamics", section_heading))
        cohort = market_health.get("cohort_stats", {})
        mkt_rows = [
            [
                Paragraph("<b>Market State:</b>", table_cell_bold),
                Paragraph(f"<b>{market_health.get('market_state', 'Balanced')}</b> ({market_health.get('liquidity_rating', 'Standard')})", table_cell_style),
                Paragraph("<b>Months of Inventory (MOI):</b>", table_cell_bold),
                Paragraph(f"{market_health.get('months_of_inventory', 3.5)} Months", table_cell_style)
            ],
            [
                Paragraph("<b>Neighborhood Median DOM:</b>", table_cell_bold),
                Paragraph(f"{market_health.get('neighborhood_median_dom', 24)} Days", table_cell_style),
                Paragraph("<b>Sale-to-List Realization:</b>", table_cell_bold),
                Paragraph(f"{round(market_health.get('sale_to_list_ratio', 0.99) * 100, 1)}%", table_cell_style)
            ],
            [
                Paragraph("<b>Cohort $/Sq.Ft. Benchmark:</b>", table_cell_bold),
                Paragraph(f"{curr_sym}{cohort.get('median_sqft_rate', 0):,.2f} / sq.ft. (Avg: {curr_sym}{cohort.get('avg_sqft_rate', 0):,.2f})", table_cell_style),
                Paragraph("<b>3-Month Price Trend:</b>", table_cell_bold),
                Paragraph(str(market_health.get("price_trend_3mo", "+0.8%")), table_cell_style)
            ]
        ]
        mkt_table = Table(mkt_rows, colWidths=[135, 135, 135, 135])
        mkt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
            ('BOX', (0, 0), (-1, -1), 0.75, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(mkt_table)
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Summary:</b> {market_health.get('market_summary', '')}", body_style))
        story.append(Spacer(1, 10))

        # 5. Pricing Strategy Sensitivity Scenarios
        story.append(Paragraph("3. Pricing Strategy & Days on Market (DOM) Sensitivity", section_heading))
        scenarios = prediction.get("scenarios", [])
        scen_rows = [
            [
                Paragraph("<b>Strategy</b>", table_cell_header),
                Paragraph("<b>Recommended Price</b>", table_cell_header),
                Paragraph("<b>Expected DOM</b>", table_cell_header),
                Paragraph("<b>Strategic Rationale & Absorption Outcome</b>", table_cell_header)
            ]
        ]
        for s in scenarios:
            scen_rows.append([
                Paragraph(f"<b>{s.get('strategy', '')}</b>", table_cell_bold),
                Paragraph(f"<b>{curr_sym}{s.get('list_price', 0):,}</b>", table_cell_style),
                Paragraph(f"<b>{s.get('expected_dom', 0)} Days</b>", table_cell_style),
                Paragraph(s.get('rationale', ''), table_cell_style)
            ])
        scen_table = Table(scen_rows, colWidths=[120, 95, 75, 250])
        scen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#F0FDF4")), # light green
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#EFF6FF")), # light blue
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#FFFBEB")), # light amber
            ('BOX', (0, 0), (-1, -1), 0.75, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(scen_table)
        story.append(Spacer(1, 10))

        # 6. Comparable Properties Analyzed (Web Search Comps)
        story.append(Paragraph("4. Comparable Properties Fetched from Web Search (Past 3-6 Months)", section_heading))
        comps = search_data.get("comparables", [])[:6]
        comp_rows = [
            [
                Paragraph("<b>Comparable Address</b>", table_cell_header),
                Paragraph("<b>Sold Price</b>", table_cell_header),
                Paragraph("<b>DOM</b>", table_cell_header),
                Paragraph("<b>Beds/Baths</b>", table_cell_header),
                Paragraph("<b>Sq.Ft.</b>", table_cell_header),
                Paragraph("<b>$/Sq.Ft.</b>", table_cell_header),
                Paragraph("<b>Sold Date</b>", table_cell_header),
                Paragraph("<b>Source</b>", table_cell_header)
            ]
        ]
        for c in comps:
            comp_rows.append([
                Paragraph(str(c.get("address", ""))[:28], table_cell_style),
                Paragraph(f"{curr_sym}{c.get('sold_price', 0):,}", table_cell_bold),
                Paragraph(f"{c.get('days_on_market', 'N/A')}d", table_cell_style),
                Paragraph(f"{c.get('bedrooms', 3)}b / {c.get('bathrooms', 2)}ba", table_cell_style),
                Paragraph(f"{c.get('sqft', 0):,}", table_cell_style),
                Paragraph(f"{curr_sym}{c.get('price_per_sqft', 0):,.1f}", table_cell_style),
                Paragraph(str(c.get("sold_date", "Recent")), table_cell_style),
                Paragraph(str(c.get("source", "Web")), table_cell_style)
            ])
        comp_table = Table(comp_rows, colWidths=[120, 68, 32, 58, 48, 56, 68, 90])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
            ('BOX', (0, 0), (-1, -1), 0.75, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 10))

        # 7. Detailed Analytical Reasoning
        story.append(Paragraph("5. Detailed Predictive Reasoning & Appraisal Breakdown", section_heading))
        reasoning = prediction.get("reasoning", {})
        
        reasons_content = [
            ("A. Micro-Market Dynamics & Inventory Context", reasoning.get("micro_market_dynamics", "")),
            ("B. Comparable Sales Baseline & $/Sq.Ft. Benchmark", reasoning.get("comparable_sales_evidence", "")),
            ("C. Property Feature & Condition Adjustments", reasoning.get("property_adjustments", "")),
            ("D. Days on Market (DOM) Velocity Forecast", reasoning.get("dom_velocity_drivers", "")),
            ("E. Actionable Pricing Strategy & Negotiation Advisory", reasoning.get("strategic_recommendations", ""))
        ]

        def _format_markdown_for_reportlab(text: str) -> str:
            # Escape ampersands that are not already part of an entity
            clean = re.sub(r"&(?!amp;|lt;|gt;|bull;|quot;|#\d+;)", "&amp;", text)
            # Convert **bold** to <b>bold</b>
            clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean)
            # Convert bullet characters
            clean = clean.replace("•", "&bull;")
            # Convert newlines to breaks
            clean = clean.replace("\n", "<br/>")
            return clean

        for heading, text in reasons_content:
            clean_text = _format_markdown_for_reportlab(text)
            story.append(Paragraph(f"<b>{heading}</b>", bold_body))
            story.append(Spacer(1, 2))
            story.append(Paragraph(clean_text, body_style))
            story.append(Spacer(1, 6))

        # 8. Disclaimer and Methodology
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=0.75, color=border_color, spaceBefore=4, spaceAfter=6))
        disclaimer = (
            "<font size=7 color='#6B7280'><b>Methodology & Disclaimer:</b> This Real Estate Market Prediction Report is "
            "synthesized using multi-source algorithmic scraping and comparative market regression across the requested target websites "
            f"({', '.join(search_data.get('target_websites', []))}) over the past 3 to 6 months. Predictions reflect prevailing "
            "macroeconomic conditions, hedonic physical attribute adjustments, and local neighborhood absorption velocity. "
            "This report is intended for analytical and strategic planning purposes.</font>"
        )
        story.append(Paragraph(disclaimer, table_cell_style))

        # Build PDF
        doc.build(story)
        return buffer.getvalue()

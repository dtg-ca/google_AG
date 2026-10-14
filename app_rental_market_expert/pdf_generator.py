import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from file_parser import PropertyRequest
from market_analyzer import MarketAnalysis
from recommendation_engine import RecommendationResult

def create_rental_market_pdf(
    req: PropertyRequest,
    analysis: MarketAnalysis,
    rec: RecommendationResult
) -> bytes:
    """
    Generates a professional executive PDF report of the rental market analysis and recommendations.
    Returns bytes suitable for Streamlit download_button.
    """
    buffer = io.BytesIO()
    # 0.5 inch margins = 36 pt
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    base_styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=base_styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B')
    )
    section_heading = ParagraphStyle(
        'SectionHead',
        parent=base_styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A')
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    table_header_style = ParagraphStyle(
        'TableHead',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("RENTAL MARKET EXPERT & PRICING INTELLIGENCE REPORT", title_style))
    now_str = datetime.datetime.now().strftime("%B %d, %Y - %H:%M")
    story.append(Paragraph(f"Generated on {now_str} | Market Comps & Absorption Analysis", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=12))

    # 2. Property Overview Block
    story.append(Paragraph("1. Subject Property & Search Scope", section_heading))
    
    prop_data = [
        [
            Paragraph("<b>Property Address:</b>", table_cell_style),
            Paragraph(req.full_address, table_cell_style),
            Paragraph("<b>Property Type:</b>", table_cell_style),
            Paragraph(req.property_type, table_cell_style)
        ],
        [
            Paragraph("<b>City / Province:</b>", table_cell_style),
            Paragraph(f"{req.city}, {req.state_province} ({req.country})", table_cell_style),
            Paragraph("<b>Layout:</b>", table_cell_style),
            Paragraph(f"{req.bedrooms} Bed(s) | {req.bathrooms} Bath(s)", table_cell_style)
        ],
        [
            Paragraph("<b>Postal / Zip:</b>", table_cell_style),
            Paragraph(req.postal_code or "N/A", table_cell_style),
            Paragraph("<b>Furnished / Parking:</b>", table_cell_style),
            Paragraph(f"{req.furnished} | {req.parking}", table_cell_style)
        ]
    ]
    prop_table = Table(prop_data, colWidths=[1.3*inch, 2.2*inch, 1.4*inch, 2.3*inch])
    prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(prop_table)
    story.append(Spacer(1, 10))

    # 3. Suggested Rent & Strategic Tiers Callout Box
    story.append(Paragraph("2. Executive Recommendation: Suggested Rent & Pricing Tiers", section_heading))
    sym = rec.currency_symbol

    tier_rows = [
        [
            Paragraph("Pricing Strategy", table_header_style),
            Paragraph("Suggested Monthly Rent", table_header_style),
            Paragraph("Est. Days to Sign Lease", table_header_style),
            Paragraph("Strategic Objective & Tradeoff", table_header_style),
        ]
    ]
    for t in rec.pricing_tiers:
        tier_rows.append([
            Paragraph(f"<b>{t['tier']}</b>", table_cell_style),
            Paragraph(f"<b>{sym}{int(t['rent']):,} / month</b>", table_cell_style),
            Paragraph(t['expected_days_to_fill'], table_cell_style),
            Paragraph(t['strategy'], table_cell_style),
        ])
    
    tier_table = Table(tier_rows, colWidths=[1.8*inch, 1.4*inch, 1.3*inch, 2.7*inch])
    tier_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#ECFDF5')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFFBEB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tier_table)
    story.append(Spacer(1, 10))

    # 4. Past 4 Months Market Trend & Absorption Table
    story.append(Paragraph("3. Past 4-Month Web Search Trends & Fulfillment Absorption", section_heading))
    trend_rows = [
        [
            Paragraph("Month Period", table_header_style),
            Paragraph("Median Comps Rent", table_header_style),
            Paragraph("MoM Change", table_header_style),
            Paragraph("Avg Days to Fill", table_header_style),
            Paragraph("Lease Fulfillment Rate", table_header_style)
        ]
    ]
    for m in analysis.past_4_months:
        trend_rows.append([
            Paragraph(m.month_name, table_cell_style),
            Paragraph(f"{sym}{int(m.median_rent):,}", table_cell_style),
            Paragraph(f"{'+' if m.mom_growth_pct > 0 else ''}{m.mom_growth_pct}%", table_cell_style),
            Paragraph(f"{m.avg_days_to_fill} days", table_cell_style),
            Paragraph(f"{m.fulfillment_rate_pct}% fulfilled", table_cell_style),
        ])
    trend_table = Table(trend_rows, colWidths=[1.5*inch, 1.4*inch, 1.2*inch, 1.4*inch, 1.7*inch])
    trend_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(trend_table)
    story.append(Spacer(1, 8))

    # Market Velocity summary sentence
    story.append(Paragraph(
        f"<b>Market Velocity Summary:</b> Current absorption speed is categorized as <b>{analysis.fulfillment_velocity}</b> "
        f"with an overall demand index of <b>{analysis.demand_index}/100</b>.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # 5. Seasonality & Target Tenant Segment
    story.append(Paragraph("4. Optimum Advertising Window & Target Tenant Segment", section_heading))
    optimum_str = ", ".join(rec.optimum_months[:3])
    slowest_str = ", ".join(rec.slowest_months[:2])

    seg_rows = [
        [
            Paragraph("<b>Optimum Months to Advertise:</b>", table_cell_style),
            Paragraph(f"<b>{optimum_str}</b> (Peak tenant inquiries; list {rec.lead_time_days} days in advance)", table_cell_style)
        ],
        [
            Paragraph("<b>Slowest Months to Avoid:</b>", table_cell_style),
            Paragraph(f"{slowest_str} (Severe seasonal slowdown; price conservatively if listing)", table_cell_style)
        ],
        [
            Paragraph("<b>Best Target Segment:</b>", table_cell_style),
            Paragraph(f"<b>{rec.target_segment.primary}</b> (Secondary: {rec.target_segment.secondary})", table_cell_style)
        ],
        [
            Paragraph("<b>Target Demographic Profile:</b>", table_cell_style),
            Paragraph(rec.target_segment.demographic_summary, table_cell_style)
        ],
        [
            Paragraph("<b>Key Value Drivers for Tenants:</b>", table_cell_style),
            Paragraph(" • " + " • ".join(rec.target_segment.key_value_drivers), table_cell_style)
        ],
        [
            Paragraph("<b>Suggested Listing Headline:</b>", table_cell_style),
            Paragraph(f"<i>\"{rec.target_segment.listing_hook}\"</i>", table_cell_style)
        ]
    ]
    seg_table = Table(seg_rows, colWidths=[2.2*inch, 5.0*inch])
    seg_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(seg_table)
    story.append(Spacer(1, 10))

    # 6. Best Platforms for Fast Responses
    story.append(Paragraph("5. Best Websites & Channels for Fast Responses", section_heading))
    plat_rows = [
        [
            Paragraph("Rank", table_header_style),
            Paragraph("Website / Channel", table_header_style),
            Paragraph("1st Inquiry Speed", table_header_style),
            Paragraph("Lead Profile", table_header_style),
            Paragraph("Execution Pro-Tip", table_header_style),
        ]
    ]
    for p in rec.fast_response_platforms[:4]:
        plat_rows.append([
            Paragraph(f"#{p.rank}", table_cell_style),
            Paragraph(f"<b>{p.name}</b>", table_cell_style),
            Paragraph(p.expected_response_time, table_cell_style),
            Paragraph(p.lead_quality, table_cell_style),
            Paragraph(p.pro_tip, table_cell_style),
        ])
    plat_table = Table(plat_rows, colWidths=[0.5*inch, 1.8*inch, 1.2*inch, 1.7*inch, 2.0*inch])
    plat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#047857')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(plat_table)
    story.append(Spacer(1, 10))

    # 7. Detailed Reasoning & Strategic Takeaway
    story.append(Paragraph("6. Analytical Reasoning & Strategic Rationale", section_heading))
    for pt in rec.reasoning_points:
        clean_pt = pt.replace("**", "")
        story.append(Paragraph(f"• {clean_pt}", body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph("Rental Market Expert AI | Powered by Web Search Market Aggregation & Fulfillment Analytics", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

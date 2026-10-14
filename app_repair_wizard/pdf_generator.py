"""
Generates comprehensive, professional printable PDF repair dossiers using ReportLab.
Includes complete intake details, safety precautions, root causes, DIY steps,
itemized outside professional repair cost estimates (parts + labor),
nearest repair centers near postal address, and online forum citations.
"""

import io
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

def generate_repair_pdf(
    dossier: Dict[str, Any],
    equipment_info: Dict[str, str],
    research_data: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Creates a comprehensive PDF document containing the entire repair dossier:
    intake, diagnostics, DIY instructions, outside professional cost estimate,
    nearest repair locations, and online research references.
    """
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
    
    # Custom Typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=10
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#374151")
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    warning_style = ParagraphStyle(
        'WarningText',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#991B1B")
    )

    story = []

    # 1. Document Title & Header
    title_text = dossier.get("title", "FixMate Comprehensive Repair Dossier")
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph(f"FixMate Expert Diagnostics & Outside Repair Evaluation • Location: {equipment_info.get('location', 'Unspecified')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=8))

    # 2. Equipment Intake & Quick Summary Table
    pro_est = dossier.get("pro_repair_estimate", {})
    pro_total = pro_est.get("total_pro_estimate", dossier.get("estimated_cost_pro", "$250 - $450"))
    
    overview_data = [
        [
            Paragraph("<b>Equipment Category:</b>", bold_body_style),
            Paragraph(f"{equipment_info.get('category', 'N/A')} ({equipment_info.get('subtype', '')})", body_style),
            Paragraph("<b>Safety Hazard Level:</b>", bold_body_style),
            Paragraph(f"<b>{dossier.get('safety_hazard_level', 'Moderate')}</b>", warning_style)
        ],
        [
            Paragraph("<b>Make & Model:</b>", bold_body_style),
            Paragraph(f"{equipment_info.get('make', 'N/A')} {equipment_info.get('model', 'N/A')}", body_style),
            Paragraph("<b>Difficulty Rating:</b>", bold_body_style),
            Paragraph(str(dossier.get("difficulty_rating", "Intermediate")), body_style)
        ],
        [
            Paragraph("<b>User Postal Location:</b>", bold_body_style),
            Paragraph(equipment_info.get("location", "Not specified"), body_style),
            Paragraph("<b>Est. DIY Part Cost:</b>", bold_body_style),
            Paragraph(f"<b>{dossier.get('estimated_cost_diy', '$20 - $50')}</b> ({dossier.get('estimated_time', '45 min')})", body_style)
        ],
        [
            Paragraph("<b>DIY Recommendation:</b>", bold_body_style),
            Paragraph(dossier.get("diy_recommendation", "Recommended DIY"), body_style),
            Paragraph("<b>Est. Outside Pro Cost:</b>", bold_body_style),
            Paragraph(f"<b>{pro_total}</b> (Parts + Labor)", body_style)
        ]
    ]

    overview_table = Table(overview_data, colWidths=[115, 155, 120, 150])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 8))

    # 3. Problem Statement & Reported Symptoms
    story.append(Paragraph("Reported Problem & Symptoms", section_heading))
    story.append(Paragraph(equipment_info.get("problem", "No description provided"), body_style))
    story.append(Spacer(1, 6))

    # 4. Critical Safety Precautions
    warnings = dossier.get("safety_warnings", [])
    if warnings:
        warn_content = [
            [Paragraph("<b>⚠️ CRITICAL SAFETY PRECAUTIONS BEFORE COMMENCING:</b>", ParagraphStyle('WTitle', parent=warning_style, fontName='Helvetica-Bold', fontSize=9))]
        ]
        for w in warnings:
            warn_content.append([Paragraph(f"• {w}", warning_style)])
        
        warn_table = Table(warn_content, colWidths=[540])
        warn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#EF4444")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(warn_table)
        story.append(Spacer(1, 8))

    # 5. Root Cause Analysis Table
    story.append(Paragraph("Diagnosed Root Causes & Verification Methods", section_heading))
    rc_data = [
        [
            Paragraph("<b>Probable Fault / Cause</b>", bold_body_style),
            Paragraph("<b>Likelihood</b>", bold_body_style),
            Paragraph("<b>Diagnostic Verification Test Method</b>", bold_body_style)
        ]
    ]
    for rc in dossier.get("root_cause_analysis", []):
        rc_data.append([
            Paragraph(f"<b>{rc.get('cause', '')}</b><br/>{rc.get('explanation', '')}", body_style),
            Paragraph(f"<b>{rc.get('probability', 'Medium')}</b>", body_style),
            Paragraph(rc.get("test_method", "Visual inspection / continuity check"), body_style)
        ])
    
    rc_table = Table(rc_data, colWidths=[200, 70, 270])
    rc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E7FF")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rc_table)
    story.append(Spacer(1, 8))

    # 6. Required Tools & Replacement Parts
    tools = dossier.get("required_tools", [])
    parts = dossier.get("likely_parts_needed", [])
    
    tools_str = "<br/>".join([f"□ {t}" for t in tools]) if tools else "Standard household tool set"
    parts_str = "<br/>".join([f"• <b>{p.get('part_name', 'Part')}:</b> {p.get('typical_cost', '')} (Tip: {p.get('replacement_tip', '')})" for p in parts]) if parts else "No replacement parts required"

    tp_table = Table([
        [
            Paragraph("<b>Required Tools Checklist:</b>", bold_body_style),
            Paragraph("<b>Likely Replacement Parts:</b>", bold_body_style)
        ],
        [
            Paragraph(tools_str, body_style),
            Paragraph(parts_str, body_style)
        ]
    ], colWidths=[270, 270])
    tp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tp_table)
    story.append(Spacer(1, 8))

    # 7. Step-by-Step DIY Repair Guide
    story.append(Paragraph("Step-by-Step DIY Repair Guide", section_heading))
    step_data = [
        [
            Paragraph("<b>Phase / Step</b>", bold_body_style),
            Paragraph("<b>Repair Instructions & Insider Pro-Tips</b>", bold_body_style)
        ]
    ]
    for step in dossier.get("step_by_step_guide", []):
        text = f"{step.get('instruction', '')}"
        if step.get('pro_tip'):
            text += f"<br/><font color='#1D4ED8'><b>Pro Tip:</b> {step.get('pro_tip')}</font>"
        step_data.append([
            Paragraph(f"<b>{step.get('phase', 'Step')}</b>", bold_body_style),
            Paragraph(text, body_style)
        ])

    step_table = Table(step_data, colWidths=[130, 410])
    step_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(step_table)
    story.append(Spacer(1, 8))

    # 8. OUTSIDE PROFESSIONAL REPAIR COST ESTIMATE (PARTS + LABOR)
    story.append(Paragraph("Outside Professional Repair Cost Estimate (Parts + Labor)", section_heading))
    story.append(Paragraph("Itemized cost estimate from an authorized service provider or local repair shop if DIY is too difficult:", body_style))
    story.append(Spacer(1, 4))

    pro_table_data = [
        [
            Paragraph("<b>Cost Component</b>", bold_body_style),
            Paragraph("<b>Industry Rate / Scope</b>", bold_body_style),
            Paragraph("<b>Estimated Expense</b>", bold_body_style)
        ],
        [
            Paragraph("<b>Diagnostic / Trip Fee:</b>", body_style),
            Paragraph("Standard truck roll & initial fault diagnosis", body_style),
            Paragraph(pro_est.get("diagnostic_call_fee", "$85 - $125"), body_style)
        ],
        [
            Paragraph("<b>Labor Expense:</b>", body_style),
            Paragraph(f"{pro_est.get('labor_hours', '1.5 hrs')} @ {pro_est.get('labor_hourly_rate', '$120 / hr')}", body_style),
            Paragraph(pro_est.get("labor_subtotal", "$150 - $260"), body_style)
        ],
        [
            Paragraph("<b>Parts (with Shop Markup):</b>", body_style),
            Paragraph("OEM replacement parts + 20-30% shop markup", body_style),
            Paragraph(pro_est.get("estimated_parts_retail", "$45 - $95"), body_style)
        ],
        [
            Paragraph("<b>Shop Supplies & Disposal:</b>", body_style),
            Paragraph("Consumables, recycling fee & hardware", body_style),
            Paragraph(pro_est.get("supplies_and_disposal", "$15 - $25"), body_style)
        ],
        [
            Paragraph("<b>TOTAL PROFESSIONAL ESTIMATE:</b>", bold_body_style),
            Paragraph("<b>Total Out-of-Pocket Professional Cost</b>", bold_body_style),
            Paragraph(f"<b><font color='#B91C1C'>{pro_est.get('total_pro_estimate', '$295 - $505')}</font></b>", bold_body_style)
        ],
        [
            Paragraph("<b>Estimated DIY Savings:</b>", bold_body_style),
            Paragraph("Cost difference of fixing it yourself", body_style),
            Paragraph(f"<b><font color='#15803D'>{pro_est.get('diy_savings', 'Save ~$250 - $430')}</font></b>", bold_body_style)
        ]
    ]

    pro_cost_table = Table(pro_table_data, colWidths=[170, 210, 160])
    pro_cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FEF3C7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#FDE68A")),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor("#FEE2E2")),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor("#DCFCE7")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(pro_cost_table)
    story.append(Spacer(1, 6))

    if pro_est.get("when_to_hire_pro"):
        story.append(Paragraph(f"<b>When to Escalate to Outside Repair:</b> <i>{pro_est.get('when_to_hire_pro')}</i>", body_style))
        story.append(Spacer(1, 8))

    # 9. NEAREST OUTSIDE REPAIR CENTERS NEAR USER LOCATION
    if research_data and research_data.get("pro_shops"):
        story.append(Paragraph("Nearest Outside Repair Locations & Service Centers", section_heading))
        shop_data = [
            [
                Paragraph("<b>Service Center / Business</b>", bold_body_style),
                Paragraph("<b>Source / Directory</b>", bold_body_style),
                Paragraph("<b>Service Overview & Details</b>", bold_body_style)
            ]
        ]
        for s in research_data["pro_shops"][:4]:
            shop_data.append([
                Paragraph(f"<b>{s.get('title', 'Service Provider')}</b>", body_style),
                Paragraph(s.get("source", "Web"), body_style),
                Paragraph(s.get("snippet", "")[:130] + "...", body_style)
            ])
        
        shop_table = Table(shop_data, colWidths=[180, 100, 260])
        shop_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(shop_table)
        story.append(Spacer(1, 8))

    # 10. LOCAL PARTS HUBS & HARDWARE WAREHOUSES
    if research_data and research_data.get("local_parts"):
        story.append(Paragraph("Local Parts Warehouses & Hardware Stores Discovered", section_heading))
        parts_data = [
            [
                Paragraph("<b>Store / Supply Warehouse</b>", bold_body_style),
                Paragraph("<b>Category / Source</b>", bold_body_style),
                Paragraph("<b>Store Details</b>", bold_body_style)
            ]
        ]
        for lp in research_data["local_parts"][:4]:
            parts_data.append([
                Paragraph(f"<b>{lp.get('title', 'Parts Store')}</b>", body_style),
                Paragraph(lp.get("source", "Local"), body_style),
                Paragraph(lp.get("snippet", "")[:130] + "...", body_style)
            ])
        
        lp_table = Table(parts_data, colWidths=[180, 100, 260])
        lp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0FDF4")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BBF7D0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(lp_table)
        story.append(Spacer(1, 8))

    # 11. Community Wisdom & Real Forum Insights
    wisdom = dossier.get("community_wisdom", [])
    if wisdom:
        story.append(Paragraph("Community Wisdom & Reddit / Forum Insights", section_heading))
        for w in wisdom:
            story.append(Paragraph(f"• <i>{w}</i>", body_style))
        story.append(Spacer(1, 8))

    # 12. Online Research Citations & Source Links
    if research_data and research_data.get("all_sources"):
        story.append(Paragraph("Online Research References & Forum Citations", section_heading))
        ref_data = [
            [
                Paragraph("<b>Reference Title</b>", bold_body_style),
                Paragraph("<b>Type / Source</b>", bold_body_style),
                Paragraph("<b>Web URL / Direct Link</b>", bold_body_style)
            ]
        ]
        for src in research_data["all_sources"][:8]:
            ref_data.append([
                Paragraph(src.get("title", "")[:45] + ("..." if len(src.get("title", "")) > 45 else ""), body_style),
                Paragraph(f"{src.get('type', 'Guide')} ({src.get('source', '')})", body_style),
                Paragraph(f"<font color='#2563EB'>{src.get('url', '')[:50]}...</font>", body_style)
            ])
        
        ref_table = Table(ref_data, colWidths=[180, 110, 250])
        ref_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(ref_table)
        story.append(Spacer(1, 8))

    # 13. Document Footer
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9CA3AF"), spaceAfter=5))
    story.append(Paragraph("FixMate Technical Dossier • Always disconnect power and fuel lines before servicing • Consult licensed tradespeople for hazardous tasks", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from file_parser import PropertyRequest, parse_json_input, parse_csv_input, parse_freeform_text, parse_file
from search_engine import search_rental_market_web, get_currency_symbol
from market_analyzer import analyze_market_data, MarketAnalysis
from recommendation_engine import generate_recommendations, RecommendationResult
from pdf_generator import create_rental_market_pdf

# Set page setup
st.set_page_config(
    page_title="Rental Market Expert | AI Pricing & Seasonality Advisor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .card-metric {
        background-color: #F8FAFC;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2563EB;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 600;
    }
    .badge-fast {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-target {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "property_req" not in st.session_state:
    st.session_state.property_req = PropertyRequest(
        country="Canada",
        state_province="Ontario",
        city="Toronto",
        street="180 University Ave",
        postal_code="M5H 0A2",
        property_type="2-Bedroom Apartment",
        bedrooms=2.0,
        bathrooms=2.0,
        furnished="Unfurnished",
        parking="Dedicated / Included",
        pet_friendly=True,
        utilities_included=False,
        amenities=["In-suite laundry", "Balcony", "Fitness centre"]
    )

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "rec_result" not in st.session_state:
    st.session_state.rec_result = None

# Sidebar: App Overview & Quick Demo Loaders
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3", use_container_width=True)
    st.markdown("### 🏢 Rental Market Expert")
    st.markdown(
        "Analyzes live rental websites, forums, and 4-month market absorption "
        "to pinpoint optimal rent, peak listing months, tenant personas, and fast-response channels."
    )
    st.markdown("---")
    st.markdown("#### ⚡ Quick Demo Scenarios")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("🇨🇦 Toronto 2-Bed", use_container_width=True):
            st.session_state.property_req = PropertyRequest(
                country="Canada",
                state_province="Ontario",
                city="Toronto",
                street="180 University Ave",
                postal_code="M5H 0A2",
                property_type="2-Bedroom Apartment",
                bedrooms=2.0,
                bathrooms=2.0,
                furnished="Unfurnished",
                parking="Dedicated / Included",
                pet_friendly=True
            )
            st.session_state.analysis_result = None
            st.rerun()

    with col_d2:
        if st.button("🇺🇸 Austin 1-Bed", use_container_width=True):
            st.session_state.property_req = PropertyRequest(
                country="United States",
                state_province="Texas",
                city="Austin",
                street="400 Colorado St",
                postal_code="78701",
                property_type="1-Bedroom Apartment",
                bedrooms=1.0,
                bathrooms=1.0,
                furnished="Unfurnished",
                parking="Garage Parking",
                pet_friendly=True
            )
            st.session_state.analysis_result = None
            st.rerun()

    col_d3, col_d4 = st.columns(2)
    with col_d3:
        if st.button("🇬🇧 London Studio", use_container_width=True):
            st.session_state.property_req = PropertyRequest(
                country="United Kingdom",
                state_province="Greater London",
                city="London",
                street="120 Shoreditch High St",
                postal_code="E1 6JE",
                property_type="Studio / Bachelor",
                bedrooms=0.0,
                bathrooms=1.0,
                furnished="Furnished",
                parking="Street / None"
            )
            st.session_state.analysis_result = None
            st.rerun()

    with col_d4:
        if st.button("🇺🇸 SF Room", use_container_width=True):
            st.session_state.property_req = PropertyRequest(
                country="United States",
                state_province="California",
                city="San Francisco",
                street="750 Mission St",
                postal_code="94103",
                property_type="Private Room in Shared House",
                bedrooms=1.0,
                bathrooms=1.0,
                furnished="Furnished",
                utilities_included=True
            )
            st.session_state.analysis_result = None
            st.rerun()

    st.markdown("---")
    st.info("💡 **Pro-Tip:** Upload a file or paste any unstructured text containing the property details to auto-populate all fields.")

# App Header
st.markdown('<div class="main-header">Rental Market Expert & Strategy Advisor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'Real-time rental market intelligence: Suggested Rent • Peak Vacancy Months • Target Tenant Segment • Fast-Response Platforms'
    '</div>',
    unsafe_allow_html=True
)

# Navigation Tabs
tab_input, tab_recommendations, tab_trends, tab_pdf = st.tabs([
    "📝 1. Property Request Input",
    "🎯 2. Recommendations & Rent Advisory",
    "📊 3. Past 4-Month Trends & Live Comps",
    "📄 4. Export PDF Report"
])

# ----------------------------------------------------
# TAB 1: PROPERTY REQUEST INPUT
# ----------------------------------------------------
with tab_input:
    st.subheader("Specify Target Property Details")
    st.write("You can either upload a file, paste unstructured text, or fill out the form manually:")

    input_mode = st.radio(
        "Choose Input Method:",
        ["📁 Upload Request File (JSON / CSV / TXT)", "✍️ Paste Unstructured Text / Freeform Request", "📋 Interactive Form"],
        horizontal=True
    )

    if input_mode == "📁 Upload Request File (JSON / CSV / TXT)":
        st.markdown("**Upload a request file containing Country, Province/State, City, Street, Postal Code, and Property/Room Type:**")
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["json", "csv", "txt", "text"],
            help="Accepts .json, .csv, or plain text containing your property address and room type"
        )
        if uploaded_file is not None:
            try:
                parsed = parse_file(uploaded_file)
                st.session_state.property_req = parsed
                st.success(f"✅ Successfully parsed file `{uploaded_file.name}`!")
            except Exception as e:
                st.error(f"Error parsing file: {e}")

    elif input_mode == "✍️ Paste Unstructured Text / Freeform Request":
        st.markdown("**Paste any email, text prompt, or listing note containing the address and room type:**")
        sample_prompt = (
            "I need a market rental analysis for a 2-bedroom apartment located at 180 University Avenue, "
            "Toronto, Ontario, M5H 0A2, Canada. It has 2 full bathrooms, in-suite laundry, and 1 underground parking spot."
        )
        pasted_text = st.text_area(
            "Paste request text here:",
            value=st.session_state.property_req.raw_text or sample_prompt,
            height=130
        )
        if st.button("🔍 Parse Pasted Text", type="secondary"):
            parsed = parse_freeform_text(pasted_text)
            st.session_state.property_req = parsed
            st.success("✅ Extracted property address & specifications from text!")

    st.markdown("---")
    st.markdown("#### Review & Adjust Property Specifications")

    req = st.session_state.property_req

    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox(
            "Country",
            ["Canada", "United States", "United Kingdom", "Australia", "Germany", "France", "Other"],
            index=["Canada", "United States", "United Kingdom", "Australia", "Germany", "France", "Other"].index(req.country)
            if req.country in ["Canada", "United States", "United Kingdom", "Australia", "Germany", "France", "Other"] else 0
        )
        street = st.text_input("Street Address", value=req.street)
    with col2:
        state_province = st.text_input("Province / State", value=req.state_province)
        postal_code = st.text_input("Postal / Zip Code", value=req.postal_code)
    with col3:
        city = st.text_input("City", value=req.city)
        property_type = st.selectbox(
            "Property / Room Type",
            [
                "1-Bedroom Apartment",
                "2-Bedroom Apartment",
                "3-Bedroom Apartment/House",
                "Studio / Bachelor",
                "Private Room in Shared House",
                "Basement Apartment",
                "Townhouse",
                "Single Family House"
            ],
            index=[
                "1-Bedroom Apartment",
                "2-Bedroom Apartment",
                "3-Bedroom Apartment/House",
                "Studio / Bachelor",
                "Private Room in Shared House",
                "Basement Apartment",
                "Townhouse",
                "Single Family House"
            ].index(req.property_type) if req.property_type in [
                "1-Bedroom Apartment",
                "2-Bedroom Apartment",
                "3-Bedroom Apartment/House",
                "Studio / Bachelor",
                "Private Room in Shared House",
                "Basement Apartment",
                "Townhouse",
                "Single Family House"
            ] else 0
        )

    col4, col5, col6, col7 = st.columns(4)
    with col4:
        bedrooms = st.number_input("Bedrooms", min_value=0.0, max_value=10.0, value=float(req.bedrooms), step=0.5)
    with col5:
        bathrooms = st.number_input("Bathrooms", min_value=0.5, max_value=8.0, value=float(req.bathrooms), step=0.5)
    with col6:
        furnished = st.selectbox("Furnishing", ["Unfurnished", "Furnished", "Partial"], index=["Unfurnished", "Furnished", "Partial"].index(req.furnished) if req.furnished in ["Unfurnished", "Furnished", "Partial"] else 0)
    with col7:
        parking = st.selectbox("Parking", ["Street / None", "Dedicated / Included", "Garage Parking"], index=["Street / None", "Dedicated / Included", "Garage Parking"].index(req.parking) if req.parking in ["Street / None", "Dedicated / Included", "Garage Parking"] else 0)

    col8, col9 = st.columns(2)
    with col8:
        pet_friendly = st.checkbox("Pet Friendly (Dogs / Cats Allowed)", value=req.pet_friendly)
    with col9:
        utilities_included = st.checkbox("Utilities Included (Heat / Hydro / Water / Wifi)", value=req.utilities_included)

    # Save to session
    st.session_state.property_req.country = country
    st.session_state.property_req.state_province = state_province
    st.session_state.property_req.city = city
    st.session_state.property_req.street = street
    st.session_state.property_req.postal_code = postal_code
    st.session_state.property_req.property_type = property_type
    st.session_state.property_req.bedrooms = bedrooms
    st.session_state.property_req.bathrooms = bathrooms
    st.session_state.property_req.furnished = furnished
    st.session_state.property_req.parking = parking
    st.session_state.property_req.pet_friendly = pet_friendly
    st.session_state.property_req.utilities_included = utilities_included

    st.markdown(f"**Full Property Identifier:** `{st.session_state.property_req.full_address}` ({property_type})")

    # Run Analysis Button
    run_btn = st.button("🚀 Search Rental Market & Generate Recommendations", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Searching rental market portals, forums, and analyzing past 4 months trends..."):
            web_results = search_rental_market_web(
                city=city,
                state_province=state_province,
                country=country,
                property_type=property_type,
                max_results=15
            )
            analysis = analyze_market_data(st.session_state.property_req, web_results)
            rec = generate_recommendations(analysis)
            st.session_state.analysis_result = analysis
            st.session_state.rec_result = rec
            st.success("✅ Rental market analysis completed!")
            st.info("👉 Switch to Tab 2 ('Recommendations & Rent Advisory') or Tab 3 ('Past 4-Month Trends') to view findings.")

# Automatically compute if not yet generated
if st.session_state.analysis_result is None:
    web_results = search_rental_market_web(
        city=st.session_state.property_req.city,
        state_province=st.session_state.property_req.state_province,
        country=st.session_state.property_req.country,
        property_type=st.session_state.property_req.property_type,
        max_results=15
    )
    st.session_state.analysis_result = analyze_market_data(st.session_state.property_req, web_results)
    st.session_state.rec_result = generate_recommendations(st.session_state.analysis_result)

analysis = st.session_state.analysis_result
rec = st.session_state.rec_result
sym = rec.currency_symbol

# ----------------------------------------------------
# TAB 2: RECOMMENDATIONS & RENT ADVISORY
# ----------------------------------------------------
with tab_recommendations:
    st.subheader(f"Strategic Recommendations for {analysis.property_request.city or 'Target Area'}")
    st.caption(f"Property: {analysis.property_request.full_address} | {analysis.property_request.property_type}")

    # Top KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-label">Recommended Target Rent</div>
            <div class="metric-value">{sym}{int(rec.suggested_rent_target):,}<span style="font-size: 1rem; color: #64748B;">/mo</span></div>
            <span class="badge-target">Optimal Absorption</span>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-label">Fast-Fill Rent (Low Vacancy)</div>
            <div class="metric-value">{sym}{int(rec.suggested_rent_fast_fill):,}<span style="font-size: 1rem; color: #64748B;">/mo</span></div>
            <span class="badge-fast">&lt; 7 Days to Lease</span>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-label">Peak Advertising Month</div>
            <div class="metric-value" style="color: #059669;">{rec.optimum_months[0]}</div>
            <span style="font-size: 0.8rem; color: #64748B;">List {rec.lead_time_days} days ahead</span>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-label">Fastest Response Portal</div>
            <div class="metric-value" style="font-size: 1.35rem; color: #D97706;">{rec.fast_response_platforms[0].name}</div>
            <span style="font-size: 0.8rem; color: #64748B;">Replies {rec.fast_response_platforms[0].expected_response_time}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Suggested Rent Pricing Tiers
    st.markdown("### 💰 Suggested Rent & Pricing Tiers")
    tiers_df = pd.DataFrame([
        {
            "Strategy Tier": t["tier"],
            "Suggested Monthly Rent": f"{sym}{int(t['rent']):,}",
            "Est. Vacancy Downtime": t["expected_days_to_fill"],
            "Strategic Rationale": t["strategy"]
        } for t in rec.pricing_tiers
    ])
    st.dataframe(tiers_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 2. Seasonality Calendar & Optimum Months to Advertise
    col_seas_text, col_seas_chart = st.columns([1, 1.3])
    with col_seas_text:
        st.markdown("### 📅 Optimum Months to Advertise Vacancy")
        st.markdown(f"""
        - **🏆 Prime Advertising Window:** **{', '.join(rec.optimum_months[:3])}**
          - Inquiries peak during these months due to professional relocations, university semesters, and favorable moving weather.
          - **Action:** Begin advertising **{rec.lead_time_days} days** prior to target move-in date to secure signed leases with high-credit tenants.
        - **❄️ Slow Months to Avoid:** **{', '.join(rec.slowest_months[:2])}**
          - Moving volumes drop significantly during late autumn and the winter holidays.
          - If your unit becomes vacant during these months, adopt the **Fast-Fulfillment Rent ({sym}{int(rec.suggested_rent_fast_fill)})** or offer lease concessions (e.g. free storage) to prevent extended cash flow drain.
        """)
        st.info(f"💡 **Vacancy Math:** 2 weeks of vacancy at {sym}{int(rec.suggested_rent_target)}/mo costs {sym}{int(rec.suggested_rent_target * 0.5):,}. Sacrificing {sym}{int(rec.suggested_rent_target - rec.suggested_rent_fast_fill)}/mo for instant placement saves money immediately.")

    with col_seas_chart:
        # Plotly Seasonality Heatmap / Bar Chart
        months_keys = list(rec.seasonality_12_months.keys())
        scores = list(rec.seasonality_12_months.values())
        colors = ['#10B981' if s >= 90 else ('#3B82F6' if s >= 70 else '#94A3B8') for s in scores]

        fig_seas = go.Figure(data=[
            go.Bar(
                x=months_keys,
                y=scores,
                marker_color=colors,
                text=[f"{s}/100" for s in scores],
                textposition='auto'
            )
        ])
        fig_seas.update_layout(
            title="12-Month Rental Demand & Inquiry Seasonality Index",
            xaxis_title="Month",
            yaxis_title="Demand Index (0-100)",
            yaxis_range=[0, 110],
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_seas, use_container_width=True)

    st.markdown("---")

    # 3. Best Target Segment & Fastest Response Websites
    col_seg, col_plat = st.columns([1, 1])

    with col_seg:
        st.markdown("### 🎯 Best Target Customer Segment")
        st.markdown(f"""
        - **Primary Persona:** **{rec.target_segment.primary}**
        - **Secondary Persona:** {rec.target_segment.secondary}
        - **Demographic Profile:** {rec.target_segment.demographic_summary}
        """)
        st.markdown("**Key Tenant Value Drivers:**")
        for driver in rec.target_segment.key_value_drivers:
            st.markdown(f"- ✅ {driver}")

        st.markdown(f"**Recommended Listing Headline Hook:**")
        st.code(rec.target_segment.listing_hook, language="text")

    with col_plat:
        st.markdown("### ⚡ Best Websites for Fast Responses")
        plat_df = pd.DataFrame([
            {
                "Rank": f"#{p.rank}",
                "Platform": p.name,
                "First Response": p.expected_response_time,
                "Audience Profile": p.lead_quality,
                "Cost": p.cost
            } for p in rec.fast_response_platforms
        ])
        st.dataframe(plat_df, use_container_width=True, hide_index=True)

        st.markdown(f"**Top Platform Tip ({rec.fast_response_platforms[0].name}):**")
        st.caption(rec.fast_response_platforms[0].pro_tip)

    st.markdown("---")

    # 4. Detailed Analytical Reasoning
    st.markdown("### 🧠 Comprehensive Analytical Reasoning")
    for pt in rec.reasoning_points:
        st.markdown(f"- {pt}")

# ----------------------------------------------------
# TAB 3: PAST 4-MONTH TRENDS & LIVE COMPS
# ----------------------------------------------------
with tab_trends:
    st.subheader("Past 4 Months Rental Market Trajectory & Web Findings")
    st.write(
        "Aggregates data fetched from rental market search engines, localized listing sites, "
        "and community discussions over the past 4 months."
    )

    t_col1, t_col2 = st.columns([1.2, 1])
    with t_col1:
        # Plot 4-Month Trend Chart
        df_4m = pd.DataFrame([
            {
                "Month": m.month_name,
                "Median Rent": m.median_rent,
                "MoM Change (%)": m.mom_growth_pct,
                "Days to Fill": m.avg_days_to_fill,
                "Fulfillment Rate (%)": m.fulfillment_rate_pct
            } for m in analysis.past_4_months
        ])

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_4m["Month"],
            y=df_4m["Median Rent"],
            mode="lines+markers",
            name="Median Rent",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=8)
        ))
        fig_trend.update_layout(
            title=f"4-Month Median Rent Trajectory ({sym})",
            xaxis_title="Month (Past 4 Months)",
            yaxis_title=f"Median Rent ({sym})",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with t_col2:
        st.markdown("#### 4-Month Fulfillment Metrics")
        st.dataframe(df_4m[["Month", "Median Rent", "MoM Change (%)", "Days to Fill", "Fulfillment Rate (%)"]], use_container_width=True, hide_index=True)
        st.metric("Average Days on Market (Past 4 Months)", f"{analysis.avg_days_on_market} Days", delta=f"{analysis.fulfillment_velocity}")

    st.markdown("---")

    # Live Comps & Community Forum Findings
    st.markdown("#### 🌐 Live Web Search Listings & Local Forum Discussions")
    st.caption("Data points extracted from rental websites, real estate portals, and local landlord/tenant discussion threads:")

    for idx, comp in enumerate(analysis.sample_comps, start=1):
        with st.expander(f"{comp.get('category', 'Listing')}: {comp.get('title', 'Market Comp')} ({comp.get('source', 'Web')})", expanded=(idx <= 2)):
            st.markdown(f"**Source:** [{comp.get('source', 'Link')}]({comp.get('url', '#')}) | **Timeframe:** {comp.get('date_ref', 'Recent')}")
            st.write(comp.get('snippet', 'No description available.'))
            if comp.get('prices_found'):
                st.markdown(f"**Identified Rent Figures:** `{[f'{sym}{int(p)}' for p in comp['prices_found']]}`")

    st.markdown("---")
    st.markdown("#### 🗣️ Community Forum & Sentiment Highlights")
    for s in analysis.sentiment_insights:
        st.markdown(f"- 💬 {s}")

# ----------------------------------------------------
# TAB 4: EXPORT PDF REPORT
# ----------------------------------------------------
with tab_pdf:
    st.subheader("📄 Export Executive Rental Market Report")
    st.write("Generate and download a high-resolution PDF report containing the full analysis, pricing tiers, seasonality curve, platform strategies, and analytical reasoning.")

    col_pdf_preview, col_pdf_download = st.columns([1.5, 1])

    with col_pdf_preview:
        st.markdown(f"""
        ### Report Summary Preview
        - **Target Property:** {analysis.property_request.full_address}
        - **Property / Room Type:** {analysis.property_request.property_type}
        - **Suggested Target Rent:** **{sym}{int(rec.suggested_rent_target):,} / month**
        - **Fast-Lease Rent:** **{sym}{int(rec.suggested_rent_fast_fill):,} / month**
        - **Peak Advertising Window:** **{', '.join(rec.optimum_months[:2])}**
        - **Top Fast Response Platform:** **{rec.fast_response_platforms[0].name}**
        - **Target Tenant Persona:** **{rec.target_segment.primary}**
        - **Fulfillment Absorption:** {analysis.fulfillment_velocity} ({analysis.avg_days_on_market} avg days on market)
        """)

    with col_pdf_download:
        st.markdown("### Generate PDF")
        if st.button("🔄 Render Printable PDF File", type="primary", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                pdf_bytes = create_rental_market_pdf(analysis.property_request, analysis, rec)
                st.session_state.pdf_data = pdf_bytes
                st.success("✅ PDF report ready for download!")

        if "pdf_data" not in st.session_state:
            # Generate default PDF in session state
            st.session_state.pdf_data = create_rental_market_pdf(analysis.property_request, analysis, rec)

        safe_city = (analysis.property_request.city or "Market").replace(" ", "_")
        filename = f"Rental_Report_{safe_city}_{analysis.property_request.property_type.replace(' ', '_')}.pdf"

        st.download_button(
            label="📥 Download Full PDF Report",
            data=st.session_state.pdf_data,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )
        st.caption("PDF includes formal headers, tables, colored strategic callout boxes, and executive summary.")

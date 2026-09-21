"""
Real Estate Market Predictor - Streamlit Application.
Role: Real Estate Predictor
Objective: For a given address in a neighborhood, search the web for the past 3-6 months
and predict the selling price and days on market to sell with comprehensive reasoning and PDF export.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import DEFAULT_WEBSITES, PROPERTY_TYPES, PROPERTY_CONDITIONS, TIME_HORIZONS
from file_parser import parse_input_file
from search_engine import RealEstateSearchEngine
from market_analyzer import MarketHealthAnalyzer
from predictor import RealEstatePredictor
from pdf_generator import RealEstatePDFGenerator

# ---------------------------------------------------------
# Page Setup & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Real Estate Market Predictor",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive aesthetic
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .role-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1E3A8A, #0D9488);
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.8rem;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: 4px;
    }
    .stDownloadButton button {
        background: linear-gradient(135deg, #0D9488, #1E3A8A) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.6rem 1.4rem !important;
        border-radius: 8px !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    .status-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/real-estate.png", width=70)
    st.markdown("### ⚙️ Engine Settings")
    
    time_horizon = st.selectbox(
        "Observation Time Window",
        TIME_HORIZONS,
        index=0,
        help="Search the web for listings, sales comps, and reports over this duration."
    )
    
    st.markdown("---")
    st.markdown("#### 🤖 AI Enhancement (Optional)")
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Optional. If provided, enhances executive market commentary using Gemini LLM. App runs smoothly without it."
    )
    
    if "analysis_results" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📄 Export PDF Report")
        _side_pdf = st.session_state["analysis_results"]["pdf_bytes"]
        _side_city = st.session_state["prop_data"].get("city", "City")
        _side_street = st.session_state["prop_data"].get("street", "Property")
        _side_filename = f"RealEstate_Prediction_{_side_city}_{_side_street}".replace(" ", "_").replace(",", "").replace(".", "") + ".pdf"
        st.download_button(
            label="📥 Export PDF report",
            data=_side_pdf,
            file_name=_side_filename,
            mime="application/pdf",
            key="sidebar_pdf_btn",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown("#### 📂 Sample Request Files")
    st.caption("Inspect or download sample property requests:")
    
    sample_ca_path = "sample_inputs/sample_canada_property.json"
    if os.path.exists(sample_ca_path):
        with open(sample_ca_path, "r") as f:
            st.download_button(
                "📥 Download Toronto Sample (JSON)",
                data=f.read(),
                file_name="sample_toronto_property.json",
                mime="application/json"
            )

    sample_us_path = "sample_inputs/sample_us_property.json"
    if os.path.exists(sample_us_path):
        with open(sample_us_path, "r") as f:
            st.download_button(
                "📥 Download Austin Sample (JSON)",
                data=f.read(),
                file_name="sample_austin_property.json",
                mime="application/json"
            )

    st.markdown("---")
    st.caption("Real Estate Predictor Engine v2.0 • Powered by Multi-Source Web Intelligence & Hedonic Valuation Regression")


# ---------------------------------------------------------
# Header & Hero
# ---------------------------------------------------------
st.markdown('<div class="role-badge">ROLE: REAL ESTATE PREDICTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏡 Real Estate Market Predictor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">For any given address, search the web over the past 3 to 6 months across leading property websites, '
    'analyze neighborhood market health, and predict the <b>expected selling price</b> and <b>days on market (DOM)</b> to sell. '
    'Export publication-grade PDF appraisal reports.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Session State Initialization for Property Data
# ---------------------------------------------------------
if "prop_data" not in st.session_state:
    st.session_state["prop_data"] = {
        "country": "Canada",
        "province_state": "Ontario",
        "city": "Toronto",
        "street": "142 Elmwood Ave",
        "postal_code": "M2N 3M3",
        "property_type": "Single Family Detached",
        "bedrooms": 4,
        "bathrooms": 3.5,
        "sqft": 2650,
        "lot_size": "50 x 130 ft",
        "year_built": 2005,
        "condition": "Excellent (Fully Renovated)",
        "websites": ["realtor.ca", "zolo.ca", "housesigma.com", "redfin.ca"],
        "time_horizon": "Past 3 Months"
    }

# ---------------------------------------------------------
# Input Section: Tabs for File Upload vs Interactive Form
# ---------------------------------------------------------
input_tab1, input_tab2 = st.tabs(["📝 Interactive Property Form", "📁 Upload Request File (JSON / TXT / CSV)"])

with input_tab2:
    st.markdown("#### Option 1: Upload User Request File")
    st.info("Upload a request file containing Country, Province/State, City, Street, Postal Code, and Target Websites to search.")
    
    col_demo1, col_demo2, col_demo3 = st.columns(3)
    with col_demo1:
        if st.button("🇨🇦 Load Toronto Sample"):
            with open("sample_inputs/sample_canada_property.json") as f:
                st.session_state["prop_data"] = parse_input_file(f.read(), "sample_canada_property.json")
            st.success("Loaded Toronto Detached Home sample!")
            st.rerun()
    with col_demo2:
        if st.button("🇺🇸 Load Austin Sample"):
            with open("sample_inputs/sample_us_property.json") as f:
                st.session_state["prop_data"] = parse_input_file(f.read(), "sample_us_property.json")
            st.success("Loaded Austin Townhouse sample!")
            st.rerun()
    with col_demo3:
        if st.button("🏢 Load Toronto Condo Sample"):
            with open("sample_inputs/sample_request.txt") as f:
                st.session_state["prop_data"] = parse_input_file(f.read(), "sample_request.txt")
            st.success("Loaded Toronto Condo sample from text!")
            st.rerun()

    uploaded_file = st.file_uploader(
        "Choose an input file (.json, .txt, .yaml, .csv)",
        type=["json", "txt", "yaml", "yml", "csv"]
    )
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode("utf-8")
            parsed = parse_input_file(content, uploaded_file.name)
            st.session_state["prop_data"] = parsed
            st.success(f"Successfully parsed request file: **{uploaded_file.name}**")
            with st.expander("👁️ View Parsed Property Data", expanded=False):
                st.json(parsed)
        except Exception as e:
            st.error(f"Error parsing uploaded file: {str(e)}")

with input_tab1:
    st.markdown("#### Option 2: Enter Property & Target Search Websites")
    
    c1, c2, c3 = st.columns([2, 1.5, 1.5])
    with c1:
        street_in = st.text_input("Street Address", value=st.session_state["prop_data"].get("street", "142 Elmwood Ave"))
    with c2:
        city_in = st.text_input("City", value=st.session_state["prop_data"].get("city", "Toronto"))
    with c3:
        prov_in = st.text_input("Province / State", value=st.session_state["prop_data"].get("province_state", "Ontario"))

    c4, c5, c6 = st.columns([1.5, 1.5, 2])
    with c4:
        country_in = st.text_input("Country", value=st.session_state["prop_data"].get("country", "Canada"))
    with c5:
        postal_in = st.text_input("Postal / Zip Code", value=st.session_state["prop_data"].get("postal_code", "M2N 3M3"))
    with c6:
        type_curr = st.session_state["prop_data"].get("property_type", "Single Family Detached")
        type_idx = PROPERTY_TYPES.index(type_curr) if type_curr in PROPERTY_TYPES else 0
        type_in = st.selectbox("Property Type", PROPERTY_TYPES, index=type_idx)

    c7, c8, c9, c10 = st.columns(4)
    with c7:
        beds_in = st.number_input("Bedrooms", min_value=1, max_value=20, value=int(st.session_state["prop_data"].get("bedrooms", 4)))
    with c8:
        baths_in = st.number_input("Bathrooms", min_value=1.0, max_value=15.0, step=0.5, value=float(st.session_state["prop_data"].get("bathrooms", 3.5)))
    with c9:
        sqft_in = st.number_input("Interior Sq.Ft.", min_value=300, max_value=30000, step=50, value=int(st.session_state["prop_data"].get("sqft", 2650)))
    with c10:
        year_in = st.number_input("Year Built", min_value=1800, max_value=2027, value=int(st.session_state["prop_data"].get("year_built", 2005)))

    c11, c12 = st.columns([1.5, 2.5])
    with c11:
        cond_curr = st.session_state["prop_data"].get("condition", "Excellent (Fully Renovated)")
        cond_idx = PROPERTY_CONDITIONS.index(cond_curr) if cond_curr in PROPERTY_CONDITIONS else 1
        cond_in = st.selectbox("Property Condition", PROPERTY_CONDITIONS, index=cond_idx)
    with c12:
        lot_in = st.text_input("Lot Size / Dimensions", value=st.session_state["prop_data"].get("lot_size", "50 x 130 ft"))

    st.markdown("##### 🌐 Websites to Search for Past 3-6 Months Data")
    default_sites_str = ", ".join(st.session_state["prop_data"].get("websites", DEFAULT_WEBSITES[:4]))
    websites_in_str = st.text_area(
        "Enter websites separated by commas (e.g., realtor.ca, zillow.com, redfin.com, zolo.ca):",
        value=default_sites_str,
        height=68,
        help="The search engine will target these specific property listing and sales databases."
    )

    # Update session state with current form values
    st.session_state["prop_data"].update({
        "country": country_in,
        "province_state": prov_in,
        "city": city_in,
        "street": street_in,
        "postal_code": postal_in,
        "property_type": type_in,
        "bedrooms": beds_in,
        "bathrooms": baths_in,
        "sqft": sqft_in,
        "lot_size": lot_in,
        "year_built": year_in,
        "condition": cond_in,
        "websites": [s.strip() for s in websites_in_str.split(",") if s.strip()],
        "time_horizon": time_horizon
    })

# ---------------------------------------------------------
# Run Analysis & Prediction Button
# ---------------------------------------------------------
st.markdown("---")
btn_col1, btn_col2 = st.columns([2.5, 2.5])
with btn_col1:
    run_btn = st.button("🔍 Search Web & Predict Selling Price & DOM", type="primary", use_container_width=True)
with btn_col2:
    if "analysis_results" in st.session_state:
        _cur_pdf = st.session_state["analysis_results"]["pdf_bytes"]
        _cur_city = st.session_state["prop_data"].get("city", "City")
        _cur_street = st.session_state["prop_data"].get("street", "Property")
        _cur_filename = f"RealEstate_Prediction_{_cur_city}_{_cur_street}".replace(" ", "_").replace(",", "").replace(".", "") + ".pdf"
        st.download_button(
            label="📥 Export PDF report",
            data=_cur_pdf,
            file_name=_cur_filename,
            mime="application/pdf",
            key="action_bar_pdf_btn",
            use_container_width=True
        )

if run_btn:
    prop_info = st.session_state["prop_data"]
    websites = prop_info.get("websites", ["realtor.ca", "zillow.com"])

    with st.status("🚀 Real Estate Predictor Agent in Progress...", expanded=True) as status:
        st.write(f"📡 Step 1: Querying web for recent sales & listings on {', '.join(websites[:4])} over {time_horizon}...")
        search_engine = RealEstateSearchEngine()
        search_data = search_engine.search_market_data(
            property_info=prop_info,
            websites=websites,
            time_horizon=time_horizon
        )
        st.write(f"✅ Found {len(search_data.get('comparables', []))} comparable sales and neighborhood reports.")

        st.write("📊 Step 2: Analyzing neighborhood market health & absorption velocity for similar property types...")
        analyzer = MarketHealthAnalyzer()
        market_health = analyzer.analyze_health(prop_info, search_data)
        st.write(f"✅ Market state identified: **{market_health.get('market_state')}** (Health Score: {market_health.get('health_score')}/100).")

        st.write("🎯 Step 3: Computing expected selling price, days on market (DOM), and hedonic adjustments...")
        predictor = RealEstatePredictor()
        prediction = predictor.predict(
            property_info=prop_info,
            market_health=market_health,
            search_data=search_data,
            api_key=api_key_input
        )
        st.write(f"✅ Predicted Selling Price: **{prediction.get('currency_symbol')}{prediction.get('expected_price'):,}** | Predicted DOM: **{prediction.get('expected_dom')} Days**.")

        st.write("📄 Step 4: Generating executive PDF appraisal report for export...")
        pdf_gen = RealEstatePDFGenerator()
        pdf_bytes = pdf_gen.generate_pdf(
            property_info=prop_info,
            market_health=market_health,
            prediction=prediction,
            search_data=search_data
        )
        st.write("✅ PDF report compiled and ready for download.")
        status.update(label="✨ Analysis & Prediction Complete!", state="complete", expanded=False)

    # Save to session state so user can interact with charts/tabs without losing results
    st.session_state["analysis_results"] = {
        "prop_info": prop_info,
        "search_data": search_data,
        "market_health": market_health,
        "prediction": prediction,
        "pdf_bytes": pdf_bytes
    }

# ---------------------------------------------------------
# Display Results
# ---------------------------------------------------------
if "analysis_results" in st.session_state:
    res = st.session_state["analysis_results"]
    prop_info = res["prop_info"]
    search_data = res["search_data"]
    mhealth = res["market_health"]
    pred = res["prediction"]
    pdf_bytes = res["pdf_bytes"]

    curr_sym = pred.get("currency_symbol", "$")
    street = prop_info.get("street", "Property")
    city = prop_info.get("city", "City")

    st.markdown("## 📊 Prediction Dashboard & Market Analysis")
    st.markdown(f"**Target Property:** `{street}, {city}, {prop_info.get('province_state', '')} {prop_info.get('postal_code', '')}`")

    # PDF Export Section (Prominent)
    clean_addr = f"{city}_{street}".replace(" ", "_").replace(",", "").replace(".", "")
    pdf_filename = f"RealEstate_Prediction_{clean_addr}.pdf"

    exp_col1, exp_col2 = st.columns([2.5, 2])
    with exp_col1:
        st.download_button(
            label="📥 Export PDF report",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    with exp_col2:
        st.caption(f"📄 File: `{pdf_filename}` ({len(pdf_bytes):,} bytes)")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Four Key Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.85rem; font-weight:700; color:#64748B;">EXPECTED SELLING PRICE</div>
            <div class="metric-val">{curr_sym}{pred['expected_price']:,}</div>
            <div class="metric-sub">Range: {curr_sym}{pred['price_range_low']:,} – {curr_sym}{pred['price_range_high']:,}</div>
            <div style="font-size:0.8rem; color:#0D9488; font-weight:600; margin-top:3px;">{curr_sym}{pred['expected_sqft_rate']:,.1f} / sq.ft.</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.85rem; font-weight:700; color:#64748B;">EXPECTED DAYS ON MARKET (DOM)</div>
            <div class="metric-val" style="color:#0D9488;">{pred['expected_dom']} Days</div>
            <div class="metric-sub">Expected Range: {pred['dom_range_low']} – {pred['dom_range_high']} Days</div>
            <div style="font-size:0.8rem; color:#1E3A8A; font-weight:600; margin-top:3px;">{pred['velocity_tag']}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.85rem; font-weight:700; color:#64748B;">MARKET CLIMATE</div>
            <div class="metric-val" style="color:{mhealth['market_color']};">{mhealth['market_state']}</div>
            <div class="metric-sub">Health Index: <b>{mhealth['health_score']}/100</b></div>
            <div style="font-size:0.8rem; color:#4B5563; margin-top:3px;">{mhealth['months_of_inventory']} Mo. Supply • {round(mhealth['sale_to_list_ratio']*100, 1)}% List/Sale</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.85rem; font-weight:700; color:#64748B;">VALUATION CONFIDENCE</div>
            <div class="metric-val" style="color:#10B981;">{pred['confidence_score']}%</div>
            <div class="metric-sub">Based on {mhealth['cohort_stats']['sample_size']} Web Comps</div>
            <div style="font-size:0.8rem; color:#64748B; margin-top:3px;">Observation: {search_data.get('time_horizon', '3 Mo.')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Visual Analytics (Plotly Charts)
    # ---------------------------------------------------------
    chart_tab1, chart_tab2, chart_tab3 = st.tabs([
        "📈 Comps Price vs. Days on Market",
        "🎯 Pricing Strategy Sensitivity",
        "📊 Price per Sq.Ft. Benchmark"
    ])

    comps_df = pd.DataFrame(search_data.get("comparables", []))
    
    with chart_tab1:
        if not comps_df.empty:
            fig1 = go.Figure()

            # Comps scatter
            fig1.add_trace(go.Scatter(
                x=comps_df["days_on_market"],
                y=comps_df["sold_price"],
                mode='markers+text',
                name='Web Comps',
                text=comps_df['address'].str.slice(0, 22),
                textposition='top center',
                marker=dict(
                    size=12,
                    color=comps_df["price_per_sqft"],
                    colorscale='Teal',
                    showscale=True,
                    colorbar=dict(title=f"$/Sq.Ft. ({curr_sym})")
                ),
                hovertemplate="<b>%{text}</b><br>Sold Price: " + curr_sym + "%{y:,.0f}<br>DOM: %{x} days<extra></extra>"
            ))

            # Subject Property Prediction Marker
            fig1.add_trace(go.Scatter(
                x=[pred["expected_dom"]],
                y=[pred["expected_price"]],
                mode='markers+text',
                name='Predicted Subject Property',
                text=["★ PREDICTED TARGET"],
                textposition='bottom center',
                marker=dict(size=18, color='#EF4444', symbol='star'),
                hovertemplate="<b>Target Prediction</b><br>Expected Price: " + curr_sym + "%{y:,.0f}<br>Expected DOM: %{x} days<extra></extra>"
            ))

            fig1.update_layout(
                title=f"Market Liquidity: Sold Price vs. Days on Market ({city})",
                xaxis_title="Days on Market (DOM)",
                yaxis_title=f"Sold Price ({curr_sym})",
                template="plotly_white",
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No comparable listings available for chart.")

    with chart_tab2:
        scenarios_df = pd.DataFrame(pred.get("scenarios", []))
        if not scenarios_df.empty:
            fig2 = px.bar(
                scenarios_df,
                x="strategy",
                y="list_price",
                color="expected_dom",
                color_continuous_scale="Blues_r",
                text="list_price",
                labels={"strategy": "Pricing Strategy", "list_price": f"Price ({curr_sym})", "expected_dom": "Expected DOM"},
                title="Pricing Strategy Sensitivity: Price vs. Days to Sell"
            )
            fig2.update_traces(texttemplate=curr_sym + '%{text:,.0f}', textposition='outside')
            fig2.update_layout(template="plotly_white", height=420)
            st.plotly_chart(fig2, use_container_width=True)

    with chart_tab3:
        if not comps_df.empty:
            rates = list(comps_df["price_per_sqft"])
            rates.append(pred["expected_sqft_rate"])
            labels = list(comps_df["address"].str.slice(0, 18))
            labels.append("★ Subject Property (Predicted)")
            colors = ["#94A3B8"] * len(comps_df) + ["#1E3A8A"]

            fig3 = go.Figure(data=[
                go.Bar(
                    x=labels,
                    y=rates,
                    marker_color=colors,
                    text=[f"{curr_sym}{r:,.0f}" for r in rates],
                    textposition='auto'
                )
            ])
            fig3.update_layout(
                title=f"Price per Sq.Ft. Benchmark vs. Similar Comps ({city})",
                xaxis_title="Property",
                yaxis_title=f"Price / Sq.Ft. ({curr_sym})",
                template="plotly_white",
                height=420
            )
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # Detailed Reasoning & Market Narrative Breakdown
    # ---------------------------------------------------------
    st.markdown("### 🧠 Predictive Reasoning & Appraisal Breakdown")
    st.markdown(
        f"<div class='status-box'><b>Role Synthesis:</b> As a Real Estate Predictor, the valuation of "
        f"<b>{curr_sym}{pred['expected_price']:,}</b> and DOM forecast of <b>{pred['expected_dom']} days</b> "
        f"are justified by five distinct structural pillars:</div>",
        unsafe_allow_html=True
    )

    reasoning = pred.get("reasoning", {})

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        with st.expander("🏛️ 1. Neighborhood Micro-Market Dynamics & Inventory", expanded=True):
            st.markdown(reasoning.get("micro_market_dynamics", ""))

        with st.expander("⚖️ 3. Physical Feature & Condition Adjustments (Hedonic)", expanded=True):
            st.markdown(reasoning.get("property_adjustments", ""))
            st.markdown("##### Valuation Adjustment Schedule:")
            adjs = pred.get("adjustments", {})
            adj_df = pd.DataFrame([
                {"Factor": "Cohort SqFt Base Valuation", "Adjustment Amount": f"{curr_sym}{adjs.get('base_valuation', 0):,}"},
                {"Factor": "Bedrooms Differential", "Adjustment Amount": f"{curr_sym}{adjs.get('bedroom_adjustment', 0):,}"},
                {"Factor": "Bathrooms Differential", "Adjustment Amount": f"{curr_sym}{adjs.get('bathroom_adjustment', 0):,}"},
                {"Factor": "Property Condition", "Adjustment Amount": f"{curr_sym}{adjs.get('condition_adjustment', 0):,}"},
                {"Factor": "Age / Year Built", "Adjustment Amount": f"{curr_sym}{adjs.get('age_adjustment', 0):,}"},
                {"Factor": "Market Climate Momentum", "Adjustment Amount": f"{curr_sym}{adjs.get('market_momentum_adjustment', 0):,}"}
            ])
            st.dataframe(adj_df, hide_index=True, use_container_width=True)

    with r_col2:
        with st.expander("📊 2. Comparable Sales Evidence & Cohort Benchmark", expanded=True):
            st.markdown(reasoning.get("comparable_sales_evidence", ""))

        with st.expander("⏱️ 4. Days on Market (DOM) Velocity Forecast", expanded=True):
            st.markdown(reasoning.get("dom_velocity_drivers", ""))

        with st.expander("🎯 5. Actionable Pricing Advisory & Scenarios", expanded=True):
            st.markdown(reasoning.get("strategic_recommendations", ""))

    st.markdown("---")

    # ---------------------------------------------------------
    # Comparable Properties Table
    # ---------------------------------------------------------
    st.markdown("### 📋 Comparable Properties Fetched from Web Search (Past 3-6 Months)")
    if not comps_df.empty:
        display_comps = comps_df[[
            "address", "sold_price", "days_on_market", "bedrooms", "bathrooms", "sqft", "price_per_sqft", "sold_date", "source"
        ]].copy()
        display_comps.columns = [
            "Address", f"Sold Price ({curr_sym})", "DOM", "Beds", "Baths", "Sq.Ft.", f"$/Sq.Ft. ({curr_sym})", "Sold Date", "Portal Source"
        ]
        display_comps[f"Sold Price ({curr_sym})"] = display_comps[f"Sold Price ({curr_sym})"].map(lambda x: f"{curr_sym}{x:,}")
        display_comps[f"$/Sq.Ft. ({curr_sym})"] = display_comps[f"$/Sq.Ft. ({curr_sym})"].map(lambda x: f"{curr_sym}{x:,.1f}")

        st.dataframe(display_comps, hide_index=True, use_container_width=True)

    # ---------------------------------------------------------
    # Sources & Web Transparency
    # ---------------------------------------------------------
    with st.expander("🌐 Web Search Citations & Target Websites Queried", expanded=False):
        st.markdown(f"**Target Websites Searched:** `{', '.join(search_data.get('target_websites', []))}`")
        st.markdown(f"**Search Horizon:** `{search_data.get('time_horizon', 'Past 3 Months')}`")
        st.markdown(f"**Live Query Strings Dispatched:**")
        for q in search_data.get("search_queries", []):
            st.code(q, language="text")

        snippets = search_data.get("raw_snippets", [])
        if snippets:
            st.markdown("##### Extracted Web Snippets:")
            for snip in snippets[:4]:
                st.markdown(f"• **[{snip.get('title')}]({snip.get('href')})**: {snip.get('body')}")

"""
FixMate: Expert DIY Repair Solutions Wizard
Streamlit Application for Equipment Diagnostics, Real-Time Web & Forum Research,
Location-Aware Parts Sourcing, and Outside Professional Repair Cost Estimation.
"""

import os
import json
import streamlit as st
from config import APP_TITLE, APP_SUBTITLE, EQUIPMENT_TAXONOMY, PREFERRED_GEMINI_MODELS
from sample_data import SAMPLE_PRESETS
from research_engine import ResearchEngine
from repair_agent import RepairAgent
from pdf_generator import generate_repair_pdf
from history_manager import HistoryManager

# Page Configuration
st.set_page_config(
    page_title="FixMate - Expert DIY Repair Wizard",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished modern aesthetic
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .main-header p {
        color: #E0E7FF;
        margin-top: 6px;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1E293B;
    }
    .hazard-badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #F87171;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .hazard-badge-moderate {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FCD34D;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .hazard-badge-low {
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .source-card {
        border-left: 4px solid #2563EB;
        background-color: #F8FAFC;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
    .forum-card {
        border-left: 4px solid #EA580C;
        background-color: #FFF7ED;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
    .local-card {
        border-left: 4px solid #16A34A;
        background-color: #F0FDF4;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
    .pro-card {
        border-left: 4px solid #7C3AED;
        background-color: #FAF5FF;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
    .step-box {
        background-color: #F1F5F9;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-left: 5px solid #3B82F6;
    }
    .pro-tip {
        background-color: #EFF6FF;
        border-radius: 6px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.9rem;
        color: #1E40AF;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "dossier" not in st.session_state:
    st.session_state.dossier = None
if "research_data" not in st.session_state:
    st.session_state.research_data = None
if "equipment_info" not in st.session_state:
    st.session_state.equipment_info = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "step_progress" not in st.session_state:
    st.session_state.step_progress = {}

# Header Banner
st.markdown(f"""
<div class="main-header">
    <h1>🛠️ {APP_TITLE}</h1>
    <p>{APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar: Controls, Presets & Settings
with st.sidebar:
    st.header("⚙️ Configuration & Quick Start")
    
    # Preset Loader
    st.subheader("🚀 Quick Test Scenarios")
    preset_choice = st.selectbox(
        "Load a realistic test case:",
        options=["-- Select a Preset --"] + list(SAMPLE_PRESETS.keys()),
        index=0
    )
    
    loaded_preset = None
    if preset_choice != "-- Select a Preset --":
        loaded_preset = SAMPLE_PRESETS[preset_choice]
        st.info(f"Loaded: **{preset_choice}**")

    st.divider()

    # API Configuration
    st.subheader("🔑 AI Diagnostics Engine")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google Gemini API Key (Optional Override):",
        value=env_key,
        type="password",
        help="Leave default to use the environment key. If empty, the app runs with the expert heuristic engine."
    )
    
    if api_key_input:
        st.success("API Key Active (Gemini AI Enabled)")
    else:
        st.warning("Offline / Heuristic Engine Mode Active")

    st.divider()

    # Research Engine Settings
    st.subheader("🔍 Online Research Settings")
    include_forums = st.checkbox("Include Reddit / iFixit Forums", value=True)
    include_videos = st.checkbox("Include YouTube Video Guides", value=True)
    include_local = st.checkbox("Include Postal Address Parts Search", value=True)
    include_pros = st.checkbox("Include Nearest Outside Repair Shops", value=True)
    
    st.divider()
    st.caption("FixMate v2.5 • Powered by Gemini & Multi-Engine Web Scraping")

# App Navigation Tabs
tab_diagnose, tab_assistant, tab_history, tab_help = st.tabs([
    "🔧 Diagnostic Intake & Plan",
    "💬 Live Repair Assistant",
    "🕒 Saved Repair History",
    "ℹ️ Guide & DIY Safety"
])

# -------------------------------------------------------------
# TAB 1: DIAGNOSTIC INTAKE & PLAN
# -------------------------------------------------------------
with tab_diagnose:
    st.subheader("1. Enter Equipment & Problem Details")
    
    col1, col2 = st.columns([1, 1])
    
    # Category Selection
    category_list = list(EQUIPMENT_TAXONOMY.keys())
    default_cat_idx = 0
    if loaded_preset and loaded_preset["category"] in category_list:
        default_cat_idx = category_list.index(loaded_preset["category"])
        
    with col1:
        selected_category = st.selectbox(
            "Equipment Category:",
            options=category_list,
            index=default_cat_idx,
            help="Select the general industry or device class."
        )
        
        cat_info = EQUIPMENT_TAXONOMY[selected_category]
        subtypes = cat_info["subtypes"]
        default_sub_idx = 0
        if loaded_preset and loaded_preset.get("subtype") in subtypes:
            default_sub_idx = subtypes.index(loaded_preset["subtype"])
            
        selected_subtype = st.selectbox(
            "Specific Equipment Type:",
            options=subtypes,
            index=default_sub_idx
        )
        
        # Make / Brand
        common_makes = cat_info["common_makes"]
        default_make = loaded_preset["make"] if loaded_preset else common_makes[0]
        
        make_input = st.text_input(
            "Make / Manufacturer Brand:",
            value=default_make,
            help="e.g., Whirlpool, Honda, Samsung, DeWalt, Apple, Bosch"
        )

    with col2:
        # Model Number
        default_model = loaded_preset["model"] if loaded_preset else ""
        model_input = st.text_input(
            "Model Number or Name:",
            value=default_model,
            placeholder="e.g. WTW5000DW0, HRN216, RF28R7351SR",
            help="Crucial for locating exact wiring diagrams, exploded parts views, and recall notices."
        )
        st.caption(f"💡 **Model Tag Tip:** {cat_info['model_tip']}")
        
        # Postal Address / Physical Location
        default_loc = loaded_preset["location"] if loaded_preset else "Chicago, IL 60601, USA"
        location_input = st.text_input(
            "Physical Location / Postal Address:",
            value=default_loc,
            placeholder="Street address or City, State/Province, ZIP/Postal Code",
            help="Used to locate nearby parts warehouses, local hardware supply stores, and nearest professional repair facilities."
        )

    # Problem Description
    st.subheader("2. Describe the Problem")
    default_problem = loaded_preset["problem"] if loaded_preset else ""
    problem_input = st.text_area(
        "Describe what is happening in detail:",
        value=default_problem,
        height=110,
        placeholder="Detail what is failing, any error codes shown (e.g., F02, E15), weird noises (grinding, buzzing), leaks, burning smell, or when the problem first started..."
    )

    # Optional Skills & Tools Expander
    with st.expander("🛠️ User DIY Skill Level & Tools Available (Optional)", expanded=False):
        c_skill, c_tools = st.columns([1, 2])
        with c_skill:
            skill_level = st.radio(
                "Your DIY Experience:",
                options=["Beginner", "Intermediate", "Advanced"],
                index=1 if (not loaded_preset or loaded_preset.get("skill_level") == "Intermediate") else (0 if loaded_preset.get("skill_level") == "Beginner" else 2),
                horizontal=True
            )
        with c_tools:
            standard_tools = [
                "Basic Screwdriver Set", "Digital Multimeter", "Socket / Ratchet Set", 
                "Adjustable Wrench / Pliers", "Soldering Iron", "Heat Gun / Hair Dryer", 
                "Towel & Drain Bucket", "Safety Glasses & Gloves"
            ]
            default_tool_selection = loaded_preset.get("tools", standard_tools[:4]) if loaded_preset else standard_tools[:3]
            selected_tools = st.multiselect(
                "Tools You Have On Hand:",
                options=standard_tools,
                default=[t for t in default_tool_selection if t in standard_tools]
            )

    # Diagnose Button
    st.write("")
    diagnose_clicked = st.button("🔍 Research & Generate Expert DIY Solution", type="primary", use_container_width=True)

    if diagnose_clicked:
        if not make_input.strip() or not problem_input.strip():
            st.error("Please provide at least the Make/Manufacturer and a Problem Description.")
        else:
            with st.status("Analyzing problem and researching online repair knowledge...", expanded=True) as status:
                st.write("📡 **Querying technical manuals and repair databases...**")
                engine = ResearchEngine()
                
                # Execute web & forum research
                research_res = engine.aggregate_research(
                    category=selected_category,
                    make=make_input.strip(),
                    model=model_input.strip(),
                    problem=problem_input.strip(),
                    location=location_input.strip()
                )
                st.write(f"✅ Found {len(research_res['guides'])} technical guides & {len(research_res['forums'])} community forum discussions.")

                if location_input.strip():
                    st.write("📍 **Mapping local parts stores & nearest professional repair facilities...**")
                    st.write(f"✅ Discovered {len(research_res.get('pro_shops', []))} outside repair centers & parts suppliers.")

                st.write("🧠 **Synthesizing authoritative DIY repair dossier & outside cost estimates...**")
                agent = RepairAgent(api_key=api_key_input)
                
                dossier = agent.generate_repair_plan(
                    category=selected_category,
                    subtype=selected_subtype,
                    make=make_input.strip(),
                    model=model_input.strip(),
                    problem=problem_input.strip(),
                    location=location_input.strip(),
                    skill_level=skill_level,
                    tools_on_hand=selected_tools,
                    research_data=research_res
                )
                
                # Store in session state
                st.session_state.dossier = dossier
                st.session_state.research_data = research_res
                st.session_state.equipment_info = {
                    "category": selected_category,
                    "subtype": selected_subtype,
                    "make": make_input.strip(),
                    "model": model_input.strip(),
                    "location": location_input.strip(),
                    "problem": problem_input.strip(),
                    "skill_level": skill_level,
                    "tools": selected_tools
                }
                
                # Auto save to local history
                HistoryManager.save_case(
                    st.session_state.equipment_info,
                    dossier,
                    research_res
                )
                
                status.update(label="Diagnostic Dossier Ready!", state="complete", expanded=False)

    # -------------------------------------------------------------
    # DISPLAY DIAGNOSTIC DOSSIER
    # -------------------------------------------------------------
    if st.session_state.dossier:
        d = st.session_state.dossier
        eq = st.session_state.equipment_info
        rd = st.session_state.research_data
        pro_est = d.get("pro_repair_estimate", {})

        st.divider()
        st.subheader(f"📋 {d.get('title', 'DIY Repair Dossier')}")
        st.caption(f"Engine Source: **{d.get('meta_source', 'FixMate AI')}**")

        # Metric Badges Row
        mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
        
        hazard = d.get("safety_hazard_level", "Moderate")
        with mcol1:
            hazard_class = "hazard-badge-high" if hazard in ["High", "Extreme"] else ("hazard-badge-moderate" if hazard == "Moderate" else "hazard-badge-low")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Safety Hazard</div>
                <div class="{hazard_class}">{hazard}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with mcol2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Difficulty</div>
                <div class="metric-value">{d.get('difficulty_rating', 'Intermediate')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with mcol3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Est. DIY Time</div>
                <div class="metric-value">{d.get('estimated_time', '45 min')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with mcol4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">DIY Part Cost</div>
                <div class="metric-value">{d.get('estimated_cost_diy', '$25')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with mcol5:
            pro_total_str = pro_est.get("total_pro_estimate", d.get('estimated_cost_pro', '$250'))
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Outside Pro Cost</div>
                <div class="metric-value" style="color: #991B1B;">{pro_total_str}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # Section: Safety Warnings
        warnings = d.get("safety_warnings", [])
        if warnings:
            st.error("### ⚠️ Critical Safety Precautions Before Touching Anything:")
            for w in warnings:
                st.markdown(f"- 🛑 **{w}**")

        # Section: Probable Root Causes
        st.subheader("🔍 Root Cause Analysis & Diagnostic Tests")
        st.write("Ranked by likelihood according to technical manuals and real repair forum frequency:")
        
        rc_list = d.get("root_cause_analysis", [])
        for i, rc in enumerate(rc_list):
            prob = rc.get("probability", "Medium")
            prob_color = "🔴" if prob == "High" else ("🟡" if prob == "Medium" else "🟢")
            with st.expander(f"{prob_color} **Cause {i+1}: {rc.get('cause', 'Unknown')}** ({prob} Likelihood)", expanded=(i==0)):
                st.markdown(f"**Explanation:** {rc.get('explanation', '')}")
                st.info(f"**🔬 How to Test & Verify:** {rc.get('test_method', '')}")

        # Section: Tools & Parts
        t_col, p_col = st.columns(2)
        with t_col:
            st.subheader("🛠️ Required Tools")
            tools = d.get("required_tools", [])
            for t in tools:
                st.markdown(f"- [ ] `{t}`")

        with p_col:
            st.subheader("🔩 Likely Replacement Parts")
            parts = d.get("likely_parts_needed", [])
            for p in parts:
                st.markdown(f"**{p.get('part_name', 'Part')}**")
                st.markdown(f"- Est. Cost: **{p.get('typical_cost', 'N/A')}**")
                if p.get("part_number_hint"):
                    st.markdown(f"- Search Tag: `{p.get('part_number_hint')}`")
                if p.get("replacement_tip"):
                    st.caption(f"💡 {p.get('replacement_tip')}")

        # Section: Step-by-Step DIY Guide with Interactive Checkboxes
        st.subheader("📋 Step-by-Step DIY Repair Guide")
        st.write("Follow these phases in order. Check off each step as you complete it on your workbench:")
        
        steps = d.get("step_by_step_guide", [])
        for idx, step in enumerate(steps):
            phase = step.get("phase", f"Step {idx+1}")
            instr = step.get("instruction", "")
            pro_tip = step.get("pro_tip", "")
            
            c_check, c_body = st.columns([0.05, 0.95])
            with c_check:
                step_key = f"step_done_{idx}"
                st.checkbox("", key=step_key)
            with c_body:
                st.markdown(f"""
                <div class="step-box">
                    <h4 style="margin: 0 0 6px 0; color: #1E3A8A;">{phase}</h4>
                    <div>{instr}</div>
                    {f'<div class="pro-tip">💡 <b>Pro Insider Tip:</b> {pro_tip}</div>' if pro_tip else ''}
                </div>
                """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # NEW SECTION: OUTSIDE PROFESSIONAL REPAIR ESTIMATE & NEAREST LOCATIONS
        # ---------------------------------------------------------------------
        st.divider()
        st.subheader("🏢 Outside Professional Repair Cost Estimate (Assuming DIY is Too Difficult)")
        st.write(f"If this repair is beyond your available tools or comfort level, here is the itemized cost estimate from an authorized outside service center near **{eq.get('location', 'your location')}**:")

        pcol1, pcol2 = st.columns([1.2, 1])
        with pcol1:
            st.markdown(f"""
            | Cost Component | Scope / Details | Estimated Amount |
            | :--- | :--- | :--- |
            | **Diagnostic / Trip Call Fee** | Initial dispatch & fault verification | **{pro_est.get('diagnostic_call_fee', '$85 - $125')}** |
            | **Labor Charges** | {pro_est.get('labor_hours', '1.5 hrs')} @ {pro_est.get('labor_hourly_rate', '$120 / hr')} | **{pro_est.get('labor_subtotal', '$150 - $260')}** |
            | **OEM Replacement Parts** | Parts with standard 20-30% shop markup | **{pro_est.get('estimated_parts_retail', '$45 - $95')}** |
            | **Shop Supplies & Disposal** | Hazardous recycling & consumables | **{pro_est.get('supplies_and_disposal', '$15 - $25')}** |
            | **TOTAL PROFESSIONAL REPAIR** | **Estimated Total Outside Cost** | 🔴 **{pro_est.get('total_pro_estimate', '$295 - $505')}** |
            | **YOUR DIY SAVINGS** | Cost savings if you repair yourself | 🟢 **{pro_est.get('diy_savings', 'Save ~$250 - $430')}** |
            """)

        with pcol2:
            st.markdown(f"""
            <div style="background-color: #FEF3C7; border: 1px solid #FCD34D; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 6px 0; color: #92400E;">⚠️ When to Escalate to an Outside Pro</h4>
                <p style="margin: 0; font-size: 0.95rem; color: #78350F;">
                    {pro_est.get('when_to_hire_pro', 'If specialized tools, refrigerant evacuation, high voltage capacitors, or deep mechanical disassemblies are required.')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            if rd and rd.get("location_links"):
                ll = rd["location_links"]
                st.link_button("🗺️ Google Maps: Nearest Repair Shops", ll.get("google_maps_pros", "#"), use_container_width=True)
                st.link_button("⭐ Yelp: Top-Rated Local Repair Pros", ll.get("yelp_pros", "#"), use_container_width=True)

        # Nearest Outside Repair Centers List
        if rd and rd.get("pro_shops"):
            st.write("##### 📍 Nearest Outside Repair Locations Discovered Online:")
            for shop in rd["pro_shops"][:4]:
                st.markdown(f"""
                <div class="pro-card">
                    <b><a href="{shop.get('url')}" target="_blank">{shop.get('title')}</a></b> ({shop.get('source')})<br/>
                    <small>{shop.get('snippet')}</small>
                </div>
                """, unsafe_allow_html=True)

        # Section: Local Parts Sourcing & Postal Address Integration
        st.subheader("📍 Local Sourcing & Neighborhood Parts Hub")
        st.markdown(f"**Target Location:** `{eq.get('location', 'User Postal Address')}`")
        
        advice = d.get("local_sourcing_advice", "")
        if advice:
            st.info(f"🧭 **Local Sourcing Guidance:** {advice}")

        # Location Links
        if rd and rd.get("location_links"):
            ll = rd["location_links"]
            lcol1, lcol2, lcol3, lcol4 = st.columns(4)
            with lcol1:
                st.link_button("🗺️ Open Google Maps Nearby", ll.get("google_maps", "#"), use_container_width=True)
            with lcol2:
                st.link_button("⭐ Search Yelp Local Stores", ll.get("yelp", "#"), use_container_width=True)
            with lcol3:
                st.link_button("🏬 Home Depot Store Locator", ll.get("home_depot", "#"), use_container_width=True)
            with lcol4:
                st.link_button("📦 Repair Clinic Fast Shipping", ll.get("repairclinic", "#"), use_container_width=True)

        # Local Store Search Results
        if rd and rd.get("local_parts"):
            st.write("##### Nearby Parts Warehouses & Hardware Stores Discovered Online:")
            for item in rd["local_parts"][:4]:
                st.markdown(f"""
                <div class="local-card">
                    <b><a href="{item.get('url')}" target="_blank">{item.get('title')}</a></b> ({item.get('source')})<br/>
                    <small>{item.get('snippet')}</small>
                </div>
                """, unsafe_allow_html=True)

        # Section: Community Wisdom & Forum Insights
        st.subheader("💬 Community Wisdom & Real Forum Insights")
        wisdom = d.get("community_wisdom", [])
        if wisdom:
            for w in wisdom:
                st.markdown(f"""
                <div class="forum-card">
                    💬 <b>Community Finding:</b> {w}
                </div>
                """, unsafe_allow_html=True)

        # Section: Technical Guides & Videos
        if rd:
            t1, t2 = st.columns(2)
            with t1:
                st.subheader("📖 Technical Repair Guides & Manuals")
                for g in rd.get("guides", [])[:3]:
                    st.markdown(f"""
                    <div class="source-card">
                        <b><a href="{g.get('url')}" target="_blank">{g.get('title')}</a></b><br/>
                        <small>{g.get('snippet')[:140]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
            with t2:
                st.subheader("🎥 Video Walkthroughs")
                for v in rd.get("videos", [])[:3]:
                    st.markdown(f"""
                    <div class="source-card">
                        <b><a href="{v.get('url')}" target="_blank">{v.get('title')}</a></b><br/>
                        <small>{v.get('snippet')[:140]}...</small>
                    </div>
                    """, unsafe_allow_html=True)

        # Download & Export Bar (Full Output in PDF)
        st.divider()
        st.subheader("💾 Export Entire Output to PDF / JSON")
        exp1, exp2 = st.columns(2)
        
        with exp1:
            try:
                pdf_data = generate_repair_pdf(d, eq, rd)
                filename = f"FixMate_Complete_Repair_Dossier_{eq.get('make')}_{eq.get('model')}.pdf".replace(" ", "_")
                st.download_button(
                    label="📄 Download Complete PDF Dossier (Full Output + Pro Costs)",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    help="Generates an exhaustive multi-page PDF including all diagnostic steps, pro cost estimates, nearest repair locations, and forum citations."
                )
            except Exception as e:
                st.error(f"Could not generate PDF: {e}")

        with exp2:
            json_str = json.dumps({"dossier": d, "equipment": eq, "research": rd}, indent=2)
            st.download_button(
                label="📝 Download Complete JSON Technical Report",
                data=json_str,
                file_name=f"complete_repair_report_{eq.get('make')}.json",
                mime="application/json",
                use_container_width=True
            )

# -------------------------------------------------------------
# TAB 2: INTERACTIVE REPAIR ASSISTANT
# -------------------------------------------------------------
with tab_assistant:
    st.subheader("💬 Live Interactive Repair Assistant")
    st.write("Stuck on a screw? Need help testing a component with your multimeter? Or wondering if an outside repair quote is fair? Ask in real time!")

    if not st.session_state.dossier:
        st.info("💡 Generate or load a repair diagnosis in the first tab to begin asking questions about your specific equipment.")
    else:
        eq = st.session_state.equipment_info
        st.success(f"Active Session: **{eq.get('make')} {eq.get('model')}** ({eq.get('subtype')})")

        # Display Chat History
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🛠️"):
                    st.write(msg["content"])

        # Chat Input
        user_q = st.chat_input("Ask a question about this repair or outside cost estimates...")
        if user_q:
            # Append user message
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)

            # Generate reply
            agent = RepairAgent(api_key=api_key_input)
            with st.chat_message("assistant", avatar="🛠️"):
                with st.spinner("Analyzing question against technical repair manual & cost database..."):
                    reply = agent.ask_followup(
                        question=user_q,
                        chat_history=st.session_state.chat_history,
                        dossier=st.session_state.dossier
                    )
                    st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

# -------------------------------------------------------------
# TAB 3: SAVED REPAIR HISTORY
# -------------------------------------------------------------
with tab_history:
    st.subheader("🕒 Saved Repair Sessions")
    history_records = HistoryManager.load_history()

    if not history_records:
        st.info("No saved repair cases yet. Any diagnostics you run will automatically be saved here!")
    else:
        st.write(f"Showing **{len(history_records)}** saved diagnostic cases:")
        for record in history_records:
            cid = record.get("id", "CASE")
            eq = record.get("equipment_info", {})
            d = record.get("dossier", {})
            rd = record.get("research_data", {})
            ts = record.get("timestamp", "Recent")

            with st.expander(f"📦 **{eq.get('make', 'Device')} {eq.get('model', '')}** - {eq.get('subtype', 'Equipment')} ({ts})"):
                c_info, c_action = st.columns([2.5, 1.5])
                with c_info:
                    st.markdown(f"**Problem:** {eq.get('problem', 'No description')}")
                    st.markdown(f"**Location:** `{eq.get('location', 'N/A')}`")
                    st.markdown(f"**Diagnosis:** {d.get('title', 'N/A')}")
                    pro_est_record = d.get("pro_repair_estimate", {})
                    st.markdown(f"**DIY Cost:** `{d.get('estimated_cost_diy', 'N/A')}` | **Outside Pro Cost:** `{pro_est_record.get('total_pro_estimate', d.get('estimated_cost_pro', 'N/A'))}`")
                
                with c_action:
                    if st.button("🔄 Reload into Active View", key=f"reload_{cid}", use_container_width=True):
                        st.session_state.dossier = d
                        st.session_state.equipment_info = eq
                        st.session_state.research_data = rd
                        st.session_state.chat_history = []
                        st.rerun()

                    try:
                        pdf_bytes = generate_repair_pdf(d, eq, rd)
                        st.download_button(
                            "📄 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Repair_{eq.get('make')}_{cid}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{cid}",
                            use_container_width=True
                        )
                    except Exception:
                        pass

                    if st.button("🗑️ Delete", key=f"del_{cid}", use_container_width=True):
                        HistoryManager.delete_case(cid)
                        st.rerun()

# -------------------------------------------------------------
# TAB 4: ABOUT & DIY SAFETY
# -------------------------------------------------------------
with tab_help:
    st.subheader("🛡️ Universal DIY Safety Rules")
    st.markdown("""
    1. **Always Disconnect Energy Sources First:**
       - Unplug electrical cords or switch off double-pole circuit breakers.
       - Shut off water supply isolation valves under sinks or at the water main.
       - Turn off gas shutoff valves before inspecting burners or furnace assemblies.
    2. **Beware of Stored Energy:**
       - **Capacitors** in microwaves, air conditioners, and motor start windings retain lethal voltages (2,000V+) even after unplugging.
       - **Garage door springs and mechanical recoil springs** store extreme tension capable of severe bodily injury.
    3. **Protect Yourself:**
       - Wear ANSI-approved eye protection and work gloves. Sheet metal enclosures inside appliances have razor-sharp stamped edges.
    4. **Know When to Stop & Call Outside Help:**
       - If you smell natural gas, see signs of scorched circuit boards with melted solder traces, or detect refrigerant leaks, stop immediately and contact a certified local technician.
    """)

    st.subheader("🏷️ Where to Find Equipment Model Number Plates")
    st.markdown("""
    - **Washing Machines & Dryers:** Inside the door rim, on the drum opening frame, or on the rear top edge of the control console.
    - **Refrigerators:** On the upper left or right interior wall of the fresh food compartment, or behind the front bottom kickplate.
    - **Dishwashers:** Along the top or side edge of the stainless steel inner door panel.
    - **Lawn Mowers & Small Engines:** Stamped directly into the metal valve cover / engine casing (Honda/Briggs), or on the rear deck decal.
    - **Smartphones & Electronics:** Inside *Settings > General > About*, or printed in micro-text on the bottom chassis.
    """)

    st.subheader("⚖️ Legal Disclaimer")
    st.caption("FixMate is an educational DIY advisory tool. Working on electrical, gas, or pressurized mechanical equipment carries inherent risks of property damage or physical injury. Always exercise extreme caution, follow official manufacturer warnings, and consult certified licensed technicians for hazardous tasks.")

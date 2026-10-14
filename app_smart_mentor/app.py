"""
app.py - Smart Mentor: Strategic Knowledge & Advisory Application.
Built with Streamlit, Google Gemini, Multi-Source Search (News, PubMed, OpenAlex, Wikipedia, Forums),
and ReportLab PDF generation.
"""

import os
import re
from datetime import datetime
from typing import Dict, List

import streamlit as st

from mentor_engine import MentorAdvisoryReport, SmartMentorEngine
from pdf_generator import generate_mentor_pdf
from search_engine import MultiSourceSearchEngine, SearchResultItem

# Set Streamlit page configuration
st.set_page_config(
    page_title="Smart Mentor | Strategic Knowledge & Advisory",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for executive advisory theme
st.markdown(
    """
    <style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hero Header */
    .mentor-hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #1E3A8A 100%);
        border-radius: 16px;
        padding: 32px 36px;
        color: #FFFFFF;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .mentor-hero h1 {
        font-family: 'Newsreader', serif;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        color: #F8FAFC;
    }
    .mentor-hero p {
        font-size: 1.05rem;
        color: #94A3B8;
        margin: 0;
        max-width: 850px;
        line-height: 1.5;
    }
    
    /* Section Cards */
    .advisory-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .section-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .badge-primary { background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; }
    .badge-success { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .badge-warning { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .badge-info { background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD; }
    
    /* Word count chip */
    .word-count-chip {
        float: right;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
    }
    .chip-ok { background: #DCFCE7; color: #15803D; }
    .chip-warn { background: #FEE2E2; color: #B91C1C; }
    
    /* Action Step styling */
    .action-step-item {
        border-left: 3px solid #3B82F6;
        padding-left: 12px;
        margin-bottom: 12px;
    }
    
    /* Citation pills */
    .source-pill {
        display: inline-block;
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin: 2px 4px 2px 0;
        color: #334155;
    }
    
    /* Preset card */
    .preset-btn {
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
        color: #1E293B !important;
        text-align: left !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Preset Dilemma Templates
SAMPLE_PRESETS = [
    {
        "title": "⚖️ Employment Non-Compete Dilemma",
        "category": "Legal & Regulatory",
        "topic": "Enforceability of nationwide non-compete clauses for remote software engineers",
        "context": "Received a promising job offer from a US-based firm, but the agreement has a 2-year nationwide restrictive covenant prohibiting work in any adjacent cloud software domain.",
        "tone": "Prudent & Protective (Shield Against Legal Exposure)",
    },
    {
        "title": "🩺 GLP-1 Weight Loss & Lean Mass Preservation",
        "category": "Health & Medical Science",
        "topic": "Clinical efficacy and risks of GLP-1 receptor agonists (Semaglutide/Tirzepatide) on muscle loss and metabolic rebound",
        "context": "Doctor proposed initiating GLP-1 therapy for elevated HbA1c and weight management. I am worried about sarcopenia (lean muscle loss), lifelong medication dependence, and gastrointestinal risks.",
        "tone": "Analytical & Evidence-First (Clinical Rigor & Safeguards)",
    },
    {
        "title": "🌐 Geopolitical Tariffs & Supply Chain Impact",
        "category": "Current Affairs & Society",
        "topic": "Impact of escalating international trade tariffs on consumer hardware electronics and personal business inventory",
        "context": "I run a small consumer electronics import/distribution business. Proposed tariff hikes could increase import costs by 25%. Need a survival and hedging action plan.",
        "tone": "Strategic & Visionary (Proactive Risk Mitigation)",
    },
    {
        "title": "🤖 AI Disruption in Professional Creative Careers",
        "category": "Technology & Innovation",
        "topic": "Generative AI displacement of technical writing, corporate copywriting, and digital illustration roles",
        "context": "10-year veteran freelance copywriter and content strategist experiencing declining contract renewals as enterprise clients adopt automated LLM workflows.",
        "tone": "Direct & Tactical (Adaptive Career Pivot & High-Value Defense)",
    },
]

# Initialize Session State
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""
if "category_input" not in st.session_state:
    st.session_state.category_input = "Current Affairs & Society"
if "context_input" not in st.session_state:
    st.session_state.context_input = ""
if "tone_input" not in st.session_state:
    st.session_state.tone_input = "Prudent & Protective (Shield Against Vulnerabilities)"
if "sources_input" not in st.session_state:
    st.session_state.sources_input = ["news", "medical", "legal", "wikipedia", "forums"]


# Dialog for Framing Question
@st.dialog("🎯 Frame Your Topic with Smart Mentor", width="large")
def frame_question_dialog():
    st.markdown(
        """
        <p style="color: #64748B; font-size: 0.95rem; margin-top: -10px;">
        Use this guided dialog to structure your topic, personal vulnerabilities, and advisory goals. 
        The Smart Mentor will align real-time search across global news, medical literature, legal archives, and public forums to formulate your advisory report.
        </p>
        """,
        unsafe_allow_html=True,
    )

    d_topic = st.text_input(
        "📌 Topic / Issue / Problem to Investigate *",
        value=st.session_state.topic_input,
        placeholder="e.g. Starting GLP-1 medication, Tenant rights during mold infestation, AI career pivot...",
        key="dlg_topic",
    )

    col1, col2 = st.columns(2)
    with col1:
        categories = [
            "Current Affairs & Society",
            "Health & Medical Science",
            "Legal & Regulatory",
            "Career & Business Strategy",
            "Technology & Innovation",
            "Personal Dilemma & Ethics",
            "Cross-Disciplinary",
        ]
        cat_idx = categories.index(st.session_state.category_input) if st.session_state.category_input in categories else 0
        d_category = st.selectbox("📂 Category / Domain", categories, index=cat_idx, key="dlg_cat")

    with col2:
        tones = [
            "Prudent & Protective (Shield Against Vulnerabilities)",
            "Strategic & Visionary (Long-term Leverage & Upside)",
            "Analytical & Evidence-First (Clinical & Statistical Rigor)",
            "Direct & Tactical (Rapid Actionable Execution)",
            "Empathetic & Holistic (Balanced Human Centric Guidance)",
        ]
        tone_idx = tones.index(st.session_state.tone_input) if st.session_state.tone_input in tones else 0
        d_tone = st.selectbox("🧭 Desired Mentor Stance", tones, index=tone_idx, key="dlg_tone")

    d_context = st.text_area(
        "🛡️ Your Personal Context & Specific Vulnerabilities",
        value=st.session_state.context_input,
        placeholder="Describe your current situation, key concerns, what you are trying to protect or achieve, and any constraints...",
        height=110,
        key="dlg_ctx",
    )

    st.markdown("<b>🔍 Information Repositories to Query:</b>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        q_news = st.checkbox("Current Affairs", value=True, key="dlg_q_news")
    with c2:
        q_med = st.checkbox("Medical (PubMed)", value=True, key="dlg_q_med")
    with c3:
        q_leg = st.checkbox("Legal/Academic", value=True, key="dlg_q_leg")
    with c4:
        q_wiki = st.checkbox("Encyclopedic", value=True, key="dlg_q_wiki")
    with c5:
        q_for = st.checkbox("Social Forums", value=True, key="dlg_q_for")

    if st.button("🚀 Submit to Smart Mentor", type="primary", use_container_width=True):
        if not d_topic.strip():
            st.error("Please enter a topic or issue before proceeding.")
            return

        st.session_state.topic_input = d_topic.strip()
        st.session_state.category_input = d_category
        st.session_state.context_input = d_context.strip()
        st.session_state.tone_input = d_tone

        active_sources = []
        if q_news:
            active_sources.append("news")
        if q_med:
            active_sources.append("medical")
        if q_leg:
            active_sources.append("legal")
        if q_wiki:
            active_sources.append("wikipedia")
        if q_for:
            active_sources.append("forums")
        st.session_state.sources_input = active_sources

        st.session_state.run_analysis_flag = True
        st.rerun()


# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("### 🧭 Smart Mentor System")
    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 14px;">
        An expert advisor powered by multidisciplinary wisdom, synthesizing real-time facts across news, medical repositories, legal frameworks, and community discourse.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # API Key Configuration
    st.markdown("#### 🔑 Model & API Engine")
    env_has_key = bool(os.environ.get("GEMINI_API_KEY"))
    custom_api_key = st.text_input(
        "Google Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Reads GEMINI_API_KEY from environment by default. You can also paste your own key here.",
    )
    if custom_api_key:
        st.success("✅ Gemini Engine Active")
    else:
        st.info("ℹ️ Using Built-in Deterministic Knowledge Synthesis")

    st.markdown("---")
    st.markdown("#### 📚 Active Information Repositories")
    sb_news = st.checkbox("Current Affairs & Global News", value="news" in st.session_state.sources_input)
    sb_med = st.checkbox("Medical Repositories (PubMed / NCBI)", value="medical" in st.session_state.sources_input)
    sb_leg = st.checkbox("Legal & Academic (OpenAlex)", value="legal" in st.session_state.sources_input)
    sb_wiki = st.checkbox("Society & Reference (Wikipedia)", value="wikipedia" in st.session_state.sources_input)
    sb_for = st.checkbox("Social Discussion Forums (Community)", value="forums" in st.session_state.sources_input)

    st.session_state.sources_input = [
        src
        for src, active in [
            ("news", sb_news),
            ("medical", sb_med),
            ("legal", sb_leg),
            ("wikipedia", sb_wiki),
            ("forums", sb_for),
        ]
        if active
    ]

    st.markdown("---")
    st.markdown("#### 📜 Advisory Session History")
    if st.session_state.history:
        for idx, h_report in enumerate(reversed(st.session_state.history)):
            btn_label = f"• {h_report.topic[:28]}..."
            if st.button(btn_label, key=f"hist_{idx}"):
                st.session_state.current_report = h_report
                st.session_state.chat_messages = []
                st.rerun()
    else:
        st.caption("No reports generated yet in this session.")

    st.markdown("---")
    st.caption("Smart Mentor Advisory v2.0 • Streamlit & Gemini")


# ==========================================
# MAIN INTERFACE
# ==========================================

# Hero Header
st.markdown(
    """
    <div class="mentor-hero">
        <h1>🧭 The Smart Mentor</h1>
        <p>
            An authoritative, multi-disciplinary expert providing wisdom and strategic clarity across current affairs,
            clinical medical repositories, legal frameworks, and community discourse. Formulate your question to receive a 
            rigorously verified brief and self-protection action plan.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Preset Templates Expander
with st.expander("💡 Quick-Start Dilemma Templates (Click to Auto-Fill)", expanded=False):
    p_cols = st.columns(len(SAMPLE_PRESETS))
    for i, preset in enumerate(SAMPLE_PRESETS):
        with p_cols[i]:
            st.markdown(f"**{preset['title']}**")
            st.caption(f"Domain: {preset['category']}")
            if st.button("Load Template", key=f"btn_preset_{i}", use_container_width=True):
                st.session_state.topic_input = preset["topic"]
                st.session_state.category_input = preset["category"]
                st.session_state.context_input = preset["context"]
                st.session_state.tone_input = preset["tone"]
                st.success("Template Loaded!")
                st.rerun()

# Prominent Framing Action Area
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown("### 📋 Formulate & Frame Your Dilemma")
with top_col2:
    if st.button("✨ Open Guided Framing Dialog", type="primary", use_container_width=True):
        frame_question_dialog()

# Inline Input Form
with st.container():
    c_topic, c_cat = st.columns([2.5, 1])
    with c_topic:
        main_topic = st.text_input(
            "Topic / Issue / Dilemma",
            value=st.session_state.topic_input,
            placeholder="e.g. New non-compete clause in employment offer, Starting GLP-1 weight loss medications, Housing tenant dispute...",
            key="main_topic_input",
        )
    with c_cat:
        categories = [
            "Current Affairs & Society",
            "Health & Medical Science",
            "Legal & Regulatory",
            "Career & Business Strategy",
            "Technology & Innovation",
            "Personal Dilemma & Ethics",
            "Cross-Disciplinary",
        ]
        curr_cat_idx = categories.index(st.session_state.category_input) if st.session_state.category_input in categories else 0
        main_category = st.selectbox("Category", categories, index=curr_cat_idx, key="main_category_select")

    c_ctx, c_tone = st.columns([2.5, 1])
    with c_ctx:
        main_context = st.text_area(
            "Your Personal Context & Vulnerability (What are you trying to protect or decide?)",
            value=st.session_state.context_input,
            placeholder="Provide relevant background, your primary stakes, specific risks you want to avoid, or key questions...",
            height=85,
            key="main_context_input",
        )
    with c_tone:
        tones = [
            "Prudent & Protective (Shield Against Vulnerabilities)",
            "Strategic & Visionary (Long-term Leverage & Upside)",
            "Analytical & Evidence-First (Clinical & Statistical Rigor)",
            "Direct & Tactical (Rapid Actionable Execution)",
            "Empathetic & Holistic (Balanced Human Centric Guidance)",
        ]
        curr_tone_idx = tones.index(st.session_state.tone_input) if st.session_state.tone_input in tones else 0
        main_tone = st.selectbox("Mentor Guidance Stance", tones, index=curr_tone_idx, key="main_tone_select")

    btn_search_col, _, _ = st.columns([1.5, 1, 1])
    with btn_search_col:
        run_consultation = st.button("🔍 Search Repositories & Consult Smart Mentor", type="primary", use_container_width=True)


# Trigger Consultation Logic
should_run = run_consultation or st.session_state.get("run_analysis_flag", False)

if should_run:
    st.session_state.run_analysis_flag = False
    topic_to_use = main_topic.strip() or st.session_state.topic_input.strip()

    if not topic_to_use:
        st.warning("⚠️ Please provide a topic, problem, or question for the Smart Mentor to investigate.")
    else:
        st.session_state.topic_input = topic_to_use
        st.session_state.category_input = main_category
        st.session_state.context_input = main_context.strip()
        st.session_state.tone_input = main_tone

        # Progress Execution Container
        progress_box = st.status("🧭 Smart Mentor is conducting multi-source investigation...", expanded=True)

        with progress_box:
            searcher = MultiSourceSearchEngine()

            st.write("📡 Scanning real-time Current Affairs & News RSS...")
            st.write("🔬 Querying Clinical Medical Literature in PubMed (NCBI)...")
            st.write("⚖️ Retrieving Legal, Regulatory & Academic Archives (OpenAlex)...")
            st.write("📖 Cross-referencing Encyclopedic Foundations (Wikipedia)...")
            st.write("💬 Synthesizing Public Forum Debates & Community Sentiments...")

            search_results = searcher.aggregate_multi_source_search(
                query=topic_to_use,
                sources_to_query=st.session_state.sources_input,
                category=main_category,
            )

            total_items = sum(len(v) for v in search_results.values())
            st.write(f"✅ Retrieved **{total_items} live references** across selected repositories.")

            formatted_context = searcher.format_search_context(search_results)

            st.write("🧠 Engaging Smart Mentor Synthesis Engine (Enforcing Section Word Limits)...")
            mentor_engine = SmartMentorEngine(api_key=custom_api_key or os.environ.get("GEMINI_API_KEY", ""))

            report = mentor_engine.generate_advisory(
                topic=topic_to_use,
                category=main_category,
                user_context=st.session_state.context_input,
                mentor_tone=main_tone,
                search_results=search_results,
                search_context_text=formatted_context,
            )

            st.session_state.current_report = report
            st.session_state.history.append(report)
            st.session_state.chat_messages = []
            progress_box.update(label="🎯 Advisory Brief Complete!", state="complete", expanded=False)


# ==========================================
# DISPLAY ADVISORY REPORT
# ==========================================
curr_report = st.session_state.current_report

if curr_report:
    st.markdown("---")

    # Action Toolbar: PDF Download + Quick Stats
    col_head_left, col_head_right = st.columns([2.5, 1.5])
    with col_head_left:
        st.markdown(f"## 📋 Advisory Brief: {curr_report.topic}")
        st.caption(f"Domain: {curr_report.category} • Mentor Persona: {curr_report.mentor_tone} • Engine: {curr_report.model_used}")

    with col_head_right:
        # Generate PDF on the fly
        try:
            pdf_data = generate_mentor_pdf(curr_report)
            safe_filename = f"Smart_Mentor_Advisory_{re.sub(r'[^a-zA-Z0-9]+', '_', curr_report.topic[:30])}.pdf"
            st.download_button(
                label="📥 Download Advisory Report (PDF)",
                data=pdf_data,
                file_name=safe_filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF creation notice: {e}")

    # Layout Tabs: Structured Advisory, Verified Citations, and Follow-up Consultation
    tab_advisory, tab_sources, tab_qa = st.tabs([
        "📑 Structured Advisory Brief",
        f"🔍 Consulted Repositories & Citations ({len(curr_report.sources_consulted)})",
        "💬 Ask Smart Mentor (Follow-Up)",
    ])

    with tab_advisory:
        # ---------------------------------------------------------
        # SECTION A: The Question / Input from User
        # ---------------------------------------------------------
        with st.container():
            st.markdown(
                """
                <div class="advisory-card">
                    <span class="section-badge badge-primary">Section A</span>
                    <h3 style="margin-top: 0; color: #1E293B;">The Question / Input from User</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(curr_report.question_input_section)

        # ---------------------------------------------------------
        # SECTION B: Summary of Search Results (< 1000 words)
        # ---------------------------------------------------------
        with st.container():
            wc_b = curr_report.summary_word_count
            chip_class = "chip-ok" if wc_b < 1000 else "chip-warn"
            chip_label = f"{wc_b} words (Limit &lt; 1000) {'✅' if wc_b < 1000 else '⚠️'}"

            st.markdown(
                f"""
                <div class="advisory-card">
                    <span class="word-count-chip {chip_class}">{chip_label}</span>
                    <span class="section-badge badge-info">Section B</span>
                    <h3 style="margin-top: 0; color: #1E293B;">Summary of Results from Search Exercise</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(curr_report.summary_results_section)

        # ---------------------------------------------------------
        # SECTION C: Analysis & Insights (< 500 words)
        # ---------------------------------------------------------
        with st.container():
            wc_c = curr_report.analysis_word_count
            chip_class_c = "chip-ok" if wc_c < 500 else "chip-warn"
            chip_label_c = f"{wc_c} words (Limit &lt; 500) {'✅' if wc_c < 500 else '⚠️'}"

            st.markdown(
                f"""
                <div class="advisory-card">
                    <span class="word-count-chip {chip_class_c}">{chip_label_c}</span>
                    <span class="section-badge badge-warning">Section C</span>
                    <h3 style="margin-top: 0; color: #1E293B;">Analysis & Insights from Searched References</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(curr_report.analysis_insights_section)

        # ---------------------------------------------------------
        # SECTION D: Action Plans / Next Steps
        # ---------------------------------------------------------
        with st.container():
            st.markdown(
                """
                <div class="advisory-card">
                    <span class="section-badge badge-success">Section D</span>
                    <h3 style="margin-top: 0; color: #1E293B;">Action Plans / Next Steps for the User to Provide & Protect Oneself</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(curr_report.action_plans_section)

    with tab_sources:
        st.markdown("### 🌐 Live References & Multi-Source Citations")
        st.caption(
            "Real-time intelligence retrieved across Current Affairs RSS, PubMed Clinical Literature, "
            "OpenAlex Legal/Academic Repositories, Wikipedia, and Social Forum debates."
        )

        if not curr_report.sources_consulted:
            st.info("No external search sources were loaded for this topic.")
        else:
            # Group sources by repository type
            sources_by_type: Dict[str, List[SearchResultItem]] = {}
            for item in curr_report.sources_consulted:
                sources_by_type.setdefault(item.source_type, []).append(item)

            for s_type, items in sources_by_type.items():
                st.markdown(f"#### 📌 {s_type} ({len(items)} records)")
                for idx, src in enumerate(items, 1):
                    with st.container():
                        c_title, c_link = st.columns([3.5, 1])
                        with c_title:
                            st.markdown(f"**{idx}. [{src.title}]({src.url})**")
                            details = []
                            if src.author_or_journal:
                                details.append(src.author_or_journal)
                            if src.published:
                                details.append(src.published)
                            if details:
                                st.caption(" • ".join(details))
                            st.write(src.snippet)
                        with c_link:
                            if src.url:
                                st.link_button("🔗 Open Source", src.url, use_container_width=True)
                        st.markdown("<hr style='margin: 8px 0; border-color: #F1F5F9;'>", unsafe_allow_html=True)

    with tab_qa:
        st.markdown("### 💬 Mentor Consultation Room")
        st.caption("Ask follow-up questions or request personalized tactical adjustments based on this advisory brief.")

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        follow_up = st.chat_input("Ask your Smart Mentor a follow-up question regarding this advisory...")
        if follow_up:
            st.session_state.chat_messages.append({"role": "user", "content": follow_up})
            with st.chat_message("user"):
                st.markdown(follow_up)

            with st.chat_message("assistant"):
                with st.spinner("Mentor is reviewing your context and formulating counsel..."):
                    mentor_engine = SmartMentorEngine(api_key=custom_api_key or os.environ.get("GEMINI_API_KEY", ""))
                    answer = mentor_engine.ask_follow_up(
                        curr_report,
                        st.session_state.chat_messages,
                        follow_up,
                    )
                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})

else:
    # Empty State Guidance
    st.markdown(
        """
        <div style="background: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 12px; padding: 48px; text-align: center; margin-top: 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🧭</div>
            <h3 style="color: #1E293B; margin-bottom: 8px;">Your Smart Mentor is Ready to Advise</h3>
            <p style="color: #64748B; max-width: 600px; margin: 0 auto 20px auto;">
                Select one of the quick templates above, open the <b>Guided Framing Dialog</b>, 
                or enter your topic directly into the input fields to begin a comprehensive multi-source advisory search.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

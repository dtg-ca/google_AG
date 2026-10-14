"""
app.py
Bestseller Story Studio - Streamlit Web Application
Commercial fiction and screenplay generation engine powered by 6-month market trends,
Google Gemini API, universal multi-format exports, and Dual-View reading room.
"""

import os
import re
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

from trend_engine import get_bestseller_trends, CURATED_GENRE_TRENDS
from generator import generate_story_content
from exporters import (
    export_to_docx, 
    export_to_pdf, 
    export_to_markdown, 
    export_to_fountain, 
    get_text_metrics
)
from storage import (
    save_project, 
    list_projects, 
    load_project, 
    delete_project,
    save_novel_project,
    list_novel_projects,
    load_novel_project
)
from novel_builder import (
    initialize_book_structure,
    generate_chapter_prose,
    generate_all_chapters_sequential,
    compile_full_manuscript,
    extract_chapter1_from_blueprint,
    extract_outline_from_blueprint,
    parse_outline_into_beats,
    sync_outline_into_project,
    DEFAULT_CHAPTER_BEATS
)


# Page Configuration
st.set_page_config(
    page_title="Bestseller Story Studio | AGY Author Suite",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Author Studio Styling
st.markdown("""
<style>
    /* Dark Luxury Studio Theme */
    .stApp {
        background-color: #0B0F17;
        color: #F1F5F9;
    }
    
    .studio-header {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #F59E0B 0%, #EC4899 50%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .studio-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    .trend-pill {
        display: inline-block;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #FBBF24;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .metric-card {
        background: #131B2E;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #38BDF8;
    }
    .metric-lbl {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Screenplay Courier Reader */
    .screenplay-container {
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        line-height: 1.6;
        background-color: #0F172A;
        color: #E2E8F0;
        padding: 36px 48px;
        border: 1px solid #334155;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        white-space: pre-wrap;
        max-height: 700px;
        overflow-y: auto;
    }

    /* Prose Book Typography Reader */
    .book-container {
        font-family: 'Georgia', 'Merriweather', serif;
        font-size: 17px;
        line-height: 1.8;
        background-color: #111827;
        color: #F3F4F6;
        padding: 40px 52px;
        border: 1px solid #1F2937;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        white-space: pre-wrap;
        max-height: 700px;
        overflow-y: auto;
    }

    .market-box {
        background: #131D31;
        border-left: 4px solid #F59E0B;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }

    .act-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .act-1 { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4); }
    .act-2a { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .act-2b { background: rgba(236, 72, 153, 0.2); color: #F472B6; border: 1px solid rgba(236, 72, 153, 0.4); }
    .act-3 { background: rgba(139, 92, 246, 0.2); color: #A78BFA; border: 1px solid rgba(139, 92, 246, 0.4); }

    /* =========================================================
       Dialog Boxes, Modals & Text Input Field Legibility
       Ensures text going into input/dialog boxes is clearly dark
       and readable (#0F172A) on high-contrast backgrounds.
       ========================================================= */

    /* 1. Main Page Input & Text Area Boxes */
    .stTextInput input,
    .stTextArea textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="base-input"] textarea {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    /* Container wraps for input fields */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    /* Placeholder text visibility */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }

    /* Selectbox / Dropdowns */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] * {
        color: #0F172A !important;
    }
    div[data-baseweb="popover"] ul li,
    div[data-baseweb="menu"] ul li,
    ul[role="listbox"] li {
        color: #0F172A !important;
    }

    /* Widget Labels on Dark Background */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }

    /* 2. Streamlit Modal Dialogs & Dialog Boxes */
    div[data-testid="stDialog"],
    div[role="dialog"],
    div[aria-modal="true"],
    .stModal {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 12px !important;
    }

    /* All text inside Dialog Boxes */
    div[data-testid="stDialog"] p,
    div[data-testid="stDialog"] span,
    div[data-testid="stDialog"] div,
    div[data-testid="stDialog"] h1,
    div[data-testid="stDialog"] h2,
    div[data-testid="stDialog"] h3,
    div[data-testid="stDialog"] h4,
    div[data-testid="stDialog"] h5,
    div[data-testid="stDialog"] h6,
    div[data-testid="stDialog"] label,
    div[data-testid="stDialog"] li,
    div[role="dialog"] p,
    div[role="dialog"] span,
    div[role="dialog"] div,
    div[role="dialog"] h1,
    div[role="dialog"] h2,
    div[role="dialog"] h3,
    div[role="dialog"] label,
    div[role="dialog"] li {
        color: #0F172A !important;
    }

    /* Text typed into input boxes inside Dialogs */
    div[data-testid="stDialog"] input,
    div[data-testid="stDialog"] textarea,
    div[role="dialog"] input,
    div[role="dialog"] textarea {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
    }

    div[data-testid="stDialog"] input::placeholder,
    div[data-testid="stDialog"] textarea::placeholder,
    div[role="dialog"] input::placeholder,
    div[role="dialog"] textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "storyline" not in st.session_state:
    st.session_state.storyline = ""
if "current_content" not in st.session_state:
    st.session_state.current_content = ""
if "current_title" not in st.session_state:
    st.session_state.current_title = ""
if "current_ingredients" not in st.session_state:
    st.session_state.current_ingredients = {}
if "last_output_type" not in st.session_state:
    st.session_state.last_output_type = "Novel (Blueprint + Chapter 1)"
if "model_used_label" not in st.session_state:
    st.session_state.model_used_label = ""
if "book_project" not in st.session_state:
    st.session_state.book_project = None
if "selected_ch_num" not in st.session_state:
    st.session_state.selected_ch_num = 1
if "current_outline" not in st.session_state:
    st.session_state.current_outline = ""


# Sidebar: Controls & Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/open-book.png", width=64)
    st.markdown("### **Bestseller Story Studio**")
    st.caption("Commercial Fiction & Screenplay Intelligence")
    st.markdown("---")
    
    # 1. API Configuration
    st.markdown("#### **1. AI Engine Config**")
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_api_key,
        type="password",
        help="Reads automatically from .env (GEMINI_API_KEY) or enter manually."
    )
    active_api_key = api_key_input.strip() if api_key_input else env_api_key
    
    if active_api_key:
        st.success("API Key Active (Ready)", icon="🔑")
    else:
        st.info("No API Key: Studio Offline Engine active", icon="💡")
        
    model_choice = st.selectbox(
        "Gemini Model Architecture",
        options=[
            "gemini-3.8-flash",
            "gemini-flash-latest",
            "gemini-3.5-flash-lite",
            "gemini-3-flash-preview"
        ],
        index=0,
        help="gemini-3.8-flash delivers high-speed commercial fiction generation."
    )
    
    st.markdown("---")
    
    # 2. Creative Fine-Tuning Sliders
    st.markdown("#### **2. Creative Sliders**")
    audience_dial = st.selectbox(
        "Target Readership",
        options=[
            "Adult Commercial Fiction",
            "New Adult (NA) / Crossover",
            "Young Adult (YA)",
            "Literary Commercial",
            "Psychological Suspense"
        ],
        index=0
    )
    
    pov_dial = st.selectbox(
        "Narrative Perspective (POV)",
        options=[
            "Third Person Limited",
            "First Person ('I')",
            "Multi-POV (Dual Timelines/Leads)",
            "Third Person Omniscient"
        ],
        index=0
    )
    
    pacing_dial = st.select_slider(
        "Pacing & Narrative Tension",
        options=[
            "Slow Burn / Atmospheric",
            "Commercial Page-Turner",
            "High-Octane / Relentless"
        ],
        value="Commercial Page-Turner"
    )
    
    st.markdown("---")
    saved_list = list_projects()
    st.caption(f"📁 **Saved Projects in Archive:** {len(saved_list)}")

# Main Layout Header
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div class="studio-header">Bestseller Story Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="studio-subtitle">Transform storylines into market-topping <b>Novels</b>, <b>Movie Scripts</b>, and <b>Short Stories</b> infused with live 6-month commercial fiction trends.</div>',
        unsafe_allow_html=True
    )
with col_status:
    st.markdown(
        f"""
        <div style="background:#131B2E; padding:10px 14px; border-radius:8px; border:1px solid #1E293B; margin-top:5px;">
            <div style="font-size:0.75rem; color:#94A3B8;">ACTIVE AI MODEL</div>
            <div style="font-size:0.95rem; font-weight:700; color:#38BDF8;">{model_choice}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Primary Navigation Tabs
tab_workshop, tab_builder, tab_reader, tab_archive, tab_market_guide = st.tabs([
    "🖋️ Studio Workshop", 
    "📚 Chapter-by-Chapter Novel Engine",
    "📖 Dual-View Reader & Exporters", 
    "🗄️ Saved Projects Archive", 
    "📈 Market Trend Intelligence"
])


# ==========================================
# TAB 1: STUDIO WORKSHOP
# ==========================================
with tab_workshop:
    col_input, col_config = st.columns([5, 3])
    
    with col_input:
        st.markdown("#### **Step 1: Your Storyline & Concept Premise**")
        storyline_input = st.text_area(
            "Enter Storyline / Core Premise",
            value=st.session_state.storyline,
            placeholder="e.g. A disgraced cyber-security investigator takes a high-paying job auditing an isolated Alpine wellness retreat, only to discover the guests are being psychologically engineered to confess crimes they never committed...",
            height=140,
            help="Describe the main character, inciting incident, core conflict, or high-concept what-if hook."
        )
        st.session_state.storyline = storyline_input
        
        # Quick Presets
        st.caption("Quick Inspiration Starters:")
        p_col1, p_col2, p_col3 = st.columns(3)
        if p_col1.button("🔍 Psychological Thriller"):
            st.session_state.storyline = "A nanny in an elite Manhattan penthouse uncovers a hidden surveillance network running into every apartment on the block, and the footage shows her own family thirty years ago."
            st.rerun()
        if p_col2.button("💘 Enemies-to-Lovers"):
            st.session_state.storyline = "Two cutthroat rival literary agents are forced to share a remote Maine lakehouse for 2 weeks when their star celebrity author demands they co-edit her secret tell-all manuscript."
            st.rerun()
        if p_col3.button("⚡ High-Stakes Sci-Fi"):
            st.session_state.storyline = "A salvage pilot extracts a pristine cryogenic escape pod from a dead star cruiser, only to realize the occupant is an identical clone of herself wearing a uniform from forty years in the future."
            st.rerun()

    with col_config:
        st.markdown("#### **Step 2: Genre & Output Architecture**")
        genre_choice = st.selectbox(
            "Theme / Category of Fiction",
            options=[
                "Thriller",
                "Romance",
                "Drama",
                "Sci-Fi / Fantasy",
                "Mystery / Crime",
                "Horror / Supernatural",
                "Historical Fiction",
                "Literary Commercial"
            ],
            index=0
        )
        
        output_type_choice = st.selectbox(
            "Target Output Type",
            options=[
                "Novel (Blueprint + Chapter 1)",
                "Movie Script - Short Film",
                "Movie Script - Feature Treatment + Act I",
                "Short Story (Complete)"
            ],
            index=0
        )
        st.session_state.last_output_type = output_type_choice

        st.markdown("#### **Step 3: Workflow Mode**")
        workflow_mode = st.radio(
            "Select Workflow Engine",
            options=["⚡ Fast Track (1-Click)", "🧪 Market Lab (Inspect & Tweak)"],
            horizontal=True
        )

    st.markdown("---")

    # Workflow Execution Paths
    if workflow_mode == "⚡ Fast Track (1-Click)":
        if st.button("🚀 Synthesize Trends & Generate Masterwork", type="primary", use_container_width=True):
            if not storyline_input.strip():
                st.warning("Please enter a storyline or pick one of the quick inspiration starters above.")
            else:
                with st.spinner("🔍 Scanning 6-month bestseller trends (APIs + BookTok / Goodreads reviews)..."):
                    trends = get_bestseller_trends(genre_choice, storyline_input)
                    st.session_state.current_ingredients = trends
                
                with st.spinner(f"✍️ Drafting {output_type_choice} via {model_choice}..."):
                    result = generate_story_content(
                        storyline=storyline_input,
                        genre=genre_choice,
                        output_type=output_type_choice,
                        ingredients=trends,
                        audience=audience_dial,
                        pov=pov_dial,
                        pacing=pacing_dial,
                        api_key=active_api_key,
                        model_name=model_choice
                    )
                    st.session_state.current_content = result["content"]
                    st.session_state.model_used_label = result["model_used"]
                    # Extract title
                    first_line = result["content"].split("\n")[0].replace("#", "").strip()
                    st.session_state.current_title = first_line if first_line else f"{genre_choice} Masterwork"
                    
                    if "Novel" in output_type_choice:
                        ch1_text = extract_chapter1_from_blueprint(result["content"])
                        outline_text = extract_outline_from_blueprint(result["content"])
                        st.session_state.current_outline = outline_text
                        st.session_state.book_project = initialize_book_structure(
                            title=st.session_state.current_title,
                            storyline=storyline_input,
                            genre=genre_choice,
                            ingredients=trends,
                            chapter_count=15,
                            custom_ch1_content=ch1_text,
                            outline_text=outline_text
                        )
                st.success("✨ Novel blueprint, outline & Chapter 1 generated! Ready to auto-draft all chapters in Tab 2.")
                st.balloons()

    else: # Market Lab (Inspect & Tweak)
        st.markdown("### 🧪 **Market Lab: Trend Intelligence & Ingredient Customizer**")
        st.write("Scan real-time 6-month commercial fiction signals to review and customize the secret sauce before drafting.")
        
        if st.button("🔎 Scan 6-Month Bestseller Radar", type="secondary"):
            with st.spinner("Analyzing recent comps, tropes, and reader sentiment..."):
                trends = get_bestseller_trends(genre_choice, storyline_input)
                st.session_state.current_ingredients = trends
                st.success("Trend Radar synthesized!")

        if st.session_state.current_ingredients:
            t = st.session_state.current_ingredients
            st.markdown(f"**Identified Genre Benchmark:** `{t.get('matched_benchmark')}` | **Live Market Signals:** `{t.get('live_signals_count', 0)}`")
            
            lab_col1, lab_col2 = st.columns(2)
            with lab_col1:
                st.markdown("##### 📚 **Recent 6-Month Market Comps**")
                for comp in t.get("recent_comps", []):
                    st.markdown(f"- 📖 *{comp}*")
                
                st.markdown("##### ⚡ **Top Commercial Tropes**")
                for trope in t.get("top_tropes", []):
                    st.markdown(f'<span class="trend-pill">✦ {trope}</span>', unsafe_allow_html=True)

            with lab_col2:
                st.markdown("##### 👥 **Character Dynamics & Tension**")
                for dyn in t.get("character_dynamics", []):
                    st.markdown(f"- 🎭 {dyn}")
                    
                st.markdown("##### 🎯 **Pacing & Cliffhanger Mechanics**")
                st.markdown(f"- **Pacing Arc:** {t.get('emotional_beats_pacing', [''])[0]}")
                st.markdown(f"- **Cliffhanger Style:** {t.get('cliffhanger_styles')}")
                st.markdown(f"- **Viral Hook:** {t.get('viral_hooks')}")

            st.markdown("---")
            if st.button(f"🎬 Generate {output_type_choice} with Custom Lab Ingredients", type="primary", use_container_width=True):
                with st.spinner(f"Drafting tailored {output_type_choice}..."):
                    result = generate_story_content(
                        storyline=storyline_input,
                        genre=genre_choice,
                        output_type=output_type_choice,
                        ingredients=t,
                        audience=audience_dial,
                        pov=pov_dial,
                        pacing=pacing_dial,
                        api_key=active_api_key,
                        model_name=model_choice
                    )
                    st.session_state.current_content = result["content"]
                    st.session_state.model_used_label = result["model_used"]
                    first_line = result["content"].split("\n")[0].replace("#", "").strip()
                    st.session_state.current_title = first_line if first_line else f"{genre_choice} Masterwork"
                    
                    if "Novel" in output_type_choice:
                        ch1_text = extract_chapter1_from_blueprint(result["content"])
                        outline_text = extract_outline_from_blueprint(result["content"])
                        st.session_state.current_outline = outline_text
                        st.session_state.book_project = initialize_book_structure(
                            title=st.session_state.current_title,
                            storyline=storyline_input,
                            genre=genre_choice,
                            ingredients=t,
                            chapter_count=15,
                            custom_ch1_content=ch1_text,
                            outline_text=outline_text
                        )
                    st.success("✨ Novel blueprint, outline & Chapter 1 drafted! Ready to auto-draft all chapters in Tab 2.")

# ==========================================
# TAB 2: CHAPTER-BY-CHAPTER NOVEL ENGINE
# ==========================================
with tab_builder:
    st.markdown("### 📚 **Hierarchical Sliding-Window Novel Builder**")
    st.markdown(
        "Draft full-length commercial novels (15–25+ chapters) with unbroken continuity and low API costs "
        "using a **3-Tier Hierarchical Sliding Window** (Story Bible + Micro-Beats + Rolling Continuity Anchor)."
    )

    # 1. Project Initialization & Sync Panel
    with st.expander("⚙️ **Novel Project Configuration & Sync**", expanded=(st.session_state.book_project is None)):
        cfg_col1, cfg_col2, cfg_col3 = st.columns([2, 1, 1])
        with cfg_col1:
            builder_title = st.text_input(
                "Book Title",
                value=st.session_state.current_title if st.session_state.current_title else "The Shadows of the Citadel"
            )
        with cfg_col2:
            builder_genre = st.selectbox(
                "Genre Category",
                options=[
                    "Thriller", "Romance", "Drama", "Sci-Fi / Fantasy",
                    "Mystery / Crime", "Horror / Supernatural", "Historical Fiction", "Literary Commercial"
                ],
                index=0,
                key="builder_genre_select"
            )
        with cfg_col3:
            builder_ch_count = st.number_input(
                "Target Chapters",
                min_value=5,
                max_value=30,
                value=15,
                step=1,
                help="Standard commercial novels feature 15 to 25 chapters (~35,000 to 65,000 words)."
            )

        builder_storyline = st.text_area(
            "Core Premise / Master Storyline",
            value=st.session_state.storyline if st.session_state.storyline else "A disgraced investigator takes a high-paying job auditing an isolated Alpine retreat, uncovering a clandestine psychological conditioning program.",
            height=90
        )

        initial_outline_val = ""
        if st.session_state.book_project and st.session_state.book_project.get("outline"):
            initial_outline_val = st.session_state.book_project["outline"]
        elif st.session_state.current_outline:
            initial_outline_val = st.session_state.current_outline
        elif st.session_state.current_content:
            initial_outline_val = extract_outline_from_blueprint(st.session_state.current_content)

        builder_outline = st.text_area(
            "📋 Master Outline / Beat Sheet (Used to generate and map all chapters)",
            value=initial_outline_val,
            height=130,
            help="Paste or edit your chapter outline here (e.g. Chapter 1: Title - Beat description). The engine maps each chapter to these exact beats."
        )

        b_btn_col1, b_btn_col2 = st.columns([1, 1])
        with b_btn_col1:
            if st.button("✨ Initialize / Sync Novel Project", type="primary", use_container_width=True):
                custom_ch1 = extract_chapter1_from_blueprint(st.session_state.current_content)
                outline_to_use = builder_outline.strip() or extract_outline_from_blueprint(st.session_state.current_content)
                st.session_state.current_outline = outline_to_use

                st.session_state.book_project = initialize_book_structure(
                    title=builder_title,
                    storyline=builder_storyline,
                    genre=builder_genre,
                    ingredients=st.session_state.current_ingredients,
                    chapter_count=int(builder_ch_count),
                    custom_ch1_content=custom_ch1,
                    outline_text=outline_to_use
                )
                st.session_state.selected_ch_num = 1
                st.success(f"Initialized '{builder_title}' with {len(st.session_state.book_project['chapters'])} chapters mapped from outline!")
                st.rerun()

            if st.session_state.book_project and builder_outline.strip():
                if st.button("🔄 Re-Parse Outline into Chapter Beats", use_container_width=True, help="Re-maps chapter beats from the edited outline above"):
                    sync_outline_into_project(st.session_state.book_project, builder_outline.strip(), int(builder_ch_count))
                    st.success("Chapters successfully re-mapped from outline!")
                    st.rerun()

        with b_btn_col2:
            saved_novels = list_novel_projects()
            if saved_novels:
                novel_options = {f"{n['title']} ({n['drafted_count']}/{n['total_chapters']} ch - {n['total_words']:,} words)": n['id'] for n in saved_novels}
                selected_novel_name = st.selectbox("Load Saved Novel Project", options=list(novel_options.keys()), key="load_novel_select")
                if st.button("📂 Load Selected Novel", use_container_width=True):
                    loaded_bp = load_novel_project(novel_options[selected_novel_name])
                    if loaded_bp:
                        st.session_state.book_project = loaded_bp
                        st.session_state.selected_ch_num = 1
                        st.success(f"Loaded '{loaded_bp.get('title')}'!")
                        st.rerun()
            else:
                st.caption("No previously saved multi-chapter novels found.")

    if not st.session_state.book_project:
        st.info("👆 Configure your book above and click **'Initialize / Sync Novel Project'** to generate chapter-by-chapter!", icon="💡")
    else:
        bp = st.session_state.book_project
        chapters = bp.get("chapters", [])
        total_ch = len(chapters)
        drafted_chapters = [c for c in chapters if c.get("status") == "Drafted"]
        drafted_count = len(drafted_chapters)
        total_words = sum(c.get("word_count", 0) for c in drafted_chapters)
        pct_done = drafted_count / max(1, total_ch)

        # Progress & High-Level Metrics
        st.markdown(f"#### **Project:** {bp.get('title')} (`{bp.get('genre')}`)")
        st.progress(pct_done)
        
        stat1, stat2, stat3, stat4, stat5 = st.columns(5)
        stat1.markdown(f'<div class="metric-card"><div class="metric-val">{drafted_count}/{total_ch}</div><div class="metric-lbl">Drafted Chapters</div></div>', unsafe_allow_html=True)
        stat2.markdown(f'<div class="metric-card"><div class="metric-val">{total_words:,}</div><div class="metric-lbl">Total Words</div></div>', unsafe_allow_html=True)
        stat3.markdown(f'<div class="metric-card"><div class="metric-val">{round(total_words / 225)} min</div><div class="metric-lbl">Est. Reading Time</div></div>', unsafe_allow_html=True)
        stat4.markdown(f'<div class="metric-card"><div class="metric-val">{round(total_words / max(1, drafted_count)):,}</div><div class="metric-lbl">Avg Words / Ch</div></div>', unsafe_allow_html=True)
        
        est_cost = drafted_count * 0.04
        cost_label = f"${est_cost:.2f}" if active_api_key else "$0.00 (Demo)"
        stat5.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#10B981;">{cost_label}</div><div class="metric-lbl">Est. API Cost</div></div>', unsafe_allow_html=True)

        chars = bp.get("characters") or {}
        p_name = chars.get("protagonist", {}).get("name", "Lead Protagonist")
        p_role = chars.get("protagonist", {}).get("role", "")
        a_name = chars.get("antagonist", {}).get("name", "Adversary")
        a_role = chars.get("antagonist", {}).get("role", "")
        s_name = chars.get("supporting", {}).get("name", "Key Ally")
        s_role = chars.get("supporting", {}).get("role", "")
        if p_name:
            st.markdown(
                f"""
                <div style="background:rgba(56, 189, 248, 0.08); border:1px solid rgba(56, 189, 248, 0.25); border-radius:8px; padding:10px 16px; margin-bottom:16px; font-size:0.85rem; color:#CBD5E1;">
                    <span style="color:#38BDF8; font-weight:700;">🎭 Core Cast Continuity:</span>
                    <span style="margin-left:10px;"><b>Protagonist:</b> {p_name} <i>({p_role})</i></span>
                    <span style="margin-left:15px;"><b>Adversary:</b> {a_name} <i>({a_role})</i></span>
                    <span style="margin-left:15px;"><b>Ally:</b> {s_name} <i>({s_role})</i></span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Batch Auto-Drafting Suite
        st.markdown("#### ⚡ **Batch Chapter Drafting from Outline**")
        batch_col1, batch_col2 = st.columns([2, 1])
        with batch_col1:
            auto_btn_label = f"🚀 Auto-Draft All Remaining Chapters from Outline (Gemini Sliding Window)" if active_api_key else f"🚀 Auto-Draft All Remaining Chapters from Outline (Offline Dynamic Engine)"
            if st.button(auto_btn_label, type="primary", use_container_width=True):
                # Ensure the current outline text area is synchronized before drafting
                if builder_outline.strip() and builder_outline.strip() != bp.get("outline", "").strip():
                    sync_outline_into_project(bp, builder_outline.strip(), len(chapters) or int(builder_ch_count))
                    chapters = bp.get("chapters", [])
                    total_ch = len(chapters)
                pending_chapters = [c for c in chapters if c.get("status") != "Drafted" or not c.get("content", "").strip()]
                if not pending_chapters:
                    st.info("All chapters are already drafted! You can re-generate individual chapters below.")
                else:
                    progress_bar = st.progress(0.0)
                    status_placeholder = st.empty()
                    for idx, c in enumerate(pending_chapters, start=1):
                        status_placeholder.markdown(f"⏳ **Drafting Chapter {c['number']}/{total_ch}: {c['title']} ({c['act']})...**")
                        gen_res = generate_chapter_prose(
                            book_project=bp,
                            chapter_number=c['number'],
                            audience=audience_dial,
                            pov=pov_dial,
                            pacing=pacing_dial,
                            api_key=active_api_key,
                            model_name=model_choice
                        )
                        c["content"] = gen_res["content"]
                        c["summary"] = gen_res["summary"]
                        c["status"] = "Drafted"
                        c["word_count"] = len(gen_res["content"].split())
                        progress_bar.progress(idx / len(pending_chapters))

                    status_placeholder.empty()
                    progress_bar.empty()
                    new_total_words = sum(c.get("word_count", 0) for c in chapters)
                    st.success(f"🎉 Successfully drafted all {total_ch} chapters from the outline! Total: {new_total_words:,} words.")
                    st.balloons()
                    st.rerun()

        with batch_col2:
            if st.button("⏩ Draft Next 3 Pending Chapters", use_container_width=True):
                # Ensure current outline text area is synchronized before drafting
                if builder_outline.strip() and builder_outline.strip() != bp.get("outline", "").strip():
                    sync_outline_into_project(bp, builder_outline.strip(), len(chapters) or int(builder_ch_count))
                    chapters = bp.get("chapters", [])
                    total_ch = len(chapters)
                pending_chapters = [c for c in chapters if c.get("status") != "Drafted" or not c.get("content", "").strip()]
                if not pending_chapters:
                    st.info("All chapters are already drafted!")
                else:
                    batch_target = pending_chapters[:3]
                    progress_bar = st.progress(0.0)
                    status_placeholder = st.empty()
                    for idx, c in enumerate(batch_target, start=1):
                        status_placeholder.markdown(f"⏳ **Drafting Chapter {c['number']}/{total_ch}: {c['title']}...**")
                        gen_res = generate_chapter_prose(
                            book_project=bp,
                            chapter_number=c['number'],
                            audience=audience_dial,
                            pov=pov_dial,
                            pacing=pacing_dial,
                            api_key=active_api_key,
                            model_name=model_choice
                        )
                        c["content"] = gen_res["content"]
                        c["summary"] = gen_res["summary"]
                        c["status"] = "Drafted"
                        c["word_count"] = len(gen_res["content"].split())
                        progress_bar.progress(idx / len(batch_target))
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.success(f"Drafted next {len(batch_target)} chapters from the outline!")
                    st.rerun()

        st.markdown("<hr style='border: 1px solid #1E293B; margin: 20px 0;'>", unsafe_allow_html=True)

        # Chapter Navigation and Selector
        ch_titles = [f"Ch {c['number']}: {c['title']} [{c['act']}] - {c['status']} ({c.get('word_count', 0):,} words)" for c in chapters]
        current_idx = max(0, min(st.session_state.selected_ch_num - 1, total_ch - 1))
        
        col_ch_sel, col_quick_next = st.columns([3, 1])
        with col_ch_sel:
            chosen_ch_idx = st.selectbox(
                "Select Chapter to Edit / Generate:",
                options=range(total_ch),
                index=current_idx,
                format_func=lambda i: ch_titles[i],
                key="ch_picker_dropdown"
            )
            st.session_state.selected_ch_num = chosen_ch_idx + 1
        
        current_ch = chapters[chosen_ch_idx]

        with col_quick_next:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            next_pending = next((c for c in chapters if c["status"] == "Pending"), None)
            if next_pending:
                if st.button(f"⏩ Jump to Next Pending (Ch {next_pending['number']})", use_container_width=True):
                    st.session_state.selected_ch_num = next_pending["number"]
                    st.rerun()

        # Act badge styling
        act_class = "act-1"
        if "II-A" in current_ch.get("act", ""):
            act_class = "act-2a"
        elif "II-B" in current_ch.get("act", ""):
            act_class = "act-2b"
        elif "III" in current_ch.get("act", ""):
            act_class = "act-3"

        # Beat Assignment & Continuity Display
        col_beat, col_buffer = st.columns([1, 1])
        with col_beat:
            mb_items = "".join([f"<li>{mb}</li>" for mb in current_ch.get('micro_beats', [])])
            st.markdown(
                f"""
                <div style="background:#131B2E; padding:16px 20px; border-radius:8px; border:1px solid #1E293B; height:100%;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="act-tag {act_class}">{current_ch['act']}</span>
                        <span style="font-size:0.85rem; color:#94A3B8; font-weight:600;">Status: <b>{current_ch['status']}</b></span>
                    </div>
                    <div style="font-size:1.15rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;">Chapter {current_ch['number']}: {current_ch['title']}</div>
                    <div style="font-size:0.9rem; color:#CBD5E1; margin-bottom:12px;"><b>Core Beat:</b> {current_ch['beat_description']}</div>
                    <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.5px; font-weight:700;">Scene Micro-Treatment:</div>
                    <ul style="font-size:0.85rem; color:#94A3B8; margin-top:4px; padding-left:18px;">
                        {mb_items}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_buffer:
            prev_ch = next((c for c in chapters if c["number"] == current_ch["number"] - 1), None)
            prev_sum_display = prev_ch.get("summary", "") if prev_ch else "[Beginning of novel — establishing baseline world]"
            prev_words = prev_ch.get("content", "").split() if prev_ch else []
            prev_ending_snippet = " ".join(prev_words[-60:]) if len(prev_words) >= 30 else "[No previous chapter prose yet]"

            st.markdown(
                f"""
                <div style="background:#131B2E; padding:16px 20px; border-radius:8px; border:1px solid #1E293B; height:100%;">
                    <div style="font-size:0.75rem; color:#38BDF8; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">
                        🔗 Sliding-Window Memory Buffer
                    </div>
                    <div style="font-size:0.85rem; color:#E2E8F0; margin-bottom:8px;">
                        <b>Chapter {current_ch['number'] - 1 if prev_ch else 0} Summary:</b><br>
                        <span style="color:#94A3B8; font-style:italic;">"{prev_sum_display}"</span>
                    </div>
                    <div style="font-size:0.85rem; color:#E2E8F0;">
                        <b>Continuity Anchor (Previous Ending Scene):</b><br>
                        <span style="color:#64748B; font-size:0.8rem; font-family:serif;">"...{prev_ending_snippet}"</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
        with btn_col1:
            generate_btn_label = f"⚡ Generate Chapter {current_ch['number']} with Gemini (Sliding Window)" if active_api_key else f"⚡ Generate Chapter {current_ch['number']} (Offline Dynamic Engine)"
            if st.button(generate_btn_label, type="primary", use_container_width=True):
                if builder_outline.strip() and builder_outline.strip() != bp.get("outline", "").strip():
                    sync_outline_into_project(bp, builder_outline.strip(), len(chapters) or int(builder_ch_count))
                    current_ch = next((c for c in bp.get("chapters", []) if c["number"] == st.session_state.selected_ch_num), current_ch)
                with st.spinner(f"Drafting Chapter {current_ch['number']}: {current_ch['title']} with sliding continuity..."):
                    gen_res = generate_chapter_prose(
                        book_project=bp,
                        chapter_number=current_ch['number'],
                        audience=audience_dial,
                        pov=pov_dial,
                        pacing=pacing_dial,
                        api_key=active_api_key,
                        model_name=model_choice
                    )
                    current_ch["content"] = gen_res["content"]
                    current_ch["summary"] = gen_res["summary"]
                    current_ch["status"] = "Drafted"
                    current_ch["word_count"] = len(gen_res["content"].split())
                    st.success(f"✨ Chapter {current_ch['number']} drafted ({current_ch['word_count']:,} words)!")
                    st.rerun()

        with btn_col2:
            if st.button(f"💾 Save Chapter {current_ch['number']} Edits", use_container_width=True):
                current_ch["word_count"] = len(current_ch.get("content", "").split())
                if current_ch["content"].strip():
                    current_ch["status"] = "Drafted"
                st.success("Chapter changes saved in session!")

        with btn_col3:
            if st.button("💾 Save Entire Novel Project", use_container_width=True):
                saved_id = save_novel_project(bp)
                st.success(f"Novel project saved to archive! (ID: {saved_id})")

        # In-line Prose Editor & Rolling Ledger
        edit_tab_prose, edit_tab_ledger = st.tabs(["✍️ Chapter Prose Manuscript", "📋 Rolling Continuity Summary"])
        with edit_tab_prose:
            new_prose = st.text_area(
                f"Chapter {current_ch['number']} Prose",
                value=current_ch.get("content", ""),
                height=450,
                key=f"prose_editor_{current_ch['number']}"
            )
            current_ch["content"] = new_prose
            current_ch["word_count"] = len(new_prose.split())

            # Commercial Checkpoints Checklist
            st.caption("Commercial Fiction Quality Checkpoints: ")
            c_chk1, c_chk2, c_chk3 = st.columns(3)
            c_chk1.markdown("✅ **Sensory Anchors:** Tactile details, scents, acoustic pressure")
            c_chk2.markdown("✅ **Dialogue Subtext:** Characters speak with agendas, not data dumps")
            c_chk3.markdown("✅ **Tension Audit:** Micro-cliffhanger ending or unavoidable dilemma")

        with edit_tab_ledger:
            st.markdown(f"#### **Rolling Continuity Summary for Chapter {current_ch['number']}**")
            st.write("This 2–3 sentence summary is passed into the continuity buffer when writing the next chapter.")
            new_summary = st.text_area(
                "Rolling Summary",
                value=current_ch.get("summary", ""),
                height=120,
                key=f"summary_editor_{current_ch['number']}"
            )
            current_ch["summary"] = new_summary

        st.markdown("---")

        # Full Manuscript Compiler & Publishing Suite
        st.markdown("### 📥 **Full Manuscript Compiler & Publishing Suite**")
        st.write("Stitch all drafted chapters together into a unified, formatted book manuscript ready for Amazon KDP, agents, or line editing.")

        comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)

        compiled_md = compile_full_manuscript(bp)
        
        # Word .docx
        full_docx = export_to_docx(compiled_md, title=bp.get("title", "Novel"), is_screenplay=False)
        comp_col1.download_button(
            label="📄 Export Full Novel (.docx)",
            data=full_docx,
            file_name=f"{bp.get('title', 'novel').lower().replace(' ', '_')}_manuscript.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

        # PDF .pdf
        full_pdf = export_to_pdf(compiled_md, title=bp.get("title", "Novel"), is_screenplay=False)
        comp_col2.download_button(
            label="📑 Export Full Novel (.pdf)",
            data=full_pdf,
            file_name=f"{bp.get('title', 'novel').lower().replace(' ', '_')}_manuscript.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # Markdown .md
        full_md_bytes = export_to_markdown(compiled_md)
        comp_col3.download_button(
            label="📝 Export Full Novel (.md)",
            data=full_md_bytes,
            file_name=f"{bp.get('title', 'novel').lower().replace(' ', '_')}_manuscript.md",
            mime="text/markdown",
            use_container_width=True
        )

        # Send compiled to Dual-View Reader
        if comp_col4.button("📖 Read Full Book in Dual-View Reader", use_container_width=True):
            st.session_state.current_content = compiled_md
            st.session_state.current_title = bp.get("title", "Untitled Novel")
            st.session_state.last_output_type = f"Full Novel ({drafted_count}/{total_ch} Chapters)"
            st.success("Manuscript loaded into Dual-View Reader! Switch to Dual-View Reader tab.")

# ==========================================
# TAB 3: DUAL-VIEW READER & EXPORTERS
# ==========================================
with tab_reader:

    if not st.session_state.current_content:
        st.info("No manuscript generated yet. Go to the **Studio Workshop** tab to generate your first story or screenplay!", icon="💡")
    else:
        content = st.session_state.current_content
        metrics = get_text_metrics(content)
        is_screenplay = "Movie Script" in st.session_state.last_output_type

        # Metrics Bar
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.markdown(f'<div class="metric-card"><div class="metric-val">{metrics["words"]:,}</div><div class="metric-lbl">Total Words</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-val">{metrics["chars"]:,}</div><div class="metric-lbl">Characters</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="metric-val">{metrics["reading_time_mins"]} min</div><div class="metric-lbl">Est. Reading Time</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="metric-val">{metrics["estimated_screen_mins"]} pages</div><div class="metric-lbl">Screenplay Runtime</div></div>', unsafe_allow_html=True)
        m5.markdown(f'<div class="metric-card"><div class="metric-val" style="font-size:1.1rem; color:#A78BFA; padding-top:4px;">{st.session_state.model_used_label.split(" ")[0]}</div><div class="metric-lbl">Engine Source</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Dual-View Mode Switcher
        r_head_col, r_mode_col = st.columns([3, 2])
        with r_head_col:
            st.markdown(f"### **{st.session_state.current_title or 'Manuscript'}**")
            st.caption(f"Format: {st.session_state.last_output_type}")
        with r_mode_col:
            reader_mode = st.radio(
                "Reading View Mode",
                options=["📚 Book Typography View (Prose)", "📜 Screenplay Courier View (Film/TV)"],
                index=1 if is_screenplay else 0,
                horizontal=True
            )

        # Reader Canvas
        if "Courier" in reader_mode:
            st.markdown(f'<div class="screenplay-container">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="book-container">{content}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Universal Export & Persistence Toolbar
        st.markdown("#### **Export & Studio Actions**")
        exp_col1, exp_col2, exp_col3, exp_col4, exp_col5 = st.columns(5)
        
        # Word .docx
        docx_data = export_to_docx(content, title=st.session_state.current_title, is_screenplay=is_screenplay)
        exp_col1.download_button(
            label="📄 Export Word (.docx)",
            data=docx_data,
            file_name=f"{st.session_state.current_title.lower().replace(' ', '_')[:25]}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

        # PDF .pdf
        pdf_data = export_to_pdf(content, title=st.session_state.current_title, is_screenplay=is_screenplay)
        exp_col2.download_button(
            label="📑 Export PDF (.pdf)",
            data=pdf_data,
            file_name=f"{st.session_state.current_title.lower().replace(' ', '_')[:25]}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # Markdown .md
        md_data = export_to_markdown(content)
        exp_col3.download_button(
            label="📝 Export Markdown (.md)",
            data=md_data,
            file_name=f"{st.session_state.current_title.lower().replace(' ', '_')[:25]}.md",
            mime="text/markdown",
            use_container_width=True
        )

        # Fountain / Screenplay .fountain
        fountain_data = export_to_fountain(content)
        exp_col4.download_button(
            label="🎬 Export Fountain (.fountain)",
            data=fountain_data,
            file_name=f"{st.session_state.current_title.lower().replace(' ', '_')[:25]}.fountain",
            mime="text/plain",
            use_container_width=True,
            help="Industry standard plain-text script format for Final Draft, Highland, and WriterDuet."
        )

        # Save to Project Archive
        if exp_col5.button("💾 Save to Studio Archive", use_container_width=True):
            pid = save_project(
                title=st.session_state.current_title,
                storyline=st.session_state.storyline,
                genre=st.session_state.current_ingredients.get("genre", "Fiction"),
                output_type=st.session_state.last_output_type,
                content=content,
                ingredients=st.session_state.current_ingredients,
                audience=audience_dial,
                pov=pov_dial,
                pacing=pacing_dial,
                model_used=st.session_state.model_used_label
            )
            st.success(f"Saved to project archive (ID: {pid})!")

        # Raw Text Accordion for Direct Copying
        with st.expander("📋 View Plain Text / Copy to Clipboard"):
            st.text_area("Full Plain Text Content", value=content, height=220)

# ==========================================
# TAB 4: SAVED PROJECTS ARCHIVE
# ==========================================
with tab_archive:
    st.markdown("### 🗄️ **Saved Projects & Manuscripts**")
    st.write("Browse, reload, or manage your previously generated multi-chapter novels, stories, blueprints, and screenplays.")

    # 1. Multi-Chapter Novel Projects Section
    st.markdown("#### 📚 **Multi-Chapter Novel Projects**")
    saved_novels = list_novel_projects()
    if not saved_novels:
        st.caption("No multi-chapter novel projects saved yet. Create one in the **Chapter-by-Chapter Novel Engine** tab!")
    else:
        for np in saved_novels:
            with st.container():
                ncol_info, ncol_load, ncol_del = st.columns([6, 2, 1])
                with ncol_info:
                    st.markdown(f"##### 📖 **{np['title']}**")
                    st.caption(f"**Saved:** {np['saved_at']} | **Genre:** `{np['genre']}` | **Chapters Drafted:** `{np['drafted_count']}/{np['total_chapters']}` | **Total Words:** `{np['total_words']:,}`")
                with ncol_load:
                    if st.button("📂 Open in Novel Engine", key=f"load_novel_{np['id']}", use_container_width=True):
                        loaded_bp = load_novel_project(np["id"])
                        if loaded_bp:
                            st.session_state.book_project = loaded_bp
                            st.session_state.selected_ch_num = 1
                            st.success(f"Loaded novel '{loaded_bp.get('title')}' into Novel Engine! Switch to Tab 2.")
                with ncol_del:
                    if st.button("🗑️", key=f"del_novel_{np['id']}", help="Delete novel project"):
                        delete_project(np["id"])
                        st.warning(f"Deleted {np['title']}")
                        st.rerun()
                st.markdown("<hr style='margin:10px 0; border-color:#1E293B;'>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Stories, Screenplays & Blueprints Section
    st.markdown("#### 📜 **Single Stories, Blueprints & Screenplays**")
    projects = list_projects()
    # Filter out novel_ files from single stories list
    single_projects = [p for p in projects if not p["id"].startswith("novel_")]
    if not single_projects:
        st.info("No saved single stories found yet. Generate a story in the Studio Workshop and click 'Save to Studio Archive'!")
    else:
        for p in single_projects:
            with st.container():
                p_col_info, p_col_load, p_col_del = st.columns([6, 2, 1])
                with p_col_info:
                    st.markdown(f"#### 📖 **{p['title']}**")
                    st.caption(f"**Date:** {p['saved_at']} | **Genre:** `{p['genre']}` | **Format:** `{p['output_type']}`")
                    st.write(p["preview"])
                
                with p_col_load:
                    if st.button("📂 Load in Reader", key=f"load_{p['id']}", use_container_width=True):
                        full_data = load_project(p["id"])
                        if full_data:
                            st.session_state.current_content = full_data["content"]
                            st.session_state.current_title = full_data["title"]
                            st.session_state.storyline = full_data.get("storyline", "")
                            st.session_state.last_output_type = full_data.get("output_type", "Novel (Blueprint + Chapter 1)")
                            st.session_state.current_ingredients = full_data.get("ingredients", {})
                            st.session_state.model_used_label = full_data.get("model_used", "Loaded from Archive")
                            st.success(f"Loaded '{full_data['title']}'! Switch to Dual-View Reader.")
                
                with p_col_del:
                    if st.button("🗑️", key=f"del_{p['id']}", help="Delete project"):
                        delete_project(p["id"])
                        st.warning(f"Deleted {p['title']}")
                        st.rerun()
                st.markdown("---")

# ==========================================
# TAB 5: 6-MONTH MARKET INTELLIGENCE MATRIX
# ==========================================

with tab_market_guide:
    st.markdown("### 📈 **6-Month Commercial Bestseller Benchmark Guide**")
    st.write("The commercial fiction market is fast-moving. Here are the core tropes, emotional pacing structures, and reader sentiment trends that dominate charts across major genres.")
    
    for g_name, g_data in CURATED_GENRE_TRENDS.items():
        with st.expander(f"✨ {g_name} — Trends, Tropes & Bestseller Blueprint"):
            st.markdown(f"**Recent Comp Titles:** {', '.join(g_data['recent_comps'])}")
            st.markdown(f"**Tone & Voice:** {g_data['tone_voice']}")
            st.markdown(f"**Cliffhanger Mechanic:** {g_data['cliffhanger_styles']}")
            st.markdown(f"**Viral Hook Trigger:** {g_data['viral_hooks']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Top Bestselling Tropes:**")
                for t in g_data["top_tropes"]:
                    st.markdown(f"- {t}")
            with c2:
                st.markdown("**Character Dynamics & Friction:**")
                for d in g_data["character_dynamics"]:
                    st.markdown(f"- {d}")

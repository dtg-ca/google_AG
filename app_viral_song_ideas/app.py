"""
app.py
Viral Song Idea Generator - Streamlit Web Application
Role: Viral Song Idea Generator
Objective: Search social media, discussion forums, and websites to generate
song concepts engineered to achieve over 1,000,000 views.
"""

import streamlit as st
from trend_engine import compile_trend_radar
from generator import generate_viral_ideas
from pdf_exporter import generate_pdf_report

# Configure Page
st.set_page_config(
    page_title="Viral Song Idea Generator",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Studio Styling
st.markdown("""
<style>
    /* Dark Studio Aesthetic */
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF0050 0%, #A855F7 50%, #00F2FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .target-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(255, 0, 80, 0.15), rgba(0, 242, 254, 0.15));
        border: 1px solid rgba(0, 242, 254, 0.35);
        color: #38BDF8;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .song-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .song-title-header {
        font-size: 1.5rem;
        font-weight: 800;
        color: #F3F4F6;
        padding-bottom: 8px;
        border-bottom: 2px solid #374151;
        margin-bottom: 18px;
    }
    .section-label {
        font-size: 1.05rem;
        font-weight: 700;
        color: #E2E8F0;
        margin-top: 14px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    /* Item b: Storyline Box */
    .storyline-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-left: 5px solid #FF0050;
        border-radius: 8px;
        padding: 14px;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #F8FAFC;
        margin-bottom: 8px;
    }
    .char-badge-ok {
        background-color: #064E3B;
        color: #34D399;
        font-size: 0.78rem;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    /* Bonus Lyrics Box */
    .lyrics-box {
        background-color: #1E1B4B;
        border: 1px solid #3730A3;
        border-radius: 8px;
        padding: 14px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        color: #E0E7FF;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    /* Item c: Standalone Style Box */
    .style-container {
        background-color: #131D31;
        border: 1px solid #2563EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    /* Item d: Rationale Box */
    .rationale-box {
        background-color: #1A1D2E;
        border: 1px solid #4B5563;
        border-left: 5px solid #10B981;
        border-radius: 8px;
        padding: 14px;
        font-size: 0.92rem;
        color: #E5E7EB;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    /* Item e: Video Storyline Box */
    .video-story-box {
        background-color: #181926;
        border: 1px solid #6366F1;
        border-radius: 8px;
        padding: 14px;
        font-size: 0.92rem;
        color: #EDE9FE;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    /* Item f: Google Flow Prompts Box */
    .flow-prompt-step {
        background: #0D1117;
        border: 1px solid #30363D;
        border-left: 3px solid #A855F7;
        border-radius: 6px;
        padding: 9px 12px;
        margin-bottom: 6px;
        font-size: 0.88rem;
        color: #C9D1D9;
    }
    .screen-hook-badge {
        background: #3B0764;
        border: 1px solid #9333EA;
        color: #F3E8FF;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 8px;
        display: block;
    }
    /* Generate Button */
    .stButton>button {
        background: linear-gradient(90deg, #FF0050 0%, #A855F7 50%, #00F2FE 100%);
        color: white;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        padding: 0.7rem 1.8rem;
        font-size: 1.05rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.92;
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(255, 0, 80, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## 🎛️ Viral Radar Settings")
    st.caption("A&R Intelligence & Real-Time Trend Scanner")
    st.markdown("---")

    api_key = st.text_input(
        "Google Gemini API Key (Optional)",
        type="password",
        help="Optional: Enter a Gemini API key for dynamic LLM generation. If left blank, the app uses its built-in story-synthesizing AI engine."
    )

    num_ideas = st.slider("Number of Song Concepts", min_value=1, max_value=4, value=3)

    vibe_category = st.selectbox(
        "Target Viral Category / Aesthetic",
        [
            "All Trending Story Archetypes",
            "Bedroom Pop & Vulnerable Notes App Stories",
            "Dark Phonk & Villain-Era Career / Gym Stories",
            "Indie Pop & Serendipitous Travel Encounters",
            "Nostalgic 2000s Indie Sleaze / Chaotic Stories",
            "Acoustic Confession & Situationship Dilemmas"
        ]
    )

    st.markdown("---")
    st.markdown("### 📡 Scanned Sources")
    st.markdown("""
    - **Reddit Forums:** `r/AskReddit`, `r/TwoHotTakes`, `r/popheads`, `r/relationships`, `r/me_irl`, `r/GenZ`
    - **Web Radar:** Viral TikTok storytimes, trending hooks, meme dilemmas
    """)

# -------------------- MAIN DASHBOARD --------------------
st.markdown('<div class="main-title">🔥 Viral Song Idea Generator</div>', unsafe_allow_html=True)
st.markdown('<span class="target-badge">🎯 OBJECTIVE: DISCOVER REAL-WORLD STORIES TO GENERATE SONGS WITH 1,000,000+ VIEW POTENTIAL</span>', unsafe_allow_html=True)
st.markdown("Extracts real stories and dilemmas from social discussion forums and the web to craft **storyline-driven lyrics**, standalone **musical styles**, **TopMedia AI prompts**, and **Google Flow video campaigns**.")

# Input & Search Guidance
col_input, col_btn = st.columns([3.5, 1.2])
with col_input:
    user_guidance = st.text_area(
        "Input your suggestions, keywords, or instructions to guide the search:",
        placeholder="e.g. A story about finding an ex's hoodie in the car trunk, quiet quitting a corporate job, serendipitous airport missed connection, late night drive confession...",
        height=85
    )
with col_btn:
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Find Stories & Generate", use_container_width=True)

# Session State
if "generated_ideas" not in st.session_state:
    st.session_state.generated_ideas = []
if "trend_radar" not in st.session_state:
    st.session_state.trend_radar = None

# Generation Process
if generate_btn:
    with st.status("🔍 Searching social platforms, Reddit forums & society websites...", expanded=True) as status:
        st.write("1. Scanning `r/AskReddit`, `r/TwoHotTakes`, `r/relationships`, and web narratives for real human stories...")
        radar = compile_trend_radar(user_guidance)
        st.session_state.trend_radar = radar
        
        st.write("2. Weaving scanned stories into narrative storylines (< 400 chars), standalone styles, and Google Flow video blueprints...")
        ideas = generate_viral_ideas(
            user_instruction=user_guidance,
            vibe_category=vibe_category,
            count=num_ideas,
            api_key=api_key,
            trend_context=radar["summary_text"],
            scanned_stories=radar.get("all_stories", [])
        )
        st.session_state.generated_ideas = ideas
        status.update(label="✅ Viral Blueprints Successfully Generated!", state="complete", expanded=False)

# Display Scanned Stories Source Expander
if st.session_state.trend_radar and st.session_state.trend_radar.get("all_stories"):
    with st.expander("📖 View Real-World Web & Forum Stories Scanned as Source Material", expanded=False):
        for idx, s in enumerate(st.session_state.trend_radar["all_stories"][:8], 1):
            st.markdown(f"**{idx}. [{s['source']}]** {s['title']}")
            if s.get("snippet") and s["snippet"] != s["title"]:
                st.caption(f"Context: \"{s['snippet']}\"")

# -------------------- ALL SECTIONS DISPLAYED IN FULL (NO HIDDEN TABS) --------------------
if st.session_state.generated_ideas:
    st.markdown("---")
    res_header_col, pdf_col = st.columns([3, 1.4])
    with res_header_col:
        st.subheader(f"✨ Generated Viral Song Blueprints ({len(st.session_state.generated_ideas)} Complete Concepts)")
    with pdf_col:
        # PDF Generator & Download Button
        pdf_data = generate_pdf_report(st.session_state.generated_ideas, user_guidance)
        st.download_button(
            label="📥 Save Output as PDF",
            data=pdf_data,
            file_name="Viral_Song_Ideas_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Render each song idea with EVERY SINGLE REQUIRED SECTION PROMINENTLY IN VIEW
    for i, song in enumerate(st.session_state.generated_ideas, 1):
        with st.container():
            st.markdown('<div class="song-card">', unsafe_allow_html=True)
            
            # ----------------- SECTION A: Suggested Name -----------------
            st.markdown(f'<div class="song-title-header">🎵 a. Suggested Name: <span style="color:#38BDF8;">"{song.get("name", "Untitled Song")}"</span></div>', unsafe_allow_html=True)

            # ----------------- SECTION B: Storyline for Lyrics & TopMedia AI -----------------
            storyline_text = song.get("storyline_lyrics_basis", "")
            char_count = len(storyline_text)
            st.markdown(f"""
            <div class="section-label">
                📖 <b>b. Context / Theme / Storyline (Basis for Song Lyrics & TopMedia AI Description Box)</b>
                <span class="char-badge-ok">✓ {char_count} / 400 Characters</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="storyline-box">{storyline_text}</div>', unsafe_allow_html=True)
            st.caption("💡 Formatted specifically to paste into the TopMedia AI Music Generator description box. It weaves the scanned web stories into a storytelling narrative arc that drives the lyrics.")

            # Bonus: Sample Lyrics Preview
            lyrics = song.get("lyrics_preview", {})
            if lyrics:
                with st.expander("🎤 View Generated Song Lyrics Preview (Derived from this Storyline)", expanded=True):
                    st.markdown(f"""
                    <div class="lyrics-box">
                        <b>[Verse 1]:</b><br/>{lyrics.get('verse', '')}<br/><br/>
                        <b>[Viral TikTok Chorus Hook]:</b><br/>{lyrics.get('chorus', '')}
                    </div>
                    """, unsafe_allow_html=True)

            # ----------------- SECTION C: Suggested Style (SEPARATE BOX BY ITSELF) -----------------
            st.markdown('<div class="section-label">🎹 <b>c. Suggested Musical Style (Standalone Production Box)</b></div>', unsafe_allow_html=True)
            style = song.get("style", {})
            st.markdown(f"""
            <div class="style-container">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div>
                        <p style="margin: 4px 0;"><b>🎵 Genre & Subgenre:</b> <span style="color:#60A5FA;">{style.get('genre', 'N/A')}</span></p>
                        <p style="margin: 4px 0;"><b>⏱️ Tempo / Meter:</b> <span style="color:#60A5FA;">{style.get('tempo', 'N/A')}</span></p>
                        <p style="margin: 4px 0;"><b>🎼 Musical Key:</b> <span style="color:#60A5FA;">{style.get('key', 'N/A')}</span></p>
                    </div>
                    <div>
                        <p style="margin: 4px 0;"><b>🎸 Key Instruments:</b> <span style="color:#60A5FA;">{style.get('instruments', 'N/A')}</span></p>
                        <p style="margin: 4px 0;"><b>✨ Mood & Vibe:</b> <span style="color:#60A5FA;">{style.get('mood', 'N/A')}</span></p>
                        <p style="margin: 4px 0;"><b>🎙️ Vocal Delivery:</b> <span style="color:#60A5FA;">{style.get('vocal_delivery', 'N/A')}</span></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ----------------- SECTION D: Viral Rationale -----------------
            st.markdown('<div class="section-label">📈 <b>d. Rationale for Why This Song Might Go Viral (1M+ Views)</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="rationale-box">{song.get("viral_rationale", "High emotional relatability and seamless loop design.")}</div>', unsafe_allow_html=True)

            # ----------------- SECTION E: TikTok Video Storyline (Google Flow) -----------------
            st.markdown('<div class="section-label">🎬 <b>e. Storyline for Generating TikTok Video to Promote This Song (Google Flow Concept)</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="video-story-box">{song.get("tiktok_video_storyline", "N/A")}</div>', unsafe_allow_html=True)

            # ----------------- SECTION F: Google Flow Scene-by-Scene Prompts -----------------
            st.markdown('<div class="section-label">🎥 <b>f. Google Flow / Veo Video Generation Prompts & Screen Hook</b></div>', unsafe_allow_html=True)
            hook_text = song.get("screen_text_hook", "")
            if hook_text:
                st.markdown(f'<div class="screen-hook-badge">📱 <b>TikTok Screen Text Overlay Hook:</b> "{hook_text}"</div>', unsafe_allow_html=True)
            
            prompts = song.get("google_flow_prompts", [])
            for step_prompt in prompts:
                st.markdown(f'<div class="flow-prompt-step">{step_prompt}</div>', unsafe_allow_html=True)

            # ----------------- SECTION G: Viral Hashtags -----------------
            st.markdown('<div class="section-label">🏷️ <b>g. Hashtags to Get This Song Go Viral</b></div>', unsafe_allow_html=True)
            tags = song.get("hashtags", [])
            hashtag_str = " ".join(tags) if isinstance(tags, list) else str(tags)
            st.code(hashtag_str, language="markdown")
            st.caption("📋 One-click copy for your TikTok / Reels video caption.")

            st.markdown('</div>', unsafe_allow_html=True)

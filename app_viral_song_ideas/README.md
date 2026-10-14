# 🎵 Viral Song Idea Generator (TikTok & Social Media)

An AI-powered A&R dashboard engineered to search social media, discussion forums, and web trends to generate viral song concepts capable of achieving **1,000,000+ views** on TikTok, Instagram Reels, and YouTube Shorts.

## 🚀 Key Features

1. **Streamlit UI**: Modern dark-mode interface with real-time trend radars and responsive generation controls.
2. **Search Guidance Input**: Option to input custom keywords, themes, situationship stories, or emotional hooks to guide the search and generation.
3. **Multi-Source Trend Radar**:
   - Reddit communities (`r/popheads`, `r/musicproduction`, `r/tiktokhelp`, `r/AskReddit`, `r/GenZ`, `r/me_irl`)
   - Web search for trending TikTok sounds, audio tropes, and aesthetic tags.
4. **Structured Viral Outputs (All 6 Required Sections)**:
   - **a. Suggested Name for this song**
   - **b. TopMedia AI Music Generator Description**: Guaranteed under 400 characters, formatted with optimal prompt syntax.
   - **c. Suggested Style**: Genre, key instruments, tempo (BPM), musical key, and vocal delivery.
   - **d. Rationale for 1M+ Views**: Psychological hooks, 7-second audio loopability, and algorithm retention mechanics.
   - **e. Google Flow TikTok Video Storyline**: Scene-by-scene prompts (0:00 to 0:20 loop) for Google Flow / Veo with on-screen text overlay hooks.
   - **f. Viral Hashtags**: Tailored mix of high-volume and niche discovery tags.
5. **PDF Export**: Instant, one-click downloadable PDF report formatted with ReportLab.

---

## 💻 Quick Start Guide

### 1. Activate the Virtual Environment
In PowerShell:
```powershell
& "G:\google_AG\.venv_AG\Scripts\Activate.ps1"
```
Or run directly using the `.venv_AG` python/streamlit executable:
```powershell
& "G:\google_AG\.venv_AG\Scripts\streamlit.exe" run app.py
```

### 2. Launching the App
```powershell
streamlit run app.py
```

---

## 📁 Project Structure

```
viral_song_ideas/
├── app.py              # Streamlit web application & user interface
├── trend_engine.py     # Scrapes/fetches Reddit & web social trend signals
├── generator.py        # Generates viral song ideas & enforces < 400 char limit
├── pdf_exporter.py     # Compiles professional PDF reports
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

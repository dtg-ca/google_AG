# 📚 Bestseller Story Studio

An AI-powered commercial fiction and screenwriting studio designed to transform story concepts into market-topping **Novels (Blueprint + Chapter 1)**, **Movie Scripts (Short Film or Feature Treatment + Act I)**, and **Standalone Short Stories**, engineered with real-time **6-month bestseller trends**.

---

## 🌟 Key Features

1. **Hybrid 6-Month Bestseller Trend Engine**
   - Combines public APIs (Google Books API) with live web search (DuckDuckGo targeting BookTok, Goodreads reader sentiment, and bestseller discussions).
   - Dynamically extracts and pairs tailored ingredients: recent comps, top tropes, character dynamics, emotional beats, voice/tone, cliffhanger styles, and viral hooks.

2. **Chapter-by-Chapter Novel Engine (Hierarchical Sliding Window)**
   - Expands master blueprints into full-length commercial novels (15–25+ chapters) cost-effectively (<$1.50 in API costs).
   - **Automated Outline-to-Chapter Mapping**: Parses any generated or custom outline (`Chapter 1..N`, markdown acts, or bulleted beat sheets) directly into structured chapter beats with 3 micro-beats each (Hook & Objective, Obstacle & Escalation, Micro-Cliffhanger).
   - **Batch Auto-Drafting Suite**: 1-click **Auto-Draft All Remaining Chapters from Outline** or **Draft Next 3 Chapters** with real-time progress bars, sliding continuity summaries, and ending anchor matching.
   - **3-Tier Sliding Window**: Static Master Story Bible (~1,000 tokens) + Chapter Beat & Scene Micro-Treatment (~500 tokens) + Rolling Continuity Anchor (Chapter $N-1$ summary + exact last 250 words) (~800 tokens).
   - **Prose & Continuity Editor**: In-line drafting with commercial checkpoints (sensory anchors, dialogue subtext, tension audit) and rolling ledger editing.
   - **Manuscript Compiler**: Stitches all chapters into unified manuscripts downloadable in **Word (`.docx`)**, **PDF (`.pdf`)**, and **Markdown (`.md`)**.

3. **3 Professional Output Types**
   - **Novel**: Commercial proposal (logline, comp titles, target audience), character dossiers, multi-chapter 3-act beat sheet (*Save the Cat!* structure), and a polished Chapter 1.
   - **Movie Script**: User toggle between **Complete Short Film (10–15 pages)** or **Feature Film Treatment + Act I Opening**, formatted in standard industry screenplay typography.
   - **Short Story**: Standalone, complete narrative (~2,500–4,500 words) ready for publication.

3. **Hybrid Workflow Modes**
   - **Fast Track (1-Click)**: Instant, seamless generation from storyline input.
   - **Market Lab (Advanced)**: Scan 6-month trends first; inspect comps, tropes, and character dynamics; customize ingredients before generating.

4. **Dedicated Dual-View Reader**
   - **Prose Book Typography View**: Elegant serif styling, reading line height, and chapter navigation.
   - **Screenplay Courier View**: Authentic 12pt monospace screenplay layout.
   - **Real-Time Analytics**: Word count, character count, estimated reading time, and screenplay runtime/pages.

5. **Universal Export Suite & History Archive**
   - One-click export to **Word (`.docx`)**, **PDF (`.pdf`)**, **Markdown (`.md`)**, and **Fountain (`.fountain`)** for Final Draft / Highland.
   - **Saved Projects Archive**: Locally persisted JSON session manager to save, reload, compare, and delete past drafts.

6. **Creative Sliders & Model Switching**
   - Model switching between `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, and `gemini-1.5-flash`.
   - Pre-generation dials for **Target Audience**, **Narrative Perspective (POV)**, and **Pacing Intensity**.
   - Built-in offline creative engine if an API key is not yet configured.

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
From the repository root (`G:\google_AG`):
```powershell
.\.venv_AG\Scripts\Activate.ps1
```

### 2. Configure API Key
Create or edit `.env` in `app_best_selling_author/` (or copy from `.env.example`):
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(You can also paste the API key directly into the app sidebar at runtime).*

### 3. Launch the Application
```powershell
cd app_best_selling_author
streamlit run app.py
```
Or run directly from the workspace root:
```powershell
streamlit run .\app_best_selling_author\app.py
```

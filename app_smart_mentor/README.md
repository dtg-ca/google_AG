# 🧭 Smart Mentor: Strategic Knowledge & Advisory Application

An intelligent, multi-disciplinary advisory application built with **Streamlit**, **Google Gemini**, and a real-time **Multi-Source Knowledge Retrieval Engine**.

The **Smart Mentor** acts as a seasoned expert who possesses the wisdom, strategic foresight, and multidisciplinary knowledge to answer user questions across a wide variety of topics—including current affairs, clinical medical science, legal frameworks, and community discourse.

---

## 🌟 Key Features & Objectives Fulfilled

1. **Streamlit UI**:
   - Modern, executive theme with custom CSS styling, responsive cards, and clean typography.
   - Quick-start dilemma presets for instant demonstration (Medical, Legal Non-Compete, Tariffs, AI Disruption).

2. **User-Friendly Guided Dialog Box (`st.dialog`)**:
   - Dedicated modal dialog to frame complex questions step-by-step:
     - Topic / Issue / Problem title
     - Category / Domain selection
     - Desired Mentor Guidance Stance / Tone
     - Personal Context & Vulnerabilities (what you seek to protect)
     - Information Repositories selection toggles
   - Inline framing form for immediate on-page entry as well.

3. **Multi-Source Real-Time Search Engine**:
   - **Current Affairs & Global News**: Google News RSS real-time feed across major journalistic institutions.
   - **Medical Content Repositories**: National Center for Biotechnology Information (**NCBI / PubMed**) E-Utilities for peer-reviewed clinical studies and health consensus.
   - **Legal, Regulatory & Academic Repositories**: **OpenAlex API** for statutory, judicial, and academic research papers.
   - **Society & Foundational Reference**: **Wikipedia API** for contextual definitions, background, and encyclopedic overviews.
   - **Social Media & Community Discussion Forums**: Targeted forum analysis capturing real-world public sentiments, practical lived experiences, and debate on platforms like Reddit and Quora.

4. **Structured 4-Section Output with Strict Word Limits**:
   - **Section A**: *The Question / Input from User* (reframed query, domain, context, stakes).
   - **Section B**: *Summary of Search Results* (**strictly < 1000 words**, tracked with real-time word count badges).
   - **Section C**: *Analysis & Insights from Searched References* (**strictly < 500 words**, mentor wisdom, underlying trade-offs, and systemic blind spots).
   - **Section D**: *Action Plans / Next Steps for the User* (concrete, prioritized roadmap organized by Immediate, Tactical, and Strategic phases with safety checklists).

5. **PDF Export Functionality**:
   - One-click **Download Advisory Report (PDF)** button powered by **ReportLab**.
   - Generates an executive-grade document featuring all 4 sections, metadata cards, formatted tables, source references, and running headers/footers with dynamic `"Page X of Y"` numbering.

6. **Interactive Follow-Up Mentorship Room**:
   - Allows the user to continue the dialogue directly with the Smart Mentor, asking clarifying questions, exploring alternative perspectives, and stress-testing action plans.

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Environment Setup
Make sure you have Python 3.10+ installed.

```bash
# Clone or navigate to the repository
cd G:\google_AG\app_smart_mentor

# (Optional) Set your Google Gemini API Key
set GEMINI_API_KEY="your-gemini-api-key"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit App
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

- `app.py`: Streamlit application interface, state management, guided `@st.dialog` modal, tabbed views, and follow-up consultation room.
- `search_engine.py`: Multi-source search engine querying Google News, PubMed, OpenAlex, Wikipedia, and social discussion feeds with error handling.
- `mentor_engine.py`: Gemini client integrating multi-source intelligence, enforcing section layouts and word limits (< 1000w summary, < 500w analysis), with automatic fallback resilience.
- `pdf_generator.py`: ReportLab PDF document builder generating multi-page styled advisory briefs with metadata and citation tables.
- `requirements.txt`: Python package dependencies.
- `README.md`: System documentation and user guide.

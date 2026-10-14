# 🛠️ FixMate: Expert DIY Repair Solutions Wizard

FixMate is an intelligent DIY equipment repair assistant designed to diagnose faults, research authoritative repair guides and real community discussions across the web, provide itemized outside professional repair cost estimates (parts + labor), locate nearby repair centers, and export complete technical dossiers to PDF.

---

## 🌟 Key Features

1. **Equipment & Problem Intake**:
   - Structured equipment taxonomy covering **Major Appliances**, **HVAC & Home Climate**, **Lawn & Garden / Outdoor Power**, **Consumer Electronics & Computing**, **Automotive & Small Engines**, **Plumbing & Fixtures**, and **Power Tools**.
   - Model plate identification tips tailored to each equipment category.
   - Detailed symptom reporting with common presets.
   - Captures user's physical location / postal address (e.g., Street, City, State/Province, ZIP/Postal code).

2. **Outside Professional Cost Estimation (Parts + Labor)**:
   - Evaluates the financial and technical trade-offs assuming the DIY solution is too difficult for the user.
   - Itemized professional breakdown:
     - **Diagnostic / Service Call Trip Fee** (Standard dispatch fee)
     - **Labor Charges** (Estimated labor hours × regional hourly rates)
     - **OEM Replacement Parts** (Retail price with typical 20-30% shop markup)
     - **Shop Supplies & Disposal Fees** (Consumables and hazardous recycling)
     - **Total Estimated Professional Cost Range**
     - **DIY Cost Savings** ($ and % saved by fixing it yourself)
     - **Escalation Criteria**: Concrete conditions on when to stop DIY and hire a professional.
   - Searches and lists **Nearest Outside Repair Locations & Service Centers** found near the user's postal address, with 1-click Google Maps and Yelp search navigators.

3. **Multi-Source Real-Time Online Research**:
   - **Technical Guides & Service Manuals**: Aggregates from sources like RepairClinic, iFixit, and AppliancePartsPros.
   - **Community Forums**: Scrapes Reddit (`r/fixit`, `r/appliances`, `r/DIY`, `r/MechanicAdvice`) and DoItYourself forums for real community solutions.
   - **Video Guides**: Locates relevant YouTube teardown and repair walkthroughs.
   - **Local Parts Hub**: Discovers nearby parts supply warehouses, hardware stores, and store locators (Home Depot, AutoZone, etc.).

4. **AI Diagnostic Dossier (Powered by Google Gemini)**:
   - **Safety Precaution Alert**: Specific warnings (high voltage, gas shutoff, water isolation, capacitor hazards).
   - **Root Cause Analysis**: Ranked likely causes with verification tests.
   - **Tools & Parts Breakdown**: Interactive checklist and replacement part tags.
   - **Step-by-Step Guide**: Sequential phases with interactive checkboxes and pro-tips.
   - **Community Wisdom**: Quotes and warnings from actual forum discussions.

5. **Complete PDF Export of Entire Output**:
   - Generates an exhaustive, multi-page printable PDF report via ReportLab containing:
     - Complete equipment intake & user postal address
     - Safety warnings
     - Root causes & verification tests
     - Required tools & DIY parts
     - Step-by-step DIY repair guide
     - **Full Outside Professional Repair Cost Estimate Table (Parts + Labor)**
     - **Nearest Outside Repair Locations Discovered**
     - Local parts suppliers & hardware stores
     - Community wisdom & forum quotes
     - **Comprehensive Online Research Citations & Clickable URLs**
   - Take the PDF offline to your workbench or garage!

6. **Interactive Repair Assistant & History**:
   - **Live Follow-up Chat**: Ask real-time questions while taking apart the machine (e.g. multimeter testing, stubborn screws, comparing repair quotes).
   - **Session History**: Auto-saves past diagnostic sessions in local storage.

---

## 🚀 Quick Start Guide

### 1. Requirements & Installation

```bash
pip install -r requirements.txt
```

### 2. Set Your Gemini API Key (Optional)

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

*Note: If no API key is set or the API is experiencing high demand, FixMate automatically engages its built-in Expert Heuristic Engine with live web search grounding.*

### 3. Launch the Streamlit App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📁 Project Architecture

```
app_repair_wizard/
│
├── app.py                 # Streamlit UI & interaction layer
├── config.py              # Equipment taxonomy, forum targets & settings
├── research_engine.py     # Multi-backend web, forum, local parts & pro repair searcher
├── repair_agent.py        # Gemini AI diagnostic agent with pro cost estimation & fallback
├── pdf_generator.py       # Full-dossier printable PDF generator (ReportLab)
├── sample_data.py         # Realistic demo presets for 1-click testing
├── history_manager.py     # Local JSON persistence for past repair cases
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

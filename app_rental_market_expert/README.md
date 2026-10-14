# 🏢 Rental Market Expert & Pricing Intelligence App

An AI-powered Streamlit web application designed for property owners, real estate investors, and property managers. It analyzes localized rental market portals and community forums across the past 4 months to recommend the **optimal rental price**, **optimum vacancy advertising windows**, **target tenant personas**, and the **highest-velocity listing platforms**, backed by an exportable **PDF report**.

---

## 🌟 Key Features

1. **Streamlit UI & Interactive Visualizations**:
   - Modern dashboard interface with KPI cards, 12-month seasonality curves, and 4-month market fulfillment charts built with Plotly.
2. **Multi-Format Input System**:
   - **Interactive Form:** Select Country, State/Province, City, Street, Postal Code, Property/Room Type, and amenities.
   - **File Upload:** Upload user request files in `.json`, `.csv`, or `.txt` formats.
   - **Free-Form Text Parser:** Paste unstructured emails or notes; built-in NLP/regex extracts addresses and unit details automatically.
   - **Sidebar Quick Demos:** 1-click loading for common real-world markets (Toronto 2-bed, Austin 1-bed, London studio, SF room).
3. **Targeted Web Search & 4-Month Trend Analysis**:
   - Queries relevant portals by jurisdiction (e.g., Zillow, Rentals.ca, Apartments.com, Rightmove, Zoopla, PadMapper, Craigslist).
   - Scrapes community forums (Reddit, tenant discussion boards) for sentiment, demand elasticity, and price resistance.
   - Evaluates the **past 4 months** for median asking rents, month-over-month shifts, and absorption velocity (Average Days on Market).
4. **Data-Driven Strategic Recommendations**:
   - **Suggested Rent Tiers:** Fast-Fulfillment (<7 days fill), Recommended Fair Market Target, and Premium Yield.
   - **Optimum Advertising Calendar:** 12-month seasonality demand index highlighting peak windows vs. winter slowdowns.
   - **Target Tenant Segment:** Demographic profiling with top value drivers and a tailored listing headline hook.
   - **Fastest-Response Platforms:** Ranked platforms with expected first-inquiry speeds and listing pro-tips.
   - **Transparent Rationale:** Full analytical breakdown explaining comps, vacancy holding costs, and price elasticity.
5. **Executive PDF Export**:
   - One-click generation of a branded, printable PDF report using ReportLab containing tables, callouts, and recommendations.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit App
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📂 Project Architecture

```
app_rental_market_expert/
├── app.py                      # Main Streamlit dashboard & UI tabs
├── file_parser.py              # Parser for JSON, CSV, TXT, and freeform text
├── search_engine.py            # Live web search engine across portals & forums
├── market_analyzer.py          # 4-month trend analysis & fulfillment velocity
├── recommendation_engine.py    # Pricing tiers, seasonality index & platform ranking
├── pdf_generator.py            # ReportLab PDF report generation
├── requirements.txt            # Python dependencies
├── sample_requests/            # Ready-to-test sample files
│   ├── sample_toronto_2bed.json
│   ├── sample_austin_1bed.txt
│   └── sample_london_studio.csv
└── README.md
```

---

## 📄 Sample File Formats

### JSON (`sample_requests/sample_toronto_2bed.json`)
```json
{
  "Country": "Canada",
  "Province/State": "Ontario",
  "City": "Toronto",
  "Street": "180 University Avenue",
  "Postal code": "M5H 0A2",
  "Property/room type": "2-Bedroom Apartment",
  "Bedrooms": 2,
  "Bathrooms": 2
}
```

### CSV (`sample_requests/sample_london_studio.csv`)
```csv
Country,Province/State,City,Street,Postal Code,Property/Room Type,Bedrooms,Bathrooms
United Kingdom,Greater London,London,120 Shoreditch High St,E1 6JE,Studio / Bachelor,0,1
```

### Plain Text (`sample_requests/sample_austin_1bed.txt`)
```text
Street: 400 Colorado St
City: Austin
State/Province: Texas
Postal Code: 78701
Country: United States
Property/Room Type: 1-Bedroom Apartment
```

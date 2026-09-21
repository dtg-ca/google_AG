# 🏡 Real Estate Market Predictor

**Role:** Real Estate Predictor  
**Objective:** For any given property address in a neighborhood, search the web for the past 3 to 6 months across leading real estate portals, analyze neighborhood market health for similar property types, and predict the **expected selling price** and **expected days on market (DOM)** to sell with comprehensive reasoning and publication-grade PDF report export.

---

## 🌟 Core Features

1. **Interactive Streamlit UI**:
   - Modern, executive dashboard designed for real estate analysts, brokers, investors, and homeowners.
   - Four instant metric summary cards: **Expected Selling Price**, **Expected Days on Market (DOM)**, **Market Climate / Health Score**, and **Valuation Confidence**.
   - Interactive Plotly charts:
     - *Comps Price vs. Days on Market (Scatter plot with Target marker)*
     - *Pricing Strategy Sensitivity (Quick Liquidity vs. Fair Market vs. Aggressive)*
     - *Price per Sq.Ft. Benchmark comparison*
   - Expandable breakdown of predictive reasoning across 5 key pillars.

2. **Dual Input Methods (Form & File Upload)**:
   - **Interactive Form Input**: Direct entry of Country, Province/State, City, Street, Postal Code, Property Type, Bedrooms, Bathrooms, SqFt, Lot Size, Year Built, Condition, and Websites to search.
   - **File Upload Support**: Accepts `.json`, `.yaml`, `.yml`, `.csv`, or structured `.txt` files containing property details and target websites.
   - **One-Click Sample Loaders**: Pre-packaged templates for Toronto Detached Homes, Austin Townhouses, and Toronto High-Rise Condos.

3. **Web Search & Data Extraction (Past 3 to 6 Months)**:
   - Queries user-specified websites (e.g. `realtor.ca`, `zillow.com`, `redfin.com`, `zolo.ca`, `housesigma.com`, `homes.com`) over the past 3 to 6 months.
   - Extracts recent sold comps, list prices, days on market (DOM), square footage, and neighborhood market health indicators.
   - Fully resilient search engine with municipal calibration safeguards.

4. **Neighborhood Market Health Analysis**:
   - Computes Market Temperature (Seller's Market, Balanced Market, Buyer's Market).
   - Evaluates Months of Inventory (MOI), Sale-to-List price ratio, and neighborhood turnover velocity.
   - Filters cohort statistics for similar property types.

5. **Hedonic Valuation & Days on Market (DOM) Prediction Engine**:
   - Calculates central expected selling price and 95% confidence price range.
   - Predicts expected days on market (DOM) and range for firm contract execution.
   - Full Hedonic Adjustment Schedule: Size, Bedrooms, Bathrooms, Property Condition, Age, and Market Momentum.
   - Three Strategic Pricing Scenarios (Competitive / Fast Liquidity, Fair Market Value, Aggressive Ceiling).
   - In-depth, transparent predictive reasoning.

6. **Publication-Grade PDF Report Export**:
   - One-click PDF download compiled with ReportLab.
   - Includes executive summary, property specs, market health table, pricing sensitivity matrix, comparable sales table, structured appraisal reasoning, and web source citations.

---

## 📁 Project Architecture

```
app_real_estate_market_predictor/
│
├── app.py                      # Streamlit UI & Interactive Dashboard
├── config.py                   # Default websites, property types, metro benchmarks
├── file_parser.py              # Parser for JSON, YAML, CSV, and Plain Text request files
├── search_engine.py            # Targeted web search & comp data extraction engine
├── market_analyzer.py          # Market health, absorption & cohort statistics engine
├── predictor.py                # Hedonic pricing & Days on Market (DOM) prediction engine
├── pdf_generator.py            # Executive PDF report generator (ReportLab)
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
└── sample_inputs/              # Sample user request files
    ├── sample_canada_property.json
    ├── sample_us_property.json
    └── sample_request.txt
```

---

## 🚀 Getting Started

### 1. Install Dependencies

Ensure Python 3.10+ is installed, then run:

```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit App

Run the Streamlit application from the project root:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📄 User Request Input File Formats

You can upload request files in any of the following formats:

### JSON Format (`sample_canada_property.json`):
```json
{
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
```

### Plain Text Format (`sample_request.txt`):
```text
Country: Canada
Province: Ontario
City: Toronto
Street: 88 Finch Ave E
Postal Code: M2N 4R5
Property Type: Condominium Apartment
Bedrooms: 2
Bathrooms: 2
Square Feet: 920
Year Built: 2016
Condition: Good (Well Maintained)
Websites: realtor.ca, zolo.ca, housesigma.com
Time Horizon: Past 3 Months
```

---

## 🛡️ Optional AI Enhancement

The system operates with a high-fidelity algorithmic and hedonic valuation engine out of the box without requiring any API keys. If you wish to enable generative AI commentary using Google Gemini:

1. Add your key in the Streamlit sidebar under **Gemini API Key**, or
2. Set the environment variable:
   ```bash
   set GEMINI_API_KEY=your_api_key_here
   ```

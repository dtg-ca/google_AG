import os
from file_parser import parse_json_input, parse_csv_input, parse_freeform_text, PropertyRequest
from search_engine import search_rental_market_web
from market_analyzer import analyze_market_data
from recommendation_engine import generate_recommendations
from pdf_generator import create_rental_market_pdf

def test_pipeline():
    print("1. Testing JSON file parsing...")
    with open("sample_requests/sample_toronto_2bed.json", "r") as f:
        req = parse_json_input(f.read())
    print("   Parsed:", req.full_address, "| Type:", req.property_type)

    print("2. Testing CSV file parsing...")
    with open("sample_requests/sample_london_studio.csv", "r") as f:
        csv_req = parse_csv_input(f.read())
    print("   Parsed:", csv_req.full_address, "| Type:", csv_req.property_type)

    print("3. Testing Freeform TXT parsing...")
    with open("sample_requests/sample_austin_1bed.txt", "r") as f:
        txt_req = parse_freeform_text(f.read())
    print("   Parsed:", txt_req.full_address, "| Type:", txt_req.property_type)

    print("4. Testing Web Search & Comps Engine...")
    comps = search_rental_market_web(req.city, req.state_province, req.country, req.property_type, max_results=6)
    print(f"   Retrieved {len(comps)} comps/sources.")

    print("5. Testing Market Analysis (4-Month Trends)...")
    analysis = analyze_market_data(req, comps)
    print(f"   Baseline Median: {analysis.currency_symbol}{analysis.baseline_median_price}")
    print(f"   4-Month trend points: {[m.month_name for m in analysis.past_4_months]}")

    print("6. Testing Recommendation Engine...")
    rec = generate_recommendations(analysis)
    print(f"   Suggested Target Rent: {rec.currency_symbol}{rec.suggested_rent_target}")
    print(f"   Peak Months: {rec.optimum_months[:2]}")
    print(f"   Primary Segment: {rec.target_segment.primary}")
    print(f"   Top Fast Platform: {rec.fast_response_platforms[0].name}")

    print("7. Testing PDF Export Generation...")
    pdf_bytes = create_rental_market_pdf(req, analysis, rec)
    print(f"   PDF generated successfully! Size: {len(pdf_bytes)} bytes.")
    
    assert len(pdf_bytes) > 1000, "PDF bytes should be non-empty"
    print("\nSUCCESS: All pipeline tests passed successfully!")

if __name__ == "__main__":
    test_pipeline()

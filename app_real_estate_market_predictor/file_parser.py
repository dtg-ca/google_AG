"""
Input file parser supporting JSON, YAML, plain text, and CSV formats
for real estate property prediction requests.
"""

import json
import csv
import io
import re
from typing import Dict, Any, Optional

def parse_input_file(content: str, filename: str = "") -> Dict[str, Any]:
    """
    Parses property request file contents into a standardized dictionary:
    {
        "country": str,
        "province_state": str,
        "city": str,
        "street": str,
        "postal_code": str,
        "property_type": str,
        "bedrooms": int,
        "bathrooms": float,
        "sqft": int,
        "lot_size": str,
        "year_built": int,
        "condition": str,
        "websites": list[str],
        "time_horizon": str
    }
    """
    filename_lower = filename.lower()
    
    # 1. Attempt JSON
    if filename_lower.endswith(".json") or content.strip().startswith("{"):
        try:
            data = json.loads(content)
            return normalize_property_dict(data)
        except Exception:
            pass

    # 2. Attempt CSV parsing only if explicitly named .csv or comma-delimited tabular rows
    if filename_lower.endswith(".csv"):
        try:
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
            if rows:
                return normalize_property_dict(rows[0])
        except Exception:
            pass

    # 3. Attempt Key-Value / YAML parsing
    lines = content.splitlines()
    kv_data = {}
    current_key = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip().lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            val = parts[1].strip()
            kv_data[key] = val
            current_key = key
        elif current_key and (line.startswith("-") or line.startswith("*")):
            # List item under current key
            val = line.lstrip("-* ").strip()
            if isinstance(kv_data[current_key], list):
                kv_data[current_key].append(val)
            else:
                kv_data[current_key] = [kv_data[current_key], val] if kv_data[current_key] else [val]

    if kv_data:
        return normalize_property_dict(kv_data)

    # Return default empty dict if parsing failed
    return normalize_property_dict({})


def normalize_property_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes keys from various naming conventions into standard property attributes.
    """
    clean = {}
    
    # Address field mappings
    country_keys = ["country", "nation", "cntry"]
    province_keys = ["province_state", "province", "state", "prov", "st", "region", "province/state"]
    city_keys = ["city", "municipality", "town", "locality"]
    street_keys = ["street", "address", "street_address", "streetaddress", "road"]
    postal_keys = ["postal_code", "postalcode", "zip", "zipcode", "zip_code", "postcode"]
    
    # Property spec mappings
    type_keys = ["property_type", "type", "home_type", "housing_type"]
    bed_keys = ["bedrooms", "beds", "bed", "br"]
    bath_keys = ["bathrooms", "baths", "bath", "ba"]
    sqft_keys = ["sqft", "square_feet", "interior_sqft", "area_sqft", "square_footage", "size"]
    lot_keys = ["lot_size", "lot_sqft", "lot", "lot_area"]
    year_keys = ["year_built", "year", "built", "age"]
    cond_keys = ["condition", "status", "quality"]
    websites_keys = ["websites", "websites_to_search", "target_websites", "sites", "search_websites", "source_websites"]
    time_keys = ["time_horizon", "time_window", "time_period", "past_months"]

    def find_val(keys, default=""):
        for k, v in raw.items():
            k_clean = str(k).lower().strip().replace(" ", "_").replace("-", "_").replace("/", "_")
            if k_clean in keys:
                return v
        return default

    clean["country"] = str(find_val(country_keys, "Canada")).strip()
    clean["province_state"] = str(find_val(province_keys, "Ontario")).strip()
    clean["city"] = str(find_val(city_keys, "Toronto")).strip()
    clean["street"] = str(find_val(street_keys, "142 Elmwood Ave")).strip()
    clean["postal_code"] = str(find_val(postal_keys, "M2N 3M3")).strip()
    
    clean["property_type"] = str(find_val(type_keys, "Single Family Detached")).strip()
    
    # Numeric conversions
    try:
        clean["bedrooms"] = int(re.sub(r"[^\d]", "", str(find_val(bed_keys, 3))) or 3)
    except Exception:
        clean["bedrooms"] = 3

    try:
        bath_val = str(find_val(bath_keys, 2.5)).replace(",", ".")
        clean["bathrooms"] = float(re.findall(r"[\d\.]+", bath_val)[0]) if re.findall(r"[\d\.]+", bath_val) else 2.5
    except Exception:
        clean["bathrooms"] = 2.5

    try:
        sqft_val = str(find_val(sqft_keys, 2200))
        clean["sqft"] = int(re.sub(r"[^\d]", "", sqft_val) or 2200)
    except Exception:
        clean["sqft"] = 2200

    clean["lot_size"] = str(find_val(lot_keys, "40 x 120 ft")).strip()

    try:
        clean["year_built"] = int(re.sub(r"[^\d]", "", str(find_val(year_keys, 1995))) or 1995)
    except Exception:
        clean["year_built"] = 1995

    clean["condition"] = str(find_val(cond_keys, "Good (Well Maintained)")).strip()
    
    # Websites
    websites_raw = find_val(websites_keys, ["realtor.ca", "zillow.com", "redfin.com", "zolo.ca"])
    if isinstance(websites_raw, list):
        clean["websites"] = [str(w).strip() for w in websites_raw if str(w).strip()]
    elif isinstance(websites_raw, str):
        # Could be comma or newline separated
        delims = [",", "\n", ";"]
        found_delim = ","
        for d in delims:
            if d in websites_raw:
                found_delim = d
                break
        clean["websites"] = [w.strip() for w in websites_raw.split(found_delim) if w.strip()]
    else:
        clean["websites"] = ["realtor.ca", "zillow.com", "redfin.com", "zolo.ca"]

    clean["time_horizon"] = str(find_val(time_keys, "Past 3 Months")).strip()

    return clean

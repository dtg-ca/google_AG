import json
import csv
import io
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class PropertyRequest:
    country: str = "United States"
    state_province: str = ""
    city: str = ""
    street: str = ""
    postal_code: str = ""
    property_type: str = "1-Bedroom Apartment"
    bedrooms: float = 1.0
    bathrooms: float = 1.0
    approx_sqft: Optional[int] = None
    furnished: str = "Unfurnished"  # Unfurnished, Furnished, Partial
    parking: str = "Street / None"
    pet_friendly: bool = False
    utilities_included: bool = False
    amenities: List[str] = field(default_factory=list)
    raw_text: str = ""

    @property
    def full_address(self) -> str:
        parts = []
        if self.street:
            parts.append(self.street)
        if self.city:
            parts.append(self.city)
        if self.state_province:
            parts.append(self.state_province)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else "Unknown Address"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "state_province": self.state_province,
            "city": self.city,
            "street": self.street,
            "postal_code": self.postal_code,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "approx_sqft": self.approx_sqft,
            "furnished": self.furnished,
            "parking": self.parking,
            "pet_friendly": self.pet_friendly,
            "utilities_included": self.utilities_included,
            "amenities": self.amenities,
            "full_address": self.full_address
        }


def parse_json_input(text_content: str) -> PropertyRequest:
    """Parse JSON string into PropertyRequest object with case-insensitive key lookup."""
    raw_data = json.loads(text_content)
    # Normalize keys to lower-case without special characters
    data = {}
    for k, v in raw_data.items():
        if isinstance(k, str):
            clean_k = re.sub(r'[^a-z0-9]', '', k.lower())
            data[clean_k] = v

    country = data.get("country", "United States")
    state_province = data.get("stateprovince") or data.get("provincestate") or data.get("state") or data.get("province") or ""
    city = data.get("city", "")
    street = data.get("street") or data.get("address", "")
    postal_code = data.get("postalcode") or data.get("zip") or data.get("zipcode") or ""
    property_type = data.get("propertyroomtype") or data.get("propertytype") or data.get("roomtype") or "1-Bedroom Apartment"

    try:
        bedrooms = float(data.get("bedrooms", 1.0))
    except (ValueError, TypeError):
        bedrooms = 1.0

    try:
        bathrooms = float(data.get("bathrooms", 1.0))
    except (ValueError, TypeError):
        bathrooms = 1.0

    approx_sqft = data.get("approxsqft") or data.get("sqft")
    if approx_sqft is not None:
        try:
            approx_sqft = int(approx_sqft)
        except (ValueError, TypeError):
            approx_sqft = None

    return PropertyRequest(
        country=str(country).strip(),
        state_province=str(state_province).strip(),
        city=str(city).strip(),
        street=str(street).strip(),
        postal_code=str(postal_code).strip(),
        property_type=str(property_type).strip(),
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        approx_sqft=approx_sqft,
        furnished=str(data.get("furnished", "Unfurnished")),
        parking=str(data.get("parking", "Street / None")),
        pet_friendly=bool(data.get("petfriendly", False)),
        utilities_included=bool(data.get("utilitiesincluded", False)),
        amenities=data.get("amenities", []),
        raw_text=text_content
    )


def parse_csv_input(text_content: str) -> PropertyRequest:
    """Parse CSV text into PropertyRequest (reads first data row)."""
    f = io.StringIO(text_content.strip())
    reader = csv.DictReader(f)
    for row in reader:
        # Standardize keys
        lower_keys = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        country = lower_keys.get("country", "United States")
        state_province = lower_keys.get("province/state") or lower_keys.get("province") or lower_keys.get("state") or ""
        city = lower_keys.get("city", "")
        street = lower_keys.get("street") or lower_keys.get("address", "")
        postal_code = lower_keys.get("postal code") or lower_keys.get("postal_code") or lower_keys.get("zip", "")
        prop_type = lower_keys.get("property/room type") or lower_keys.get("property_type") or lower_keys.get("room type", "1-Bedroom Apartment")
        
        bed_str = lower_keys.get("bedrooms", "1")
        try:
            bedrooms = float(re.findall(r"[\d.]+", bed_str)[0]) if re.findall(r"[\d.]+", bed_str) else 1.0
        except Exception:
            bedrooms = 1.0

        bath_str = lower_keys.get("bathrooms", "1")
        try:
            bathrooms = float(re.findall(r"[\d.]+", bath_str)[0]) if re.findall(r"[\d.]+", bath_str) else 1.0
        except Exception:
            bathrooms = 1.0

        return PropertyRequest(
            country=country,
            state_province=state_province,
            city=city,
            street=street,
            postal_code=postal_code,
            property_type=prop_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            raw_text=text_content
        )
    return PropertyRequest(raw_text=text_content)


def parse_freeform_text(text: str) -> PropertyRequest:
    """
    Intelligently extracts Country, Province/State, City, Street, Postal Code,
    and Property/Room Type from unstructured user text.
    """
    req = PropertyRequest(raw_text=text)

    # 1. Detect Country
    country_patterns = [
        (r"\b(Canada|CA)\b", "Canada"),
        (r"\b(United States|USA|US|America)\b", "United States"),
        (r"\b(United Kingdom|UK|Great Britain|England|Scotland|Wales)\b", "United Kingdom"),
        (r"\b(Australia|AU|NSW|VIC|QLD)\b", "Australia"),
        (r"\b(Germany|DE)\b", "Germany"),
        (r"\b(France|FR)\b", "France"),
    ]
    for pattern, name in country_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            req.country = name
            break

    # 2. Postal Code detection
    # Canadian postal code: A1A 1A1
    can_match = re.search(r"\b([A-CEGHJ-NPR-TVXY]\d[A-CEGHJ-NPR-TV-Z][ -]?\d[A-CEGHJ-NPR-TV-Z]\d)\b", text, re.IGNORECASE)
    # US zip code: 12345 or 12345-6789
    us_match = re.search(r"\b(\d{5}(?:-\d{4})?)\b", text)
    # UK postcode: e.g. SW1A 1AA, EC1A 1BB
    uk_match = re.search(r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b", text, re.IGNORECASE)

    if req.country == "Canada" and can_match:
        req.postal_code = can_match.group(1).upper()
    elif req.country == "United Kingdom" and uk_match:
        req.postal_code = uk_match.group(1).upper()
    elif us_match:
        req.postal_code = us_match.group(1)
    elif can_match:
        req.postal_code = can_match.group(1).upper()
        req.country = "Canada"
    elif uk_match:
        req.postal_code = uk_match.group(1).upper()
        req.country = "United Kingdom"

    # 3. Property / Room Type detection
    prop_type_map = [
        (r"(studio|bachelor)", "Studio / Bachelor", 0.0),
        (r"(1[- ]?bed|one[- ]?bed|1[- ]?br|1[- ]?bedroom)", "1-Bedroom Apartment", 1.0),
        (r"(2[- ]?bed|two[- ]?bed|2[- ]?br|2[- ]?bedroom)", "2-Bedroom Apartment", 2.0),
        (r"(3[- ]?bed|three[- ]?bed|3[- ]?br|3[- ]?bedroom)", "3-Bedroom Apartment/House", 3.0),
        (r"(4[- ]?bed|four[- ]?bed|4[- ]?br|4[- ]?bedroom)", "4-Bedroom House", 4.0),
        (r"(private room|room in shared|single room|shared flat)", "Private Room in Shared House", 1.0),
        (r"(basement suite|basement apartment|in-law suite)", "Basement Apartment", 1.0),
        (r"(condo|condominium)", "Condominium Apartment", 1.0),
        (r"(townhouse|townhome)", "Townhouse", 3.0),
        (r"(single[- ]?family|detached house|house)", "Single Family House", 3.0)
    ]
    for pattern, prop_name, beds in prop_type_map:
        if re.search(pattern, text, re.IGNORECASE):
            req.property_type = prop_name
            req.bedrooms = beds
            break

    # 4. Check for Bathrooms
    bath_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:bath|bathroom|ba)\b", text, re.IGNORECASE)
    if bath_match:
        try:
            req.bathrooms = float(bath_match.group(1))
        except ValueError:
            pass

    # 5. Extract Address Lines or Key-Value pairs if present
    # Check for labeled inputs like "Address: ...", "City: ...", "State: ...", "Province: ..."
    field_patterns = {
        "street": r"(?:street|address|st\.?):\s*([^\n,]+)",
        "city": r"(?:city|town):\s*([^\n,]+)",
        "state_province": r"(?:state|province|state/province|prov):\s*([^\n,]+)",
        "postal_code": r"(?:postal code|zip|zip code|postal):\s*([^\n,]+)",
        "country": r"(?:country):\s*([^\n,]+)",
        "property_type": r"(?:property type|room type|property/room type|type):\s*([^\n,]+)",
    }
    for field_name, pat in field_patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            setattr(req, field_name, val)

    # If street / city / province not yet set via labeled fields, attempt common line-based or comma-based parsing
    if not req.city or not req.street:
        # Common address pattern: "123 Main St, Austin, TX 78701"
        addr_match = re.search(
            r"(\d+[\w\s\.-]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln|Court|Ct|Circle|Cir|Terrace|Ter|Parkway|Pkwy)?)[,\n]\s*([A-Za-z\s]+)[,\n]\s*([A-Za-z\s]{2,20})\s*(\d{5}(?:-\d{4})?|[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d)?",
            text, re.IGNORECASE
        )
        if addr_match:
            if not req.street:
                req.street = addr_match.group(1).strip()
            if not req.city:
                req.city = addr_match.group(2).strip()
            if not req.state_province:
                req.state_province = addr_match.group(3).strip()
            if addr_match.group(4) and not req.postal_code:
                req.postal_code = addr_match.group(4).strip()

    # Fallback default values if still empty
    if not req.city:
        # Look for well-known cities
        major_cities = [
            ("Toronto", "ON", "Canada"),
            ("Vancouver", "BC", "Canada"),
            ("Montreal", "QC", "Canada"),
            ("Calgary", "AB", "Canada"),
            ("Ottawa", "ON", "Canada"),
            ("New York", "NY", "United States"),
            ("San Francisco", "CA", "United States"),
            ("Los Angeles", "CA", "United States"),
            ("Chicago", "IL", "United States"),
            ("Austin", "TX", "United States"),
            ("Seattle", "WA", "United States"),
            ("Miami", "FL", "United States"),
            ("Boston", "MA", "United States"),
            ("London", "Greater London", "United Kingdom"),
            ("Manchester", "Greater Manchester", "United Kingdom"),
            ("Sydney", "NSW", "Australia"),
            ("Melbourne", "VIC", "Australia")
        ]
        for c, s, ctry in major_cities:
            if re.search(rf"\b{c}\b", text, re.IGNORECASE):
                req.city = c
                if not req.state_province:
                    req.state_province = s
                if not req.country or req.country == "United States":
                    req.country = ctry
                break

    # Amenities detection
    if re.search(r"furnished\b", text, re.IGNORECASE) and not re.search(r"unfurnished", text, re.IGNORECASE):
        req.furnished = "Furnished"
    if re.search(r"(pet[ -]?friendly|dogs? allowed|cats? allowed)", text, re.IGNORECASE):
        req.pet_friendly = True
    if re.search(r"(utilities included|all inclusive|bills included)", text, re.IGNORECASE):
        req.utilities_included = True
    if re.search(r"(parking|garage|driveway)", text, re.IGNORECASE):
        req.parking = "Dedicated / Included"

    return req


def parse_file(uploaded_file) -> PropertyRequest:
    """Dispatch uploaded file based on its filename extension."""
    filename = uploaded_file.name.lower()
    content = uploaded_file.getvalue().decode("utf-8", errors="replace")

    if filename.endswith(".json"):
        try:
            return parse_json_input(content)
        except Exception:
            return parse_freeform_text(content)
    elif filename.endswith(".csv"):
        try:
            return parse_csv_input(content)
        except Exception:
            return parse_freeform_text(content)
    else:
        # Plain text, markdown, or unstructured
        return parse_freeform_text(content)

"""
Configuration and constants for Real Estate Market Predictor.
"""

# Default target websites to search for real estate listings and market data
DEFAULT_WEBSITES = [
    "realtor.ca",
    "zillow.com",
    "redfin.com",
    "zolo.ca",
    "housesigma.com",
    "realtor.com",
    "homes.com",
    "trulia.com"
]

PROPERTY_TYPES = [
    "Single Family Detached",
    "Semi-Detached",
    "Townhouse",
    "Condominium Apartment",
    "Duplex / Multi-Family",
    "Luxury Estate",
    "Bungalow",
    "Mobile / Manufactured"
]

PROPERTY_CONDITIONS = [
    "Newly Built / Turnkey Luxury",
    "Excellent (Fully Renovated)",
    "Good (Well Maintained)",
    "Fair (Cosmetic Updates Needed)",
    "Fixer-Upper (Major Renovation Required)"
]

TIME_HORIZONS = [
    "Past 3 Months",
    "Past 6 Months"
]

# Market benchmarks per square foot and base DOM metrics for common metro areas
METRO_BENCHMARKS = {
    "toronto": {"currency": "CAD", "base_sqft": 820, "base_dom": 22, "sale_to_list": 0.99, "market_health": "Balanced Market"},
    "vancouver": {"currency": "CAD", "base_sqft": 1050, "base_dom": 26, "sale_to_list": 0.98, "market_health": "Balanced to Buyer's"},
    "montreal": {"currency": "CAD", "base_sqft": 520, "base_dom": 38, "sale_to_list": 0.98, "market_health": "Balanced Market"},
    "calgary": {"currency": "CAD", "base_sqft": 390, "base_dom": 24, "sale_to_list": 1.01, "market_health": "Seller's Market"},
    "ottawa": {"currency": "CAD", "base_sqft": 450, "base_dom": 30, "sale_to_list": 0.98, "market_health": "Balanced Market"},
    "austin": {"currency": "USD", "base_sqft": 340, "base_dom": 38, "sale_to_list": 0.96, "market_health": "Buyer's Market"},
    "seattle": {"currency": "USD", "base_sqft": 610, "base_dom": 19, "sale_to_list": 1.02, "market_health": "Seller's Market"},
    "san francisco": {"currency": "USD", "base_sqft": 920, "base_dom": 25, "sale_to_list": 1.02, "market_health": "Balanced Market"},
    "los angeles": {"currency": "USD", "base_sqft": 750, "base_dom": 32, "sale_to_list": 0.99, "market_health": "Balanced Market"},
    "new york": {"currency": "USD", "base_sqft": 880, "base_dom": 48, "sale_to_list": 0.97, "market_health": "Balanced Market"},
    "miami": {"currency": "USD", "base_sqft": 580, "base_dom": 44, "sale_to_list": 0.95, "market_health": "Buyer's Market"},
    "chicago": {"currency": "USD", "base_sqft": 280, "base_dom": 33, "sale_to_list": 0.98, "market_health": "Balanced Market"},
    "dallas": {"currency": "USD", "base_sqft": 240, "base_dom": 35, "sale_to_list": 0.97, "market_health": "Balanced Market"},
    "default_us": {"currency": "USD", "base_sqft": 320, "base_dom": 32, "sale_to_list": 0.98, "market_health": "Balanced Market"},
    "default_ca": {"currency": "CAD", "base_sqft": 550, "base_dom": 28, "sale_to_list": 0.98, "market_health": "Balanced Market"}
}

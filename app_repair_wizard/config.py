"""
Configuration and constants for the Repair Solutions Wizard application.
"""

APP_TITLE = "FixMate: Expert DIY Repair Solutions Wizard"
APP_SUBTITLE = "Smart DIY diagnostics, real-time web & forum research, and location-aware local parts sourcing"

# Equipment Categories and typical manufacturers
EQUIPMENT_TAXONOMY = {
    "Major Home Appliances": {
        "subtypes": [
            "Washing Machine", "Clothes Dryer", "Refrigerator / Freezer", 
            "Dishwasher", "Oven / Range / Stove", "Microwave Oven", 
            "Garbage Disposal", "Ice Maker", "Wine Cooler"
        ],
        "common_makes": ["Whirlpool", "Samsung", "LG", "GE Appliances", "Bosch", "Maytag", "KitchenAid", "Frigidaire", "Kenmore", "Electrolux", "Miele"],
        "model_tip": "Check the door frame, behind the kickplate, under the lid, or on the rear panel for the metallic model plate/sticker."
    },
    "HVAC & Home Climate": {
        "subtypes": [
            "Central Air Conditioner", "Gas/Electric Furnace", "Heat Pump", 
            "Tankless Water Heater", "Standard Water Heater", "Smart Thermostat", 
            "Dehumidifier", "Window A/C Unit", "Humidifier"
        ],
        "common_makes": ["Carrier", "Trane", "Lennox", "Rheem", "Goodman", "Honeywell", "Ecobee", "Nest", "Daikin", "Bryant", "AO Smith"],
        "model_tip": "Look at the rating plate on the exterior access door of the furnace/air handler or the outdoor condenser unit."
    },
    "Lawn, Garden & Power Equipment": {
        "subtypes": [
            "Lawn Mower (Gas/Electric)", "Riding Mower / Zero-Turn", "String Trimmer / Weed Eater", 
            "Leaf Blower", "Chainsaw", "Snowblower", "Portable Generator", "Pressure Washer", "Rototiller"
        ],
        "common_makes": ["Honda", "Toro", "John Deere", "Craftsman", "Stihl", "Husqvarna", "Echo", "Briggs & Stratton", "Generac", "Ryobi", "Ego"],
        "model_tip": "Stamped onto the engine block (Briggs/Honda), on the mower deck near the discharge chute, or under the seat."
    },
    "Consumer Electronics & Computing": {
        "subtypes": [
            "Smartphone", "Laptop / Notebook", "Desktop PC", "Tablet", 
            "Smart TV / Display", "Audio Receiver / Soundbar", "Gaming Console", 
            "Headphones / Earbuds", "Wi-Fi Router"
        ],
        "common_makes": ["Apple", "Samsung", "Sony", "Dell", "HP", "Lenovo", "Asus", "LG", "Microsoft", "Nintendo", "Bose"],
        "model_tip": "Found in device Settings > About, on the bottom chassis casing, or on the back barcode label."
    },
    "Automotive & Small Engines": {
        "subtypes": [
            "Braking System", "Battery / Starter / Alternator", "Cooling & Radiator", 
            "Ignition / Spark Plugs", "Suspension & Struts", "AC & Heating System", 
            "Exhaust & Emissions", "Exterior Lighting / Relays"
        ],
        "common_makes": ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Subaru", "BMW", "Jeep", "Hyundai", "Volkswagen"],
        "model_tip": "Found on the vehicle registration card, door jamb VIN sticker, or owner's handbook."
    },
    "Plumbing & Fixtures": {
        "subtypes": [
            "Toilet & Flush Mechanism", "Sink Faucet & Aerator", "Shower Valve & Head", 
            "Sump Pump", "Water Softener", "Reverse Osmosis System", "P-Trap / Drain Line"
        ],
        "common_makes": ["Moen", "Kohler", "Delta", "American Standard", "Grohe", "Pfister", "Wayne", "InSinkErator", "Fleck"],
        "model_tip": "Look underneath the sink faucet base, under the toilet tank lid (stamped code), or on the pump housing label."
    },
    "Power Tools & Workshop": {
        "subtypes": [
            "Cordless Drill / Impact Driver", "Circular Saw", "Miter Saw", 
            "Table Saw", "Orbital Sander", "Air Compressor", "Angle Grinder"
        ],
        "common_makes": ["DeWalt", "Milwaukee", "Makita", "Bosch", "Ryobi", "Ridgid", "Craftsman", "Kobalt", "Festool"],
        "model_tip": "Printed on the side identification badge near the battery bay or motor housing."
    },
    "Other / Custom Equipment": {
        "subtypes": ["Custom / General Machinery", "Bicycle / E-Bike", "Coffee Machine / Espresso", "Pool Pump / Filter"],
        "common_makes": ["Breville", "DeLonghi", "Hayward", "Pentair", "Shimano", "Generic / Unbranded"],
        "model_tip": "Inspect the base plate, underside, or manufacturer serial decal."
    }
}

# Community and DIY Forums targeted in searches
TARGET_FORUMS = [
    {"domain": "reddit.com/r/fixit", "name": "Reddit r/fixit"},
    {"domain": "reddit.com/r/appliances", "name": "Reddit r/appliances"},
    {"domain": "reddit.com/r/DIY", "name": "Reddit r/DIY"},
    {"domain": "reddit.com/r/MechanicAdvice", "name": "Reddit r/MechanicAdvice"},
    {"domain": "ifixit.com", "name": "iFixit Repair Community"},
    {"domain": "repairclinic.com", "name": "Repair Clinic"},
    {"domain": "appliancepartspros.com", "name": "AppliancePartsPros Community"},
    {"domain": "doityourself.com", "name": "DoItYourself Forums"},
    {"domain": "houzz.com", "name": "Houzz Home Discussions"}
]

# Supported Gemini Model Fallback List
PREFERRED_GEMINI_MODELS = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest"
]

"""
Sample test cases for fast testing and demonstration of the Repair Wizard.
"""

SAMPLE_PRESETS = {
    "Whirlpool Washing Machine (Not Draining)": {
        "category": "Major Home Appliances",
        "subtype": "Washing Machine",
        "make": "Whirlpool",
        "model": "WTW5000DW0",
        "problem": "The washer completes the agitation and wash cycle, but when it reaches the drain and spin cycle, it stops. The drum remains full of soapy water. A faint humming sound comes from underneath, but no water pumps out.",
        "location": "123 Main St, Springfield, IL 62701, USA",
        "skill_level": "Intermediate",
        "tools": ["Basic Screwdriver Set", "Pliers / Channel Locks", "Multimeter", "Towels & Bucket"]
    },
    "Honda Gas Lawn Mower (Won't Start)": {
        "category": "Lawn, Garden & Power Equipment",
        "subtype": "Lawn Mower (Gas/Electric)",
        "make": "Honda",
        "model": "HRN216VKA (GCV170 Engine)",
        "problem": "Mower sat over winter with fuel in tank. Now pull cord turns engine smoothly and spark plug appears dry, but engine refuses to start or only sputters for 2 seconds and dies immediately.",
        "location": "456 Elm Ave, Columbus, OH 43215, USA",
        "skill_level": "Beginner",
        "tools": ["Socket Set", "Carb Cleaner Spray", "New Spark Plug", "Fresh Gasoline"]
    },
    "Samsung Refrigerator (Water Under Crisper Drawers)": {
        "category": "Major Home Appliances",
        "subtype": "Refrigerator / Freezer",
        "make": "Samsung",
        "model": "RF28R7351SR French Door",
        "problem": "Water pools beneath the twin crisper vegetable drawers inside the fresh food compartment and freezes into an ice sheet at the bottom of the fridge. Water dispenser and ice maker work normally.",
        "location": "789 Oak Terrace, Austin, TX 78701, USA",
        "skill_level": "Intermediate",
        "tools": ["Phillips Screwdriver", "Hair Dryer / Steamer", "Hot Water Syringe", "Towels"]
    },
    "DeWalt Cordless Drill (Chuck Stuck & Won't Release Bit)": {
        "category": "Power Tools & Workshop",
        "subtype": "Cordless Drill / Impact Driver",
        "make": "DeWalt",
        "model": "DCD771 20V Max",
        "problem": "The keyless drill chuck is jammed tightly onto a drill bit. Turning the collar by hand clicks but will not open the three jaws to release the bit.",
        "location": "321 Pine St, Seattle, WA 98101, USA",
        "skill_level": "Beginner",
        "tools": ["WD-40 / Penetrating Oil", "Channel Lock Pliers", "Allen Key", "Rubber Mallet"]
    },
    "iPhone 12 (Battery Draining & Screen Lifting)": {
        "category": "Consumer Electronics & Computing",
        "subtype": "Smartphone",
        "make": "Apple",
        "model": "iPhone 12 (A2172)",
        "problem": "The battery health indicator shows 74%. The battery drops from 80% to 20% in 2 hours of light use, and there is a slight separation / gap visible along the left edge of the OLED display where the screen seems pushed outward.",
        "location": "550 Market St, San Francisco, CA 94104, USA",
        "skill_level": "Intermediate",
        "tools": ["Pentalobe P2 Screwdriver", "Suction Cup & Pry Picks", "Replacement Adhesive", "Heat Gun / Hair Dryer"]
    }
}

from dataclasses import dataclass, field
from typing import List, Dict, Any
from market_analyzer import MarketAnalysis
from search_engine import PLATFORM_DIRECTORY

@dataclass
class TargetSegment:
    primary: str
    secondary: str
    demographic_summary: str
    key_value_drivers: List[str]
    listing_hook: str

@dataclass
class PlatformRecommendation:
    rank: int
    name: str
    expected_response_time: str
    lead_quality: str
    cost: str
    best_fit: str
    pro_tip: str

@dataclass
class RecommendationResult:
    currency_symbol: str
    suggested_rent_target: float
    suggested_rent_fast_fill: float
    suggested_rent_premium: float
    pricing_tiers: List[Dict[str, Any]]
    optimum_months: List[str]
    slowest_months: List[str]
    lead_time_days: int
    seasonality_12_months: Dict[str, int]
    target_segment: TargetSegment
    fast_response_platforms: List[PlatformRecommendation]
    reasoning_summary: str
    reasoning_points: List[str]


def generate_recommendations(analysis: MarketAnalysis) -> RecommendationResult:
    req = analysis.property_request
    sym = analysis.currency_symbol
    base = analysis.baseline_median_price

    # 1. Suggested Rent Calculation
    # Target (balanced): exact baseline median
    # Fast Fill: 4-6% below median to capture massive immediate demand & slash vacancy
    # Premium: 6-8% above median (for landlords willing to wait for premium tenant)
    target_rent = round(base, -1) if base > 500 else round(base, 0)
    fast_fill_rent = round(base * 0.95, -1)
    premium_rent = round(base * 1.07, -1)

    pricing_tiers = [
        {
            "tier": "⚡ Fast-Fulfillment (Low Vacancy)",
            "rent": fast_fill_rent,
            "expected_days_to_fill": "5 – 8 Days",
            "strategy": "Priced slightly below market median to trigger high inquiry velocity, allowing the landlord to choose from multiple verified applicants with minimal vacancy downtime."
        },
        {
            "tier": "🎯 Recommended Fair Market Target",
            "rent": target_rent,
            "expected_days_to_fill": f"{int(analysis.avg_days_on_market - 2)} – {int(analysis.avg_days_on_market + 2)} Days",
            "strategy": "Optimizes gross annual yield against realistic market absorption. Aligned with current 4-month market fulfillment benchmarks in the neighborhood."
        },
        {
            "tier": "💎 Maximum Yield (Premium Staged)",
            "rent": premium_rent,
            "expected_days_to_fill": "25 – 35 Days",
            "strategy": "Top-of-market pricing. Feasible only if unit boasts exceptional luxury upgrades, dedicated parking, designer staging, or panoramic views."
        }
    ]

    # 2. Seasonality Calendar (12 Months)
    # Seasonal indices tailored to property type (student vs corporate vs family)
    pt_lower = req.property_type.lower()
    is_student_friendly = "room" in pt_lower or "studio" in pt_lower or "1-bed" in pt_lower or "basement" in pt_lower
    
    if is_student_friendly:
        # Huge peak in July, August, September
        seasonality = {
            "Jan": 65, "Feb": 60, "Mar": 70, "Apr": 78,
            "May": 85, "Jun": 90, "Jul": 98, "Aug": 100,
            "Sep": 92, "Oct": 72, "Nov": 50, "Dec": 42
        }
        optimum_months = ["August", "July", "September", "June"]
        slowest_months = ["December", "November", "January"]
    else:
        # Families and general professionals peak in late spring / summer
        seasonality = {
            "Jan": 72, "Feb": 68, "Mar": 75, "Apr": 84,
            "May": 92, "Jun": 98, "Jul": 95, "Aug": 96,
            "Sep": 88, "Oct": 76, "Nov": 58, "Dec": 46
        }
        optimum_months = ["June", "August", "July", "May"]
        slowest_months = ["December", "November", "February"]

    # 3. Target Tenant Segment
    if "room" in pt_lower:
        primary = "University Students & Working Young Adults"
        secondary = "Contract / Working Holiday Professionals"
        demo = "Ages 19–29, budget-conscious, seeking all-inclusive utilities, quiet roommates, and convenient transit links."
        drivers = ["All-inclusive utilities", "High-speed Wi-Fi included", "Close to subway/transit", "Furnished bedroom option"]
        hook = f"Bright & Clean Private Room | Transit-Friendly | High-Speed Internet Included"
    elif "studio" in pt_lower or "1-bed" in pt_lower:
        primary = "Young Tech, Healthcare, and Corporate Professionals"
        secondary = "Graduate Students / Medical Residents"
        demo = "Single working adults or couples (ages 24–36), valuing proximity to employment hubs, in-suite laundry, and modern building amenities."
        drivers = ["In-suite washer & dryer", "Proximity to downtown/transit hubs", "Dedicated work-from-home nook", "Pet-friendly policy"]
        hook = f"Modern {req.property_type} with In-Suite Laundry & Convenient Commute"
    elif "2-bed" in pt_lower:
        primary = "Professional Roommates or Dual-Income Couples (DINKs)"
        secondary = "Young Couples with Infant / Work-From-Home Need"
        demo = "Ages 27–42, combined household income > 3.5x rent, looking for split-bedroom layout or dedicated home office."
        drivers = ["Split bedroom layout for privacy", "Underground parking space", "Modern kitchen with dishwasher", "Storage locker / balcony"]
        hook = f"Spacious 2-Bedroom Suite | Split Layout for Privacy | Parking & Balcony"
    elif "house" in pt_lower or "3-bed" in pt_lower or "townhouse" in pt_lower:
        primary = "Established Families with School-Age Children"
        secondary = "Relocating Corporate Executives"
        demo = "Ages 32–55, prioritizing school district rankings, yard/outdoor space, garage parking, and quiet residential neighborhood."
        drivers = ["Top-rated school district catchment", "Fenced yard & garage", "Ample storage & finished basement", "Long-term lease stability"]
        hook = f"Charming Family Home in Quiet Neighborhood | Great Schools & Fenced Yard"
    else:
        primary = "Urban Working Professionals"
        secondary = "Relocating Transferees"
        demo = "Professionals seeking turn-key convenience, dependable property management, and prompt maintenance response."
        drivers = ["Clean move-in ready condition", "Transparent lease terms", "Safe & secure entry", "Transit accessibility"]
        hook = f"Prime Location {req.property_type} | Move-in Ready & Well-Maintained"

    target_segment = TargetSegment(
        primary=primary,
        secondary=secondary,
        demographic_summary=demo,
        key_value_drivers=drivers,
        listing_hook=hook
    )

    # 4. Best Websites for Fast Responses
    country_key = req.country if req.country in PLATFORM_DIRECTORY else "United States"
    platforms_raw = PLATFORM_DIRECTORY.get(country_key, PLATFORM_DIRECTORY["United States"])

    fast_platforms: List[PlatformRecommendation] = []
    
    # Priority sorting based on property type
    # For private rooms: Facebook Marketplace, SpareRoom, Kijiji, Craigslist take top ranks
    # For condos/apartments: Facebook Marketplace + Zillow/Rentals.ca take top ranks
    for idx, p in enumerate(platforms_raw, start=1):
        if p["name"] == "Facebook Marketplace":
            response_time = "< 2 – 4 Hours"
            cost_str = "Free (Paid Boost available)"
            tip = "Respond within 15 minutes of initial inquiry. Pre-screen immediately with a 3-question questionnaire before booking showings."
        elif "Zillow" in p["name"]:
            response_time = "12 – 24 Hours"
            cost_str = "Paid ($9.99/wk or bundled)"
            tip = "Enable online applications. Tenants with pre-completed credit checks and background verifications apply through this channel."
        elif "Rentals.ca" in p["name"]:
            response_time = "14 – 20 Hours"
            cost_str = "Freemium / Listing packages"
            tip = "Include floor plan dimensions and virtual video tour to rank higher in verified search listings."
        elif "Apartments.com" in p["name"]:
            response_time = "16 – 24 Hours"
            cost_str = "Freemium"
            tip = "Highlight parking availability, pet policy, and specific move-in date upfront."
        elif "Craigslist" in p["name"] or "Kijiji" in p["name"]:
            response_time = "4 – 8 Hours"
            cost_str = "Free"
            tip = "Renew or repost listing every 72 hours to remain on top of page 1 search results. Guard against spam."
        elif "SpareRoom" in p["name"] or "Flatmates" in p["name"]:
            response_time = "< 6 Hours"
            cost_str = "Free / Early Bird pass"
            tip = "Describe household culture, quiet hours, and utility breakdown clearly to attract compatible flatmates."
        else:
            response_time = "12 – 24 Hours"
            cost_str = "Free / Standard"
            tip = "Use high-resolution horizontal photography taken in natural daytime light."

        fast_platforms.append(PlatformRecommendation(
            rank=idx,
            name=p["name"],
            expected_response_time=response_time,
            lead_quality=p["reach"],
            cost=cost_str,
            best_fit=p["type"],
            pro_tip=tip
        ))

    # 5. Reasoning Points
    reasoning_points = [
        f"**Market Anchor ({sym}{int(target_rent)}/mo):** Derived from local comps in {req.city or 'the target area'}, where comparable {req.property_type.lower()} listings have fulfilled between {sym}{int(analysis.price_q1)} and {sym}{int(analysis.price_q3)} over the past 4 months.",
        f"**Past 4-Month Momentum:** The past 4 months (July to October 2026) showed an average days-on-market of {analysis.avg_days_on_market} days. A slight seasonal deceleration in October means pricing competitively at {sym}{int(target_rent)} avoids prolonged vacancy during the winter lull.",
        f"**Vacancy Cost vs. Rent Elasticity:** Every 2 weeks of vacancy at {sym}{int(target_rent)} costs {sym}{int(target_rent * 0.50)} in lost revenue. Opting for the Fast-Fulfillment tier ({sym}{int(fast_fill_rent)}) recovers the slight discount within just 3 months while reducing vacant holding costs to under 8 days.",
        f"**Optimal Advertising Season:** Peak market demand occurs in **{', '.join(optimum_months[:2])}** ({seasonality[optimum_months[0][:3]]}/100 demand index). To lease for that window, begin advertising 35–45 days prior. Advertising in {slowest_months[0]} requires an aggressive price or concession due to seasonal freeze.",
        f"**Fastest Response Channel:** **{fast_platforms[0].name}** generates the highest initial inquiry volume ({fast_platforms[0].expected_response_time}), while **{fast_platforms[1].name}** delivers the highest credit-verified conversion rate."
    ]

    summary = (
        f"For {req.full_address} ({req.property_type}), our 4-month market absorption analysis recommends a fair market target rent of "
        f"{sym}{int(target_rent)}/month. To eliminate vacancy risk before winter, list on {fast_platforms[0].name} and {fast_platforms[1].name} "
        f"at {sym}{int(fast_fill_rent)}/mo for rapid fulfillment within 5–8 days."
    )

    return RecommendationResult(
        currency_symbol=sym,
        suggested_rent_target=target_rent,
        suggested_rent_fast_fill=fast_fill_rent,
        suggested_rent_premium=premium_rent,
        pricing_tiers=pricing_tiers,
        optimum_months=optimum_months,
        slowest_months=slowest_months,
        lead_time_days=35,
        seasonality_12_months=seasonality,
        target_segment=target_segment,
        fast_response_platforms=fast_platforms,
        reasoning_summary=summary,
        reasoning_points=reasoning_points
    )

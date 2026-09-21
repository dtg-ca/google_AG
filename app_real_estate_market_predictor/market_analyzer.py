"""
Market Health Analyzer module.
Evaluates market temperature, absorption rate, price trends,
and comparative cohort statistics for similar properties over the past 3 to 6 months.
"""

import math
from typing import Dict, List, Any


class MarketHealthAnalyzer:
    """
    Analyzes real estate market health for properties similar to the target property.
    """

    def analyze_health(
        self,
        property_info: Dict[str, Any],
        search_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates market health metrics, comparable statistics, and cohort trends.
        """
        comps = search_data.get("comparables", [])
        market_stats = search_data.get("market_stats", {})
        prop_type = property_info.get("property_type", "Residential")
        target_sqft = property_info.get("sqft", 2000)

        # 1. Filter and process similar comps
        similar_comps = [c for c in comps if c.get("property_type") == prop_type]
        if not similar_comps:
            similar_comps = comps

        # Extract values
        prices = [c["sold_price"] for c in similar_comps if c.get("sold_price", 0) > 0]
        dom_list = [c["days_on_market"] for c in similar_comps if c.get("days_on_market", 0) > 0]
        sqft_rates = [c["price_per_sqft"] for c in similar_comps if c.get("price_per_sqft", 0) > 0]

        if not prices:
            prices = [1000000]
        if not dom_list:
            dom_list = [24]
        if not sqft_rates:
            sqft_rates = [market_stats.get("benchmark_sqft_price", 550)]

        # Cohort statistics
        median_price = int(sorted(prices)[len(prices) // 2])
        avg_price = int(sum(prices) / len(prices))
        min_price = min(prices)
        max_price = max(prices)

        median_dom = int(sorted(dom_list)[len(dom_list) // 2])
        avg_dom = round(sum(dom_list) / len(dom_list), 1)
        min_dom = min(dom_list)
        max_dom = max(dom_list)

        median_sqft_rate = round(sorted(sqft_rates)[len(sqft_rates) // 2], 2)
        avg_sqft_rate = round(sum(sqft_rates) / len(sqft_rates), 2)

        # 2. Market health classification
        moi = market_stats.get("months_of_inventory", 3.5)
        sale_to_list = market_stats.get("sale_to_list_ratio", 0.99)
        raw_health_score = market_stats.get("health_score", 70)

        # Refined Health Score Calculation (0 - 100)
        # Low MOI (< 2.5) -> High seller score; High MOI (> 5.5) -> Low seller score
        moi_factor = max(10, min(100, int(100 - (moi - 1.5) * 16)))
        dom_factor = max(10, min(100, int(100 - (median_dom - 10) * 2)))
        ratio_factor = max(10, min(100, int((sale_to_list - 0.90) * 500)))

        composite_health_score = int(0.4 * moi_factor + 0.35 * dom_factor + 0.25 * ratio_factor)
        composite_health_score = max(20, min(95, composite_health_score))

        if composite_health_score >= 75:
            market_state = "Seller's Market"
            market_color = "#10B981"  # Emerald green
            market_summary = (
                f"Strong seller advantage characterized by tight inventory ({moi} months) "
                f"and rapid turnover (median {median_dom} DOM). Sellers maintain strong pricing power, "
                f"and properties frequently command {round(sale_to_list * 100, 1)}% of list price."
            )
            liquidity_rating = "High Velocity / High Demand"
        elif composite_health_score >= 55:
            market_state = "Balanced Market"
            market_color = "#3B82F6"  # Royal blue
            market_summary = (
                f"Stable equilibrium between buyers and sellers with {moi} months of supply. "
                f"Homes sell in approximately {median_dom} days at roughly {round(sale_to_list * 100, 1)}% "
                f"of ask. Accurate market-aligned pricing is required to avoid extended days on market."
            )
            liquidity_rating = "Steady / Standard Velocity"
        else:
            market_state = "Buyer's Market"
            market_color = "#F59E0B"  # Amber
            market_summary = (
                f"Buyer-favorable market with elevated inventory ({moi} months) and prolonged "
                f"absorption times (median {median_dom} DOM). Buyers have negotiating room, with sales "
                f"averaging {round(sale_to_list * 100, 1)}% of list price."
            )
            liquidity_rating = "Low Velocity / Price Sensitive"

        currency = market_stats.get("currency", "USD")

        return {
            "health_score": composite_health_score,
            "market_state": market_state,
            "market_color": market_color,
            "market_summary": market_summary,
            "liquidity_rating": liquidity_rating,
            "months_of_inventory": moi,
            "sale_to_list_ratio": sale_to_list,
            "neighborhood_median_dom": median_dom,
            "cohort_stats": {
                "sample_size": len(similar_comps),
                "median_price": median_price,
                "avg_price": avg_price,
                "min_price": min_price,
                "max_price": max_price,
                "median_dom": median_dom,
                "avg_dom": avg_dom,
                "min_dom": min_dom,
                "max_dom": max_dom,
                "median_sqft_rate": median_sqft_rate,
                "avg_sqft_rate": avg_sqft_rate,
                "currency": currency
            },
            "price_trend_3mo": market_stats.get("price_trend_3mo", "+1.2% past 3 months"),
            "target_cohort": prop_type
        }

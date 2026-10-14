"""
Research engine for gathering online repair guides, forum discussions, local parts suppliers,
and nearest professional outside repair centers based on user's postal address.
Uses DuckDuckGo (ddgs) with multi-backend fallbacks to fetch real-world solutions and community wisdom.
"""

import re
import urllib.parse
from typing import List, Dict, Any
from ddgs import DDGS

class ResearchEngine:
    """Orchestrates multi-query web and discussion forum research for DIY repairs and outside service."""

    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def _clean_text(self, text: str) -> str:
        """Strips excessive whitespace and unwanted markup."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _safe_search(self, query: str, max_results: int = 4) -> List[Dict[str, Any]]:
        """Executes search with backend fallbacks (auto -> html -> lite)."""
        backends = ["auto", "html", "lite"]
        for b in backends:
            try:
                with DDGS(timeout=self.timeout) as ddgs:
                    raw = list(ddgs.text(query, backend=b, max_results=max_results))
                    if raw:
                        return raw
            except Exception:
                continue
        return []

    def search_repair_guides(self, make: str, model: str, category: str, problem: str, max_results: int = 4) -> List[Dict[str, Any]]:
        """Search reputable technical repair sites, manuals, and troubleshooting databases."""
        short_prob = " ".join(problem.split()[:6])
        query = f"{make} {model} {short_prob} DIY fix troubleshooting"
        raw_results = self._safe_search(query, max_results=max_results)
        
        # Broader query if no results
        if not raw_results:
            raw_results = self._safe_search(f"{make} {short_prob} repair guide", max_results=max_results)

        results = []
        for item in raw_results:
            title = self._clean_text(item.get("title", ""))
            link = item.get("href", "")
            body = self._clean_text(item.get("body", ""))
            if title and link:
                results.append({
                    "type": "Technical Guide",
                    "title": title,
                    "url": link,
                    "snippet": body,
                    "source": self._extract_domain(link)
                })
        return results

    def search_forum_discussions(self, make: str, model: str, problem: str, max_results: int = 4) -> List[Dict[str, Any]]:
        """Search community discussion forums (Reddit r/fixit, iFixit, DoItYourself)."""
        short_prob = " ".join(problem.split()[:6])
        
        # First attempt: Reddit and iFixit
        query = f"site:reddit.com/r/fixit OR site:reddit.com/r/appliances {make} {model} {short_prob}"
        raw_results = self._safe_search(query, max_results=max_results)

        # Second attempt: broader community forum search
        if not raw_results:
            query = f"{make} {short_prob} forum solved fix"
            raw_results = self._safe_search(query, max_results=max_results)

        results = []
        for item in raw_results:
            title = self._clean_text(item.get("title", ""))
            link = item.get("href", "")
            body = self._clean_text(item.get("body", ""))
            if title and link:
                source_label = "Reddit" if "reddit.com" in link else ("iFixit" if "ifixit.com" in link else self._extract_domain(link))
                results.append({
                    "type": "Community Forum",
                    "title": title,
                    "url": link,
                    "snippet": body,
                    "source": source_label
                })
        return results

    def search_local_parts_suppliers(self, category: str, location_str: str, make: str = "", max_results: int = 4) -> List[Dict[str, Any]]:
        """Search local hardware stores, parts supply warehouses, and authorized retailers based on address/zip."""
        if not location_str or len(location_str.strip()) < 3:
            return []

        clean_loc = location_str.strip()
        cat_lower = category.lower()

        if "appliance" in cat_lower:
            search_terms = "appliance parts store supply"
            category_tag = "Appliance Parts"
        elif "automotive" in cat_lower or "engine" in cat_lower:
            search_terms = "auto parts supply store AutoZone OReilly"
            category_tag = "Auto Parts"
        elif "hvac" in cat_lower or "climate" in cat_lower:
            search_terms = "HVAC supply house heating cooling parts"
            category_tag = "HVAC Supply"
        elif "lawn" in cat_lower or "garden" in cat_lower:
            search_terms = "lawn mower small engine parts dealer hardware"
            category_tag = "Power Equipment Dealer"
        elif "electronic" in cat_lower or "comput" in cat_lower:
            search_terms = "electronics parts computer repair components"
            category_tag = "Electronics & Tech"
        elif "plumb" in cat_lower:
            search_terms = "plumbing supply house wholesale parts"
            category_tag = "Plumbing Supply"
        else:
            search_terms = "hardware store parts tools Home Depot Ace"
            category_tag = "Hardware & Tools"

        query = f"{search_terms} {clean_loc}"
        raw_results = self._safe_search(query, max_results=max_results)

        results = []
        for item in raw_results:
            title = self._clean_text(item.get("title", ""))
            link = item.get("href", "")
            body = self._clean_text(item.get("body", ""))
            if title and link:
                results.append({
                    "type": f"Local {category_tag}",
                    "title": title,
                    "url": link,
                    "snippet": body,
                    "source": self._extract_domain(link)
                })
        return results

    def search_professional_repair_shops(self, category: str, location_str: str, make: str = "", max_results: int = 4) -> List[Dict[str, Any]]:
        """Search professional repair centers, technicians, and mechanics near user's location."""
        if not location_str or len(location_str.strip()) < 3:
            return []

        clean_loc = location_str.strip()
        cat_lower = category.lower()

        if "appliance" in cat_lower:
            kw = f"{make} appliance repair service company" if make else "appliance repair service technicians"
        elif "automotive" in cat_lower or "engine" in cat_lower:
            kw = "auto repair shop certified mechanic service"
        elif "hvac" in cat_lower or "climate" in cat_lower:
            kw = "HVAC heating and cooling repair company technician"
        elif "lawn" in cat_lower or "garden" in cat_lower:
            kw = "lawn mower small engine repair service shop"
        elif "electronic" in cat_lower or "comput" in cat_lower:
            kw = "electronics phone computer repair shop service"
        elif "plumb" in cat_lower:
            kw = "licensed plumber plumbing repair service"
        else:
            kw = "equipment repair service center professional"

        query = f"{kw} {clean_loc}"
        raw_results = self._safe_search(query, max_results=max_results)

        results = []
        for item in raw_results:
            title = self._clean_text(item.get("title", ""))
            link = item.get("href", "")
            body = self._clean_text(item.get("body", ""))
            if title and link:
                results.append({
                    "type": "Professional Repair Center",
                    "title": title,
                    "url": link,
                    "snippet": body,
                    "source": self._extract_domain(link)
                })
        return results

    def search_video_tutorials(self, make: str, model: str, problem: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search video teardown and repair walkthroughs (YouTube)."""
        short_prob = " ".join(problem.split()[:5])
        query = f"site:youtube.com {make} {model} {short_prob} repair replace"
        raw_results = self._safe_search(query, max_results=max_results)

        results = []
        for item in raw_results:
            title = self._clean_text(item.get("title", ""))
            link = item.get("href", "")
            body = self._clean_text(item.get("body", ""))
            if title and link and "youtube.com" in link:
                results.append({
                    "type": "Video Walkthrough",
                    "title": title,
                    "url": link,
                    "snippet": body,
                    "source": "YouTube"
                })
        return results

    def build_location_links(self, category: str, location_str: str) -> Dict[str, str]:
        """Build instant interactive mapping and sourcing URLs for the postal address."""
        if not location_str:
            return {}

        cat_lower = category.lower()
        if "appliance" in cat_lower:
            store_kw = "appliance parts store"
            pro_kw = "appliance repair service"
        elif "auto" in cat_lower:
            store_kw = "auto parts store"
            pro_kw = "auto repair mechanic"
        elif "hvac" in cat_lower:
            store_kw = "HVAC supply"
            pro_kw = "HVAC repair contractor"
        elif "lawn" in cat_lower:
            store_kw = "lawn mower parts"
            pro_kw = "small engine repair"
        elif "plumb" in cat_lower:
            store_kw = "plumbing supply"
            pro_kw = "plumbing contractor"
        else:
            store_kw = "hardware store"
            pro_kw = "repair service"

        encoded_loc = urllib.parse.quote_plus(location_str)
        encoded_store_query = urllib.parse.quote_plus(f"{store_kw} near {location_str}")
        encoded_pro_query = urllib.parse.quote_plus(f"{pro_kw} near {location_str}")
        
        return {
            "google_maps": f"https://www.google.com/maps/search/{encoded_store_query}",
            "google_maps_pros": f"https://www.google.com/maps/search/{encoded_pro_query}",
            "yelp": f"https://www.yelp.com/search?find_desc={urllib.parse.quote_plus(store_kw)}&find_loc={encoded_loc}",
            "yelp_pros": f"https://www.yelp.com/search?find_desc={urllib.parse.quote_plus(pro_kw)}&find_loc={encoded_loc}",
            "home_depot": f"https://www.homedepot.com/l/search/{encoded_loc}",
            "repairclinic": "https://www.repairclinic.com/",
            "appliancepartspros": "https://www.appliancepartspros.com/",
            "ifixit": "https://www.ifixit.com/Guide"
        }

    def _extract_domain(self, url: str) -> str:
        """Extract user-friendly clean domain name from URL."""
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return "Web Link"

    def aggregate_research(self, category: str, make: str, model: str, problem: str, location: str) -> Dict[str, Any]:
        """Runs parallel or coordinated searches across guides, forums, videos, local parts, and pro repair centers."""
        guides = self.search_repair_guides(make, model, category, problem, max_results=4)
        forums = self.search_forum_discussions(make, model, problem, max_results=4)
        videos = self.search_video_tutorials(make, model, problem, max_results=3)
        local_parts = self.search_local_parts_suppliers(category, location, make, max_results=4)
        pro_shops = self.search_professional_repair_shops(category, location, make, max_results=4)
        location_links = self.build_location_links(category, location)

        # Combined unique list for references
        all_sources = []
        seen_urls = set()

        for group in [guides, forums, videos, local_parts, pro_shops]:
            for item in group:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_sources.append(item)

        return {
            "guides": guides,
            "forums": forums,
            "videos": videos,
            "local_parts": local_parts,
            "pro_shops": pro_shops,
            "location_links": location_links,
            "all_sources": all_sources
        }

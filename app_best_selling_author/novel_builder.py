"""
novel_builder.py
Hierarchical Sliding-Window Chapter-by-Chapter Novel Generation Engine.
Enables cost-effective, high-continuity drafting of full-length books (10-28+ chapters)
by maintaining a static Story Bible, a rolling continuity memory buffer, and micro-beat prompts.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

DEFAULT_CHAPTER_BEATS = [
    {
        "num": 1,
        "act": "Act I",
        "title": "The Broken Ordinary World",
        "beat": "Introduce protagonist in their element, expose internal wound, plant atmospheric tension and initial hook.",
        "micro_beats": [
            "Hook & Objective: Protagonist demonstrates elite skill under daily strain.",
            "Obstacle & Escalation: A subtle anomaly hints that their reality is fractured.",
            "Micro-Cliffhanger: A cryptic warning or discovery leaves turning back impossible."
        ]
    },
    {
        "num": 2,
        "act": "Act I",
        "title": "The Inciting Intrusion",
        "beat": "The catalyst event disrupts the status quo, forcing the protagonist to face an unavoidable dilemma.",
        "micro_beats": [
            "Hook & Objective: Protagonist investigates the disturbance, seeking a return to normalcy.",
            "Obstacle & Escalation: An antagonistic force or systemic block cuts off safe retreat.",
            "Micro-Cliffhanger: High-stakes confrontation forces an immediate defensive reaction."
        ]
    },
    {
        "num": 3,
        "act": "Act I",
        "title": "The Debate & Hesitation",
        "beat": "Protagonist attempts to resist or rationalize away the problem; stakes escalate until refusal is impossible.",
        "micro_beats": [
            "Hook & Objective: Protagonist seeks counsel or looks for an escape hatch.",
            "Obstacle & Escalation: Collateral consequences endanger someone or something they cherish.",
            "Micro-Cliffhanger: The cost of inaction is shown to be lethal or catastrophic."
        ]
    },
    {
        "num": 4,
        "act": "Act I",
        "title": "Crossing the Threshold",
        "beat": "Protagonist makes an active, irreversible choice to step into unfamiliar and dangerous territory.",
        "micro_beats": [
            "Hook & Objective: Protagonist prepares gear/strategy to breach the perimeter.",
            "Obstacle & Escalation: Point-of-no-return security or environmental hurdle.",
            "Micro-Cliffhanger: The door locks behind them; the new reality begins."
        ]
    },
    {
        "num": 5,
        "act": "Act II-A",
        "title": "The New Rules & First Friction",
        "beat": "Exploring the new world/circumstances; first encounter with opposing forces and conflicting rules.",
        "micro_beats": [
            "Hook & Objective: Navigating hostile or unfamiliar social/physical terrain.",
            "Obstacle & Escalation: A misstep attracts immediate punitive attention.",
            "Micro-Cliffhanger: Narrow evasion leaves protagonist exposed and compromised."
        ]
    },
    {
        "num": 6,
        "act": "Act II-A",
        "title": "The Core Alliance (B-Story)",
        "beat": "Crucial relationship or foil introduced/deepened; ideological friction masking emerging vulnerability.",
        "micro_beats": [
            "Hook & Objective: Protagonist seeks critical asset or information from the ally/rival.",
            "Obstacle & Escalation: Clashing motives trigger sharp verbal or tactical combat.",
            "Micro-Cliffhanger: Reluctant truce established when a shared threat appears."
        ]
    },
    {
        "num": 7,
        "act": "Act II-A",
        "title": "The Trial of Competency",
        "beat": "Protagonist executes a tactical plan; shows high skill but reveals their tragic blind spot.",
        "micro_beats": [
            "Hook & Objective: Execution of an intricate infiltration, negotiation, or investigation.",
            "Obstacle & Escalation: An unforeseen variable threatens operational security.",
            "Micro-Cliffhanger: Short-term victory reveals a much larger covert trap."
        ]
    },
    {
        "num": 8,
        "act": "Act II-A",
        "title": "The Midpoint Paradigm Shift",
        "beat": "Major revelation or false victory that fundamentally changes the nature of the conflict. Stakes double.",
        "micro_beats": [
            "Hook & Objective: Protagonist believes they have cornered the adversary.",
            "Obstacle & Escalation: Staggering revelation turns hunter into hunted.",
            "Micro-Cliffhanger: The true antagonist or hidden agenda steps into the light."
        ]
    },
    {
        "num": 9,
        "act": "Act II-B",
        "title": "The Reversal & Tightening Net",
        "beat": "The antagonist/opposition reacts with devastating precision; allies scatter or question the mission.",
        "micro_beats": [
            "Hook & Objective: Scrambling to regroup after the midpoint shockwave.",
            "Obstacle & Escalation: Communication lines severed and safehouses burned.",
            "Micro-Cliffhanger: An ally goes dark or an insurmountable deadline is imposed."
        ]
    },
    {
        "num": 10,
        "act": "Act II-B",
        "title": "The Fracture of Trust",
        "beat": "A concealed secret comes to light; personal betrayal threatens the core partnership.",
        "micro_beats": [
            "Hook & Objective: Confronting inconsistent clues or deceptive behavior.",
            "Obstacle & Escalation: The hidden betrayal is brought into the open.",
            "Micro-Cliffhanger: The alliance fractures at the exact moment unity is required."
        ]
    },
    {
        "num": 11,
        "act": "Act II-B",
        "title": "All Hope Lost (Dark Night)",
        "beat": "Total defeat. The primary plan is shattered, someone is lost, and the protagonist feels entirely isolated.",
        "micro_beats": [
            "Hook & Objective: Last-ditch effort to prevent catastrophic loss fails.",
            "Obstacle & Escalation: Protagonist loses their most crucial weapon, status, or mentor.",
            "Micro-Cliffhanger: Rock bottom silence where quitting appears to be the only option."
        ]
    },
    {
        "num": 12,
        "act": "Act III",
        "title": "The Resurrected Truth",
        "beat": "In the ashes of despair, the protagonist discovers a hidden insight by overcoming their internal flaw.",
        "micro_beats": [
            "Hook & Objective: Quiet moment of reckoning; examining what was overlooked.",
            "Obstacle & Escalation: Overcoming internal shame or traumatic memory.",
            "Micro-Cliffhanger: An epiphany reveals the sole vulnerability in the enemy's armor."
        ]
    },
    {
        "num": 13,
        "act": "Act III",
        "title": "The Desperate Gambit",
        "beat": "Rallying the remnants for an audacious, high-risk counter-offensive where failure means ruin.",
        "micro_beats": [
            "Hook & Objective: Re-assembling surviving allies with a daring, unexpected strategy.",
            "Obstacle & Escalation: Enemy defenses are fortified tenfold.",
            "Micro-Cliffhanger: Initiation of the endgame sequence with zero margin for error."
        ]
    },
    {
        "num": 14,
        "act": "Act III",
        "title": "The Crucible Climax",
        "beat": "Direct confrontation with the central antagonist/obstacle. The ultimate test of will and sacrifice.",
        "micro_beats": [
            "Hook & Objective: Breaching the adversary's stronghold; physical and intellectual duel.",
            "Obstacle & Escalation: The primary strategy fails, demanding an agonizing sacrifice.",
            "Micro-Cliffhanger: Decisive maneuver determines survival or complete annihilation."
        ]
    },
    {
        "num": 15,
        "act": "Act III",
        "title": "The Transformed Horizon",
        "beat": "The aftermath of the victory/cost. Return to a changed world with a resonant, indelible closing image.",
        "micro_beats": [
            "Hook & Objective: Surveying the emotional and physical battlefield in the quiet aftermath.",
            "Obstacle & Escalation: Acknowledging the permanent scars and irrevocable changes.",
            "Micro-Cliffhanger: A resonant, indelible final scene that lingers in the reader's mind."
        ]
    }
]

def extract_chapter1_from_blueprint(blueprint_text: str) -> str:
    """Extracts Chapter 1 manuscript prose from a generated novel blueprint."""
    if not blueprint_text or not blueprint_text.strip():
        return ""
    
    # Priority patterns for Chapter 1 manuscript prose start (supporting en-dash, em-dash, hyphens, and dividers)
    patterns = [
        r'(?i)(?:^|\n)\s*(?:---\s*\n\s*)?#+\s*(?:PART\s+(?:II|2)[\s:—\-\u2013|]+)?(?:POLISHED\s+MANUSCRIPT[\s:—\-\u2013|]+)?(?:MANUSCRIPT[\s:—\-\u2013|]+)?CHAPTER\s+1\b[^\n]*',
        r'(?i)(?:^|\n)\s*(?:---\s*\n\s*)?#+\s*PART\s+(?:II|2)[\s:—\-\u2013|]+[^\n]*',
        r'(?i)(?:^|\n)\s*(?:---\s*\n\s*)?#+\s*POLISHED\s+MANUSCRIPT[\s:—\-\u2013|]+[^\n]*',
        r'(?i)(?:^|\n)\s*---\s*\n\s*#+\s*CHAPTER\s+1\b[^\n]*'
    ]
    for p in patterns:
        m = re.search(p, blueprint_text)
        if m:
            return blueprint_text[m.start():].strip()
            
    return ""

def extract_outline_from_blueprint(blueprint_text: str) -> str:
    """Extracts the outline section from a novel proposal or blueprint."""
    if not blueprint_text or not blueprint_text.strip():
        return ""
        
    # Search for outline header
    outline_start = re.search(
        r'(?i)(?:^|\n)\s*(?:#+\s*)?(?:\d+\.\s*)?(?:MASTER\s+)?(?:BEAT-BY-BEAT\s+)?(?:3-ACT\s+)?(?:CHAPTER\s+)?OUTLINE\b[^\n]*',
        blueprint_text
    )
    if not outline_start:
        outline_start = re.search(r'(?i)(?:^|\n)\s*(?:#+\s*)?(?:\d+\.\s*)?BEAT\s+SHEET\b[^\n]*', blueprint_text)

    if outline_start:
        start_idx = outline_start.start()
        # Find next major division marking start of actual manuscript prose (Part II / Polished Manuscript)
        # Avoid matching 'Chapter 1' if it is part of the outline itself!
        end_match = re.search(
            r'(?i)(?:^|\n)\s*(?:---\s*\n\s*)?#+\s*(?:PART\s+(?:II|2)\b|POLISHED\s+MANUSCRIPT\b|COMPLETE\s+MANUSCRIPT\b|FULL\s+MANUSCRIPT\b|MANUSCRIPT\b)',
            blueprint_text[start_idx:]
        )
        if not end_match:
            # Fallback: look for a top-level divider followed by Chapter 1 heading
            end_match = re.search(
                r'(?i)(?:^|\n)\s*---\s*\n\s*#+\s*(?:CHAPTER\s+1\b)',
                blueprint_text[start_idx:]
            )
        if end_match and end_match.start() > 10:
            return blueprint_text[start_idx:start_idx + end_match.start()].strip()
        return blueprint_text[start_idx:].strip()

    return ""

def parse_outline_into_beats(outline_text: str, target_chapter_count: int = 15) -> List[Dict[str, Any]]:
    """
    Parses raw outline text or markdown into structured chapter beats with micro-beats.
    Accurately handles explicit chapter headings, multi-line beat descriptions,
    numbered lists, sub-bullets, and act breakdowns without dropping user outline content.
    """
    if not outline_text or not outline_text.strip():
        step = len(DEFAULT_CHAPTER_BEATS) / max(1, target_chapter_count)
        return [dict(DEFAULT_CHAPTER_BEATS[min(len(DEFAULT_CHAPTER_BEATS) - 1, int(i * step))]) for i in range(target_chapter_count)]

    lines = [line.strip() for line in outline_text.split("\n") if line.strip()]
    parsed_chapters: List[Dict[str, Any]] = []
    current_act = "Act I"
    curr_ch: Optional[Dict[str, Any]] = None

    # Pattern for explicit chapter lines
    # Matches: "Chapter 1: Title", "Ch 1 - Title", "**Chapter 1: Title**", "1. Title", "### Chapter 1: Title"
    ch_pattern = re.compile(
        r'^(?:[-*•#>\s]*)(?:(?:Chapter|Ch\.?)\s*(\d+|[IVXLCDM]+)|\b(\d+)\.)\s*(?:[:\-—\u2013|]|\*\*)?\s*(.*?)$',
        re.IGNORECASE
    )
    # Pattern for act headings
    act_pattern = re.compile(r'^(?:[-*•#>\s]*)(?:###?\s*)?(Act\s+(?:I{1,3}|IV|V|[1-3](?:-[AB])?))\b', re.IGNORECASE)

    for line in lines:
        lower_line = line.lower()
        # Skip section headings like "## 4. Master Chapter Outline" unless it has explicit chapter number
        is_outline_header = not re.search(r'\b(?:chapter|ch\.)\s*(?:\d+|[ivxlcdm]+)', lower_line) and any(
            term in lower_line for term in ["outline", "beat sheet", "table of contents", "proposal", "blueprint"]
        )
        if is_outline_header:
            continue

        act_m = act_pattern.search(line)
        if act_m:
            act_str = act_m.group(1).upper()
            if "1" in act_str or "I" in act_str:
                current_act = "Act I"
            elif "2-B" in act_str or "II-B" in act_str:
                current_act = "Act II-B"
            elif "2" in act_str or "II" in act_str:
                current_act = "Act II-A"
            elif "3" in act_str or "III" in act_str:
                current_act = "Act III"
            continue

        ch_m = ch_pattern.match(line)
        if ch_m:
            if curr_ch:
                parsed_chapters.append(curr_ch)
                curr_ch = None

            raw_num = ch_m.group(1) or ch_m.group(2)
            try:
                ch_num = int(raw_num)
            except (ValueError, TypeError):
                roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15}
                ch_num = roman_map.get(str(raw_num).upper(), len(parsed_chapters) + 1)

            rest = ch_m.group(3).strip().strip("*_`#:")

            split_parts = re.split(r'\s+[-—\u2013|]\s*|[:|]\s*', rest, maxsplit=1)
            if len(split_parts) == 2 and split_parts[1].strip():
                title = split_parts[0].strip().strip("*_`#:")
                beat_desc = split_parts[1].strip().strip("*_`#:")
            else:
                title = rest.strip().strip("*_`#:") if rest else f"Chapter {ch_num}"
                beat_desc = ""

            if not title:
                title = f"Chapter {ch_num}"

            curr_ch = {
                "num": ch_num,
                "act": current_act,
                "title": title,
                "beat": beat_desc,
                "micro_beats": []
            }
        elif curr_ch is not None:
            # Continuation line or micro-beat of current chapter
            clean_l = line.strip().strip("*_`#")
            if clean_l.startswith(("-", "•", "*")) or any(k in clean_l.lower() for k in ["hook:", "objective:", "obstacle:", "cliffhanger:", "scene"]):
                sub = re.sub(r'^[-*•\s]+', '', clean_l).strip()
                curr_ch["micro_beats"].append(sub)
            else:
                if curr_ch["beat"]:
                    curr_ch["beat"] += " " + clean_l
                else:
                    curr_ch["beat"] = clean_l

    if curr_ch:
        parsed_chapters.append(curr_ch)

    # Fallback to bullet items if explicit chapters were fewer than 2
    if len(parsed_chapters) < 2:
        bullet_lines = [l for l in lines if l.startswith(("-", "*", "•")) or re.match(r'^\d+\.', l)]
        if len(bullet_lines) >= 2:
            parsed_chapters = []
            for i, bl in enumerate(bullet_lines, start=1):
                clean_l = re.sub(r'^[-*•\d\.\s]+', '', bl).strip()
                split_parts = re.split(r'\s+[-—\u2013|]\s*|[:|]\s*', clean_l, maxsplit=1)
                title = split_parts[0].strip().strip("*_`#:") if len(split_parts) > 1 else f"Beat {i}"
                beat_desc = split_parts[1].strip().strip("*_`#:") if len(split_parts) > 1 else clean_l

                prog = i / len(bullet_lines)
                act = "Act I" if prog <= 0.25 else ("Act II-A" if prog <= 0.5 else ("Act II-B" if prog <= 0.75 else "Act III"))

                parsed_chapters.append({
                    "num": i,
                    "act": act,
                    "title": title,
                    "beat": beat_desc,
                    "micro_beats": []
                })

    # If completely empty, fall back to DEFAULT_CHAPTER_BEATS
    if not parsed_chapters:
        step = len(DEFAULT_CHAPTER_BEATS) / max(1, target_chapter_count)
        parsed_chapters = [dict(DEFAULT_CHAPTER_BEATS[min(len(DEFAULT_CHAPTER_BEATS) - 1, int(i * step))]) for i in range(target_chapter_count)]

    # Final normalization of numbering, default beats, micro-beats, and acts
    for idx, c in enumerate(parsed_chapters, start=1):
        c["num"] = idx
        title = c.get("title", f"Chapter {idx}")
        if not c.get("beat", "").strip():
            c["beat"] = f"Key narrative development and character turning point in {title}."

        if not c.get("micro_beats"):
            c["micro_beats"] = [
                f"Hook & Objective: Protagonist confronts immediate problem in {title}.",
                f"Obstacle & Escalation: Complication arises: {c['beat'][:110]}.",
                f"Micro-Cliffhanger: High-stakes revelation forces immediate defensive action."
            ]

        if c.get("act", "Act I") == "Act I" and idx > 1:
            prog = idx / len(parsed_chapters)
            c["act"] = "Act I" if prog <= 0.25 else ("Act II-A" if prog <= 0.5 else ("Act II-B" if prog <= 0.75 else "Act III"))

    return parsed_chapters

def sync_outline_into_project(
    book_project: Dict[str, Any],
    outline_text: str,
    target_chapter_count: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Synchronizes an edited outline into the book project's chapters,
    preserving existing drafted chapter prose and status while updating titles,
    act mappings, beat descriptions, and micro-beats from the given outline.
    """
    if not outline_text or not outline_text.strip():
        return book_project.get("chapters", [])

    existing_chapters = book_project.get("chapters", [])
    count = target_chapter_count or len(existing_chapters) or 15
    new_beats = parse_outline_into_beats(outline_text.strip(), count)

    updated_chapters = []
    for i, b in enumerate(new_beats, start=1):
        existing = next((c for c in existing_chapters if c["number"] == i), None)
        content = existing.get("content", "") if existing else ""
        summary = existing.get("summary", "") if existing else ""
        status = existing.get("status", "Pending") if (existing and content.strip()) else "Pending"
        word_count = existing.get("word_count", 0) if existing else 0

        updated_chapters.append({
            "number": i,
            "act": b.get("act", "Act I"),
            "title": b.get("title", f"Chapter {i}"),
            "beat_description": b.get("beat", ""),
            "micro_beats": b.get("micro_beats", []),
            "status": status,
            "content": content,
            "summary": summary,
            "word_count": word_count
        })

    book_project["chapters"] = updated_chapters
    book_project["total_chapters"] = len(updated_chapters)
    book_project["outline"] = outline_text.strip()
    if not book_project.get("characters"):
        book_project["characters"] = extract_characters_from_project_or_blueprint(
            blueprint_text=outline_text,
            storyline=book_project.get("storyline", ""),
            genre=book_project.get("genre", "Commercial Fiction")
        )
    return updated_chapters

def extract_characters_from_project_or_blueprint(
    blueprint_text: str = "",
    storyline: str = "",
    genre: str = "Commercial Fiction"
) -> Dict[str, Dict[str, str]]:
    """
    Extracts or establishes consistent, vivid named characters (Protagonist, Antagonist, Ally)
    so every chapter features real people with names, dialogue, and physical agency.
    """
    protagonist = {"name": "", "role": ""}
    antagonist = {"name": "", "role": ""}
    supporting = {"name": "", "role": ""}

    if blueprint_text:
        m_prot = re.search(r'(?i)(?:[-*•#>\s]*)(?:Protagonist\b[^\n:]*[:—\-]\s*)([^\n]+)', blueprint_text)
        if m_prot:
            raw = m_prot.group(1).strip().strip("*_`#")
            parts = re.split(r'[\(\-—:]', raw, maxsplit=1)
            name = parts[0].strip().strip("*_`#")
            role = parts[1].replace(')', '').strip().strip("*_`#") if len(parts) > 1 else "Protagonist"
            if 1 < len(name.split()) <= 4 and name.lower() not in ["core desire", "the ghost", "fatal flaw", "autonomy"]:
                protagonist["name"] = name
                protagonist["role"] = role

        m_ant = re.search(r'(?i)(?:[-*•#>\s]*)(?:Antagonist\b[^\n:]*[:—\-]\s*)([^\n]+)', blueprint_text)
        if m_ant:
            raw = m_ant.group(1).strip().strip("*_`#")
            parts = re.split(r'[\(\-—:]', raw, maxsplit=1)
            name = parts[0].strip().strip("*_`#")
            role = parts[1].replace(')', '').strip().strip("*_`#") if len(parts) > 1 else "Primary Adversary"
            if 1 < len(name.split()) <= 4 and name.lower() not in ["motivation", "friction", "pragmatic"]:
                antagonist["name"] = name
                antagonist["role"] = role

        m_sup = re.search(r'(?i)(?:[-*•#>\s]*)(?:(?:Supporting|Catalyst|Ally)\b[^\n:]*[:—\-]\s*)([^\n]+)', blueprint_text)
        if m_sup:
            raw = m_sup.group(1).strip().strip("*_`#")
            parts = re.split(r'[\(\-—:]', raw, maxsplit=1)
            name = parts[0].strip().strip("*_`#")
            role = parts[1].replace(')', '').strip().strip("*_`#") if len(parts) > 1 else "Key Ally"
            if 1 < len(name.split()) <= 4 and name.lower() not in ["role", "relationship"]:
                supporting["name"] = name
                supporting["role"] = role

    g_lower = genre.lower()
    s_lower = storyline.lower()

    if not protagonist["name"]:
        if "sci-fi" in g_lower or "dystopian" in g_lower or "mars" in s_lower or "space" in s_lower:
            protagonist = {"name": "Dr. Sarah Hayes", "role": "Chief Life-Support Systems Engineer"}
            antagonist = {"name": "Director Ronald Vance", "role": "Colony Governor & Corporate Enforcer"}
            supporting = {"name": "Kaelen Chen", "role": "Senior Diagnostics Specialist"}
        elif "thriller" in g_lower or "mystery" in g_lower or "suspense" in g_lower or "detective" in s_lower:
            protagonist = {"name": "Detective Jack Mercer", "role": "Veteran Homicide & Fraud Investigator"}
            antagonist = {"name": "Julian Drake", "role": "High-Stakes Syndicate Fixer"}
            supporting = {"name": "Elena Vance", "role": "Forensic Intelligence Specialist"}
        elif "romance" in g_lower or "women" in g_lower:
            protagonist = {"name": "Maya Bennett", "role": "Independent Creative Director"}
            antagonist = {"name": "Liam Montgomery", "role": "Rival Firm Partner & Unyielding Foil"}
            supporting = {"name": "Chloe Rivera", "role": "Loyal Confidante & Publicist"}
        elif "fantasy" in g_lower or "paranormal" in g_lower:
            protagonist = {"name": "Caelen Ward", "role": "Exiled Boundary Scout"}
            antagonist = {"name": "Lord Malakor", "role": "High Chancellor of the Citadel"}
            supporting = {"name": "Lyra Thorne", "role": "Keeper of Ancient Lore"}
        elif "historical" in g_lower:
            protagonist = {"name": "Thomas Sterling", "role": "Resolute Frontier Navigator"}
            antagonist = {"name": "Magistrate Henry Blackwood", "role": "Imperial Enforcer"}
            supporting = {"name": "Constance Lee", "role": "Underground Network Courier"}
        else:
            protagonist = {"name": "Alex Mercer", "role": "Determined Lead Strategist"}
            antagonist = {"name": "Victor Cross", "role": "Ruthless Faction Leader"}
            supporting = {"name": "Elena Scott", "role": "Trusted Field Partner"}

    if not antagonist["name"]:
        antagonist = {"name": "Victor Cross", "role": "Ruthless Opponent"}
    if not supporting["name"]:
        supporting = {"name": "Elena Scott", "role": "Trusted Ally"}

    return {
        "protagonist": protagonist,
        "antagonist": antagonist,
        "supporting": supporting
    }

def initialize_book_structure(
    title: str,
    storyline: str,
    genre: str,
    ingredients: Optional[Dict[str, Any]] = None,
    chapter_count: int = 15,
    custom_ch1_content: str = "",
    outline_text: str = ""
) -> Dict[str, Any]:
    """Initializes a new multi-chapter book project structure mapped to story acts, characters, and parsed outline."""
    clean_title = title.replace("#", "").strip() or "Untitled Commercial Novel"
    ingredients = ingredients or {}

    characters = extract_characters_from_project_or_blueprint(
        blueprint_text=outline_text,
        storyline=storyline,
        genre=genre
    )

    # 1. Select beats from given outline if available, else standard acts
    if outline_text and outline_text.strip():
        selected_beats = parse_outline_into_beats(outline_text, chapter_count)
    else:
        if chapter_count <= 15:
            step = len(DEFAULT_CHAPTER_BEATS) / max(1, chapter_count)
            selected_beats = [dict(DEFAULT_CHAPTER_BEATS[min(len(DEFAULT_CHAPTER_BEATS) - 1, int(i * step))]) for i in range(chapter_count)]
        else:
            selected_beats = [dict(b) for b in DEFAULT_CHAPTER_BEATS]
            extra_needed = chapter_count - len(selected_beats)
            for idx in range(extra_needed):
                insert_pos = 9 + (idx % 3)
                selected_beats.insert(insert_pos, {
                    "num": len(selected_beats) + 1,
                    "act": "Act II-B",
                    "title": f"Escalating Complications Part {idx + 1}",
                    "beat": "Deepening psychological pressure, unexpected obstacle, and ticking clock countdown.",
                    "micro_beats": [
                        "Hook & Objective: Pushing through mounting exhaustion to secure a critical lead.",
                        "Obstacle & Escalation: Antagonist retaliates with ruthless counter-measures.",
                        "Micro-Cliffhanger: Time runs critically short as an emergency alert triggers."
                    ]
                })

    chapters = []
    for i, b in enumerate(selected_beats, start=1):
        is_ch1 = (i == 1 and bool(custom_ch1_content.strip()))
        content = custom_ch1_content.strip() if is_ch1 else ""
        summary = (
            f"In Chapter 1 ({b.get('title', 'Introduction')}), {characters['protagonist']['name']} confronts the initial dilemma and the inciting tension is established."
            if is_ch1 else ""
        )
        chapters.append({
            "number": i,
            "act": b.get("act", "Act I"),
            "title": b.get("title", f"Chapter {i}"),
            "beat_description": b.get("beat", ""),
            "micro_beats": b.get("micro_beats", []),
            "status": "Drafted" if is_ch1 else "Pending",
            "content": content,
            "summary": summary,
            "word_count": len(content.split()) if content else 0
        })

    return {
        "title": clean_title,
        "storyline": storyline,
        "genre": genre,
        "ingredients": ingredients,
        "outline": outline_text,
        "characters": characters,
        "total_chapters": len(chapters),
        "chapters": chapters,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

FALLBACK_GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview"
]

def generate_dynamic_offline_prose(
    book_project: Dict[str, Any],
    chapter_number: int,
    audience: str = "Adult Commercial",
    pov: str = "Third Person Limited",
    pacing: str = "Commercial Page-Turner"
) -> Dict[str, str]:
    """
    Synthesizes rich, page-turning, dialogue-heavy chapter prose and rolling continuity summary
    honoring the given outline, micro-beats, named characters, and previous chapter buffer
    when operating in offline demo mode or when API calls are unavailable.
    """
    chapters = book_project.get("chapters", [])
    current_ch = next((c for c in chapters if c["number"] == chapter_number), None)
    if not current_ch:
        raise ValueError(f"Chapter {chapter_number} not found.")

    prev_ch = next((c for c in chapters if c["number"] == chapter_number - 1), None)
    prev_summary = prev_ch.get("summary", "") if prev_ch else ""
    prev_content = prev_ch.get("content", "") if prev_ch else ""
    prev_words = prev_content.split()
    prev_ending_anchor = " ".join(prev_words[-60:]) if prev_words else ""

    title = book_project.get("title", "Untitled Novel")
    genre = book_project.get("genre", "Commercial Fiction")
    storyline = book_project.get("storyline", "A high-stakes commercial story.")
    ch_title = current_ch.get("title", f"Chapter {chapter_number}")
    beat_desc = current_ch.get("beat_description", f"Dramatic escalation in {ch_title}.")
    micro_beats = current_ch.get("micro_beats", [])

    characters = book_project.get("characters") or extract_characters_from_project_or_blueprint(
        blueprint_text=book_project.get("outline", ""),
        storyline=storyline,
        genre=genre
    )
    prot = characters.get("protagonist", {}).get("name", "Alex Mercer")
    prot_last = prot.split()[-1]
    antag = characters.get("antagonist", {}).get("name", "Victor Cross")
    antag_last = antag.split()[-1]
    ally = characters.get("supporting", {}).get("name", "Elena Scott")

    m_hook = micro_beats[0] if len(micro_beats) > 0 else f"{prot} establishes immediate control over the new perimeter."
    m_mid = micro_beats[1] if len(micro_beats) > 1 else f"An unexpected breach or confrontation forces a high-risk counter-move."
    m_end = micro_beats[2] if len(micro_beats) > 2 else f"A sudden revelation triggers a breathless chapter cliffhanger."

    # Clean micro-beat labels
    for prefix in ["hook & objective:", "obstacle & escalation:", "micro-cliffhanger:", "scene 1:", "scene 2:", "scene 3:"]:
        m_hook = re.sub(f'(?i)^{re.escape(prefix)}\\s*', '', m_hook).strip()
        m_mid = re.sub(f'(?i)^{re.escape(prefix)}\\s*', '', m_mid).strip()
        m_end = re.sub(f'(?i)^{re.escape(prefix)}\\s*', '', m_end).strip()

    clean_beat = beat_desc.rstrip('.')

    paragraphs = []
    paragraphs.append(f"## Chapter {chapter_number}: {ch_title}\n")

    # 1. Opening Pickup & Immediate Objective
    if chapter_number == 1:
        paragraphs.append(
            f"The clock on {prot}'s terminal had just ticked past 03:40 AM when the primary warning tripped. "
            f"Outside the reinforced windows, the night was pitch-black and restless. "
            f"Across the workspace, the objective was undeniable: {clean_beat}. "
            f"Every instinct screamed that the window of opportunity was vanishing fast."
        )
        paragraphs.append(
            f"\"{prot_last},\" {ally} whispered, hurrying into the room and pulling the reinforced door shut behind her. "
            f"\"The external feeds just went dark. If we don't move right now, {antag} will have the entire sector cordoned off.\"\n\n"
            f"{prot} didn't blink, eyes locked onto the glowing telemetry. \"We aren't leaving until we secure the drive. "
            f"Look at the access log: {m_hook.lower().rstrip('.')}.\""
        )
    else:
        pickup_context = f"Following the recent crisis—{prev_summary.lower().rstrip('.')}—there" if prev_summary else "There"
        paragraphs.append(
            f"{pickup_context} was no room for error. The sharp sting of adrenaline was still pumping through {prot}'s veins as they regrouped. "
            f"The immediate mandate was clear: {clean_beat}."
        )
        paragraphs.append(
            f"\"{prot_last}, do you hear that?\" {ally} hissed, pressing her back flat against the cold concrete wall. "
            f"Her knuckles were white around the grip of her flashlight. \"They've already bypassed the lower checkpoint. We're running out of room to maneuver.\"\n\n"
            f"{prot} adjusted the transceiver, breath steadying. \"Keep your eyes forward,\" {prot} said. \"We came here for one thing: {m_hook.lower().rstrip('.')}. "
            f"Now cover the corridor while I cycle the lock.\""
        )

    # 2. Rising Conflict & Tactical Complication (The Mid Beat)
    paragraphs.append(
        f"The lock mechanism clicked with a heavy mechanical latch, swinging open to reveal the dim interior of the chamber. "
        f"Inside, the hum of high-voltage conduits vibrated through the steel grating beneath their boots. "
        f"Everything seemed according to plan—until the sudden chime of an override tone echoed from the overhead speakers."
    )
    paragraphs.append(
        f"\"{m_mid.capitalize().rstrip('.')},\" {prot} muttered, watching the status indicators on the central console spike into the red. "
        f"\"They didn't just trace the connection. They set an ambush.\"\n\n"
        f"Heavy footsteps echoed down the main catwalk, unhurried and deliberately loud. "
        f"From the shadow of the gantry emerged {antag}, accompanied by two heavily armed security operatives in black tactical vests."
    )
    paragraphs.append(
        f"\"You should have taken the buyout when you had the chance, {prot_last},\" {antag} said, his voice smooth, cold, and utterly relaxed. "
        f"\"You honestly believed you could walk into my perimeter and expose {storyline.lower().split('.')[0] if '.' in storyline else storyline.lower()} without an answer?\"\n\n"
        f"\"Your perimeter is built on lies, {antag_last},\" {prot} countered, fingers inching toward the concealed secondary charge on the equipment belt. "
        f"\"And everyone outside this room is about to see the unedited truth.\"\n\n"
        f"\"Not if you never leave it,\" {antag} said, nodding once to the guards."
    )

    # 3. Climax & Chapter Cliffhanger (The End Beat)
    paragraphs.append(
        f"Before the guards could raise their rifles, {ally} tossed a pressurized flare directly between the gantry grates. "
        f"A blinding white flash erupted with a deafening crack, filling the corridor with suffocating smoke and panic. "
        f"Shouts and blind gunfire ricocheted off the corrugated steel walls as {prot} tackled {ally} through the blast door, "
        f"slamming the manual release lever downward with full body weight."
    )
    paragraphs.append(
        f"The heavy titanium door dropped into its frame with a thunderous clang, sealing them in the auxiliary maintenance vault. "
        f"Breathing raggedly, {prot} wiped sweat and grit from forehead and brought up the auxiliary console."
    )
    paragraphs.append(
        f"That was when the real shock landed. {m_end.capitalize().rstrip('.')}.\n\n"
        f"On the central monitor, a single classified file unlocked automatically, revealing a revelation that shattered everything {prot} thought they knew. "
        f"Outside the sealed door, the metallic thud of a breaching explosive magnetized to the frame. "
        f"The digital timer on the charge was flashing: *00:45... 00:44...*"
    )

    prose = "\n\n".join(paragraphs)
    summary = (
        f"In Chapter {chapter_number} ({ch_title}), {prot} and {ally} confront {clean_beat.lower()}, "
        f"narrowly escaping an ambush set by {antag}. As they barricade in the auxiliary vault, {m_end.lower().rstrip('.')} is uncovered "
        f"while a breaching explosive counts down on their only door."
    )

    return {"content": prose, "summary": summary}

def generate_chapter_prose(
    book_project: Dict[str, Any],
    chapter_number: int,
    audience: str = "Adult Commercial",
    pov: str = "Third Person Limited",
    pacing: str = "Commercial Page-Turner",
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.8-flash"
) -> Dict[str, str]:
    """
    Generates prose for a specific chapter using the sliding window:
    - Story Bible (Named Characters, Premise, Tropes)
    - Chapter Beat Goal & 3 Micro-Beats (from given outline)
    - Chapter N-1 Summary & Last 250 Words (Continuity Anchor)
    Tries requested Gemini model with fallback chain, and uses dynamic
    context-aware prose synthesis if offline or API is unavailable.
    """
    chapters = book_project.get("chapters", [])
    current_ch = next((c for c in chapters if c["number"] == chapter_number), None)
    if not current_ch:
        raise ValueError(f"Chapter {chapter_number} not found.")

    prev_ch = next((c for c in chapters if c["number"] == chapter_number - 1), None)
    prev_summary = prev_ch.get("summary", "") if prev_ch else "Opening of the novel."
    prev_content = prev_ch.get("content", "") if prev_ch else ""

    prev_words = prev_content.split()
    prev_ending_anchor = " ".join(prev_words[-250:]) if prev_words else ""

    ingredients = book_project.get("ingredients", {})
    comps = ", ".join(ingredients.get("recent_comps", [])[:3])
    tropes = ", ".join(ingredients.get("top_tropes", [])[:3])

    characters = book_project.get("characters") or extract_characters_from_project_or_blueprint(
        blueprint_text=book_project.get("outline", ""),
        storyline=book_project.get("storyline", ""),
        genre=book_project.get("genre", "Commercial Fiction")
    )
    prot_name = characters.get("protagonist", {}).get("name", "Alex Mercer")
    prot_role = characters.get("protagonist", {}).get("role", "Protagonist")
    antag_name = characters.get("antagonist", {}).get("name", "Victor Cross")
    antag_role = characters.get("antagonist", {}).get("role", "Primary Adversary")
    ally_name = characters.get("supporting", {}).get("name", "Elena Scott")
    ally_role = characters.get("supporting", {}).get("role", "Key Ally")

    micro_beats_text = "\n".join([f"  • {mb}" for mb in current_ch.get("micro_beats", [])])

    if api_key and api_key.strip():
        models_to_try = [model_name] + [m for m in FALLBACK_GEMINI_MODELS if m != model_name]
        try:
            from google import genai
            client = genai.Client(api_key=api_key.strip())

            prompt = f"""You are a #1 New York Times bestselling commercial novelist writing Chapter {chapter_number} of a high-octane, unputdownable page-turner.

TARGET STYLE: Fast-moving, visceral, emotionally resonant commercial fiction for mainstream readers (in the gripping tradition of Stephen King, Lee Child, Harlan Coben, Michael Crichton, Gillian Flynn, and Suzanne Collins).

=== MASTER STORY BIBLE ===
BOOK TITLE: "{book_project.get('title')}"
GENRE: {book_project.get('genre')}
CORE STORYLINE: "{book_project.get('storyline')}"
TARGET AUDIENCE: {audience} | POV: {pov} | PACING: {pacing}

NAMED CHARACTERS:
- PROTAGONIST: {prot_name} ({prot_role})
- PRIMARY ANTAGONIST / FOIL: {antag_name} ({antag_role})
- KEY ALLY / SUPPORTING: {ally_name} ({ally_role})

=== SLIDING WINDOW CONTINUITY BUFFER ===
PREVIOUS CHAPTER SUMMARY:
"{prev_summary}"

EXACT PREVIOUS CHAPTER ENDING SCENE (FOR IMMEDIATE MOMENTUM & PHYSICAL PICKUP):
"{prev_ending_anchor if prev_ending_anchor else '[Opening Chapter of Book]'}"

=== CURRENT CHAPTER ASSIGNMENT ===
CHAPTER {chapter_number}: "{current_ch['title']}" ({current_ch.get('act', 'Act I')})
TARGET BEAT & SCENE OBJECTIVE:
"{current_ch['beat_description']}"

MICRO-BEAT SCENE MATRIX:
{micro_beats_text if micro_beats_text else f'• Scene 1: {prot_name} takes immediate action on {current_ch.get("title")}\n• Scene 2: Direct complication or confrontation involving {antag_name}\n• Scene 3: Irreversible turning point and cliffhanger'}

MANDATORY COMMERCIAL FICTION DIRECTIVES:
1. ZERO INTELLECTUAL FLUFF OR PURPLE PROSE:
   - Strictly BANNED: Abstract philosophizing, MFA essay-style metaphors, academic vocabulary, and purple prose (NEVER use clichés like "fragile architecture of...", "unspoken consequence", "visceral tapestry", "crucible of truth", "immutable reality", "testament to", "labyrinthine dance", "existential dread").
   - DO NOT write an essay about themes. Tell a propulsive, thrilling story through character action, dialogue, and rising conflict!

2. HEAVY, AUTHENTIC DIALOGUE (MANDATORY 35% TO 50% OF TEXT):
   - Characters MUST speak aloud to each other in natural, quoted dialogue ("...").
   - Dialogue should crackle with tension, competing agendas, subtext, lies, banter, and sharp interruptions.

3. PHYSICAL ACTION & SENSORY GROUNDING:
   - Anchor the scene in physical reality: concrete physical spaces, handled objects, weather, sounds, physical movements, body language, adrenaline.
   - Show characters reacting physically (quickened breathing, cold sweat, checking their watch, slamming a door) rather than explaining their inner psychological theory.

4. NAMED CHARACTERS IN DIRECT CONFLICT:
   - Feature {prot_name} actively pursuing the chapter's objective.
   - Put them in direct verbal or physical confrontation with {antag_name} or {ally_name}.

5. PUNCHY, PAGE-TURNING PACING:
   - Keep paragraphs short and readable (2 to 4 sentences max). Use strong active verbs.
   - Conclude this chapter on a sharp, dramatic turning point, revelation, or ticking deadline that compels the reader to immediately turn to Chapter {chapter_number + 1}.

6. CONTINUITY SUMMARY AT THE VERY END:
   AT THE VERY END OF YOUR OUTPUT, PROVIDE A ROLLING CONTINUITY SUMMARY IN THIS EXACT FORMAT:
   [SUMMARY]: (A concise 2-3 sentence rolling continuity summary of the events and ending cliffhanger in Chapter {chapter_number} to be passed to Chapter {chapter_number + 1})
"""
            for m_cand in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_cand,
                        contents=prompt,
                        config={"temperature": 0.82, "max_output_tokens": 8192}
                    )

                    if response and response.text:
                        full_text = response.text.strip()
                        summary = f"In Chapter {chapter_number} ({current_ch['title']}), key dramatic events unfold, escalating conflict toward the next beat."
                        clean_content = full_text

                        sum_match = re.search(r'(?i)(?:\[?SUMMARY\]?:?\s*|\*\*SUMMARY:\*\*\s*)(.*)', full_text, re.DOTALL)
                        if sum_match:
                            clean_content = full_text[:sum_match.start()].strip()
                            summary = sum_match.group(1).strip()
                        elif "[SUMMARY]:" in full_text:
                            parts = full_text.split("[SUMMARY]:")
                            clean_content = parts[0].strip()
                            summary = parts[1].strip()

                        return {"content": clean_content, "summary": summary}
                except Exception:
                    continue
        except Exception:
            pass

    # Offline / Dynamic Bespoke Generator (Honors given outline & sliding window)
    return generate_dynamic_offline_prose(
        book_project=book_project,
        chapter_number=chapter_number,
        audience=audience,
        pov=pov,
        pacing=pacing
    )

def generate_all_chapters_sequential(
    book_project: Dict[str, Any],
    audience: str = "Adult Commercial",
    pov: str = "Third Person Limited",
    pacing: str = "Commercial Page-Turner",
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.8-flash",
    progress_callback: Optional[Any] = None,
    max_to_draft: Optional[int] = None,
    skip_already_drafted: bool = True
) -> Dict[str, Any]:
    """
    Sequentially drafts pending chapters from the outline using the sliding window continuity buffer.
    Updates book_project in-place.
    """
    chapters = book_project.get("chapters", [])
    total_chapters = len(chapters)
    drafted_now = 0

    for ch in chapters:
        if max_to_draft is not None and drafted_now >= max_to_draft:
            break

        if skip_already_drafted and ch.get("status") == "Drafted" and ch.get("content", "").strip():
            continue

        ch_num = ch["number"]
        if progress_callback:
            progress_callback(ch_num, total_chapters, ch["title"])

        gen_res = generate_chapter_prose(
            book_project=book_project,
            chapter_number=ch_num,
            audience=audience,
            pov=pov,
            pacing=pacing,
            api_key=api_key,
            model_name=model_name
        )

        ch["content"] = gen_res["content"]
        ch["summary"] = gen_res["summary"]
        ch["status"] = "Drafted"
        ch["word_count"] = len(gen_res["content"].split())
        drafted_now += 1

    total_drafted = sum(1 for c in chapters if c.get("status") == "Drafted")
    total_words = sum(c.get("word_count", 0) for c in chapters)

    return {
        "success": True,
        "newly_drafted": drafted_now,
        "total_drafted": total_drafted,
        "total_chapters": total_chapters,
        "total_words": total_words
    }

def compile_full_manuscript(book_project: Dict[str, Any]) -> str:
    """Compiles all drafted chapters into a complete formatted book manuscript."""
    title = book_project.get("title", "Untitled Novel")
    genre = book_project.get("genre", "Commercial Fiction")
    chapters = book_project.get("chapters", [])
    drafted = [c for c in chapters if c.get("content", "").strip()]
    total_words = sum(c.get("word_count", 0) for c in drafted)

    if not drafted:
        return f"# {title.upper()}\n\n*A Commercial {genre} Novel*\n\n*No chapters have been drafted yet. Use the Chapter-by-Chapter Novel Engine to auto-draft chapters from your outline.*"

    doc = [
        f"# {title.upper()}\n\n"
        f"**Genre:** {genre} | **Total Chapters Drafted:** {len(drafted)}/{len(chapters)} | **Total Word Count:** {total_words:,} words\n\n"
        f"---\n\n"
        f"## TABLE OF CONTENTS\n\n"
    ]
    for c in drafted:
        doc.append(f"- **Chapter {c['number']}: {c['title']}** ({c.get('act', '')}) — *{c.get('word_count', 0):,} words*")
    doc.append("\n\n---\n\n")

    for c in drafted:
        doc.append(f"<!-- CHAPTER {c['number']} -->\n\n{c['content'].strip()}\n\n---\n\n")

    return "\n".join(doc)

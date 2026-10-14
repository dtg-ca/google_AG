"""
generator.py
Orchestrates Gemini AI to transform storylines and 6-month bestseller trends
into commercial-grade Novels (Blueprint + Ch 1), Movie Scripts (Screenplay format),
and Standalone Short Stories.
"""

import json
import os
from typing import Dict, Any, Optional

def build_system_instruction(output_type: str, genre: str, audience: str, pov: str, pacing: str) -> str:
    """Constructs elite commercial storytelling directives optimized for page-turning readability and average-reader engagement."""
    return f"""You are a #1 New York Times Bestselling Commercial Novelist and Screenwriting Master (in the gripping, unputdownable tradition of authors like Stephen King, Lee Child, Harlan Coben, Michael Crichton, Gillian Flynn, and Suzanne Collins).

Your writing is engineered for everyday readers: propulsive, visceral, dialogue-rich, emotionally gripping, and immediately accessible.

CORE SPECIFICATIONS:
- Genre: {genre}
- Target Audience: {audience}
- Point of View: {pov}
- Pacing Profile: {pacing}
- Output Format Required: {output_type}

RULES OF COMMERCIAL ENGAGEMENT:
1. ZERO INTELLECTUAL FLUFF OR PURPLE PROSE:
   - Strictly forbidden from using academic, pompous, essayistic, or pseudo-philosophical language (e.g. NEVER write about "the fragile architecture of ordinary life", "unspoken consequence", "visceral tapestry", "crucible of truth", "immutable reality", "testament to", or "existential dread").
   - Ban authorial commentary and meta-analysis. Never lecture the reader on themes; show the story unfolding in real time.

2. SNAPPY, AUTHENTIC DIALOGUE (MANDATORY):
   - At least 35% to 50% of manuscript prose must consist of spoken dialogue in quotation marks ("...").
   - Characters must sound like real human beings: sharp exchanges, hidden agendas, interruptions, lies, confessions, and banter.

3. PHYSICAL ACTION & SENSORY GROUNDING:
   - Anchor every scene in concrete physical space: cold rain on a collar, vibrating phones, footsteps on gravel, the click of a lock, slamming doors, smell of ozone or coffee.
   - Characters must take physical actions and experience physical sensations (adrenaline, tight chest, clenched fists, dry throat) rather than detached internal philosophizing.

4. NAMED CHARACTERS WITH CLEAR WANTS:
   - Name all characters immediately. Never refer to people as "the protagonist", "the investigator", or "an observer".
   - Establish what the character desperately wants right now, and the immediate obstacle blocking them.

5. PUNCHY, PAGE-TURNING SENTENCE CRAFT:
   - Keep paragraphs short (2 to 4 sentences max). Use strong, active verbs and varied sentence rhythm.
   - End chapters and scenes on high-stakes hooks, shocking discoveries, or ticking-clock dilemmas.

6. SCREENPLAY PRECISION:
   - If writing screenplay scenes, use strict industry formatting (SCENE HEADINGS in ALL CAPS, active visual action in present tense, centered CHARACTER CUES in CAPS, dialogue with subtext).
"""

FALLBACK_GENERATOR_MODELS = [
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview"
]

def generate_story_content(
    storyline: str,
    genre: str,
    output_type: str,
    ingredients: Dict[str, Any],
    audience: str = "Adult Commercial",
    pov: str = "Third Person Limited",
    pacing: str = "Commercial Page-Turner",
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.8-flash"
) -> Dict[str, Any]:
    """
    Primary generation controller.
    Calls Gemini API with model fallback chain if api_key is available,
    or produces rich tailored dynamic offline manuscripts.
    """
    # 1. Attempt Gemini Generation with model fallback chain
    if api_key and api_key.strip():
        models_to_try = [model_name] + [m for m in FALLBACK_GENERATOR_MODELS if m != model_name]
        try:
            from google import genai
            client = genai.Client(api_key=api_key.strip())
            
            prompt = construct_prompt(
                storyline=storyline,
                genre=genre,
                output_type=output_type,
                ingredients=ingredients,
                audience=audience,
                pov=pov,
                pacing=pacing
            )
            
            system_instruction = build_system_instruction(output_type, genre, audience, pov, pacing)
            
            for m_cand in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_cand,
                        contents=prompt,
                        config={
                            "system_instruction": system_instruction,
                            "temperature": 0.85,
                            "max_output_tokens": 8192
                        }
                    )
                    
                    if response and response.text:
                        return {
                            "success": True,
                            "model_used": m_cand,
                            "output_type": output_type,
                            "genre": genre,
                            "content": response.text.strip(),
                            "source": "Gemini Live API"
                        }
                except Exception:
                    continue
        except Exception:
            pass

    # 2. Rich Offline High-Quality Fallback Generator
    offline_draft = build_offline_rich_draft(
        storyline=storyline,
        genre=genre,
        output_type=output_type,
        ingredients=ingredients,
        audience=audience,
        pov=pov,
        pacing=pacing
    )
    return {
        "success": True,
        "model_used": "Studio Offline Creative Engine (Configure API key for Live Gemini)",
        "output_type": output_type,
        "genre": genre,
        "content": offline_draft,
        "source": "Offline Engine"
    }

def construct_prompt(
    storyline: str,
    genre: str,
    output_type: str,
    ingredients: Dict[str, Any],
    audience: str,
    pov: str,
    pacing: str
) -> str:
    """Builds comprehensive master prompt tailored to the chosen output format."""
    comps_str = ", ".join(ingredients.get("recent_comps", []))
    tropes_str = "\n  - " + "\n  - ".join(ingredients.get("top_tropes", []))
    dynamics_str = "\n  - " + "\n  - ".join(ingredients.get("character_dynamics", []))
    beats_str = "\n  - " + "\n  - ".join(ingredients.get("emotional_beats_pacing", []))
    
    base_instructions = f"""
STORYLINE PREMISE:
"{storyline}"

COMMERCIAL BENCHMARKS & 6-MONTH TREND INGREDIENTS TO INTEGRATE:
- Target Market Comps: {comps_str}
- Hot Tropes to Exploit: {tropes_str}
- Character Dynamics: {dynamics_str}
- Pacing / Emotional Beats: {beats_str}
- Desired Tone / Voice: {ingredients.get("tone_voice", "Compelling and vivid")}
- Cliffhanger Style: {ingredients.get("cliffhanger_styles", "High stakes reveal")}
- Viral Hook Factor: {ingredients.get("viral_hooks", "High emotional conflict")}

CREATIVE DIALS:
- Target Audience: {audience}
- Narrative POV: {pov}
- Pacing Profile: {pacing}
"""

    if output_type == "Novel (Blueprint + Chapter 1)":
        return f"""{base_instructions}
TASK: Craft a comprehensive, commercial NOVEL PACKAGE containing:

# PART I: COMMERCIAL BOOK PROPOSAL & BLUEPRINT
1. TITLE & HIGH-CONCEPT LOGLINE: A punchy, market-ready title and a 1-sentence hook.
2. MARKET POSITIONING: Target readership, why this will trend on BookTok/Amazon, and comps analysis.
3. CHARACTER DOSSIERS (SPECIFIC FULL NAMES REQUIRED):
   - Protagonist: [Full Name, Age, Role/Profession] - Core desire, fatal flaw, ghost/wound from past, transformative arc.
   - Antagonist / Foil: [Full Name, Role/Profession] - Motivations, compelling justification, friction points with protagonist.
   - Key Supporting Character: [Full Name, Role/Profession] - Relationship dynamic, truth-teller role.
4. MASTER BEAT-BY-BEAT CHAPTER OUTLINE (15 Chapters mapped across Acts I, II-A, II-B, III):
   Explicitly format each chapter on its own line:
   - Chapter 1: [Catchy Title] - [Core beat goal, dramatic tension, and turning point]
   - Chapter 2: [Catchy Title] - [Core beat goal, dramatic tension, and turning point]
   ...
   - Chapter 15: [Catchy Title] - [Core beat goal, dramatic tension, and turning point]

---

# PART II: POLISHED MANUSCRIPT — CHAPTER 1
- Write the complete, full-length, page-turning Chapter 1 (at least 1,800 to 2,500 words).
- OPEN IN MEDIA RES: Put the named protagonist immediately into a high-stakes, real-time crisis or discovery.
- HEAVY AUTHENTIC DIALOGUE (MANDATORY): Dedicate at least 35% to 50% of the scene to sharp, tension-filled dialogue in quotation marks ("...") between named characters.
- ZERO INTELLECTUAL FLUFF OR ESSAYING: Strictly avoid abstract philosophical musings, purple metaphors, and detached commentary. Ground every paragraph in physical actions, sensory details, and rising stakes.
- End on a heart-stopping, page-turning chapter cliffhanger that forces the reader to immediately flip to Chapter 2.
"""

    elif "Movie Script - Short Film" in output_type:
        return f"""{base_instructions}
TASK: Write a complete, production-ready SHORT FILM SCREENPLAY (estimated 10-15 pages).

FORMATTING REQUIREMENTS:
- Use standard industry screenplay typography:
  - SCENE HEADINGS (Sluglines) in ALL CAPS (e.g., INT. DINER - NIGHT)
  - Action blocks in present tense, concise, visual (avoid unfilmables).
  - CHARACTER NAMES centered/capitalized above dialogue.
  - Parentheticals (beat), (whispering) used judiciously.
  - Realistic, subtext-heavy dialogue.

STRUCTURE:
1. Cover Title & Logline.
2. Characters List.
3. Complete Short Film Script from opening scene to emotional/twist climax and closing image.
"""

    elif "Movie Script - Feature Treatment + Act I" in output_type:
        return f"""{base_instructions}
TASK: Craft a FEATURE FILM TREATMENT & COMPLETE SCREENPLAY ACT I.

SECTION 1: FEATURE TREATMENT
1. Title, Logline, and Genre/Tone comps.
2. Central Dramatic Question & Theme.
3. Feature Film 3-Act Narrative Arc Summary (Acts I, II-A, II-B, III).

SECTION 2: FULL SCREENPLAY ACT I
- Write the complete screenplay for ACT I in industry-standard screenplay format:
  - Opening Image / Setup scene(s).
  - Inciting Incident / Catalyst.
  - The Debate sequence.
  - Break into Act II (The threshold moment).
"""

    else:  # Short Story (Complete)
        return f"""{base_instructions}
TASK: Write a complete, standalone, publication-ready SHORT STORY (~2,500 to 4,000 words).

REQUIREMENTS:
- Self-contained narrative arc with beginning, escalating conflict, midpoint revelation, climax, and emotional resonance.
- Deep psychological interiority matching the POV: {pov}.
- Embed the viral hook and emotional cliffhanger organically.
- Rich prose style that leaves a lasting emotional impact on the reader.
"""

def get_genre_named_cast(genre: str, storyline: str) -> Dict[str, str]:
    """Provides vivid, genre-appropriate named characters if not specified in the premise."""
    g_lower = genre.lower()
    if "sci-fi" in g_lower or "dystopian" in g_lower or "mars" in storyline.lower() or "space" in storyline.lower():
        return {
            "protagonist_name": "Dr. Sarah Hayes",
            "protagonist_role": "Chief Life-Support Systems Engineer",
            "antagonist_name": "Director Ronald Vance",
            "antagonist_role": "Colony Governor & Corporate Enforcer",
            "ally_name": "Kaelen Chen",
            "ally_role": "Senior Diagnostics Specialist"
        }
    elif "thriller" in g_lower or "mystery" in g_lower or "suspense" in g_lower or "detective" in storyline.lower():
        return {
            "protagonist_name": "Detective Jack Mercer",
            "protagonist_role": "Veteran Homicide & Fraud Investigator",
            "antagonist_name": "Julian Drake",
            "antagonist_role": "High-Stakes Syndicate Fixer",
            "ally_name": "Elena Vance",
            "ally_role": "Forensic Intelligence Specialist"
        }
    elif "romance" in g_lower or "women" in g_lower:
        return {
            "protagonist_name": "Maya Bennett",
            "protagonist_role": "Independent Creative Director",
            "antagonist_name": "Liam Montgomery",
            "antagonist_role": "Rival Firm Partner & Unyielding Foil",
            "ally_name": "Chloe Rivera",
            "ally_role": "Loyal Confidante & Publicist"
        }
    elif "fantasy" in g_lower or "paranormal" in g_lower:
        return {
            "protagonist_name": "Caelen Ward",
            "protagonist_role": "Exiled Boundary Scout",
            "antagonist_name": "Lord Malakor",
            "antagonist_role": "High Chancellor of the Citadel",
            "ally_name": "Lyra Thorne",
            "ally_role": "Keeper of Ancient Lore"
        }
    elif "historical" in g_lower:
        return {
            "protagonist_name": "Thomas Sterling",
            "protagonist_role": "Resolute Frontier Navigator",
            "antagonist_name": "Magistrate Henry Blackwood",
            "antagonist_role": "Imperial Enforcer",
            "ally_name": "Constance Lee",
            "ally_role": "Underground Network Courier"
        }
    else:
        return {
            "protagonist_name": "Alex Mercer",
            "protagonist_role": "Determined Lead Strategist",
            "antagonist_name": "Victor Cross",
            "antagonist_role": "Ruthless Faction Leader",
            "ally_name": "Elena Scott",
            "ally_role": "Trusted Field Partner"
        }

def build_offline_rich_draft(
    storyline: str,
    genre: str,
    output_type: str,
    ingredients: Dict[str, Any],
    audience: str,
    pov: str,
    pacing: str
) -> str:
    """Generates an extensive, beautifully styled offline blueprint and text when API key is unconfigured."""
    title_seed = storyline.split(".")[0].strip() if storyline else "The Unspoken Equation"
    clean_title = title_seed.title()[:45]
    if len(clean_title) < 8:
        clean_title = f"The {genre} Paradox"

    comps = ", ".join(ingredients.get("recent_comps", ["Recent Bestsellers"])[:3])
    top_tropes = ingredients.get("top_tropes", [])
    tropes = ", ".join(top_tropes[:3]) if top_tropes else "High-stakes narrative tension, Deep character friction"
    clean_premise = storyline.strip() if storyline else f"A high-stakes commercial narrative in {genre}."
    logline_text = clean_premise if len(clean_premise) > 20 else f"When an unforeseen dilemma threatens everything, an unlikely protagonist must gamble on a dangerous gambit in this commercial {genre} masterwork."

    cast = get_genre_named_cast(genre, storyline)
    prot = cast["protagonist_name"]
    prot_role = cast["protagonist_role"]
    antag = cast["antagonist_name"]
    antag_role = cast["antagonist_role"]
    ally = cast["ally_name"]
    ally_role = cast["ally_role"]

    if output_type == "Novel (Blueprint + Chapter 1)":
        return f"""# {clean_title}
*A Commercial {genre} Novel*
**Market Comp Titles:** {comps}  
**Target Readership:** {audience} | **Perspective:** {pov} | **Pacing:** {pacing}

---

## PART I: COMMERCIAL BOOK BLUEPRINT & TREATMENT

### 1. High-Concept Logline
{logline_text}

### 2. Market Positioning & Commercial Appeal
- **Trending Tropes Leveraged:** {tropes}
- **Reader Sentiment Alignment:** {ingredients.get("market_sentiment_summary", "High-stakes emotional confrontation with fast-paced chapter hooks.")}
- **The Viral Hook:** {ingredients.get("viral_hooks", "The impossible choice between personal loyalty and survival.")}

### 3. Character Dossiers
- **Protagonist:** {prot} ({prot_role})
  - *Core Desire:* Uncover the truth, protect the vulnerable, and survive the escalating crisis.
  - *The Ghost / Past Wound:* A past betrayal that taught them never to rely on easy promises.
  - *The Fatal Flaw:* Reluctance to share vulnerability or ask for backup until backed into a corner.
- **Antagonist / Foil:** {antag} ({antag_role})
  - *Motivation:* Absolute control and containment of the dilemma, backed by superior authority.
  - *Friction:* Directly opposes {prot} with ruthless efficiency and institutional leverage.
- **Supporting Catalyst:** {ally} ({ally_role})
  - *Role:* Loyal partner and truth-teller whose discovery triggers the race against time.

### 4. Master Beat-by-Beat Chapter Outline
- Act I: The Fragile Status Quo
  - Chapter 1: The Inciting Catalyst - Setting the stage: {clean_premise[:120]}.
  - Chapter 2: The Direct Disruption - An unexpected obstacle forces an immediate defensive counter-measure.
  - Chapter 3: The Cold Trail - Exploring covert avenues of resistance while pressure mounts.
  - Chapter 4: Crossing the Threshold - Making the irreversible choice to step into unfamiliar and dangerous territory.
- Act II-A: The Deepening Conflict
  - Chapter 5: The Hostile Perimeter - Navigating the initial friction of the new environment under strict scrutiny.
  - Chapter 6: The Uneasy Truce - Reaching a fragile, high-stakes pact with a rival or volatile partner.
  - Chapter 7: The Trial of Competency - Demonstrating high craft and tactical cunning to secure a vital asset.
  - Chapter 8: The Midpoint Shift - A shocking revelation upends the entire premise and doubles the consequences.
- Act II-B: The Collapse & Betrayal
  - Chapter 9: The Retaliation - The opposing faction strikes back with devastating precision.
  - Chapter 10: The Fracture of Trust - Concealed secrets emerge, threatening to tear apart the core alliance.
  - Chapter 11: All Hope Lost - Total collapse of the primary plan leaves the protagonist isolated in despair.
- Act III: The Crucible & Resolution
  - Chapter 12: The Epiphany - Discovering an unforeseen vulnerability in the obstacle from an overlooked clue.
  - Chapter 13: The Desperate Gambit - Rallying surviving forces for an audacious, all-or-nothing counter-offensive.
  - Chapter 14: The Crucible Climax - Decisive confrontation where victory demands a permanent, agonizing sacrifice.
  - Chapter 15: The Transformed Horizon - The dust settles on a changed reality; facing the indelible future.

---

# PART II: POLISHED MANUSCRIPT — CHAPTER 1: THE INCITING CATALYST

The digital dispatch clock on {prot}'s terminal ticked over to 03:42 AM.

Outside the reinforced glass, cold rain whipped through the sodium-lit shadows in stinging diagonal sheets. Across the workspace, an encrypted terminal chimed with a harsh, double-toned pulse. The status banner shifted from standby yellow to urgent, strobing crimson.

"Tell me that wasn't the live feed," {ally} said, leaning into the doorway. Her jacket was soaked through at the shoulders, her jaw set tight.

{prot} didn't look up from the keyboard. "If it wasn't the live feed, we wouldn't be having this conversation. Look at the telemetry."

{ally} crossed the concrete floor, boots squeaking against damp floor mats. She braced one hand against the edge of the metal desk and peered at the scrolling hex code. Her breath caught in her throat. "My god. That's {clean_premise.lower().rstrip('.')}."

"It's already happening," {prot} said, fingers flying across the keys to lock the cache. "They bypassed secondary authorization forty minutes ago while the night shift was rotating out."

"Who signed off on the override?"

{prot} tapped the enter key. A digitized authorization seal expanded in the center of the screen, sharp and unmistakable.

"It was {antag}," {prot} said.

{ally} stared at the glowing name, her color draining. "He wouldn't dare. That's a death sentence for everyone on this grid."

"He just did." {prot} disconnected the portable storage drive and slipped it into an interior breast pocket. "And he knows someone just downloaded the audit trail."

Right on cue, the building's magnetic emergency seals engaged with a concussive thud that vibrated through the floorboards. Overhead, the fluorescent tubes flickered, died, and were replaced by the amber pulse of auxiliary emergency lights.

{prot}'s desk phone buzzed. A private incoming channel.

{prot} hit the speaker button.

"You should have looked the other way, {prot.split()[-1]}," a voice said through the speaker. Smooth, quiet, and chillingly composed. It was {antag}. "The perimeter gates are already sealed. You have ninety seconds before security breaches that door."

The line went dead with a hollow click.

{ally} pulled a compact sidearm from beneath her coat and checked the chamber. "The front exit is gone. Where do we go?"

{prot} zipped the jacket shut and headed for the emergency maintenance chute. "We go down. Move."
"""

    elif "Movie Script" in output_type:
        return f"""TITLE: {clean_title.upper()}
FORMAT: Feature Film Screenplay
GENRE: {genre.upper()}
WRITTEN FOR: {audience.upper()} MARKET

LOGLINE:
In the wake of an impossible discovery, two adversaries must navigate a web of institutional deceit before dawn.

=============================================================================

EXT. DOWNTOWN WATERFRONT - NIGHT

A wall of frozen mist rolls off the black harbor water. 
Industrial cranes loom like rusted iron skeletons against low cloud cover.

A lone sedan idles at the edge of the pier. Exhaust curls white in the freezing air.

INT. SEDAN - CONTINUOUS

Inside, ELENA (30s) grips the steering wheel. Her knuckles are stark white. 
Her breath fogging the windshield. 

On the passenger seat rests a cracked digital tablet. The screen blinks:
DOWNLOADING ENCRYPTED ARCHIVE: 98%... 99%...

ELENA
(under her breath)
Come on. Don't freeze on me now.

A harsh CLICK. 

Elena's eyes dart to the rearview mirror. 
Reflected in the glass: the rear door handle depressing. Slowly.

ELENA reaches into her coat pocket, fingers wrapping around a brass-handled knife.

The rear door swings open. A blast of wet air. 
MARCUS (40s) slides into the backseat. Impeccable dark overcoat, soaked across the shoulders. He smells of rain and expensive tobacco.

MARCUS
You shouldn't have parked beneath the harbor beacon. 
They calibrated the traffic satellites forty minutes ago.

ELENA
I needed line of sight to the antenna. Where is the key?

MARCUS
(leans forward, voice calm, razor sharp)
There is no key, Elena. There never was. 
What you're holding isn't an archive. It's a distress beacon.

The tablet emits a high-pitched CHIRP. 
The screen flashes emerald green: 
SIGNAL BROADCAST: 100% COMPLETE. TARGET COORDINATES LOCKED.

Two hundred yards down the pier, three pairs of high-intensity halogen headlights click ON simultaneously. The roar of supercharged engines tears through the silence.

ELENA
(swings around)
What did you do?

MARCUS
I leveled the playing field. Put the car in reverse.

Elena slams the transmission into gear. The tires shriek against wet concrete.

SMASH CUT TO BLACK.
"""

    else:  # Short Story
        return f"""# {clean_title}
*A Short Story in {genre}*
**By Bestseller Story Studio**

The antique grandfather clock in the study did not chime at midnight. It clicked—a dry, mechanical latch giving way behind mahogany veneer.

Julian froze with his teacup halfway to his lips. For forty-two years, that clock had measured the silence of the estate with uninterrupted cadence. To hear it falter was like watching the sun pause on the horizon.

He set the porcelain cup down, his hand steady despite the sudden chill in the room. The fire in the hearth had died to a bed of chalky embers. Across the Persian rug, the lower panel of the clock case stood ajar by a fraction of an inch.

*The secret you bury doesn't die,* his grandmother had told him the summer the lake froze over. *It only waits for the ice to melt.*

Julian rose, his slippers whispering over polished parquet. He knelt before the clock. Inside the dust-shrouded cavity, nestled behind the pendulum, lay an oblong tin box secured by rusted wire.

He recognized the wire. He had twisted it shut himself, thirty years ago, on the night the family ledger had vanished from the library.

He worked the wire free, the sharp iron biting into his thumb. Inside the tin were two items: a bundle of unopened letters addressed in his mother’s sharp, sloping calligraphy, and a brass key engraved with a number he had spent half his life trying to forget: *Room 407.*

The letters were postmarked three weeks *after* her funeral.

His phone buzzed on the mahogany desk. A single notification illuminated the dark room. 

Julian picked it up. The message was from an automated concierge service:
*"Your reservation for Room 407 has been confirmed. The guest who arrived yesterday is waiting in the lounge."*

Julian looked from the phone to the yellowed envelope in his palm. Outside, the night wind threw a handful of gravel against the library glass, and for the first time in thirty years, Julian smiled.

The game wasn't over. It had only just begun.
"""

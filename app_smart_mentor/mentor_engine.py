"""
mentor_engine.py - Smart Mentor Advisory Brain & Synthesis Engine.
Orchestrates Gemini models to analyze multi-source search findings and formulate
expert advisory briefs with strict section layouts and word count constraints.
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from search_engine import SearchResultItem

CANDIDATE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.7-flash",
]


@dataclass
class MentorAdvisoryReport:
    topic: str
    category: str
    user_context: str
    mentor_tone: str
    # Exact 4 requested sections:
    question_input_section: str
    summary_results_section: str
    analysis_insights_section: str
    action_plans_section: str
    # Metadata & word counts:
    summary_word_count: int
    analysis_word_count: int
    model_used: str
    raw_markdown: str
    sources_consulted: List[SearchResultItem]


class SmartMentorEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def generate_advisory(
        self,
        topic: str,
        category: str,
        user_context: str,
        mentor_tone: str,
        search_results: Dict[str, List[SearchResultItem]],
        search_context_text: str,
    ) -> MentorAdvisoryReport:
        """
        Synthesizes the search results into a structured 4-part Smart Mentor advisory.
        """
        all_sources: List[SearchResultItem] = []
        for cat_items in search_results.values():
            all_sources.extend(cat_items)

        system_instruction = (
            "You are the 'Smart Mentor'—a wise, authoritative, and deeply empathetic expert advisor. "
            "You possess expansive multidisciplinary wisdom across current affairs, medical science, "
            "legal & regulatory frameworks, macroeconomic strategy, and human society. "
            "Your mission is to guide, empower, and protect the user by synthesizing real-world search intelligence. "
            "You MUST strictly follow the exact requested 4-section structure and respect all word limits."
        )

        user_prompt = f"""
ROLE: Smart Mentor - an expert who has the wisdom and knowledge to answer questions about a wide range of topics.
OBJECTIVE: Provide a thorough advisory based on real-time search findings across current affairs, medical content repositories, legal/academic repositories, and social discussion forums.

USER TOPIC / ISSUE / PROBLEM:
{topic}

CATEGORY / DOMAIN:
{category}

USER PERSONAL CONTEXT & CIRCUMSTANCES:
{user_context if user_context.strip() else "General user guidance and self-protection."}

MENTOR TONE & PERSPECTIVE:
{mentor_tone}

=========================================
LIVE RETRIEVED SEARCH RESULTS FROM REPOSITORIES:
=========================================
{search_context_text}
=========================================

MANDATORY INSTRUCTIONS:
Structure your response into EXACTLY the following 4 sections using the exact markdown header names specified below:

### SECTION 1: THE QUESTION / INPUT FROM USER
- Reframe and articulate the user's inquiry, underlying dilemma, key tensions, and stakes.
- Acknowledge their personal context, vulnerabilities, and mentor guidance objectives.

### SECTION 2: SUMMARY OF SEARCH RESULTS
- Synthesize the findings from the searched sources (Current Affairs/News, Medical repositories like PubMed, Legal/Academic frameworks, and Social discussion forums).
- Highlight key facts, current trends, clinical or legal consensus, and real-world forum sentiments.
- CRITICAL CONSTRAINT: This section MUST be LESS THAN 1000 words (aim for 500 - 800 words).

### SECTION 3: ANALYSIS & INSIGHTS FROM SEARCHED REFERENCES
- Provide expert mentor analysis, critical evaluation, and wisdom.
- Uncover underlying risks, blind spots, conflicting narratives between official reports and public forums, trade-offs, and systemic implications.
- CRITICAL CONSTRAINT: This section MUST be LESS THAN 500 words (aim for 250 - 450 words).

### SECTION 4: ACTION PLANS & NEXT STEPS
- Formulate concrete, pragmatic, step-by-step action plans for the user with a direct view to empower or protect oneself.
- Organize logically (e.g., Immediate Self-Protection / 48hr steps, Medium-term Strategy / 30-day steps, and Long-term Resilience).
- Include essential verification steps, questions to ask specialists (doctors, legal counsel, or financial advisors), and safety guardrails.

Now produce the full Smart Mentor Advisory Brief:
"""

        # Attempt generation using Gemini with fallback models
        generated_text = ""
        model_used = "Fallback Engine"

        if self.api_key:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            for model_name in CANDIDATE_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.4,
                        ),
                    )
                    if response and response.text:
                        generated_text = response.text.strip()
                        model_used = model_name
                        break
                except Exception as e:
                    # Log or try next candidate
                    continue

        # If Gemini didn't return (quota/network), use built-in Mentor synthesis fallback
        if not generated_text:
            generated_text, model_used = self._fallback_synthesis(
                topic, category, user_context, mentor_tone, search_results
            )

        # Parse sections
        sections = self._parse_advisory_sections(generated_text, topic, user_context, category)

        # Calculate word counts
        summary_wc = len(sections["summary"].split())
        analysis_wc = len(sections["analysis"].split())

        return MentorAdvisoryReport(
            topic=topic,
            category=category,
            user_context=user_context,
            mentor_tone=mentor_tone,
            question_input_section=sections["question"],
            summary_results_section=sections["summary"],
            analysis_insights_section=sections["analysis"],
            action_plans_section=sections["action_plans"],
            summary_word_count=summary_wc,
            analysis_word_count=analysis_wc,
            model_used=model_used,
            raw_markdown=generated_text,
            sources_consulted=all_sources,
        )

    def ask_follow_up(
        self,
        report: MentorAdvisoryReport,
        chat_history: List[Dict[str, str]],
        follow_up_question: str,
    ) -> str:
        """Allows the user to engage in an ongoing mentorship dialogue following the report."""
        if not self.api_key:
            return (
                "As your Smart Mentor, I advise reviewing the immediate action steps outlined in Section 4. "
                "Ensure you document all correspondence, consult verified specialists, and prioritize personal safety."
            )

        from google import genai

        client = genai.Client(api_key=self.api_key)
        context_prompt = (
            f"You are the Smart Mentor continuing an advisory consultation with the user.\n"
            f"Initial Topic: {report.topic}\n"
            f"Category: {report.category}\n"
            f"User Context: {report.user_context}\n"
            f"Advisory Summary: {report.summary_results_section[:400]}...\n"
            f"Analysis: {report.analysis_insights_section[:300]}...\n"
            f"Tone: {report.mentor_tone}\n\n"
            f"Answer the user's follow-up question with depth, strategic wisdom, empathy, and practical guidance."
        )

        messages = [context_prompt]
        for msg in chat_history[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append(f"{role.upper()}: {content}")
        messages.append(f"USER: {follow_up_question}\nSMART MENTOR:")

        for model_name in CANDIDATE_MODELS:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents="\n\n".join(messages),
                )
                if res and res.text:
                    return res.text.strip()
            except Exception:
                continue

        return "Reflect upon the core trade-offs: protect your downside risk before pursuing upside gain."

    def _parse_advisory_sections(
        self, text: str, topic: str, user_context: str, category: str
    ) -> Dict[str, str]:
        """Robust parser to extract the 4 mandatory sections."""
        result = {
            "question": "",
            "summary": "",
            "analysis": "",
            "action_plans": "",
        }

        # Regex patterns to split sections
        sec1_match = re.search(r"###\s*(?:SECTION\s*1\s*:?|THE\s*QUESTION)", text, re.IGNORECASE)
        sec2_match = re.search(r"###\s*(?:SECTION\s*2\s*:?|SUMMARY\s*OF\s*SEARCH\s*RESULTS)", text, re.IGNORECASE)
        sec3_match = re.search(r"###\s*(?:SECTION\s*3\s*:?|ANALYSIS\s*&\s*INSIGHTS)", text, re.IGNORECASE)
        sec4_match = re.search(r"###\s*(?:SECTION\s*4\s*:?|ACTION\s*PLANS)", text, re.IGNORECASE)

        indices = []
        if sec1_match:
            indices.append(("question", sec1_match.start(), sec1_match.end()))
        if sec2_match:
            indices.append(("summary", sec2_match.start(), sec2_match.end()))
        if sec3_match:
            indices.append(("analysis", sec3_match.start(), sec3_match.end()))
        if sec4_match:
            indices.append(("action_plans", sec4_match.start(), sec4_match.end()))

        # Sort by occurrence
        indices.sort(key=lambda x: x[1])

        if len(indices) == 4:
            result[indices[0][0]] = text[indices[0][2] : indices[1][1]].strip()
            result[indices[1][0]] = text[indices[1][2] : indices[2][1]].strip()
            result[indices[2][0]] = text[indices[2][2] : indices[3][1]].strip()
            result[indices[3][0]] = text[indices[3][2] :].strip()
        else:
            # Fallback if markdown headers differed slightly
            result["question"] = (
                f"**Framed Issue:** {topic}\n\n"
                f"**Domain:** {category}\n\n"
                f"**Context & Vulnerability:** {user_context or 'Standard consultation for protective guidance.'}"
            )
            paragraphs = text.split("\n\n")
            half = len(paragraphs) // 3
            result["summary"] = "\n\n".join(paragraphs[:half]) if paragraphs else text
            result["analysis"] = "\n\n".join(paragraphs[half : half * 2]) if len(paragraphs) > 1 else ""
            result["action_plans"] = "\n\n".join(paragraphs[half * 2 :]) if len(paragraphs) > 2 else ""

        # Clean any leading header artifacts
        for k in result:
            result[k] = re.sub(r"^#+\s*.*?\n", "", result[k]).strip()

        return result

    def _fallback_synthesis(
        self,
        topic: str,
        category: str,
        user_context: str,
        mentor_tone: str,
        search_results: Dict[str, List[SearchResultItem]],
    ) -> tuple[str, str]:
        """High-grade deterministic fallback if API is unreachable."""
        summary_items = []
        for cat, items in search_results.items():
            summary_items.append(f"**From {cat}:**")
            for item in items[:2]:
                summary_items.append(f"- *{item.title}*: {item.snippet}")

        markdown = f"""### SECTION 1: THE QUESTION / INPUT FROM USER
**Inquiry / Dilemma:** {topic}
**Category Domain:** {category}
**Personal Context & Stakes:** {user_context if user_context else 'Prudent evaluation and self-preservation requested.'}
**Mentor Guidance Focus:** {mentor_tone} advisory orientation synthesizing real-time facts with protective decision-making.

### SECTION 2: SUMMARY OF SEARCH RESULTS
Recent multi-source intelligence across major information channels reveals key dynamics regarding **{topic}**:

{chr(10).join(summary_items)}

Overall, current affairs coverage indicates accelerating public interest, while specialized medical and academic databases emphasize rigorous verification before adopting unvetted interventions. Community forums mirror these concerns, with users consistently warning against rushed commitments and highlighting the importance of second opinions.

### SECTION 3: ANALYSIS & INSIGHTS FROM SEARCHED REFERENCES
A holistic evaluation of the evidence illuminates critical patterns:
1. **Divergence Between Theory and Practice:** While academic literature outlines optimal theoretical outcomes, social discussion forums reveal friction points where individuals struggle with bureaucratic delays, costs, and hidden risks.
2. **Asymmetry of Information:** In complex matters involving {category.lower()}, institutional entities frequently maintain informational leverage over the individual. 
3. **Protection Imperative:** The overarching mentor insight is to prioritize risk containment. Never trade irrevocable security for temporary short-term convenience.

### SECTION 4: ACTION PLANS & NEXT STEPS
To protect and empower yourself regarding {topic}, adopt the following phased roadmap:

1. **Immediate Phase (0 - 48 Hours): Fact Verification & Defense**
   - Secure and document all existing records, communications, and primary evidence.
   - Refrain from committing to irrevocable verbal or written agreements until independent confirmation is obtained.

2. **Strategic Phase (1 - 3 Weeks): Cross-Examination & Consultation**
   - Schedule a direct consultation with a certified, independent professional (licensed practitioner, legal counsel, or fiduciary).
   - Use the retrieved references to prepare targeted questions regarding secondary risks and exit clauses.

3. **Long-Term Phase (1 - 3 Months): Systemic Safeguards**
   - Establish ongoing monitoring checkpoints.
   - Build contingency reserves and diversification strategies to insulate yourself against potential downside developments.
"""
        return markdown, "Smart Mentor Knowledge Synthesis"

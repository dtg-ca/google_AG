"""
AI Repair Agent integrating Google Gemini with multi-model failover,
professional cost estimation (parts + labor), and intelligent heuristic synthesis.
"""

import os
import json
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
from config import PREFERRED_GEMINI_MODELS

class RepairAgent:
    """Expert AI diagnostic agent for equipment repairs and professional service estimation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize genai Client: {e}")

    def generate_repair_plan(
        self,
        category: str,
        subtype: str,
        make: str,
        model: str,
        problem: str,
        location: str,
        skill_level: str = "Intermediate",
        tools_on_hand: List[str] = None,
        research_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes user details and live research into an expert DIY repair plan,
        along with an itemized professional outside repair estimate (parts + labor).
        Tries Gemini API with multi-model failover; falls back to heuristic engine if unavailable.
        """
        tools_str = ", ".join(tools_on_hand) if tools_on_hand else "Standard household tools"
        research_summary = self._format_research_context(research_data)

        prompt = f"""
You are FixMate, a master diagnostic technician and certified repair engineer with 25+ years experience across appliances, electronics, automotive, HVAC, and mechanical equipment.

Analyze the user's repair request and synthesize the online research into an authoritative, practical DIY repair dossier.
IMPORTANT: You MUST also provide an itemized outside professional repair cost estimate (service call fee + labor hours & rate + OEM parts markup) for an outside repair location near the user's address, assuming the DIY solution is too difficult.

### Equipment Information:
- Category: {category}
- Specific Type: {subtype}
- Make / Brand: {make}
- Model Number: {model}
- User's Physical Location / Address: {location}
- User's Skill Level: {skill_level}
- Tools User Already Has: {tools_str}

### Problem Description:
{problem}

### Live Online Research & Discussion Forum Findings:
{research_summary}

---
Format your response as a valid JSON object strictly matching this schema (do NOT wrap with markdown backticks or commentary, just valid JSON):
{{
    "title": "Diagnosis and Repair Plan for {make} {model}",
    "safety_hazard_level": "Low | Moderate | High | Extreme",
    "safety_warnings": [
        "Immediate safety warning 1",
        "Immediate safety warning 2"
    ],
    "difficulty_rating": "1 to 5 (e.g. 2/5 - Beginner Friendly)",
    "estimated_time": "e.g. 45 - 60 minutes",
    "estimated_cost_diy": "e.g. $15 - $45",
    "estimated_cost_pro": "e.g. $280 - $450",
    "diy_recommendation": "Recommended | Proceed with Caution | Hire a Pro",
    "pro_repair_estimate": {{
        "diagnostic_call_fee": "$80 - $125 (typically credited toward labor if work approved)",
        "labor_hours": "1.0 - 2.0 hrs",
        "labor_hourly_rate": "$100 - $150 / hr",
        "labor_subtotal": "$150 - $280",
        "estimated_parts_retail": "$40 - $85 (OEM components with typical 25% shop markup)",
        "supplies_and_disposal": "$15 - $25",
        "total_pro_estimate": "$285 - $490",
        "diy_savings": "$240 - $440 (save ~85% doing it yourself)",
        "when_to_hire_pro": "Clear specific conditions where DIY is too difficult and calling an outside technician near {location} is advised."
    }},
    "root_cause_analysis": [
        {{
            "cause": "Name of probable cause",
            "probability": "High | Medium | Low",
            "explanation": "Why this happens based on forums and technical manuals",
            "test_method": "How to verify if this is the culprit"
        }}
    ],
    "required_tools": [
        "Tool 1 (e.g. 1/4 inch nut driver)",
        "Tool 2 (e.g. Multimeter)"
    ],
    "likely_parts_needed": [
        {{
            "part_name": "Name of part",
            "typical_cost": "$20 - $35",
            "part_number_hint": "OEM part code or search term",
            "replacement_tip": "Advice on OEM vs aftermarket"
        }}
    ],
    "step_by_step_guide": [
        {{
            "phase": "Phase 1: Disconnect & Prepare",
            "instruction": "Detailed clear instruction for this phase",
            "pro_tip": "Practical insider tip"
        }},
        {{
            "phase": "Phase 2: Disassembly & Access",
            "instruction": "Detailed clear instruction for this phase",
            "pro_tip": "Practical insider tip"
        }},
        {{
            "phase": "Phase 3: Component Inspection & Replacement",
            "instruction": "Detailed clear instruction for this phase",
            "pro_tip": "Practical insider tip"
        }},
        {{
            "phase": "Phase 4: Reassembly & Verification",
            "instruction": "Detailed clear instruction for this phase",
            "pro_tip": "Practical insider tip"
        }}
    ],
    "community_wisdom": [
        "Insight or forum tip reported by users who fixed this exact problem",
        "Common gotcha or pitfall to avoid"
    ],
    "local_sourcing_advice": "Specific practical guidance for getting parts or hiring outside repair centers in/near {location}."
}}
"""

        # Attempt Gemini API first with model fallback
        ai_result = None
        used_model = None

        if self.client:
            for model_name in PREFERRED_GEMINI_MODELS:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            response_mime_type="application/json"
                        )
                    )
                    if response and response.text:
                        raw_text = response.text.strip()
                        # Clean markdown json formatting if present
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        if raw_text.startswith("```"):
                            raw_text = raw_text[3:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]
                        raw_text = raw_text.strip()
                        
                        data = json.loads(raw_text)
                        ai_result = data
                        used_model = model_name
                        break
                except Exception as e:
                    print(f"Model {model_name} attempt error: {e}")
                    continue

        # If AI synthesis succeeded, return it
        if ai_result:
            ai_result["meta_source"] = f"Gemini ({used_model}) + Real-Time Forum Research"
            # Ensure pro_repair_estimate exists in ai_result
            if "pro_repair_estimate" not in ai_result:
                ai_result["pro_repair_estimate"] = self._build_default_pro_estimate(category, subtype, location)
            return ai_result

        # Graceful fallback: Expert Heuristic Engine
        print("Falling back to Heuristic Repair Synthesis Engine...")
        return self._generate_heuristic_plan(category, subtype, make, model, problem, location, skill_level, tools_on_hand, research_data)

    def _format_research_context(self, research_data: Optional[Dict[str, Any]]) -> str:
        """Formats collected web and forum snippets for AI prompt ingestion."""
        if not research_data:
            return "No prior web search data provided."

        lines = []
        if research_data.get("guides"):
            lines.append("--- Technical Guides Found ---")
            for g in research_data["guides"][:3]:
                lines.append(f"Title: {g.get('title')}\nSource: {g.get('source')}\nSummary: {g.get('snippet')}\n")

        if research_data.get("forums"):
            lines.append("--- Community Forum Discussions (Reddit/iFixit/DIY) ---")
            for f in research_data["forums"][:3]:
                lines.append(f"Forum: {f.get('source')} - {f.get('title')}\nInsights: {f.get('snippet')}\n")

        if research_data.get("pro_shops"):
            lines.append("--- Nearby Professional Repair Centers Discovered ---")
            for ps in research_data["pro_shops"][:3]:
                lines.append(f"Service: {ps.get('title')} ({ps.get('source')})\nInfo: {ps.get('snippet')}\n")

        if research_data.get("local_parts"):
            lines.append("--- Local Parts & Stores ---")
            for p in research_data["local_parts"][:3]:
                lines.append(f"Store: {p.get('title')} ({p.get('source')})\nDetails: {p.get('snippet')}\n")

        return "\n".join(lines) if lines else "Search completed with standard knowledge patterns."

    def _build_default_pro_estimate(self, category: str, subtype: str, location: str) -> Dict[str, str]:
        """Calculates realistic itemized professional repair costs based on equipment type."""
        cat_lower = category.lower()
        sub_lower = subtype.lower()

        if "appliance" in cat_lower:
            diag = "$85 - $119"
            hours = "1.0 - 2.0 hrs"
            rate = "$110 - $145 / hr"
            labor = "$140 - $260"
            parts = "$45 - $95 (OEM with 25% shop markup)"
            supplies = "$15 - $25"
            total = "$285 - $480"
            savings = "$240 - $410 (save approx 85%)"
            hire_criteria = "If the drum bearings are seized, the main electronic control board has burned traces, or access requires two people to move stacked units."
        elif "hvac" in cat_lower:
            diag = "$99 - $149"
            hours = "1.5 - 3.0 hrs"
            rate = "$125 - $185 / hr"
            labor = "$200 - $450"
            parts = "$80 - $220"
            supplies = "$25 - $45"
            total = "$400 - $850"
            savings = "$350 - $700 (save approx 80%)"
            hire_criteria = "If refrigerant line brazing/charging is required, gas valves are leaking, or the heat exchanger is cracked (carbon monoxide danger)."
        elif "automotive" in cat_lower:
            diag = "$95 - $150"
            hours = "1.5 - 2.5 hrs"
            rate = "$120 - $175 / hr"
            labor = "$180 - $390"
            parts = "$60 - $180 (OEM parts with shop markup)"
            supplies = "$20 - $35"
            total = "$350 - $720"
            savings = "$280 - $580 (save approx 80%)"
            hire_criteria = "If brake hydraulic lines need bleeding without assistance, high-torque hub nuts are seized, or vehicle lift is necessary."
        elif "electronic" in cat_lower:
            diag = "$49 - $89"
            hours = "1.0 - 1.5 hrs"
            rate = "$80 - $120 / hr"
            labor = "$90 - $170"
            parts = "$50 - $140 (OLED screen / battery)"
            supplies = "$10 - $20"
            total = "$190 - $390"
            savings = "$130 - $280 (save approx 70%)"
            hire_criteria = "If micro-soldering BGA chips is required, display glass separation requires liquid optical adhesive UV curing, or water damage has corroded logic board traces."
        elif "lawn" in cat_lower:
            diag = "$60 - $90"
            hours = "1.0 - 1.5 hrs"
            rate = "$85 - $115 / hr"
            labor = "$95 - $160"
            parts = "$25 - $60 (Carb kit / recoil starter)"
            supplies = "$10 - $15"
            total = "$190 - $320"
            savings = "$150 - $260 (save approx 80%)"
            hire_criteria = "If crankshaft is bent from striking a rock or engine block cylinder lacks compression due to scored cylinder walls."
        else:
            diag = "$75 - $110"
            hours = "1.0 - 1.5 hrs"
            rate = "$95 - $135 / hr"
            labor = "$120 - $200"
            parts = "$35 - $75"
            supplies = "$10 - $20"
            total = "$240 - $400"
            savings = "$190 - $330 (save approx 80%)"
            hire_criteria = "If specialized pullers, high-pressure test gauges, or proprietary calibration software are necessary."

        return {
            "diagnostic_call_fee": diag,
            "labor_hours": hours,
            "labor_hourly_rate": rate,
            "labor_subtotal": labor,
            "estimated_parts_retail": parts,
            "supplies_and_disposal": supplies,
            "total_pro_estimate": total,
            "diy_savings": savings,
            "when_to_hire_pro": hire_criteria
        }

    def _generate_heuristic_plan(
        self,
        category: str,
        subtype: str,
        make: str,
        model: str,
        problem: str,
        location: str,
        skill_level: str,
        tools_on_hand: Optional[List[str]],
        research_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        High-reliability rule-based synthesizer that merges real web research
        and equipment diagnostic patterns into a comprehensive solution.
        """
        prob_lower = problem.lower()
        sub_lower = subtype.lower()

        # Determine safety hazard
        if any(w in prob_lower or w in sub_lower for w in ["gas", "refrigerant", "freon", "microwave", "furnace", "high voltage", "capacitor", "240v"]):
            hazard = "High"
            warnings = [
                "HIGH VOLTAGE / FUEL HAZARD: Ensure all circuit breakers are switched off and fuel valves are shut before opening panels.",
                "Capacitors and high-voltage components retain dangerous charge even when unplugged. Discharge safely or call a professional."
            ]
        elif any(w in prob_lower or w in sub_lower for w in ["water", "leak", "drain", "pipe", "pump"]):
            hazard = "Moderate"
            warnings = [
                "ELECTRICAL & SLIP HAZARD: Disconnect power cord from wall before inspecting standing water.",
                "Shut off water supply inlet valves to prevent accidental flooding while hoses are detached."
            ]
        else:
            hazard = "Low"
            warnings = [
                "Always disconnect equipment from electrical power or remove batteries before servicing.",
                "Wear safety glasses and work gloves to protect against sharp sheet metal edges."
            ]

        # Extract forum insights from research if available
        forum_insights = []
        if research_data and research_data.get("forums"):
            for f in research_data["forums"]:
                snip = f.get("snippet", "")
                if len(snip) > 20:
                    forum_insights.append(f"{f.get('source')}: {snip[:160]}...")
        if not forum_insights:
            forum_insights = [
                f"Forum consensus on {make}: Always inspect mechanical blockages and debris traps before buying replacement electronics.",
                "Community tip: Label wiring harnesses with masking tape and snap phone photos of wire routing before detaching."
            ]

        # Determine probable causes based on domain heuristics
        causes = []
        if "drain" in prob_lower or "pump" in prob_lower:
            causes.append({
                "cause": "Debris Blockage in Drain Pump or Filter Trap",
                "probability": "High",
                "explanation": "Coins, lint, small garments, or foreign objects frequently lodge in the pump impeller or coin trap.",
                "test_method": "Remove pump filter or detach inlet hose; inspect impeller blades for rotation and foreign debris."
            })
            causes.append({
                "cause": "Failed or Seized Drain Pump Motor",
                "probability": "Medium",
                "explanation": "The motor winding can burn out or the plastic impeller can strip from the internal shaft.",
                "test_method": "Measure resistance across pump terminals with a multimeter (expect 15-25 ohms); check if motor receives 120V but fails to spin."
            })
            causes.append({
                "cause": "Lid Switch or Door Lock Interlock Malfunction",
                "probability": "Medium",
                "explanation": "Many washers will not engage the drain or spin cycle if the door latch contact is open or oxidized.",
                "test_method": "Listen for the physical click on cycle start; test switch continuity with a multimeter."
            })
        elif "heat" in prob_lower or "dryer" in prob_lower:
            causes.append({
                "cause": "Blown Thermal Fuse or High-Limit Thermostat",
                "probability": "High",
                "explanation": "Restricted exhaust airflow causes internal temperature spikes, tripping the non-resettable thermal safety fuse.",
                "test_method": "Perform a multimeter continuity test on the thermal fuse terminals; zero resistance means good, open circuit means blown."
            })
            causes.append({
                "cause": "Burned Out Heating Element Coil",
                "probability": "Medium",
                "explanation": "Thermal fatigue over years of cycles causes the coiled resistance wire to snap or ground against the casing.",
                "test_method": "Visually inspect element coils for physical breaks; check resistance (typically 8 to 12 ohms)."
            })
        elif "start" in prob_lower or "crank" in prob_lower or "spark" in prob_lower:
            causes.append({
                "cause": "Stale Fuel or Clogged Carburetor Jets",
                "probability": "High",
                "explanation": "Ethanol in pump fuel evaporates over weeks/months leaving sticky varnish that blocks micro-jets.",
                "test_method": "Spray 1 second of carb cleaner into the air intake; if engine fires briefly and dies, fuel delivery is blocked."
            })
            causes.append({
                "cause": "Fouled Spark Plug or Weak Ignition Coil",
                "probability": "Medium",
                "explanation": "Carbon buildup or oil fouling prevents high-voltage spark from jumping the plug gap.",
                "test_method": "Remove plug, ground threaded body against engine block, pull starter to observe blue spark."
            })
        else:
            causes.append({
                "cause": f"Primary Component Wear or Fault in {subtype}",
                "probability": "High",
                "explanation": f"Symptom aligns with standard wear patterns documented for {make} {model}.",
                "test_method": "Inspect connectors, verify power supply, and check physical moving parts for obstruction."
            })
            causes.append({
                "cause": "Electrical Connection or Sensor Signal Failure",
                "probability": "Medium",
                "explanation": "Vibration, thermal expansion, or corrosion can loosen wire terminals or degrade sensors.",
                "test_method": "Check harness plug seating and measure reference voltages at the control board."
            })

        # Step by step guide
        steps = [
            {
                "phase": "Phase 1: Safety Isolation & Pre-Work",
                "instruction": f"Disconnect {make} {model} from main power. If dealing with water or gas lines, shut off the upstream supply valves. Clear an organized workspace and keep a parts tray handy for fasteners.",
                "pro_tip": "Take close-up smartphone photos of every screw location, wire color, and bracket orientation before disassembly."
            },
            {
                "phase": "Phase 2: Access & Component Inspection",
                "instruction": f"Remove access panel or housing covering the suspected failure area. Visually inspect for burned terminals, foreign debris, worn drive belts, or leaking fluid.",
                "pro_tip": "Keep magnetic dish nearby to avoid dropping small screws into internal chassis wells."
            },
            {
                "phase": "Phase 3: Diagnostic Verification & Part Swap",
                "instruction": "Perform diagnostic isolation test (continuity or physical check). If testing confirms a failed component, unclip the retaining brackets and swap in the replacement part with exact orientation.",
                "pro_tip": "Never force plastic clips; use a flat pry tool to relieve tension gently to avoid snapping brittle tabs."
            },
            {
                "phase": "Phase 4: Reassembly & Calibration Run",
                "instruction": "Reinstall panels, reconnect wire harnesses firmly, restore supply lines, and plug into power. Run an empty short diagnostic cycle while watching for unusual noises or leaks.",
                "pro_tip": "Stay by the machine during the entire first test cycle to ensure normal cutoff behavior."
            }
        ]

        pro_estimate = self._build_default_pro_estimate(category, subtype, location)

        return {
            "title": f"Expert Repair Dossier: {make} {model} ({subtype})",
            "safety_hazard_level": hazard,
            "safety_warnings": warnings,
            "difficulty_rating": "2/5 - DIY Friendly",
            "estimated_time": "45 - 75 minutes",
            "estimated_cost_diy": "$20 - $60",
            "estimated_cost_pro": pro_estimate.get("total_pro_estimate", "$195 - $320"),
            "diy_recommendation": "Recommended DIY Project",
            "pro_repair_estimate": pro_estimate,
            "root_cause_analysis": causes,
            "required_tools": [
                "1/4\" and 5/16\" Hex Nut Drivers / Socket Set",
                "Phillips #2 and Flathead Screwdrivers",
                "Digital Multimeter (Continuity / Resistance)",
                "Pliers / Slip-joint Channel Locks",
                "Safety Glasses and Work Gloves"
            ],
            "likely_parts_needed": [
                {
                    "part_name": f"{subtype} Replacement Assembly / Wear Part",
                    "typical_cost": "$25 - $50",
                    "part_number_hint": f"{make} OEM Part for {model}",
                    "replacement_tip": "Compare serial/revision number on model tag to ensure exact revision match."
                }
            ],
            "step_by_step_guide": steps,
            "community_wisdom": forum_insights,
            "local_sourcing_advice": f"For immediate parts acquisition in {location}, visit local supply houses or major hardware stores (Home Depot / Lowe's / Ace) or auto/appliance supply distributors. If electrical diagnostics show live mains voltage anomalies, stop and hire a licensed local specialist.",
            "meta_source": "Expert Diagnostic Engine + Live Forum Research Grounding"
        }

    def ask_followup(
        self,
        question: str,
        chat_history: List[Dict[str, str]],
        dossier: Dict[str, Any]
    ) -> str:
        """Handles interactive follow-up questions from the user during the repair."""
        context = f"""
You are FixMate, helping a user live through their DIY repair of:
Equipment: {dossier.get('title', 'Equipment Repair')}
Safety Hazard: {dossier.get('safety_hazard_level', 'Moderate')}
Root Causes identified: {json.dumps(dossier.get('root_cause_analysis', []))}
Pro Estimate: {json.dumps(dossier.get('pro_repair_estimate', {}))}
"""
        messages_prompt = f"{context}\n\nUser Question: {question}\n\nProvide direct, practical, step-by-step guidance. Emphasize safety."

        if self.client:
            for model_name in PREFERRED_GEMINI_MODELS:
                try:
                    resp = self.client.models.generate_content(
                        model=model_name,
                        contents=messages_prompt
                    )
                    if resp and resp.text:
                        return resp.text.strip()
                except Exception:
                    continue

        # Heuristic follow-up fallback
        q_low = question.lower()
        if "pro" in q_low or "cost" in q_low or "hire" in q_low or "quote" in q_low:
            est = dossier.get("pro_repair_estimate", {})
            return f"Outside professional repair cost estimate: Total estimated cost is {est.get('total_pro_estimate', '$250-$450')}. This breaks down to a Diagnostic/Trip Fee of {est.get('diagnostic_call_fee', '$85-$120')}, Labor of {est.get('labor_subtotal', '$150-$250')} ({est.get('labor_hours', '1.5 hrs')} @ {est.get('labor_hourly_rate', '$120/hr')}), and Parts around {est.get('estimated_parts_retail', '$45-$85')}. DIY saves you {est.get('diy_savings', 'approx 80%')}."
        elif "multimeter" in q_low or "test" in q_low:
            return "To test with a multimeter: 1) Unplug the equipment first. 2) Set meter to lowest Ohms (Ω) or Continuity beep mode. 3) Touch probe tips together to verify 0.0 ohms. 4) Place probes on the component's two disconnected terminals. A good fuse/switch reads near 0 ohms (closed circuit). An open/broken component reads 'O.L' or infinite resistance."
        elif "stuck" in q_low or "remove" in q_low or "screw" in q_low:
            return "If a screw or clip is stuck: 1) Check for hidden fasteners underneath rubber feet, labels, or decorative trim. 2) Apply a drop of penetrating oil (like PB Blaster or WD-40) and wait 5 minutes. 3) Use a rubber band over the screw head to improve screwdriver bit grip and prevent stripping."
        elif "safe" in q_low or "shock" in q_low:
            return "Safety Priority: Unplug the unit immediately from the wall outlet. If dealing with large capacitors (microwaves/HVAC), short terminals with an insulated screwdriver across a 20k ohm resistor before touching any wires."
        else:
            return f"Regarding your repair: Focus first on inspecting mechanical connections and verifying that the part matches the OEM specifications for your model. Remember to keep the unit completely unplugged while handling internal parts."

import streamlit as st
import os
import json
import re
from google import genai
from google.genai import types
from fpdf import FPDF

# Initialize the Gemini client
# Ensure that the GOOGLE_API_KEY environment variable is set.
try:
    client = genai.Client()
except Exception as e:
    client = None

st.set_page_config(page_title="Expert Diet Planner", page_icon="🥗", layout="wide")

st.title("🥗 Expert Diet Planner")
st.markdown("""
Welcome! I am your Expert Diet Planner. Upload your preferences or type them below, and I will generate a custom weekly diet plan featuring quick (under 30 mins) Continental, Mediterranean, Chinese, and South Asian recipes with ingredients you can easily find in the US or Canada.
""")

if not os.environ.get("GOOGLE_API_KEY"):
    st.warning("Please set the `GOOGLE_API_KEY` environment variable to use this application.")
    api_key_input = st.text_input("Or enter your Google API Key here:", type="password")
    if api_key_input:
        client = genai.Client(api_key=api_key_input)
else:
    if client is None:
        client = genai.Client()

def parse_json_from_text(text):
    # Extract JSON between triple backticks if present
    match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        json_str = text.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def generate_diet_plan(preferences_text):
    prompt = f"""
You are an expert Diet Planner with a long and distinguished list of satisfied clients. 
Create a Weekly Diet Plan based on the user's diet type and cuisine preferences.

User Preferences:
{preferences_text}

Constraints & Requirements:
1. Create a 7-day Diet Plan.
2. Each day must include Breakfast, Lunch, Dinner, and an optional Snack.
3. Include recommended time slots in a 24-hour window, taking into account 8 hours of sleep (e.g., Sleep 11 PM - 7 AM; Breakfast 8:00 AM, Lunch 1:00 PM, Snack 4:00 PM, Dinner 7:30 PM).
4. The plan should ONLY contain recipes in these cuisine types: Continental, Mediterranean, Chinese, South Asian.
5. Cooking/preparation time for each recipe MUST NOT exceed 30 minutes.
6. Limit recipes to ingredients that can be easily procured from a local grocery store in the USA or Canada.
7. Generate a consolidated ingredient list that fully covers all recommended recipes for the week, including required quantities.
8. For each meal, provide: Recipe Name, Ingredients, Easy-to-follow Recipe instructions, and Cooking Tips (if available).

You MUST return your response as a valid JSON object with the following structure:
{{
  "ingredient_list": [
    {{"item": "Chicken Breast", "quantity": "2 lbs"}},
    {{"item": "Olive Oil", "quantity": "1 bottle"}}
  ],
  "weekly_plan": [
    {{
      "day": "Monday",
      "meals": [
        {{
          "type": "Breakfast",
          "time": "08:00 AM",
          "recipe_name": "Mediterranean Scrambled Eggs",
          "cuisine": "Mediterranean",
          "prep_time": "10 mins",
          "ingredients": ["2 Eggs", "Spinach", "Feta Cheese"],
          "recipe": "1. Beat eggs. 2. Sauté spinach. 3. Add eggs and cook. 4. Top with feta.",
          "cooking_tips": "Don't overcook the eggs."
        }}
      ]
    }}
  ]
}}
Ensure the output is strictly valid JSON without trailing commas.
"""
    
    try:
        # Use gemini-3.1-pro-preview for better adherence to complex schemas and planning
        response = client.models.generate_content(
            model='gemini-3.1-pro-preview',
            contents=prompt,
        )
        return parse_json_from_text(response.text)
    except Exception as e:
        st.error(f"Error calling Google GenAI API: {e}")
        return None

def generate_pdf(plan_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, text="Weekly Diet Plan", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    for day_plan in plan_data.get("weekly_plan", []):
        pdf.set_font("Helvetica", "B", 16)
        day = str(day_plan.get('day', '')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, text=f"Day: {day}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        for meal in day_plan.get("meals", []):
            pdf.set_font("Helvetica", "B", 12)
            m_type = str(meal.get('type', '')).encode('latin-1', 'replace').decode('latin-1')
            m_time = str(meal.get('time', '')).encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 8, text=f"{m_type} - {m_time}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", "", 11)
            r_name = str(meal.get('recipe_name', '')).encode('latin-1', 'replace').decode('latin-1')
            cuisine = str(meal.get('cuisine', 'Mixed')).encode('latin-1', 'replace').decode('latin-1')
            prep = str(meal.get('prep_time', '< 30 mins')).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(pdf.epw, 6, text=f"Recipe: {r_name} ({cuisine} | {prep})", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, text="Ingredients:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            ingredients = ", ".join(meal.get("ingredients", []))
            ingredients = ingredients.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(pdf.epw, 6, text=ingredients, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, text="Recipe:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            recipe_text = str(meal.get('recipe', '')).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(pdf.epw, 6, text=recipe_text, new_x="LMARGIN", new_y="NEXT")
            
            if meal.get("cooking_tips"):
                pdf.set_font("Helvetica", "I", 11)
                tip = str(meal.get('cooking_tips', '')).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(pdf.epw, 6, text=f"Tip: {tip}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(5)
        pdf.ln(5)
        
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, text="Weekly Grocery List", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "", 12)
    for item in plan_data.get("ingredient_list", []):
        i_name = str(item.get('item', '')).encode('latin-1', 'replace').decode('latin-1')
        i_qty = str(item.get('quantity', '')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 8, text=f"- {i_name}: {i_qty}", new_x="LMARGIN", new_y="NEXT")
        
    return bytes(pdf.output())

# Input Section
st.subheader("📝 Your Diet Preferences")
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload a text file with your preferences", type=["txt"])
    
with col2:
    text_input = st.text_area("Or type your diet type (e.g., Keto, Vegan) and cuisine preferences:", height=150)

preferences = ""
if uploaded_file is not None:
    preferences = uploaded_file.getvalue().decode("utf-8")
elif text_input:
    preferences = text_input

if "plan_data" not in st.session_state:
    st.session_state.plan_data = None

if st.button("Generate Weekly Diet Plan 🚀"):
    if not preferences.strip():
        st.error("Please provide your diet preferences via file upload or text input.")
    elif client is None:
        st.error("Google API client is not initialized. Please provide an API key.")
    else:
        with st.spinner("Our expert planner is curating your personalized diet plan... This might take a minute."):
            plan_data = generate_diet_plan(preferences)
            if plan_data:
                st.session_state.plan_data = plan_data
            else:
                st.error("Failed to parse the diet plan from the AI model. Please try again.")

if st.session_state.plan_data:
    plan_data = st.session_state.plan_data
    st.success("Your diet plan is ready!")
    
    # Download Button
    pdf_bytes = generate_pdf(plan_data)
    st.download_button(
        label="💾 Download Plan as PDF",
        data=pdf_bytes,
        file_name="Weekly_Diet_Plan.pdf",
        mime="application/pdf"
    )
    
    # Layout for Display
    tab1, tab2 = st.tabs(["📅 Weekly Diet Plan", "🛒 Weekly Grocery List"])
    
    with tab1:
        st.header("Your 7-Day Meal Plan")
        
        # Display each day in an expander
        for day_plan in plan_data.get("weekly_plan", []):
            with st.expander(f"🗓️ {day_plan.get('day')}", expanded=True):
                # Create columns for meals
                meals = day_plan.get("meals", [])
                if not meals:
                    st.write("No meals planned for this day.")
                    continue
                
                for meal in meals:
                    st.markdown(f"### {meal.get('type')} 🕒 {meal.get('time')}")
                    st.markdown(f"**{meal.get('recipe_name')}** ({meal.get('cuisine', 'Mixed')} | ⏱️ {meal.get('prep_time', '< 30 mins')})")
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.markdown("**Ingredients:**")
                        for ing in meal.get("ingredients", []):
                            st.markdown(f"- {ing}")
                    with c2:
                        st.markdown("**Recipe:**")
                        st.write(meal.get("recipe", ""))
                        if meal.get("cooking_tips"):
                            st.info(f"💡 **Tip:** {meal.get('cooking_tips')}")
                    st.divider()
                    
    with tab2:
        st.header("Weekly Grocery List")
        st.markdown("Here are all the ingredients you will need for the week, easily procurable at local USA/Canada grocery stores.")
        
        # Display as a clean table
        ingredients = plan_data.get("ingredient_list", [])
        if ingredients:
            # Convert to markdown table format for simple presentation
            table_md = "| Item | Quantity |\n|---|---|\n"
            for item in ingredients:
                table_md += f"| {item.get('item')} | {item.get('quantity')} |\n"
            st.markdown(table_md)
        else:
            st.write("Ingredient list could not be generated.")

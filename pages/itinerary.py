import streamlit as st
import google.generativeai as genai
import requests
import json
from fpdf import FPDF
import io
from PIL import Image
import re
from datetime import datetime, timedelta, date

# API KEYS
GEMINI_API_KEY = st.secrets["api_keys"]["GEMINI_API_KEY"]

SERP_API_KEY = st.secrets["api_keys"]["SERP_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# User Inputs
user_data = st.session_state.get("user_data", {})
destination = user_data.get("destination", "Not Set")
budget = user_data.get("budget", "Not Set")
travelers = user_data.get("travelers", "Not Set")
start_date = user_data.get("start_date", "Not Set")
end_date = user_data.get("end_date", "Not Set")
preferences = user_data.get("preferences", [])
transport_mode = user_data.get("transport_mode", "Not Set")
food_preference = user_data.get("food_preference", "Not Set")

# Calculate number of days
if isinstance(start_date, datetime) and isinstance(end_date, datetime):
    days = (end_date - start_date).days
    days = max(1, days)
else:
    days = 3

def clean_text(text):
    """Remove all non-ASCII characters and replace ₹ with Rs."""
    if text is None:
        return ""
    text = str(text)
    text = text.replace("₹", "Rs.")
    return ''.join(char for char in text if ord(char) < 128)

def get_detailed_itinerary(destination, days, budget, preferences, transport_mode, food_preference, start_date, travelers):
    """Generate a structured itinerary using Gemini with strict ASCII output"""
    days = (end_date - start_date).days + 1
    start_date_str = start_date.strftime('%d %B %Y') if isinstance(start_date, (date, datetime)) else "upcoming date"
    end_date_str = end_date.strftime('%d %B %Y') if isinstance(end_date, (date, datetime)) else "upcoming date"
    
    prompt = f"""
    Create a detailed itinerary for {days}-day trip to {destination} with budget Rs. {budget} for {travelers} travelers.
    Dates: {start_date_str} to {end_date_str}
    Preferences: {', '.join(preferences) if preferences else 'None'}
    Transportation: {transport_mode}
    Food: {food_preference}
    
    Important Rules:
    1. Use ONLY ASCII characters (no ₹, emoji, or special symbols)
    2. Use "Rs." instead of any currency symbols
    3. Return valid JSON with this structure:
    {{
        "title": "string",
        "budget_breakdown": {{
            "accommodation": "string",
            "transportation": "string",
            "food": "string",
            "activities": "string",
            "miscellaneous": "string",
            "total": "string"
        }},
        "days": [
            {{
                "day": number,
                "date": "string",
                "activities": "string",
                "accommodation": "string",
                "meals": "string",
                "transportation": "string",
                "highlights": "string",
                "tips": "string"
            }}
        ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```\s*$', '', response_text)
        itinerary_data = json.loads(response_text)
        
        if "days" not in itinerary_data:
            raise ValueError("Response missing 'days' field")
            
        if len(itinerary_data["days"]) != days:
            adjusted_days = []
            for i in range(days):
                if i < len(itinerary_data["days"]):
                    day = itinerary_data["days"][i]
                    day["day"] = i + 1
                    if isinstance(start_date, (date, datetime)):
                        day["date"] = (start_date + timedelta(days=i)).strftime('%A, %d %B %Y')
                else:
                    day_date = (start_date + timedelta(days=i)) if isinstance(start_date, (date, datetime)) else None
                    day_date_str = day_date.strftime('%A, %d %B %Y') if day_date else f"Day {i+1}"
                    day = {
                        "day": i+1,
                        "date": day_date_str,
                        "activities": f"Day {i+1}: Explore {destination}",
                        "accommodation": f"Accommodation for {travelers}",
                        "meals": food_preference,
                        "transportation": transport_mode,
                        "highlights": f"Discovering {destination}",
                        "tips": "Ask locals for recommendations"
                    }
                adjusted_days.append(day)
            itinerary_data["days"] = adjusted_days
        
        return itinerary_data
        
    except Exception as e:
        st.error(f"Error generating itinerary: {e}")
        fallback_data = {
            "title": f"{days}-Day {destination} Trip",
            "budget_breakdown": {"total": f"Rs. {budget}"},
            "days": [{
                "day": i+1,
                "date": (start_date + timedelta(days=i)).strftime('%A, %d %B %Y') if isinstance(start_date, (date, datetime)) else f"Day {i+1}",
                "activities": f"Day {i+1} activities",
                "accommodation": "Standard accommodation",
                "meals": food_preference,
                "transportation": transport_mode,
                "highlights": "Exploring the destination",
                "tips": "Enjoy your trip"
            } for i in range(days)]
        }
        return fallback_data

def get_location_images(destination, count=3):
    """Get destination images with error handling"""
    images = []
    try:
        url = f"https://serpapi.com/search.json?q={destination} tourist attractions&tbm=isch&api_key={SERP_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200 and 'images_results' in response.json():
            for i in range(min(count, len(response.json()['images_results']))):
                try:
                    img_url = response.json()['images_results'][i]['original']
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        images.append(Image.open(io.BytesIO(img_response.content)))
                except Exception:
                    continue
    except Exception:
        pass
    return images
def generate_itinerary_pdf(itinerary_data, images=None):
    """Generate PDF using only Arial font with guaranteed ASCII-only text"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Strict ASCII cleaner - removes ALL non-ASCII characters
        def strict_ascii(text):
            if text is None:
                return ""
            text = str(text)
            # First replace known problematic characters
            text = text.replace("₹", "Rs.").replace("✈", "").replace("•", "-")
            # Then remove any remaining non-ASCII
            return ''.join(char for char in text if ord(char) < 128)
        
        # Title (force cleaned)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, strict_ascii(itinerary_data.get("title", "Travel Itinerary")), 0, 1, 'C')
        
        # Basic info (force cleaned)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, strict_ascii(f"Destination: {destination}"), 0, 1)
        pdf.cell(0, 10, strict_ascii(f"Duration: {days} days"), 0, 1)
        pdf.cell(0, 10, strict_ascii(f"Budget: Rs. {budget}"), 0, 1)  # Rs. instead of ₹
        pdf.ln(10)
        
        # Budget breakdown (force cleaned)
        if "budget_breakdown" in itinerary_data:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Budget Breakdown", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            for category, amount in itinerary_data["budget_breakdown"].items():
                clean_cat = strict_ascii(category).capitalize()
                clean_amt = strict_ascii(amount)
                pdf.cell(95, 8, f"{clean_cat}:", 1)
                pdf.cell(95, 8, clean_amt, 1, 1)
            pdf.ln(5)
        
        # Daily itinerary (force cleaned)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Daily Itinerary", 0, 1)
        pdf.ln(5)
        
        for day in itinerary_data.get("days", []):
            pdf.set_font("Arial", 'B', 12)
            day_title = strict_ascii(f"Day {day.get('day', '')}: {day.get('date', '')}")
            pdf.cell(0, 10, day_title, 0, 1)
            
            # Function to add cleaned sections
            def add_cleaned_section(title, content):
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 8, strict_ascii(title) + ":", 0, 1)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 8, strict_ascii(content))
                pdf.ln(4)
            
            add_cleaned_section("Activities", day.get("activities", ""))
            add_cleaned_section("Accommodation", day.get("accommodation", ""))
            add_cleaned_section("Meals", day.get("meals", ""))
            add_cleaned_section("Transportation", day.get("transportation", ""))
            add_cleaned_section("Highlights", day.get("highlights", ""))
            
            # Clean tips
            if "tips" in day:
                pdf.set_font("Arial", 'I', 10)
                pdf.multi_cell(0, 8, "Tip: " + strict_ascii(day['tips']))
            
            pdf.ln(10)
        
        # Save PDF
        pdf_output = "VoyageMind_Itinerary.pdf"
        pdf.output(pdf_output)
        return pdf_output
        
    except Exception as e:
        # Ultra-simple fallback that cannot possibly fail
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Travel Itinerary", 0, 1, 'C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Destination: {destination}", 0, 1)
        pdf.cell(0, 10, f"Duration: {days} days", 0, 1)
        pdf.cell(0, 10, f"Budget: Rs. {budget}", 0, 1)
        
        fallback_output = "VoyageMind_Fallback.pdf"
        pdf.output(fallback_output)
        return fallback_output
if st.button("✅ Generate Itinerary"):
    st.info("Generating your personalized itinerary... This may take a moment.")
    
    with st.spinner("Getting destination images..."):
        images = get_location_images(destination)
    
    with st.spinner("Creating your travel plan..."):
        itinerary_data = get_detailed_itinerary(
            destination, days, budget, preferences,
            transport_mode, food_preference, start_date, travelers
        )
    
    with st.spinner("Generating PDF..."):
        itinerary_pdf = generate_itinerary_pdf(itinerary_data, images)
    
    st.success("Itinerary generated successfully!")
    
    st.subheader("Itinerary Summary")
    st.write(f"Destination: {destination}")
    if isinstance(start_date, datetime) and isinstance(end_date, datetime):
        st.write(f"Dates: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}")
    st.write(f"Budget: Rs. {budget}")
    
    with open(itinerary_pdf, "rb") as file:
        st.download_button(
            "📥 Download Itinerary", 
            file, 
            file_name=f"{destination}_Itinerary.pdf", 
            mime="application/pdf"
        )

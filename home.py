import streamlit as st
import datetime
from streamlit_extras.stylable_container import stylable_container
from streamlit.components.v1 import html

# 🌍 Page Config
st.set_page_config(
    page_title="VoyageMind - AI Travel Planner", 
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fixed CSS with cursor solution
st.markdown("""
<style>
    html, body, [class*="css"] {
        cursor: auto !important;
    }
    .main {
        background-color: #f8f9fa;
    }
    .stForm {
        background-color: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .header {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .travel-btn {
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# ✅ Initialize Session State
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "trip_type": "Leisure"
    }

# 🌍 Hero Header
with st.container():
    st.markdown("""
    <div class="header">
        <h1 style='text-align: center; margin-bottom: 0.5rem;'>✈️ VoyageMind</h1>
        <h3 style='text-align: center; font-weight: 300;'>AI that thinks like a traveler</h3>
        <p style='text-align: center; font-size: 1.1rem;'>Plan your perfect trip with our intelligent travel assistant that understands real traveler needs</p>
    </div>
    """, unsafe_allow_html=True)

# ✅ Trip Type Selector
trip_types = ["Leisure", "Adventure", "Business", "Family", "Solo", "Honeymoon"]
cols = st.columns(len(trip_types))
for i, trip_type in enumerate(trip_types):
    with cols[i]:
        if st.button(trip_type, key=f"trip_type_{i}", 
                    use_container_width=True,
                    type="primary" if st.session_state.user_data.get("trip_type") == trip_type else "secondary"):
            st.session_state.user_data["trip_type"] = trip_type

# ✅ User Input Form
with st.form("trip_form"):
    with stylable_container(
        key="form_container",
        css_styles="""
            {
                background-color: white;
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        """
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Destination Details")
            destination = st.text_input("City/Country", 
                                      value=st.session_state.user_data.get("destination", ""),
                                      placeholder="Where do you want to go?")
            
            budget = st.selectbox("Budget Range", 
                                ["Budget (₹5k-15k)", "Mid-range (₹15k-50k)", "Luxury (₹50k+)"],
                                index=1)
            
            travelers = st.slider("Number of Travelers", 1, 20, 
                                 value=st.session_state.user_data.get("travelers", 2))
            
        with col2:
            st.subheader("📅 Travel Dates")
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("From", 
                                         value=st.session_state.user_data.get("start_date", datetime.date.today()),
                                         min_value=datetime.date.today())
            with date_col2:
                end_date = st.date_input("To", 
                                       value=st.session_state.user_data.get("end_date", datetime.date.today() + datetime.timedelta(days=7)),
                                       min_value=start_date)
            
            days = (end_date - start_date).days + 1
            st.caption(f"Trip Duration: {days} days")
            
            transport_mode = st.selectbox("Preferred Transport", 
                                        ["Flight ✈️", "Train 🚆", "Road Trip 🚗", "Cruise 🚢"],
                                        index=1)
            
        st.subheader("🎯 Travel Preferences")
        pref_col1, pref_col2 = st.columns(2)
        with pref_col1:
            pace = st.radio("Travel Pace", 
                           ["Relaxed", "Moderate", "Fast-paced"],
                           horizontal=True)
            
            food_preference = st.radio("Food Preference", 
                                      ["Vegetarian 🌱", "Non-Vegetarian 🍗", "Vegan 🥑"],
                                      horizontal=True)
            
        with pref_col2:
            interests = st.multiselect("Interests",
                                     ["History & Culture", "Nature & Wildlife", "Food & Drink", 
                                      "Shopping", "Adventure Sports", "Wellness & Spa",
                                      "Nightlife", "Photography", "Local Experiences"],
                                     default=["History & Culture", "Nature & Wildlife"])
            
            special_needs = st.multiselect("Special Requirements",
                                         ["Wheelchair Access", "Pet Friendly", 
                                          "Child Friendly", "Senior Friendly",
                                          "Dietary Restrictions"])
        
        submitted = st.form_submit_button("✨ Generate Smart Itinerary", type="primary")
        
        if submitted:
            st.session_state.user_data.update({
                "destination": destination,
                "budget": budget,
                "travelers": travelers,
                "start_date": start_date,
                "end_date": end_date,
                "transport_mode": transport_mode,
                "food_preference": food_preference,
                "interests": interests,
                "special_needs": special_needs,
                "pace": pace,
                "trip_type": st.session_state.user_data["trip_type"]
            })
            st.success("🎉 Preferences saved! Our AI is crafting your perfect itinerary...")

# Features Section
st.markdown("---")
st.markdown("## ✨ Smart Travel Planning Features")

features = [
    {
        "icon": "🤖",
        "title": "AI-Powered Itinerary",
        "desc": "Our AI learns from millions of real traveler experiences to create personalized plans"
    },
    {
        "icon": "💰",
        "title": "Budget Optimization",
        "desc": "Get the best value recommendations tailored to your spending preferences"
    },
    {
        "icon": "🧳",
        "title": "Packing Assistant",
        "desc": "Smart packing lists based on destination, weather and activities"
    },
    {
        "icon": "🍽️",
        "title": "Food Recommendations",
        "desc": "Curated dining suggestions matching your taste and dietary needs"
    }
]

cols = st.columns(4)
for i, feature in enumerate(features):
    with cols[i]:
        with stylable_container(
            key=f"feature_{i}",
            css_styles="""
                {
                    background-color: white;
                    border-radius: 10px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    height: 100%;
                }
            """
        ):
            st.markdown(f"<h3>{feature['icon']} {feature['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #555;'>{feature['desc']}</p>", unsafe_allow_html=True)

# Next Steps
st.markdown("---")
st.markdown("## 🚀 Ready to Plan Your Adventure?")
st.markdown("""
1. **Save your preferences** above to get started
2. **Chat with our AI assistant** for personalized recommendations
3. **Generate your complete itinerary** with just one click
4. **Download or share** your travel plan with companions
""")

# Testimonials (optional)
with st.expander("✈️ What travelers say about us"):
    st.markdown("""
    <div style="display: flex; overflow-x: auto; gap: 1rem; padding: 1rem 0;">
        <div style="flex: 0 0 300px; background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
            <p style="font-style: italic;">"VoyageMind planned our 2-week Europe trip perfectly, hitting all our must-see spots while keeping us within budget!"</p>
            <p style="text-align: right; font-weight: bold;">— Ajith</p>
        </div>
        <div style="flex: 0 0 300px; background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
            <p style="font-style: italic;">"The AI understood exactly what kind of adventure we wanted. Best hiking recommendations!"</p>
            <p style="text-align: right; font-weight: bold;">— Kohli & Anushka</p>
        </div>
        <div style="flex: 0 0 300px; background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
            <p style="font-style: italic;">"As a solo female traveler, I felt completely safe with VoyageMind's curated suggestions."</p>
            <p style="text-align: right; font-weight: bold;">— Dora, Solo Traveler</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# JavaScript fallback for cursor (works with the CSS solution)
html("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // This reinforces the CSS solution but isn't strictly necessary
    const style = document.createElement('style');
    style.innerHTML = `html, body, [class*="css"] { cursor: auto !important; }`;
    document.head.appendChild(style);
});
</script>
""")
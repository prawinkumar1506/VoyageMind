import streamlit as st
import google.generativeai as genai
import datetime
from streamlit.components.v1 import html
from streamlit_extras.stylable_container import stylable_container
from langchain.memory import ConversationBufferMemory

# 🌍 Page Config
st.set_page_config(
    page_title="VoyageMind - Travel Concierge", 
    page_icon="🌎", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configure Gemini
genai.configure(api_key="AIzaSyC5p-7VyB6ZDAE_-8v-lelkYPkv42dUtoU")
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Custom CSS
st.markdown("""
<style>
    /* Main chat container */
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* User message bubble */
    .user-message {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border-radius: 18px 18px 0 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* AI message bubble */
    .ai-message {
        background-color: white;
        border-radius: 18px 18px 18px 0;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #eee;
    }
    
    /* Input area */
    .stTextInput>div>div>input {
        border-radius: 25px !important;
        padding: 12px 20px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Trip info cards */
    .info-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #6e8efb;
    }
    
    /* Quick action buttons */
    .quick-action {
        transition: all 0.3s ease;
        border-radius: 12px !important;
    }
    .quick-action:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_itinerary" not in st.session_state:
    st.session_state.show_itinerary = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""
if "processing" not in st.session_state:
    st.session_state.processing = False

# Retrieve user preferences
user_data = st.session_state.get("user_data", {})
destination = user_data.get("destination", "Not Set")
budget = user_data.get("budget", "Not Set")
travelers = user_data.get("travelers", "Not Set")
preferences = ", ".join(user_data.get("preferences", []))
transport_mode = user_data.get("transport_mode", None)
food_preference = user_data.get("food_preference", None)

# Date handling
if user_data.get("start_date") and user_data.get("end_date"):
    start_date = user_data["start_date"]
    end_date = user_data["end_date"]
    days = (end_date - start_date).days
    formatted_start_date = start_date.strftime(f"{start_date.day}{'st' if start_date.day == 1 else 'nd' if start_date.day == 2 else 'rd' if start_date.day == 3 else 'th'} %B %Y")
    formatted_end_date = end_date.strftime(f"{end_date.day}{'st' if end_date.day == 1 else 'nd' if end_date.day == 2 else 'rd' if end_date.day == 3 else 'th'} %B %Y")
else:
    formatted_start_date = "Not Set"
    formatted_end_date = "Not Set"
    days = "Not Set"

# 🌍 Header Section
with stylable_container(
    key="header_container",
    css_styles="""
        {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 1.5rem;
        }
    """
):
    st.markdown("<h1 style='text-align: center; color: white;'>🌍 VoyageMind Travel Concierge</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white;'>Your AI-powered travel assistant</p>", unsafe_allow_html=True)

# Trip Summary Cards
with stylable_container(
    key="info_container",
    css_styles="""
        {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
    """
):
    cols = st.columns(4)
    
    with cols[0]:
        with stylable_container(
            key="destination_card",
            css_styles="""
                .info-card {
                    background-color: white;
                    border-radius: 12px;
                    padding: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border-left: 4px solid #6e8efb;
                }
            """
        ):
            st.markdown(f"**📍 Destination**  \n{destination}")
    
    with cols[1]:
        with stylable_container(
            key="dates_card",
            css_styles="""
                .info-card {
                    background-color: white;
                    border-radius: 12px;
                    padding: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border-left: 4px solid #a777e3;
                }
            """
        ):
            st.markdown(f"**📅 Dates**  \n{formatted_start_date} to {formatted_end_date} ({days} days)")
    
    with cols[2]:
        with stylable_container(
            key="budget_card",
            css_styles="""
                .info-card {
                    background-color: white;
                    border-radius: 12px;
                    padding: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border-left: 4px solid #4CAF50;
                }
            """
        ):
            st.markdown(f"**💰 Budget**  \nRs. {budget} for {travelers} travelers")
    
    with cols[3]:
        with stylable_container(
            key="prefs_card",
            css_styles="""
                .info-card {
                    background-color: white;
                    border-radius: 12px;
                    padding: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border-left: 4px solid #FF9800;
                }
            """
        ):
            st.markdown(f"**🎯 Preferences**  \n{preferences if preferences else 'Not specified'}")

# Quick Action Buttons
st.markdown("### Quick Actions")
action_cols = st.columns(4)
with action_cols[0]:
    if st.button("📍 Top Attractions", key="attractions_btn", help="Get top attractions for your destination"):
        st.session_state.pending_query = "What are the must-see attractions?"
        st.rerun()
with action_cols[1]:
    if st.button("🍽️ Food Spots", key="food_btn", help="Find great places to eat"):
        st.session_state.pending_query = "Recommend good restaurants matching my food preferences"
        st.rerun()
with action_cols[2]:
    if st.button("🏨 Accommodation", key="hotel_btn", help="Find places to stay"):
        st.session_state.pending_query = "Suggest accommodations for my budget"
        st.rerun()
with action_cols[3]:
    if st.button("🚗 Local Transport", key="transport_btn", help="Get transport options"):
        st.session_state.pending_query = "What are the best local transportation options?"
        st.rerun()

# Chat Container
st.markdown("### Travel Assistant")
with stylable_container(
    key="chat_container",
    css_styles="""
        {
            background-color: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            height: 500px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
    """
):
    for role, message in st.session_state.chat_history:
        if role == "User":
            st.markdown(f"<div class='user-message'>{message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-message'>{message}</div>", unsafe_allow_html=True)

# User Input
with stylable_container(
    key="input_container",
    css_styles="""
        {
            background-color: white;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
    """
):
    user_query = st.text_input(
        "\U0001f4ac Ask about your trip...", 
        key="user_input", 
        placeholder="Type your question about accommodations, attractions, food, etc...",
        label_visibility="collapsed",
        value=st.session_state.pending_query
    )

# Handle user query
if user_query and user_query != st.session_state.get("last_processed_query", "") and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.last_processed_query = user_query
    st.session_state.chat_history.append(("User", user_query))
    st.session_state.pending_query = ""
    
    try:
        # Build context
        context = f"""User is planning a trip with these details:
        - Destination: {destination}
        - Duration: {days} days ({formatted_start_date} to {formatted_end_date})
        - Budget: Rs. {budget} for {travelers} travelers
        - Preferences: {preferences if preferences else 'Not specified'}
        - Transport: {transport_mode}
        - Food: {food_preference}
        
        Current query: {user_query}
        
        Respond helpfully with specific recommendations when possible. 
        Format responses with clear sections and emojis for better readability.
        """
        
        # Generate response
        response = model.generate_content(context)
        response_text = response.text if hasattr(response, "text") else "I couldn't generate a response. Please try again."
        
        # Save to memory and chat history
        st.session_state.memory.save_context({"user": user_query}, {"AI": response_text})
        st.session_state.chat_history.append(("AI", response_text))
        
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.session_state.chat_history.append(("AI", "Sorry, I encountered an error. Please try again."))
    finally:
        st.session_state.processing = False
        st.rerun()

# Add some JavaScript to enhance the chat experience
html("""
<script>
// Auto-scroll chat to bottom
function scrollChat() {
    const chatContainer = document.querySelector('[data-testid="stVerticalBlock"] > div:last-child');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
// Run scroll when page updates
document.addEventListener('DOMContentLoaded', function() {
    scrollChat();
    const observer = new MutationObserver(scrollChat);
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
""")
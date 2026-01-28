import streamlit as st
import tempfile
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Page Config makes the tab title look professional
st.set_page_config(
    page_title="Universal AI Coach",
    page_icon="🎮",
    layout="centered"
)

# --- 1. PASSWORD PROTECTION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # CHANGE THIS to your desired password
    ACTUAL_PASSWORD = "valorant-access"

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == ACTUAL_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Please enter the Investor Password:", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
        
    return False

if not check_password():
    st.stop()

# --- 2. LOAD API KEY ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Fallback for Streamlit Cloud Secrets
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("API Key not found! Check your .env file or Streamlit Secrets.")
        st.stop()

genai.configure(api_key=api_key)

# --- 3. THE MULTI-GAME BRAIN (PROMPT DICTIONARY) ---
game_prompts = {
    "Valorant": """
        You are a Radiant-rank Valorant coach. Analyze this clip frame-by-frame.
        Focus on:
        1. **Crosshair Placement:** Was it at head level? Was the pre-aim correct?
        2. **Movement:** Did they counter-strafe (stop) before shooting?
        3. **Ability Usage:** Was utility used effectively or wasted?
        Output format: "Estimated Rank", "Major Mistake", "Drill to Fix".
    """,
    "CS2 (Counter-Strike 2)": """
        You are a Global Elite CS2 coach. Analyze this clip.
        Focus on:
        1. **Recoil Control:** Was the spray pattern controlled?
        2. **Angle Isolation:** Did they peek one angle at a time or expose themselves to multiple?
        3. **Utility:** Flash/Smoke usage timing.
        Output format: "Estimated Rank", "Major Mistake", "Drill to Fix".
    """,
    "League of Legends": """
        You are a Challenger-rank LoL coach. Analyze this clip.
        Focus on:
        1. **Spacing/Tethering:** Were they in range to deal damage but safe from threats?
        2. **Camera Control:** Are they looking at the right things (map/objectives)?
        3. **Skill Usage:** Did they hit skillshots or waste cooldowns?
        Output format: "Estimated Rank", "Major Mistake", "Drill to Fix".
    """,
    "Overwatch 2": """
        You are a Top 500 Overwatch coach. Analyze this clip.
        Focus on:
        1. **Positioning:** Are they safe relative to their Tank/Support?
        2. **Target Priority:** Are they shooting the right enemy (Squishies vs Tank)?
        3. **Ult Economy:** Was the Ultimate used at a good time?
        Output format: "Estimated Rank", "Major Mistake", "Drill to Fix".
    """,
    "Rocket League": """
        You are a Supersonic Legend Rocket League coach. Analyze this clip.
        Focus on:
        1. **Boost Management:** Are they feathering boost or wasting it?
        2. **Rotation:** Are they rotating back-post on defense?
        3. **Mechanics:** Quality of aerials/dribbles.
        Output format: "Estimated Rank", "Major Mistake", "Drill to Fix".
    """
}

# --- 4. THE UI LAYOUT ---
st.title("Universal AI Gaming Coach 🎮")
st.write("Upload a gameplay clip to get professional coaching feedback.")

# Dropdown for Game Selection
selected_game = st.selectbox("Select your Game:", list(game_prompts.keys()))

uploaded_file = st.file_uploader(f"Upload a {selected_game} clip (MP4)", type=['mp4', 'mov'])

if uploaded_file is not None:
    # Save video temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    st.video(uploaded_file)
    
    if st.button(f"Analyze {selected_game} Gameplay"):
        with st.spinner(f'AI Coach is analyzing your {selected_game} mechanics...'):
            try:
                # Upload to Google
                video_file = genai.upload_file(path=video_path)
                
                # Wait for processing
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Video processing failed.")
                else:
                    # Robust Model Selection
                    try:
                         model = genai.GenerativeModel(model_name="gemini-2.5-flash")
                    except:
                         model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                    
                    # GET THE SPECIFIC PROMPT FOR THE SELECTED GAME
                    specific_prompt = game_prompts[selected_game]
                    
                    response = model.generate_content([video_file, specific_prompt])
                    
                    st.subheader(f"🛡️ {selected_game} Coach Feedback:")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Error details: {e}")

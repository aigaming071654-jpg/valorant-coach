import streamlit as st
import tempfile
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# --- 1. CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(
    page_title="AI Gaming Coach",
    page_icon="🎮",
    layout="wide"
)

# --- 2. FORCE CSS LOAD WITH CACHE CLEAR ---
st.markdown("""
<style>
    /* Import Gaming Font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Exo+2:wght@400;600&display=swap');

    /* DARK BACKGROUND - FORCED */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #16213e 100%) !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Main Container */
    [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    
    .main {
        background: transparent !important;
    }
    
    /* Headers with Neon Glow */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        text-align: center !important;
        color: #00f2fe !important;
        text-transform: uppercase !important;
        letter-spacing: 4px !important;
        text-shadow: 0 0 30px rgba(0, 242, 254, 0.8), 0 0 60px rgba(0, 242, 254, 0.5) !important;
        margin-bottom: 1rem !important;
        animation: glow 2s ease-in-out infinite alternate !important;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(0, 242, 254, 0.5), 0 0 40px rgba(0, 242, 254, 0.3); }
        to { text-shadow: 0 0 40px rgba(0, 242, 254, 0.8), 0 0 80px rgba(0, 242, 254, 0.5); }
    }
    
    h2, h3 {
        font-family: 'Exo 2', sans-serif !important;
        color: #00f2fe !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }
    
    /* All Text */
    p, div, span, label {
        font-family: 'Exo 2', sans-serif !important;
        color: #e2e8f0 !important;
    }
    
    /* Buttons - Gaming Style */
    [data-testid="stButton"] button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #0a0e27 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 3rem !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        text-transform: uppercase !important;
        letter-spacing: 3px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.5) !important;
        cursor: pointer !important;
    }
    
    [data-testid="stButton"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(0, 242, 254, 0.7) !important;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    }
    
    /* Select Box */
    [data-testid="stSelectbox"] label {
        color: #00f2fe !important;
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase !important;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 2px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 10px !important;
        color: #00f2fe !important;
        font-family: 'Exo 2', sans-serif !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] label {
        color: #00f2fe !important;
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase !important;
    }
    
    [data-testid="stFileUploader"] > section {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 2px dashed rgba(0, 242, 254, 0.4) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
    }
    
    [data-testid="stFileUploader"] > section:hover {
        border-color: rgba(0, 242, 254, 0.7) !important;
        background: rgba(30, 41, 59, 0.7) !important;
    }
    
    /* Video Player */
    video {
        border-radius: 15px !important;
        border: 3px solid rgba(0, 242, 254, 0.5) !important;
        box-shadow: 0 8px 40px rgba(0, 242, 254, 0.4) !important;
        margin: 2rem 0 !important;
    }
    
    /* Text Input (Password) */
    [data-testid="stTextInput"] label {
        color: #00f2fe !important;
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
    }
    
    [data-testid="stTextInput"] input {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 2px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: 'Exo 2', sans-serif !important;
        padding: 0.8rem !important;
    }
    
    [data-testid="stTextInput"] input:focus {
        border-color: rgba(0, 242, 254, 0.8) !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.3) !important;
    }
    
    /* Markdown Blocks */
    [data-testid="stMarkdown"] {
        color: #e2e8f0 !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(0, 242, 254, 0.3) !important;
        margin: 2rem 0 !important;
    }
    
    /* Alerts */
    [data-testid="stAlert"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 10px !important;
        border-left: 4px solid #00f2fe !important;
    }
    
    /* Spinner */
    [data-testid="stSpinner"] > div {
        border-top-color: #00f2fe !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    /* Columns */
    [data-testid="column"] {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 2px solid rgba(0, 242, 254, 0.2) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. PASSWORD PROTECTION ---
def check_password():
    ACTUAL_PASSWORD = "valorant-access"

    def password_entered():
        if st.session_state["password"] == ACTUAL_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("# 🎮 AI GAMING COACH")
    st.markdown("### ⚡ Access Restricted • Enter Credentials ⚡")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "🔐 Enter Access Code:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ Invalid Access Code")
        
    return False

if not check_password():
    st.stop()

# --- 4. MAIN APP ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("⚠️ API Key not found!")
        st.stop()

genai.configure(api_key=api_key)

# Game Prompts
game_prompts = {
    "🎯 Valorant": """
        You are a Radiant-rank Valorant coach. Analyze this clip frame-by-frame.
        Focus on:
        1. **Crosshair Placement:** Was it at head level? Was the pre-aim correct?
        2. **Movement:** Did they counter-strafe (stop) before shooting?
        3. **Ability Usage:** Was utility used effectively or wasted?
        4. **Positioning:** Were they exposed to multiple angles?
        
        Output format:
        - **Estimated Rank:** [Rank]
        - **Major Mistakes:** [List 2-3 critical errors]
        - **Drills to Fix:** [Specific practice routines]
        - **Pro Tip:** [Advanced insight]
    """,
    "🔫 CS2": """
        You are a Global Elite CS2 coach. Analyze this clip professionally.
        Focus on:
        1. **Recoil Control:** Was the spray pattern controlled?
        2. **Angle Isolation:** Did they peek one angle at a time?
        3. **Utility:** Flash/Smoke timing and placement.
        4. **Crosshair Discipline:** Pre-aim quality.
        
        Provide rank estimate, critical mistakes, and training drills.
    """,
    "⚔️ League of Legends": """
        You are a Challenger-rank LoL coach. Analyze this clip.
        Focus on:
        1. **Spacing/Tethering:** Safe damage dealing distance?
        2. **Camera Control:** Correct information gathering?
        3. **Skill Usage:** Skillshot accuracy and trading.
        4. **Map Awareness:** Minimap checking and reactions.
        
        Provide rank estimate, mistakes, and improvement plan.
    """,
    "🦾 Overwatch 2": """
        You are a Top 500 Overwatch coach. Analyze this clip.
        Focus on:
        1. **Positioning:** Safe relative to tank?
        2. **Target Priority:** Correct target selection?
        3. **Ult Economy:** Ultimate usage timing.
        4. **Cooldown Management:** Ability waste?
        
        Provide rank estimate, errors, and drills.
    """,
    "🚗 Rocket League": """
        You are a Supersonic Legend coach. Analyze this clip.
        Focus on:
        1. **Boost Management:** Efficient feathering?
        2. **Rotation:** Back-post rotation?
        3. **Mechanics:** Aerial/dribble quality.
        4. **Recovery:** Landing speed.
        
        Provide rank estimate, mistakes, and training packs.
    """
}

# --- UI ---
st.markdown("# ⚡ AI GAMING COACH ⚡")
st.markdown("### Professional Analysis • Instant Feedback • Rank Up Faster")

st.markdown("---")

# Game Selection & Upload
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎮 SELECT GAME")
    selected_game = st.selectbox(
        "Choose your game:",
        list(game_prompts.keys()),
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 📹 UPLOAD GAMEPLAY")
    uploaded_file = st.file_uploader(
        "Drop your video here",
        type=['mp4', 'mov'],
        label_visibility="collapsed"
    )

st.markdown("---")

# Video & Analysis
if uploaded_file is not None:
    # Save temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # Display video
    st.markdown("### 🎬 VIDEO PREVIEW")
    st.video(uploaded_file)
    
    st.markdown("---")
    
    # Analysis button
    if st.button(f"⚡ ANALYZE {selected_game.upper()}"):
        with st.spinner(f'🤖 AI Coach analyzing your {selected_game} gameplay...'):
            try:
                video_file = genai.upload_file(path=video_path)
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("❌ Video processing failed. Please try again.")
                else:
                    try:
                        model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
                    except:
                        try:
                            model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                        except:
                            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                    
                    response = model.generate_content([video_file, game_prompts[selected_game]])
                    
                    st.markdown("### 🛡️ COACHING FEEDBACK")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    try:
                        genai.delete_file(video_file.name)
                    except:
                        pass
                    
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                st.info("💡 Try a shorter clip (30-60 seconds) or check your API quota.")
    
    try:
        os.unlink(video_path)
    except:
        pass

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: rgba(168, 237, 234, 0.6); font-size: 0.9rem;'>⚡ Powered by AI • Built for Gamers ⚡</div>", unsafe_allow_html=True)

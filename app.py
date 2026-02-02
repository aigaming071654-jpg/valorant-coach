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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. MODERN ARCADE THEME ---
def setup_modern_arcade_theme():
    """
    Modern Arcade Gaming Theme with sleek design and vibrant accents
    """
    st.markdown("""
    <style>
        /* IMPORT MODERN GAMING FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

        /* MAIN BACKGROUND - Dark with subtle grid pattern */
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #16213e 100%);
            background-attachment: fixed;
            position: relative;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                linear-gradient(rgba(0, 242, 254, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 242, 254, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
        }
        
        /* MAIN CONTAINER */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }
        
        /* CUSTOM HEADER STYLING */
        h1 {
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 900 !important;
            font-size: 3.5rem !important;
            text-align: center;
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #a8edea 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-bottom: 0.5rem !important;
            text-shadow: 0 0 40px rgba(0, 242, 254, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.3)); }
            to { filter: drop-shadow(0 0 20px rgba(0, 242, 254, 0.6)); }
        }
        
        h2, h3 {
            font-family: 'Exo 2', sans-serif !important;
            color: #00f2fe !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        /* SUBTITLE TEXT */
        .subtitle {
            text-align: center;
            font-family: 'Exo 2', sans-serif;
            font-size: 1.2rem;
            color: #a8edea;
            margin-bottom: 2rem;
            font-weight: 300;
            letter-spacing: 1px;
        }
        
        /* GAME CARD CONTAINER */
        .game-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 2px solid rgba(0, 242, 254, 0.2);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .game-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .game-card:hover::before {
            left: 100%;
        }
        
        .game-card:hover {
            border-color: rgba(0, 242, 254, 0.5);
            box-shadow: 
                0 12px 40px rgba(0, 242, 254, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            transform: translateY(-5px);
        }
        
        /* SELECTBOX STYLING */
        .stSelectbox > div > div {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%) !important;
            border: 2px solid rgba(0, 242, 254, 0.3) !important;
            border-radius: 12px !important;
            color: #00f2fe !important;
            font-family: 'Exo 2', sans-serif !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            padding: 0.75rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: rgba(0, 242, 254, 0.6) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.2) !important;
        }
        
        /* FILE UPLOADER */
        .stFileUploader > div {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 2px dashed rgba(0, 242, 254, 0.3);
            border-radius: 16px;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        .stFileUploader > div:hover {
            border-color: rgba(0, 242, 254, 0.6);
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
        }
        
        /* ANALYZE BUTTON - PREMIUM STYLE */
        .stButton > button {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            color: #0a0e27;
            border: none;
            border-radius: 12px;
            padding: 1rem 3rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 1.3rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s ease;
            box-shadow: 
                0 4px 15px rgba(0, 242, 254, 0.4),
                0 0 40px rgba(0, 242, 254, 0.2);
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .stButton > button:hover::before {
            width: 400px;
            height: 400px;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 
                0 8px 25px rgba(0, 242, 254, 0.6),
                0 0 60px rgba(0, 242, 254, 0.4);
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
        }
        
        /* VIDEO PLAYER STYLING */
        video {
            border-radius: 16px;
            border: 3px solid rgba(0, 242, 254, 0.3);
            box-shadow: 0 8px 32px rgba(0, 242, 254, 0.2);
            margin: 1.5rem 0;
        }
        
        /* FEEDBACK PANEL */
        .feedback-panel {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
            border: 2px solid rgba(0, 242, 254, 0.4);
            border-radius: 20px;
            padding: 2rem;
            margin-top: 2rem;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                0 0 40px rgba(0, 242, 254, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
        }
        
        .feedback-panel::before {
            content: '⚡';
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 2rem;
            background: linear-gradient(135deg, #0a0e27 0%, #16213e 100%);
            padding: 0 1rem;
        }
        
        /* SPINNER CUSTOMIZATION */
        .stSpinner > div {
            border-top-color: #00f2fe !important;
            border-right-color: #4facfe !important;
        }
        
        /* TEXT STYLING */
        p, div, span, label {
            font-family: 'Exo 2', sans-serif !important;
            color: #e2e8f0 !important;
        }
        
        /* PASSWORD INPUT */
        .stTextInput > div > div > input {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%) !important;
            border: 2px solid rgba(0, 242, 254, 0.3) !important;
            border-radius: 12px !important;
            color: #00f2fe !important;
            font-family: 'Exo 2', sans-serif !important;
            font-size: 1.1rem !important;
            padding: 0.75rem !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: rgba(0, 242, 254, 0.6) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.2) !important;
        }
        
        /* HIDE STREAMLIT BRANDING */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ERROR MESSAGES */
        .stAlert {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%) !important;
            border: 2px solid rgba(239, 68, 68, 0.4) !important;
            border-radius: 12px !important;
            font-family: 'Exo 2', sans-serif !important;
        }
        
        /* SUCCESS MESSAGES */
        .stSuccess {
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(74, 172, 254, 0.1) 100%) !important;
            border: 2px solid rgba(0, 242, 254, 0.4) !important;
            border-radius: 12px !important;
        }
        
        /* DECORATIVE CORNER ACCENTS */
        .corner-accent {
            position: fixed;
            width: 200px;
            height: 200px;
            pointer-events: none;
            z-index: 0;
        }
        
        .corner-accent.top-left {
            top: 0;
            left: 0;
            background: radial-gradient(circle at top left, rgba(0, 242, 254, 0.15), transparent 70%);
        }
        
        .corner-accent.bottom-right {
            bottom: 0;
            right: 0;
            background: radial-gradient(circle at bottom right, rgba(74, 172, 254, 0.15), transparent 70%);
        }
    </style>
    
    <!-- CORNER ACCENT ELEMENTS -->
    <div class="corner-accent top-left"></div>
    <div class="corner-accent bottom-right"></div>
    """, unsafe_allow_html=True)

# APPLY THEME
setup_modern_arcade_theme()

# --- 3. PASSWORD PROTECTION WITH STYLED UI ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    ACTUAL_PASSWORD = "valorant-access"

    def password_entered():
        if st.session_state["password"] == ACTUAL_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # STYLED PASSWORD SCREEN
    st.markdown("<h1>🎮 AI GAMING COACH</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Access Restricted • Enter Credentials</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.text_input(
        "🔐 Enter Access Code:", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ Invalid Access Code")
        
    return False

if not check_password():
    st.stop()

# --- 4. MAIN APP LOGIC ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("⚠️ API Key not found! Please configure your environment.")
        st.stop()

genai.configure(api_key=api_key)

# GAME-SPECIFIC COACHING PROMPTS
game_prompts = {
    "🎯 Valorant": """
        You are a Radiant-rank Valorant coach. Analyze this clip frame-by-frame.
        Focus on:
        1. **Crosshair Placement:** Was it at head level? Was the pre-aim correct?
        2. **Movement:** Did they counter-strafe (stop) before shooting?
        3. **Ability Usage:** Was utility used effectively or wasted?
        4. **Positioning:** Were they exposed to multiple angles?
        5. **Game Sense:** Did they predict enemy positions correctly?
        
        Output format:
        - **Estimated Rank:** [Rank]
        - **Major Mistakes:** [List 2-3 critical errors]
        - **Drills to Fix:** [Specific practice routines]
        - **Pro Tip:** [Advanced insight]
    """,
    "🔫 CS2 (Counter-Strike 2)": """
        You are a Global Elite CS2 coach. Analyze this clip professionally.
        Focus on:
        1. **Recoil Control:** Was the spray pattern controlled?
        2. **Angle Isolation:** Did they peek one angle at a time?
        3. **Utility:** Flash/Smoke usage timing and placement.
        4. **Crosshair Discipline:** Pre-aim and angle holding.
        5. **Economy Awareness:** Weapon choice relative to economy.
        
        Provide rank estimate, critical mistakes, and specific aim training drills.
    """,
    "⚔️ League of Legends": """
        You are a Challenger-rank LoL coach. Analyze this clip strategically.
        Focus on:
        1. **Spacing/Tethering:** Were they in range to deal damage but safe?
        2. **Camera Control:** Are they looking at the right things?
        3. **Skill Usage:** Did they hit skillshots? Was trading effective?
        4. **Wave Management:** Were they controlling the wave properly?
        5. **Map Awareness:** Did they check minimap and react?
        
        Provide rank estimate, macro/micro mistakes, and improvement plan.
    """,
    "🦾 Overwatch 2": """
        You are a Top 500 Overwatch coach. Analyze this clip tactically.
        Focus on:
        1. **Positioning:** Are they safe relative to their Tank?
        2. **Target Priority:** Are they shooting the right enemy?
        3. **Ult Economy:** Was the Ultimate used well?
        4. **Cooldown Management:** Did they waste abilities?
        5. **Team Coordination:** Were they syncing with teammates?
        
        Provide rank estimate, positioning errors, and role-specific drills.
    """,
    "🚗 Rocket League": """
        You are a Supersonic Legend Rocket League coach. Analyze this clip mechanically.
        Focus on:
        1. **Boost Management:** Are they feathering boost efficiently?
        2. **Rotation:** Are they rotating back-post correctly?
        3. **Mechanics:** Quality of aerials/dribbles/flicks.
        4. **Positioning:** Are they reading the play correctly?
        5. **Recovery:** Speed of landing and momentum maintenance.
        
        Provide rank estimate, mechanical mistakes, and training pack recommendations.
    """
}

# --- MAIN UI ---
st.markdown("<h1>⚡ AI GAMING COACH</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Professional Analysis • Instant Feedback • Rank Up Faster</p>", unsafe_allow_html=True)

# GAME SELECTION CARD
st.markdown("<div class='game-card'>", unsafe_allow_html=True)
st.markdown("### 🎮 SELECT YOUR GAME")
selected_game = st.selectbox(
    "Choose the game you want coaching for:",
    list(game_prompts.keys()),
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# FILE UPLOAD CARD
st.markdown("<div class='game-card'>", unsafe_allow_html=True)
st.markdown("### 📹 UPLOAD GAMEPLAY CLIP")
uploaded_file = st.file_uploader(
    f"Drop your {selected_game} gameplay video here (MP4/MOV)",
    type=['mp4', 'mov'],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# VIDEO PREVIEW & ANALYSIS
if uploaded_file is not None:
    # SAVE TEMP FILE
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # DISPLAY VIDEO
    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.markdown("### 🎬 VIDEO PREVIEW")
    st.video(uploaded_file)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ANALYZE BUTTON
    if st.button(f"⚡ ANALYZE {selected_game.upper()} GAMEPLAY"):
        with st.spinner(f'🤖 AI Coach is analyzing your {selected_game} performance...'):
            try:
                # UPLOAD TO GEMINI
                video_file = genai.upload_file(path=video_path)
                
                # WAIT FOR PROCESSING
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("❌ Video processing failed. Please try again.")
                else:
                    # GENERATE ANALYSIS
                    try:
                        model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
                    except:
                        try:
                            model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                        except:
                            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                    
                    specific_prompt = game_prompts[selected_game]
                    response = model.generate_content([video_file, specific_prompt])
                    
                    # DISPLAY FEEDBACK
                    st.markdown("<div class='feedback-panel'>", unsafe_allow_html=True)
                    st.markdown(f"### 🛡️ {selected_game} PROFESSIONAL ANALYSIS")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # CLEANUP
                    try:
                        genai.delete_file(video_file.name)
                    except:
                        pass
                    
            except Exception as e:
                st.error(f"⚠️ Analysis Error: {str(e)}")
                st.info("💡 Try uploading a shorter clip (30-60 seconds) or check your API quota.")
    
    # CLEANUP TEMP FILE
    try:
        os.unlink(video_path)
    except:
        pass

# FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: rgba(168, 237, 234, 0.5); font-size: 0.9rem;'>Powered by AI • Built for Gamers</div>", unsafe_allow_html=True)

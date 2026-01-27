import streamlit as st
import tempfile
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# --- PASSWORD PROTECTION START ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # 1. Define the password (CHANGE THIS to whatever you want)
    ACTUAL_PASSWORD = "valorant-access"

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == ACTUAL_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # 2. Check if password has been verified already
    if st.session_state.get("password_correct", False):
        return True

    # 3. Show Input Field
    st.text_input(
        "Please enter the Investor Password:", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    
    # 4. Logic for incorrect password
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
        
    return False

# IF PASSWORD IS WRONG, STOP HERE.
if not check_password():
    st.stop()
# --- PASSWORD PROTECTION END ---

# --- YOUR MAIN APP STARTS BELOW (Only runs if password is correct) ---

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Try looking in Streamlit Secrets (for Cloud)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("API Key not found! Check your .env file or Streamlit Secrets.")
        st.stop()

genai.configure(api_key=api_key)

# 2. UI Layout
st.title("Valorant AI Coach 🎯")
st.write("Upload a gameplay clip (MP4) to get feedback.")

uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'mov'])

if uploaded_file is not None:
    # Save video temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    st.video(uploaded_file)
    
    if st.button("Analyze Gameplay"):
        with st.spinner('AI is watching (this takes ~20s)...'):
            try:
                # 3. Upload to Google
                video_file = genai.upload_file(path=video_path)
                
                # 4. Wait for processing
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Video processing failed.")
                else:
                    # 5. Model Selection (Updated for 2026/Stability)
                    try:
                         # Try the new standard first
                         model = genai.GenerativeModel(model_name="gemini-2.5-flash")
                    except:
                         # Fallback if 2.5 isn't available
                         model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                    
                    # The "Pro" Coach Prompt
                    prompt = """
                    You are a strict, high-ELO Valorant coach (Immortal+ rank). 
                    Analyze this gameplay clip frame-by-frame. Focus strictly on mechanics.

                    Identify 3 specific errors:
                    1. **Crosshair Placement:** Was it at head level? Was it holding wide or tight correctly for the angle?
                    2. **Movement:** Did the player counter-strafe (stop moving) before shooting? Was there unnecessary W-keying?
                    3. **Game Sense:** Did they clear angles properly or face-check?

                    Format your response as a coaching report:
                    * **Estimated Rank:** (Guess their rank based on this clip)
                    * **Major Mistake:** (The #1 thing to fix)
                    * **Drill to Fix:** (Suggest a specific training drill)
                    """
                    
                    response = model.generate_content([video_file, prompt])
                    
                    st.subheader("Coach Feedback:")
                    st.write(response.text)
                
            except Exception as e:
                st.error(f"Error details: {e}")

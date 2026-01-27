import streamlit as st
import os

# Define a simple password
# In a real startup, put this in your .env file!
# For now, we hardcode it for simplicity.
APP_PASSWORD = "valorant-access" 

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == APP_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Please enter the Investor Password:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again.
        st.text_input(
            "Please enter the Investor Password:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# --- YOUR APP STARTS HERE ---
if check_password():
    # Indent ALL your previous code under this if-statement
    st.title("Valorant AI Coach 🎯")
    
    # ... (Paste the rest of your app code here)







import streamlit as st
import tempfile
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found! Check your .env file.")
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
                    # 5. FIXED MODEL NAME HERE
                    # We use 'gemini-1.5-flash-latest' which is often more stable for free keys
                # Using the newer 2026 standard model
                    model = genai.GenerativeModel(model_name="gemini-2.5-flash")                    
                    prompt = "You are a professional Valorant coach. Watch this clip and tell me 3 specific things I did wrong regarding crosshair placement and movement."
                    
                    response = model.generate_content([video_file, prompt])
                    
                    st.subheader("Coach Feedback:")
                    st.write(response.text)
                
            except Exception as e:
                # If the specific model fails, show the exact error so we can fix it
                st.error(f"Error details: {e}")
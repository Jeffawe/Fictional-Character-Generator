import streamlit as st
import google.generativeai as genai
import os
import re
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API key and other settings
api_key = os.getenv("API_KEY")
num_requests = int(os.getenv("NUM_REQUESTS", 1))
reset_time = 24  # Reset time in hours
password = os.getenv("PASSWORD", "defaultpassword")

genai.configure(api_key=api_key)

# File to store the request count and timestamp
storage_file = "request_count.json"

# Load or initialize the request count and timestamp
def load_request_data():
    if os.path.exists(storage_file):
        with open(storage_file, "r") as file:
            data = json.load(file)
    else:
        data = {"count": 0, "timestamp": datetime.now().isoformat()}
    return data

def save_request_data(data):
    with open(storage_file, "w") as file:
        json.dump(data, file)

data = load_request_data()

# Check if 24 hours have passed since the last reset
last_reset_time = datetime.fromisoformat(data["timestamp"])
if datetime.now() - last_reset_time > timedelta(hours=reset_time):
    data["count"] = 0
    data["timestamp"] = datetime.now().isoformat()
    save_request_data(data)

# Function to process input text
def clean_text(input_text):
    cleaned_text = re.sub(r'[#*]', '', input_text)
    return cleaned_text.strip()

def process_text(input_text):
    global data
    data["count"] += 1
    save_request_data(data)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Write an interesting Character Background and name for a character with traits {input_text}")
        if response:
            return clean_text(response.text)
        else:
            return "There was an issue generating the character. Try again!"
    except ValueError:
        return "There was an issue generating the character. Try again!"
    except Exception:
        return "There was an issue generating the character. Try again!"

# Set page configuration for a better look
st.set_page_config(page_title="Fictional Character Designer", layout="centered")

# Custom CSS for additional styling
st.markdown(
    """
    <style>
    .centered-content {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .spacer {
        margin-top: 20px;
    }
    .styled-text-input {
        text-align: center;
        width: 80%;
        margin: auto;
    }
    .styled-button {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if data["count"] < num_requests:
    # Center aligned container for title and description
    st.markdown("<div class='centered-content'><h1>Design a Fictional Character</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-content'><p>Input traits to visualize your unique fictional character design.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    st.markdown("<div class='centered-content'><h3>Enter character traits below:</h3></div>", unsafe_allow_html=True)
    user_input = st.text_input("", key="input_text", max_chars=100, help="Describe your character's traits or appearance here.")

    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    st.markdown("<div class='styled-button'>", unsafe_allow_html=True)
    if st.button("Generate Character Design"):
        with st.spinner('Generating character...'):
            result = process_text(user_input)
        st.markdown(
            f"<div style='text-align: center; font-size: 1.2em; margin-top: 20px;'>{result}</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align: center; font-size: 1.2em; margin-top: 20px;'>You have reached the maximum number of requests allowed.</div>", unsafe_allow_html=True)
    entered_password = st.text_input("Enter password to continue:", type="password")
    if entered_password == password:
        st.success("Password correct! You can now generate more characters.")
        data["count"] = 0
        save_request_data(data)
        st.rerun()

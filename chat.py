import streamlit as st
import threading
import speech_recognition as sr
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini Pro model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to get response from Gemini model
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.text("Listening...")  # Display real-time voice input
        audio = r.listen(source)
        st.text("Recognizing...")
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError:
        return "Sorry, there was an error processing your request."

# Streamlit app
st.set_page_config(page_title="Special Chat Bot")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Initialize session state for input text
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ""

# Display input text area
input_text = st.text_area("Speak or Type here:", value=st.session_state['input_text'])

# Placeholder for voice input
voice_feedback = st.empty()

# Button to recognize speech and update input text
if st.button("Speak"):
    spoken_text = recognize_speech()
    if spoken_text:
        input_text += " " + spoken_text  # Append spoken text to existing text
        st.session_state['input_text'] = input_text  # Update session state
        st.rerun()  # Rerun the app to update the text area in real-time

# Button to ask a question
if st.button("Ask the question"):
    if input_text:
        # Fetch user input from the input field
        # Add user query and response to session chat history
        response = get_gemini_response(input_text)
        st.session_state['chat_history'].append(("You", input_text))
        st.subheader("The Response is")
        for chunk in response:
            st.write(chunk.text)
            st.session_state['chat_history'].append(("Bot", chunk.text))

# Display chat history
st.subheader("Chat History")
for role, text in st.session_state.get('chat_history', []):
    st.write(f"{role}: {text}")

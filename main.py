import streamlit as st
import openai
from datetime import datetime
import random
import groq

# Configure page
st.set_page_config(
    page_title="LangMaster Pro",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for UI
st.markdown("""
<style>
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Secure API key handling
def get_api_key():
    return st.secrets["groq"]["api_key"]  # Updated for Groq

# Initialize Groq client
client = groq.Client(api_key=get_api_key())


# Language configurations
LANGUAGES = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese",
    "German": "🇩🇪 German",
    "French": "🇫🇷 French"
}

# Session state for quiz progress
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = ""
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""
if "quiz_question" not in st.session_state:
    st.session_state.quiz_question = ""

# Fetch AI-generated response based on the selected language and level
def get_ai_response(prompt, language, level):
    try:
        messages = [
            {"role": "system", "content": f"You are a helpful {language} language tutor at {level} level."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Groq's best model
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Daily challenge generator
def generate_daily_challenge(language, level):
    prompt = f"Generate a beginner-level daily challenge in {language}."
    response = get_ai_response(prompt, language, level)
    return response

# Quiz question generator
def get_quiz_question(language, level):
    prompt = f"Generate a multiple-choice quiz question for {language} at {level} level."
    response = get_ai_response(prompt, language, level)
    if response:
        st.session_state.correct_answer = "Answer"  # Extracted answer based on AI response formatting
    return response

# Main function for the app
def main():
    selected_language, selected_level = render_sidebar()
    
    st.title(f"{LANGUAGES[selected_language]} LangMaster Pro")
    
    # Main navigation
    tabs = st.tabs(["Learn", "Practice", "Quiz", "Chat with AI"])

    with tabs[0]:
        render_learning_tab(selected_language, selected_level)
    with tabs[1]:
        render_practice_tab(selected_language, selected_level)
    with tabs[2]:
        render_quiz_tab(selected_language, selected_level)
    with tabs[3]:
        render_chat_tab(selected_language, selected_level)

# Sidebar with language and level options
def render_sidebar():
    st.sidebar.title("🌎 LangMaster Pro")
    selected_language = st.sidebar.selectbox("Choose Your Language", list(LANGUAGES.keys()))
    selected_level = st.sidebar.select_slider("Proficiency Level", ["Beginner", "Intermediate", "Advanced"])
    return selected_language, selected_level

# Learning tab with daily challenges and tips
def render_learning_tab(language, level):
    st.header("📚 Learning Center")
    with st.expander("🎯 Daily Challenge", expanded=True):
        challenge = generate_daily_challenge(language, level)
        st.markdown(challenge)
        if st.button("Complete Challenge"):
            st.success("Challenge completed! Check back tomorrow for a new challenge.")

# Practice tab
def render_practice_tab(language, level):
    st.header("🎯 Practice Zone")
    practice_type = st.selectbox("Choose practice type", ["Writing", "Speaking", "Grammar", "Vocabulary"])
    if practice_type == "Writing":
        user_input = st.text_area("Write in " + language)
        if st.button("Get Feedback"):
            feedback = get_ai_response(f"Provide feedback on: {user_input}", language, level)
            st.markdown(feedback)

# # Quiz tab with improved functionality
def render_quiz_tab(language, level):
    st.header("📝 Quiz Time")

    # Fetch a new question if not already fetched or if moving to a new question
    if not st.session_state.quiz_question or st.button("Next Question"):
        st.session_state.quiz_question = get_quiz_question(language, level)
        st.session_state.quiz_answered = False
        st.session_state.user_answer = ""
    
    if st.session_state.quiz_question:
        st.markdown(st.session_state.quiz_question)
        
        # Display answer options and submission button only if the question is loaded
        st.session_state.user_answer = st.radio("Choose your answer:", ["Option 1", "Option 2", "Option 3", "Option 4"], index=0, key=st.session_state.quiz_index)
        
        if not st.session_state.quiz_answered:
            if st.button("Submit Answer"):
                st.session_state.quiz_answered = True
                if st.session_state.user_answer == st.session_state.correct_answer:
                    st.success("Correct answer!")
                else:
                    st.error(f"Incorrect! The correct answer was: {st.session_state.correct_answer}")



# Chat with AI
def render_chat_tab(language, level):
    st.header("💬 Chat with AI Tutor")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Ask your language learning question"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = get_ai_response(prompt, language, level)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

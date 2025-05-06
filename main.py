from flask import Flask, render_template, request, session, redirect, url_for
from groq import Groq
import os
import markdown
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize Groq client with environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Language configurations
LANGUAGES = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese",
    "German": "🇩🇪 German",
    "French": "🇫🇷 French"
}

# Fetch AI-generated response
def get_ai_response(prompt, language, level):
    try:
        messages = [
            {"role": "system", "content": f"You are a helpful {language} language tutor at {level} level."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Daily challenge generator
def generate_daily_challenge(language, level, day_number):
    prompt = f"""
    Generate a beginner-level daily challenge in {language} formatted in Markdown. Structure it with:
    - A main header (# Daily Challenge: Day {day_number})
    - A topic subheader (## Topic: [Topic Name])
    - Exactly 3 tasks (### Task 1: [Task Name], etc.) with clear, engaging instructions
    - Use numbered lists or bullet points for subtasks
    - Keep instructions concise, motivational, and beginner-friendly
    - Vary tasks (e.g., vocabulary, speaking, writing)
    Example:
    # Daily Challenge: Day {day_number}
    ## Topic: Greetings
    ### Task 1: Vocabulary Boost
    Learn these key phrases:
    - Good morning: A friendly morning greeting
    - How are you?: Ask about someone’s day
    ### Task 2: Practice Speaking
    Say these sentences aloud:
    1. "Good morning! How are you?"
    2. "I’m happy to meet you!"
    ### Task 3: Quick Writing
    Write a short greeting to a friend in {language}.
    """
    return get_ai_response(prompt, language, level)

# Quiz question generator
def get_quiz_question(language, level):
    prompt = f"Generate a multiple-choice quiz question for {language} at {level} level."
    response = get_ai_response(prompt, language, level)
    # Mock parsing (adjust based on actual AI response format)
    return {
        "question": response,
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer": "Option 1"  # Replace with logic to extract correct answer
    }

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    # Initialize session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    if 'quiz_data' not in session:
        session['quiz_data'] = {}
    if 'chat_messages' not in session:
        session['chat_messages'] = []

    # Handle language/level selection
    if request.method == 'POST':
        session['language'] = request.form.get('language', session['language'])
        session['level'] = request.form.get('level', session['level'])
        return redirect(url_for('home'))

    return render_template('index.html', languages=LANGUAGES, selected_language=session['language'], selected_level=session['level'])

# Learning tab
@app.route('/learn', methods=['GET', 'POST'])
def learn():
    # Initialize session for challenge tracking
    if 'challenge_day' not in session:
        session['challenge_day'] = 1
        session['last_challenge_date'] = date.today().isoformat()
    
    # Check if it's a new day
    today = date.today()
    last_date = date.fromisoformat(session['last_challenge_date'])
    if today > last_date:
        session['challenge_day'] += 1
        session['last_challenge_date'] = today.isoformat()

    # Generate challenge with current day number
    challenge = generate_daily_challenge(session['language'], session['level'], session['challenge_day'])
    challenge_html = markdown.markdown(challenge)
    message = None
    if request.method == 'POST' and request.form.get('action') == 'complete':
        message = "Challenge completed! Check back tomorrow for Day {}!".format(session['challenge_day'] + 1)
    return render_template('learn.html', challenge_html=challenge_html, message=message, languages=LANGUAGES, selected_language=session['language'], selected_level=session['level'])

# Practice tab
@app.route('/practice', methods=['GET', 'POST'])
def practice():
    feedback_html = None
    if request.method == 'POST':
        user_input = request.form.get('writing_input')
        if user_input:
            feedback = get_ai_response(f"Provide concise, beginner-friendly feedback in Markdown on this {session['language']} text: {user_input}", session['language'], session['level'])
            feedback_html = markdown.markdown(feedback)
    return render_template('practice.html', feedback_html=feedback_html, languages=LANGUAGES, selected_language=session['language'], selected_level=session['level'])

# Quiz tab
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Initialize quiz state
    if 'quiz_data' not in session:
        session['quiz_data'] = {}

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'next':
            # Generate new question
            quiz_data = get_quiz_question(session['language'], session['level'])
            session['quiz_data'] = quiz_data
            session['quiz_answered'] = False
        elif action == 'submit':
            user_answer = request.form.get('answer')
            session['quiz_answered'] = True
            session['quiz_result'] = user_answer == session['quiz_data']['correct_answer']
        return redirect(url_for('quiz'))

    quiz_data = session.get('quiz_data', {})
    return render_template('quiz.html', quiz_data=quiz_data, answered=session.get('quiz_answered', False), result=session.get('quiz_result'), language=session['language'])

# Chat tab
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_prompt = request.form.get('prompt')
        if user_prompt:
            session['chat_messages'].append({"role": "user", "content": user_prompt})
            response = get_ai_response(user_prompt, session['language'], session['level'])
            session['chat_messages'].append({"role": "assistant", "content": response})
        return redirect(url_for('chat'))

    return render_template('chat.html', messages=session.get('chat_messages', []), language=session['language'])

if __name__ == '__main__':
    app.run(debug=True)
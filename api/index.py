from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask import send_from_directory
from groq import Groq
import os
import markdown
from datetime import datetime, date
import re
import random
import time

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Initialize Groq client with API key
# First try environment variable, then fallback to hardcoded (not recommended for production)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

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
    - How are you?: Ask about someone's day
    ### Task 2: Practice Speaking
    Say these sentences aloud:
    1. "Good morning! How are you?"
    2. "I'm happy to meet you!"
    ### Task 3: Quick Writing
    Write a short greeting to a friend in {language}.
    """
    return get_ai_response(prompt, language, level)

# Quiz question generator
def get_quiz_question(language, level):
    prompt = f"""
    Generate a multiple-choice quiz question for {language} at {level} level. Format as JSON:
    {{
        "question": "What does 'hello' mean in {language}?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": "Brief explanation of the answer"
    }}
    """
    
    try:
        response = get_ai_response(prompt, language, level)
        # Try to parse as JSON, fallback to simple format if needed
        import json
        try:
            return json.loads(response)
        except:
            # Fallback if AI doesn't return proper JSON
            return {
                "question": f"What is a common greeting in {language}?",
                "options": ["Hello", "Goodbye", "Thank you", "Please"],
                "correct_answer": "Hello",
                "explanation": "Hello is a standard greeting in most languages."
            }
    except Exception as e:
        return {
            "question": f"What is a basic word in {language}?",
            "options": ["Yes", "No", "Maybe", "Sometimes"],
            "correct_answer": "Yes",
            "explanation": "This is a sample question due to an error."
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
    # Initialize session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    
    # Reset challenge_day to 1 on GET (page load or reload)
    if request.method == 'GET':
        session['challenge_day'] = 1
        session.modified = True
    elif 'challenge_day' not in session:
        session['challenge_day'] = 1
        session.modified = True

    challenge = None
    challenge_html = None
    message = None

    if request.method == 'POST' and request.form.get('action') == 'complete':
        # Increment challenge day and generate new challenge
        session['challenge_day'] = session.get('challenge_day', 1) + 1
        challenge = generate_daily_challenge(session['language'], session['level'], session['challenge_day'])
        challenge_html = markdown.markdown(challenge)
        message = "Great job! Here's your next challenge!"
    else:
        # Generate current challenge
        challenge = generate_daily_challenge(session['language'], session['level'], session['challenge_day'])
        challenge_html = markdown.markdown(challenge)

    return render_template(
        'learn.html',
        challenge_html=challenge_html,
        message=message,
        languages=LANGUAGES,
        selected_language=session['language'],
        selected_level=session['level']
    )

# Practice tab
@app.route('/practice', methods=['GET', 'POST'])
def practice():
    # Ensure session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'

    feedback = None
    user_text = ""

    if request.method == 'POST':
        user_text = request.form.get('user_text', '')
        if user_text.strip():
            # Generate feedback prompt
            feedback_prompt = f"""
            Review this {session['language']} text written by a {session['level']} level student:
            "{user_text}"
            
            Provide constructive feedback covering:
            1. Grammar accuracy
            2. Vocabulary usage
            3. Sentence structure
            4. Suggestions for improvement
            
            Keep feedback encouraging and educational.
            """
            feedback = get_ai_response(feedback_prompt, session['language'], session['level'])

    return render_template(
        'practice.html',
        user_text=user_text,
        feedback=feedback,
        languages=LANGUAGES,
        selected_language=session['language'],
        selected_level=session['level']
    )

# Quiz tab
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Ensure session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'

    result_message = None
    quiz_data = session.get('quiz_data', {})

    if request.method == 'POST':
        if 'generate_quiz' in request.form:
            # Generate new quiz question
            quiz_data = get_quiz_question(session['language'], session['level'])
            session['quiz_data'] = quiz_data
            session.modified = True
        elif 'submit_answer' in request.form:
            # Check submitted answer
            user_answer = request.form.get('answer', '')
            correct_answer = quiz_data.get('correct_answer', '')
            
            if user_answer == correct_answer:
                result_message = f"🎉 Correct! {quiz_data.get('explanation', '')}"
            else:
                result_message = f"❌ Incorrect. The correct answer is: {correct_answer}. {quiz_data.get('explanation', '')}"
    
    # Generate initial quiz if none exists
    if not quiz_data:
        quiz_data = get_quiz_question(session['language'], session['level'])
        session['quiz_data'] = quiz_data
        session.modified = True

    return render_template(
        'quiz.html',
        quiz_data=quiz_data,
        result_message=result_message,
        languages=LANGUAGES,
        selected_language=session['language'],
        selected_level=session['level']
    )

# Chat tab
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # Ensure session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    if 'chat_messages' not in session:
        session['chat_messages'] = []

    user_message = ""
    assistant_response = ""
    error_message = None

    if request.method == 'POST':
        user_message = request.form.get('user_message', '').strip()
        
        if user_message:
            try:
                # Create conversation prompt
                conversation_prompt = f"""
                You are a friendly {session['language']} language tutor helping a {session['level']} level student.
                The student said: "{user_message}"
                
                Respond naturally in {session['language']} (with English translation in parentheses if needed).
                Keep your response encouraging, educational, and conversational.
                If they make mistakes, gently correct them.
                """
                
                assistant_response = get_ai_response(conversation_prompt, session['language'], session['level'])
                
                # Store conversation in session
                session['chat_messages'].append({
                    'user': user_message,
                    'assistant': assistant_response,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                session.modified = True
                
            except Exception as e:
                error_message = f"Sorry, there was an error: {str(e)}"

    return render_template(
        'chat.html',
        user_message=user_message,
        assistant_response=assistant_response,
        error_message=error_message,
        chat_messages=session.get('chat_messages', []),
        languages=LANGUAGES,
        selected_language=session['language'],
        selected_level=session['level']
    )

@app.route('/image/<filename>')
def image(filename):
    return send_from_directory('../image', filename)

# For Vercel deployment
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Export app for Vercel
def handler(request):
    return app(request.environ, request.start_response)

if __name__ == '__main__':
    app.run(debug=True)

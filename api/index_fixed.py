from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
import os
import markdown
import re
import random
import time

# Try to import Groq safely
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq not available")

# Create Flask app with proper paths for Vercel
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Secret key configuration - CRITICAL for sessions
SECRET_KEY = os.environ.get('SECRET_KEY')
if SECRET_KEY:
    app.secret_key = SECRET_KEY
    print(f"✅ SECRET_KEY loaded successfully")
else:
    # Generate a fallback secret key for development
    app.secret_key = 'dev-fallback-key-change-in-production-12345'
    print("⚠️ Using fallback SECRET_KEY - set environment variable for production")

# Groq API configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = None

# Debug environment variables
print("🔍 Environment Debug:")
print(f"GROQ_API_KEY present: {bool(GROQ_API_KEY)}")
print(f"GROQ_API_KEY length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")
print(f"GROQ_AVAILABLE: {GROQ_AVAILABLE}")

if GROQ_AVAILABLE and GROQ_API_KEY:
    try:
        # Try simple initialization first to avoid parameter issues
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized successfully")
    except TypeError as e:
        if "proxies" in str(e):
            print(f"❌ Groq proxies error: {e}")
            print("🔄 Trying alternative initialization...")
            # Try without any extra parameters
            try:
                import groq
                client = groq.Groq(api_key=GROQ_API_KEY)
                print("✅ Groq client initialized with alternative method")
            except Exception as e2:
                print(f"❌ Alternative initialization failed: {e2}")
                client = None
        else:
            print(f"❌ Groq TypeError: {e}")
            client = None
    except Exception as e:
        print(f"❌ Groq initialization failed: {type(e).__name__}: {str(e)}")
        client = None
elif not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY environment variable not found")
else:
    print("⚠️ Groq library not available")

# Language configurations
LANGUAGES = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese", 
    "German": "🇩🇪 German",
    "French": "🇫🇷 French"
}

def get_ai_response(prompt, language, level):
    """Get AI response with proper error handling and lazy initialization"""
    global client
    
    if not GROQ_AVAILABLE:
        return "❌ AI service unavailable: Groq library not installed"
    
    if not GROQ_API_KEY:
        return "❌ AI service unavailable: GROQ_API_KEY environment variable not set"
    
    # Lazy initialization - try to create client when needed
    if not client:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            print("✅ Groq client initialized on demand")
        except Exception as e:
            return f"❌ Groq client initialization failed: {type(e).__name__}: {str(e)}"
    
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
        return f"❌ AI Error: {type(e).__name__}: {str(e)}"

def generate_daily_challenge(language, level, day_number):
    """Generate daily challenge content"""
    prompt = f"""
    Generate a beginner-level daily challenge in {language} formatted in Markdown. Structure it with:
    - A main header (# Daily Challenge: Day {day_number})
    - A topic subheader (## Topic: [Topic Name])
    - Exactly 3 tasks (### Task 1: [Task Name], etc.) with clear, engaging instructions
    - Use numbered lists or bullet points for subtasks
    - Keep instructions concise, motivational, and beginner-friendly
    - Vary tasks (e.g., vocabulary, speaking, writing)
    """
    return get_ai_response(prompt, language, level)

@app.route('/', methods=['GET', 'POST'])
def home():
    """Home page with language/level selection"""
    # Initialize session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    if 'quiz_data' not in session:
        session['quiz_data'] = {}
    if 'chat_messages' not in session:
        session['chat_messages'] = []

    # Handle form submission
    if request.method == 'POST':
        session['language'] = request.form.get('language', session['language'])
        session['level'] = request.form.get('level', session['level'])
        return redirect(url_for('home'))

    return render_template('index.html', 
                         languages=LANGUAGES, 
                         selected_language=session['language'], 
                         selected_level=session['level'])

@app.route('/learn', methods=['GET', 'POST'])
def learn():
    """Learning page with daily challenges"""
    # Initialize session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    
    # Reset challenge day on GET
    if request.method == 'GET':
        session['challenge_day'] = 1
    elif 'challenge_day' not in session:
        session['challenge_day'] = 1

    challenge = None
    challenge_html = None
    message = None

    if request.method == 'POST' and request.form.get('action') == 'complete':
        # Increment challenge day
        session['challenge_day'] = session.get('challenge_day', 1) + 1
        challenge = generate_daily_challenge(session['language'], session['level'], session['challenge_day'])
        challenge_html = markdown.markdown(challenge)
        message = "Great job! Here's your next challenge!"
    else:
        # Generate current challenge
        challenge = generate_daily_challenge(session['language'], session['level'], session['challenge_day'])
        challenge_html = markdown.markdown(challenge)

    return render_template('learn.html',
                         challenge_html=challenge_html,
                         message=message,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/practice', methods=['GET', 'POST'])
def practice():
    """Practice page for writing exercises"""
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    
    feedback_html = None
    error_message = None
    user_input = None
    
    if request.method == 'POST':
        user_input = request.form.get('writing_input')
        if user_input:
            try:
                feedback = get_ai_response(
                    f"Provide concise, beginner-friendly feedback in Markdown on this {session['language']} text: {user_input}",
                    session['language'],
                    session['level']
                )
                if feedback.startswith("Error:") or feedback.startswith("AI Error:"):
                    error_message = feedback
                else:
                    feedback_html = markdown.markdown(feedback)
            except Exception as e:
                error_message = f"Failed to get feedback: {str(e)}"
    
    return render_template('practice.html',
                         feedback_html=feedback_html,
                         error_message=error_message,
                         user_input=user_input,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Quiz page with AI-generated questions"""
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    if 'quiz_data' not in session:
        session['quiz_data'] = {}
    if 'quiz_answered' not in session:
        session['quiz_answered'] = False
    if 'quiz_result' not in session:
        session['quiz_result'] = None

    def generate_new_question():
        try:
            topics = ['vocabulary', 'grammar', 'phrases', 'culture', 'common expressions']
            topic = random.choice(topics)
            prompt = f"""
            Generate a multiple-choice quiz question for {session['language']} at {session['level']} level.
            Focus on {topic}. Structure exactly as:
            - Question: [Question text]
            - Options:
              1. [Option 1]
              2. [Option 2] 
              3. [Option 3]
              4. [Option 4]
            - Correct answer: [Option text]            """
            print(f"🎯 Quiz prompt: {prompt}")
            response = get_ai_response(prompt, session['language'], session['level'])
            print(f"🎯 Quiz response: {response}")
            
            # Parse response
            question_match = re.search(r'^- Question: (.*?)(?=\n- Options:|\n|$)', response, re.DOTALL)
            options_match = re.findall(r'^\s*\d+\.\s*(.*?)$', response, re.MULTILINE)
            correct_answer_match = re.search(r'^- Correct answer: (.*)$', response, re.MULTILINE)
            
            question = question_match.group(1).strip() if question_match else "Sample question"
            options = options_match[:4] if len(options_match) >= 4 else ["Option 1", "Option 2", "Option 3", "Option 4"]
            correct_answer = correct_answer_match.group(1).strip() if correct_answer_match else options[0]
            
            return {
                'question': question,
                'question_html': markdown.markdown(question),
                'options': options,
                'correct_answer': correct_answer
            }
        except Exception as e:
            # Fallback question
            return {
                'question': f"What is a common greeting in {session['language']}?",
                'question_html': f"<p>What is a common greeting in {session['language']}?</p>",
                'options': ['Hello', 'Goodbye', 'Thank you', 'Please'],
                'correct_answer': 'Hello'
            }

    quiz_data = session.get('quiz_data', {})
    answered = session.get('quiz_answered', False)
    result = session.get('quiz_result', None)

    if request.method == 'POST':
        if request.form.get('action') == 'submit_answer':
            selected_answer = request.form.get('answer')
            if selected_answer and quiz_data:
                correct = selected_answer == quiz_data['correct_answer']
                session['quiz_result'] = {
                    'correct': correct,
                    'selected': selected_answer,
                    'correct_answer': quiz_data['correct_answer']
                }
                session['quiz_answered'] = True
                result = session['quiz_result']
        elif request.form.get('action') == 'new_question':
            quiz_data = generate_new_question()
            session['quiz_data'] = quiz_data
            session['quiz_answered'] = False
            session['quiz_result'] = None
            answered = False
            result = None

    # Generate initial question if none exists
    if not quiz_data:
        quiz_data = generate_new_question()
        session['quiz_data'] = quiz_data

    return render_template('quiz.html',
                         quiz_data=quiz_data,
                         answered=answered,
                         result=result,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat page for conversation practice"""
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    if 'chat_messages' not in session:
        session['chat_messages'] = []

    if request.method == 'POST':
        user_message = request.form.get('message')
        if user_message:
            # Add user message
            session['chat_messages'].append({
                'role': 'user',
                'content': user_message
            })
            
            # Get AI response with debugging
            prompt = f"Respond to this message in {session['language']} at {session['level']} level. Be encouraging and helpful as a language tutor: {user_message}"
            print(f"🤖 Chat prompt: {prompt}")
            ai_response = get_ai_response(prompt, session['language'], session['level'])
            print(f"🤖 Chat response: {ai_response}")
            
            # Add AI response
            session['chat_messages'].append({
                'role': 'assistant', 
                'content': ai_response
            })
            
            session.modified = True

    return render_template('chat.html',
                         messages=session['chat_messages'],
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/image/<filename>')
def image(filename):
    """Serve images from the image directory"""
    try:
        return send_from_directory('../image', filename)
    except Exception as e:
        return f"Image not found: {filename}", 404

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('../static', filename)
    except Exception as e:
        return f"Static file not found: {filename}", 404

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'groq_available': client is not None,
        'secret_key_set': bool(os.environ.get('SECRET_KEY')),
        'groq_api_key_set': bool(os.environ.get('GROQ_API_KEY'))
    }

# Test AI endpoint
@app.route('/test-ai')
def test_ai():
    """Test AI functionality"""
    try:
        test_response = get_ai_response("Say hello in a friendly way", "English", "Beginner")
        return {
            'status': 'success',
            'response': test_response,
            'client_status': client is not None
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'client_status': client is not None
        }

# Configure app for production
app.config['TEMPLATES_AUTO_RELOAD'] = True

# For local development
if __name__ == '__main__':
    app.run(debug=True)

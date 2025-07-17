from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask import send_from_directory
import os
import markdown

# Try to import Groq safely
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Secret key configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production-12345')
app.secret_key = SECRET_KEY

# Language configurations
LANGUAGES = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese",
    "German": "🇩🇪 German",
    "French": "🇫🇷 French"
}

# Initialize Groq client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = None

if GROQ_AVAILABLE and GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Groq initialization failed: {e}")
        client = None

def get_ai_response(prompt, language, level):
    """Get AI response with error handling"""
    if not client:
        return "AI service currently unavailable."
    
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
        return f"AI Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def home():
    """Home page"""
    # Initialize session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'

    # Handle form submission
    if request.method == 'POST':
        session['language'] = request.form.get('language', session['language'])
        session['level'] = request.form.get('level', session['level'])
        return redirect(url_for('home'))

    return render_template('index.html', 
                         languages=LANGUAGES, 
                         selected_language=session['language'], 
                         selected_level=session['level'])

@app.route('/learn')
def learn():
    """Learning page"""
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    
    # Simple challenge content
    challenge_html = """
    <h1>Daily Challenge: Day 1</h1>
    <h2>Topic: Greetings</h2>
    <h3>Task 1: Learn Basic Greetings</h3>
    <p>Practice saying "Hello" and "How are you?" in your target language.</p>
    """
    
    return render_template('learn.html',
                         challenge_html=challenge_html,
                         message=None,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/practice', methods=['GET', 'POST'])
def practice():
    """Practice page"""
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
            feedback = get_ai_response(
                f"Provide feedback on this {session['language']} text: {user_input}",
                session['language'],
                session['level']
            )
            feedback_html = markdown.markdown(feedback)
    
    return render_template('practice.html',
                         feedback_html=feedback_html,
                         error_message=error_message,
                         user_input=user_input,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/quiz')
def quiz():
    """Quiz page"""
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'
    
    # Simple quiz data
    quiz_data = {
        'question': f"What is a common greeting in {session['language']}?",
        'question_html': f"<p>What is a common greeting in {session['language']}?</p>",
        'options': ['Hello', 'Goodbye', 'Thank you', 'Please'],
        'correct_answer': 'Hello'
    }
    
    return render_template('quiz.html',
                         quiz_data=quiz_data,
                         answered=False,
                         result=None,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat page"""
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'

    error_message = None
    user_message = None
    assistant_response = None

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            try:
                response = get_ai_response(
                    f"Respond to this message as a {session['language']} tutor: {user_input}",
                    session['language'],
                    session['level']
                )
                user_message = user_input
                assistant_response = markdown.markdown(response)
            except Exception as e:
                error_message = f"Failed to generate response: {str(e)}"
        else:
            error_message = "Please enter a message."

    return render_template('chat.html',
                         user_message=user_message,
                         assistant_response=assistant_response,
                         error_message=error_message,
                         languages=LANGUAGES,
                         selected_language=session['language'],
                         selected_level=session['level'])

@app.route('/image/<filename>')
def image(filename):
    """Serve images"""
    try:
        return send_from_directory('../image', filename)
    except Exception:
        return "Image not found", 404

@app.route('/health')
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'groq_available': client is not None,
        'groq_api_key_set': bool(GROQ_API_KEY)
    })

# Export the Flask app for Vercel
application = app

if __name__ == '__main__':
    app.run(debug=True)

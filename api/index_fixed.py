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

# Configure session for better persistence in serverless environment
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Groq client with API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = None

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized successfully")
    except Exception as e:
        print(f"❌ Groq initialization failed: {type(e).__name__}: {str(e)}")
        client = None
else:
    print("⚠️ GROQ_API_KEY not set. AI features will not work.")

# Language configurations
LANGUAGES = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese",
    "German": "🇩🇪 German",
    "French": "🇫🇷 French"
}

# Fetch AI-generated response
def get_ai_response(prompt, language, level):
    global client
    
    if not GROQ_API_KEY:
        return "❌ AI service unavailable: GROQ_API_KEY environment variable not set"
    
    # Lazy initialization - try to create client when needed if it doesn't exist
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

# # Quiz question generator
# def get_quiz_question(language, level):
#     prompt = f"Generate a multiple-choice quiz question for {language} at {level} level."
#     response = get_ai_response(prompt, language, level)
#     # Mock parsing (adjust based on actual AI response format)
#     return {
#         "question": response,
#         "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
#         "correct_answer": "Option 1"  # Replace with logic to extract correct answer
#     }

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
        print(f"Challenge Completed - Day: {session['challenge_day']}, Challenge: {challenge}")
    else:
        # Generate current challenge
        challenge = generate_daily_challenge(session['language'], session['level'], session['challenge_day'])
        challenge_html = markdown.markdown(challenge)
        print(f"Challenge Loaded - Day: {session['challenge_day']}, Challenge: {challenge}")

    print("Session:", session)

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
                if feedback.startswith("Error:"):
                    error_message = feedback
                else:
                    feedback_html = markdown.markdown(feedback)
            except Exception as e:
                error_message = f"Failed to get feedback: {str(e)}"
    
    return render_template(
        'practice.html',
        feedback_html=feedback_html,
        error_message=error_message,
        user_input=user_input,
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
    if 'quiz_data' not in session:
        session['quiz_data'] = {}
    if 'quiz_answered' not in session:
        session['quiz_answered'] = False
    if 'quiz_result' not in session:
        session['quiz_result'] = None

    error_message = None

    def generate_new_question():
        nonlocal error_message
        try:
            # Add random seed and varied topics for unique prompt
            random_seed = random.randint(1, 1000000)
            topics = ['vocabulary', 'grammar', 'phrases', 'culture', 'common expressions']
            topic = random.choice(topics)
            prompt = f"""
                Generate a multiple-choice quiz question for {session['language']} at {session['level']} level in Markdown.
                Focus on {topic} to ensure variety.
                Structure it exactly as:
                - Question: [Question text]
                - Options:
                  1. [Option 1]
                  2. [Option 2]
                  3. [Option 3]
                  4. [Option 4]
                - Correct answer: [Option text]
                Ensure the question is engaging, relevant, factually accurate, and the correct answer is the exact text of one option (e.g., 'Hello', not '1'). Use numbered options (1., 2., 3., 4.) without bullets or dashes. Generate a new, unique question different from previous ones. Seed: {random_seed}, Timestamp: {time.time()}
                """
            response = get_ai_response(prompt, session['language'], session['level'])
            print("Quiz Response:", response)
            
            # Parse response with regex
            question_match = re.search(r'^- Question: (.*?)(?=\n- Options:|\n|$)', response, re.DOTALL)
            options_match = re.findall(r'^\s*\d+\.\s*(.*?)$', response, re.MULTILINE)
            correct_answer_match = re.search(r'^- Correct answer: (.*)$', response, re.MULTILINE)
            
            # Fallback parsing
            lines = response.strip().split('\n')
            if not question_match:
                question = next((line.strip() for line in lines if line.strip() and not line.startswith(('1.', '2.', '3.', '4.', '- ', '* ', 'Correct answer:'))), "Unknown question")
            else:
                question = question_match.group(1).strip()
            
            if not options_match:
                options = [line.strip() for line in lines if line.strip() and not line.startswith(('- Question:', 'Correct answer:'))]
                options = [opt[3:].strip() if opt.startswith(('1.', '2.', '3.', '4.')) else opt for opt in options]
                options = options[:4]
            else:
                options = options_match[:4]
            
            # Ensure exactly 4 options
            if len(options) < 4:
                options = options + [f"Option {i}" for i in range(len(options) + 1, 5)]
            options = options[:4]
            
            # Get correct answer
            correct_answer = correct_answer_match.group(1).strip() if correct_answer_match else ''
            if not correct_answer or correct_answer not in options:
                try:
                    num = int(correct_answer) - 1
                    if 0 <= num < len(options):
                        correct_answer = options[num]
                except ValueError:
                    correct_answer = options[0]
            
            quiz_data = {
                'question': question,
                'question_html': markdown.markdown(question),
                'options': options,
                'correct_answer': correct_answer
            }
            print("Generated Quiz Data:", quiz_data)
            return quiz_data
        except Exception as e:
            error_message = f"Failed to generate question: {str(e)}"
            print("Quiz Generation Error:", error_message)
            # Varied fallback questions
            fallback_questions = [
                {
                    'question': f"What is the opposite of the word 'big' in {session['language']}?",
                    'options': ['Happy', 'Small', 'Fast', 'Strong'],
                    'correct_answer': 'Small'
                },
                {
                    'question': f"How do you say 'thank you' in {session['language']}?",
                    'options': ['Hello', 'Thank you', 'Goodbye', 'Please'],
                    'correct_answer': 'Thank you'
                },
                {
                    'question': f"What is a common greeting in {session['language']}?",
                    'options': ['Hello', 'Goodbye', 'Thank you', 'Please'],
                    'correct_answer': 'Hello'
                }
            ]
            quiz_data = random.choice(fallback_questions)
            quiz_data['question_html'] = markdown.markdown(quiz_data['question'])
            print("Fallback Quiz Data:", quiz_data)
            return quiz_data

    quiz_data = session.get('quiz_data', {})
    answered = session.get('quiz_answered', False)
    result = session.get('quiz_result', None)

    # Clear error_message on GET
    if request.method == 'GET':
        error_message = None
        # Force new question on page load to avoid static question
        if quiz_data.get('question') == f"What is the opposite of the word 'big' in {session['language']}?":
            quiz_data = {}
            session['quiz_data'] = {}

    if request.method == 'POST':
        action = request.form.get('action')
        print("POST Action:", action)
        print("Form Data:", request.form)
        if action == 'next':
            # Clear session to force new question
            session['quiz_data'] = {}
            session['quiz_answered'] = False
            session['quiz_result'] = None
            quiz_data = generate_new_question()
            session['quiz_data'] = quiz_data
            session.modified = True
            print("After Next - Session:", session)
        elif action == 'submit':
            user_answer = request.form.get('answer')
            print("User Answer:", user_answer)
            print("Current Quiz Data:", quiz_data)
            if user_answer and quiz_data and 'correct_answer' in quiz_data and user_answer in quiz_data['options']:
                answered = True
                result = user_answer == quiz_data['correct_answer']
                session['quiz_answered'] = True
                session['quiz_result'] = result
                session.modified = True
            else:
                error_message = "Please select a valid answer."
                answered = False
                result = None
                session['quiz_answered'] = False
                session['quiz_result'] = None
                session.modified = True
            print("After Submit - Session:", session)

    # Generate new question if none exists or invalid
    if not quiz_data or not all(key in quiz_data for key in ['question', 'options', 'correct_answer']) or not quiz_data.get('question'):
        quiz_data = generate_new_question()
        session['quiz_data'] = quiz_data
        session['quiz_answered'] = False
        session['quiz_result'] = None
        session.modified = True

    print("Final Quiz Data:", quiz_data, "Answered:", answered, "Result:", result)

    return render_template(
        'quiz.html',
        quiz_data=quiz_data,
        answered=answered,
        result=result,
        error_message=error_message,
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

    error_message = None
    user_message = None
    assistant_response = None

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            try:
                # Generate AI response
                prompt = f"""
                    You are a conversational language tutor for {session['language']} at {session['level']} level.
                    The user has said: "{user_input}"
                    Respond in Markdown with:
                    - Feedback on the user's input (correctness, grammar, suggestions).
                    - A follow-up question or prompt to continue the conversation.
                    Keep the tone friendly and encouraging.
                    Example:
                    **Feedback**: Great job! Your sentence is correct, but you could use "hola" for a more casual greeting.
                    **Next**: How would you ask someone their name in {session['language']}?
                    """
                response = get_ai_response(prompt, session['language'], session['level'])
                
                # Store in session for persistence
                session['chat_messages'].append({
                    'role': 'user',
                    'content': user_input
                })
                session['chat_messages'].append({
                    'role': 'assistant',
                    'content': response
                })
                session.modified = True
                
                # Set variables for template (latest exchange)
                user_message = user_input
                assistant_response = markdown.markdown(response)
                
            except Exception as e:
                error_message = f"Failed to generate response: {str(e)}"
        else:
            error_message = "Please enter a message."

    # If no current exchange, show the latest from session
    if not user_message and session['chat_messages']:
        # Get the last two messages (user and assistant)
        messages = session['chat_messages']
        if len(messages) >= 2:
            last_user = next((msg for msg in reversed(messages) if msg['role'] == 'user'), None)
            last_assistant = next((msg for msg in reversed(messages) if msg['role'] == 'assistant'), None)
            
            if last_user:
                user_message = last_user['content']
            if last_assistant:
                assistant_response = markdown.markdown(last_assistant['content'])

    return render_template(
        'chat.html',
        user_message=user_message,
        assistant_response=assistant_response,
        error_message=error_message,
        languages=LANGUAGES,
        selected_language=session['language'],
        selected_level=session['level']
    )

@app.route('/image/<filename>')
def image(filename):
    return send_from_directory('../image', filename)

# Health check endpoint for debugging
@app.route('/health')
def health_check():
    """Health check endpoint for debugging deployment issues"""
    return {
        'status': 'healthy',
        'groq_available': client is not None,
        'groq_api_key_set': bool(GROQ_API_KEY),
        'secret_key_set': bool(app.secret_key)
    }

# Test AI endpoint for debugging
@app.route('/test-ai')
def test_ai():
    """Test AI functionality for debugging"""
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

# For Vercel deployment
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == '__main__':
    app.run(debug=True)

# Export app for Vercel - CRITICAL for serverless deployment
def handler(request):
    return app(request.environ, request.start_response)

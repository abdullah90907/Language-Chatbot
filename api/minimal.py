from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Language configurations
LANGUAGES = {
    "English": "🇬🇧 English",
    "Japanese": "🇯🇵 Japanese", 
    "German": "🇩🇪 German",
    "French": "🇫🇷 French"
}

@app.route('/', methods=['GET', 'POST'])
def home():
    # Initialize session defaults
    if 'language' not in session:
        session['language'] = 'English'
    if 'level' not in session:
        session['level'] = 'Beginner'

    # Handle language/level selection
    if request.method == 'POST':
        session['language'] = request.form.get('language', session['language'])
        session['level'] = request.form.get('level', session['level'])
        return redirect(url_for('home'))

    return render_template('index.html', 
                         languages=LANGUAGES, 
                         selected_language=session['language'], 
                         selected_level=session['level'])

@app.route('/test')
def test():
    return "Flask app is working on Vercel!"

@app.route('/health')
def health():
    return {"status": "healthy", "message": "LangMaster-Pro API is running"}

if __name__ == '__main__':
    app.run(debug=True)

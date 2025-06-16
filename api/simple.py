from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>LangMaster Pro - Test</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 50px; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>🌟 LangMaster Pro</h1>
        <p>Application is running successfully on Vercel!</p>
        <p>This is a test deployment.</p>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {"status": "success", "message": "API is working"}

# Export app for Vercel
application = app

if __name__ == '__main__':
    app.run(debug=True)

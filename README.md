![Lan](https://github.com/user-attachments/assets/d9565595-0c2b-4660-af2d-6a70f3c506da)
﻿
## LangMaster-Pro

LangMaster-Pro is an interactive language learning platform designed to help users master new languages through engaging tools and AI-driven features. Whether you're a beginner or an advanced learner, LangMaster-Pro offers personalized learning experiences with lessons, practice exercises, quizzes, and AI-powered chat.

## Features

- **Interactive Lessons**: Structured learning modules for various languages and proficiency levels (`learn.html`).
- **Practice Exercises**: Hands-on activities to reinforce language skills (`practice.html`).
- **Quizzes**: Test your knowledge with dynamic quizzes (`quiz.html`).
- **AI-Powered Chat**: Practice conversational skills with an AI language tutor (`chat.html`).
- **Responsive UI**: Modern design with Tailwind CSS, featuring a custom navbar with an SVG globe and Poppins font.
- **Language and Level Selection**: Choose your target language and proficiency level (Beginner, Intermediate, Advanced).
- **Engaging Media**: Video introduction and images for an immersive experience (`image/video.mp4`, `image/learn.jpg`, etc.).
- **Updated Footer**: Comprehensive footer with Quick Links, Contact, and Social Media (`index.html`).

## Technologies Used

- **Backend**:
  - Flask: Python web framework for routing and templating.
  - Python: Core programming language.
- **Frontend**:
  - HTML: Structure for web pages.
  - Tailwind CSS: Utility-first CSS framework (via CDN).
  - Jinja2: Templating engine for dynamic HTML.
  - Poppins Font: Modern typography via Google Fonts.
  - Custom CSS: Additional styling (`static/style.css`).
- **Assets**:
  - Images and Videos: Stored in `image/` (e.g., `favicon.png`, `video.mp4`).
- **Tools**:
  - Git: Version control.
  - GitHub: Repository hosting.

## Getting Started

Follow these steps to set up and run LangMaster-Pro locally.

### Prerequisites

- Python 3.8 or higher
- Git
- A web browser (e.g., Chrome, Firefox)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/LangMaster-Pro.git
   cd LangMaster-Pro
   ```

2. **Create a virtual environment** (optional, recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install flask
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the app**:
   - Open your browser and visit `http://localhost:5000/`.
   - Explore features: Home, Learn, Practice, Quiz, Chat.

### Folder Structure

```
LangMaster-Pro/
├── image/                  # Images and videos (favicon.png, video.mp4, etc.)
├── static/                 # Static files
│   └── style.css          # Custom CSS
├── templates/             # HTML templates
│   ├── base.html          # Base template with navbar (SVG globe, Poppins font)
│   ├── index.html         # Home page with video and footer
│   ├── learn.html         # Lessons page
│   ├── practice.html      # Practice exercises
│   ├── quiz.html          # Quizzes
│   └── chat.html          # AI chat interface
├── main.py                # Flask application
├── .gitignore             # Git ignore file (e.g., __pycache__, .venv)
└── README.md              # This file
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make changes and commit: `git commit -m "Add your feature"`.
4. Push to your branch: `git push origin feature/your-feature`.
5. Open a Pull Request on GitHub.

Please ensure your code follows the project's style (e.g., Tailwind CSS for styling, Flask routes for backend).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Flask App Structure Explanation

## Overview
This project contains **TWO Flask applications** that serve the **SAME PURPOSE** but are optimized for **DIFFERENT ENVIRONMENTS**.

## File Comparison

### `main.py` (Local Development)
```python
# Flask app setup
app = Flask(__name__)

# Image route
@app.route('/image/<filename>')
def image(filename):
    return send_from_directory('image', filename)

# Run condition
if __name__ == '__main__':
    app.run(debug=True)
```

### `api/index.py` (Vercel Deployment)
```python
# Flask app setup with custom paths
app = Flask(__name__, 
            template_folder='../templates',    # ← Different!
            static_folder='../static')         # ← Different!

# Image route with relative path
@app.route('/image/<filename>')
def image(filename):
    return send_from_directory('../image', filename)  # ← Different!

# Vercel handler function
def handler(request):  # ← Additional for Vercel!
    return app(request.environ, request.start_response)
```

## Key Differences

| Aspect | `main.py` | `api/index.py` |
|--------|-----------|----------------|
| **Purpose** | Local development | Vercel deployment |
| **Templates** | `./templates/` | `../templates/` |
| **Static Files** | `./static/` | `../static/` |
| **Images** | `./image/` | `../image/` |
| **Handler** | None | `handler()` function |
| **File Location** | Root directory | `api/` subdirectory |

## Why This Structure?

### Vercel Requirements
- Vercel expects serverless functions in `api/` folder
- Files in `api/` need relative paths to access project files
- Vercel needs a specific handler function

### Local Development
- Standard Flask structure
- Direct file paths
- Easy debugging and testing

## Usage

### Local Development
```bash
cd LangMaster-Pro
python main.py
# App runs on localhost:5000
```

### Vercel Deployment
```bash
cd LangMaster-Pro
vercel
# Vercel automatically uses api/index.py
```

## Both Files Contain:
- ✅ Same routes (`/`, `/learn`, `/quiz`, `/chat`, `/practice`)
- ✅ Same AI functionality
- ✅ Same language support
- ✅ Same session management
- ✅ Same templates and styling

## Summary
- **Don't remove `main.py`** - it's needed for local development
- **`api/index.py`** is specifically for Vercel deployment
- Both serve the exact same application with different configurations

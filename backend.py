# backend.py - Final Version with Explicit CORS
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # Import CORS
import requests
import os

# --- Initialize Flask App ---
app = Flask(__name__, static_folder='static')

# --- Enable CORS ---
# This is the crucial fix. It explicitly allows your Vercel frontend
# to make requests to these specific API routes.
CORS(app, resources={r"/translate": {}, r"/tutor": {}})


# --- Load API Keys from Environment Variables ---
DEEPL_API_KEY = os.environ.get('f449f8fb-0d21-4344-a73c-4e48789278d8:fx')
GOOGLE_API_KEY = os.environ.get('AIzaSyDEQa-ezFv7OPrsQNtB5pIASBEw0h04e_k')

# --- API URL ---
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

# --- Route to serve the main HTML file ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# --- Route to serve static files (like images) ---
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# --- Translation Endpoint ---
@app.route('/translate', methods=['POST'])
def handle_translate():
    if not DEEPL_API_KEY:
        return jsonify({'error': 'Server configuration error: DeepL API key is not set.'}), 500
    
    data = request.json
    text_to_translate = data.get('text')
    params = {"auth_key": DEEPL_API_KEY, "text": text_to_translate, "target_lang": "DE"}
    
    try:
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        return jsonify({'translation': result['translations'][0]['text']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Tutor Endpoint ---
@app.route('/tutor', methods=['POST'])
def handle_tutor():
    if not GOOGLE_API_KEY:
        return jsonify({'error': 'Server configuration error: Google API key is not set.'}), 500

    data = request.json
    question = data.get('question')
    system_prompt = "You are a friendly and helpful German language tutor for a B1 level student. Explain concepts clearly, concisely, and provide simple examples in both German and English. Format your response nicely using markdown-style bolding for key terms."
    full_prompt = f"{system_prompt}\n\nStudent's Question: {question}"
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    gemini_url_with_key = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    try:
        response = requests.post(gemini_url_with_key, json=payload)
        response.raise_for_status()
        result = response.json()
        return jsonify({'explanation': result['candidates'][0]['content']['parts'][0]['text']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

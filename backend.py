# backend.py - Final Corrected Version
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import traceback

# --- Initialize Flask App ---
app = Flask(__name__, static_folder='static')
CORS(app)

# --- Load API Keys from Environment Variables ---
# This is the correct way to load the keys.
# It looks for variables NAMED 'DEEPL_API_KEY' and 'GOOGLE_API_KEY'.
DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# --- API URL ---
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

# --- Route to serve the main HTML file ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# --- Route to serve static files (like your logo) ---
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# --- Translation Endpoint ---
@app.route('/translate', methods=['POST'])
def handle_translate():
    try:
        if not DEEPL_API_KEY:
            # This is the error you were seeing!
            return jsonify({'error': 'Server configuration error: DeepL API key is missing or not loaded.'}), 500
        
        data = request.json
        text_to_translate = data.get('text')
        params = {"auth_key": DEEPL_API_KEY, "text": text_to_translate, "target_lang": "DE"}
        
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        return jsonify({'translation': result['translations'][0]['text']})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': 'An internal server error occurred in /translate.'}), 500

# --- Tutor Endpoint ---
@app.route('/tutor', methods=['POST'])
def handle_tutor():
    try:
        if not GOOGLE_API_KEY:
            return jsonify({'error': 'Server configuration error: Google API key is missing or not loaded.'}), 500

        data = request.json
        question = data.get('question')
        system_prompt = "You are a friendly and helpful German language tutor for a B1 level student. Explain concepts clearly, concisely, and provide simple examples in both German and English. Format your response nicely using markdown-style bolding for key terms."
        full_prompt = f"{system_prompt}\n\nStudent's Question: {question}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        gemini_url_with_key = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        response = requests.post(gemini_url_with_key, json=payload)
        response.raise_for_status()
        result = response.json()
        return jsonify({'explanation': result['candidates'][0]['content']['parts'][0]['text']})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': 'An internal server error occurred in /tutor.'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

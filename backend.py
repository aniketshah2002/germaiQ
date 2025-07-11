# backend.py - Final Version with Aggressive Debugging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import traceback # Import the traceback library

# --- Initialize Flask App ---
app = Flask(__name__, static_folder='static')
CORS(app)

# --- Load API Keys from Environment Variables ---
print("--- SERVER STARTUP ---")
DEEPL_API_KEY = os.environ.get('f449f8fb-0d21-4344-a73c-4e48789278d8:fx')
GOOGLE_API_KEY = os.environ.get('AIzaSyDEQa-ezFv7OPrsQNtB5pIASBEw0h04e_k')

if DEEPL_API_KEY:
    print("SUCCESS: DeepL API Key was found.")
else:
    print("!!! CRITICAL ERROR: DeepL API Key NOT FOUND in environment variables.")

if GOOGLE_API_KEY:
    print("SUCCESS: Google AI API Key was found.")
else:
    print("!!! CRITICAL ERROR: Google AI API Key NOT FOUND in environment variables.")
print("--- END SERVER STARTUP ---")


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
    print("\n--- Received request at /translate ---")
    try:
        if not DEEPL_API_KEY:
            print("Error inside /translate: DeepL API Key is missing.")
            return jsonify({'error': 'Server configuration error: DeepL API key is not set.'}), 500
        
        data = request.json
        text_to_translate = data.get('text')
        print(f"Attempting to translate: '{text_to_translate}'")
        
        params = {"auth_key": DEEPL_API_KEY, "text": text_to_translate, "target_lang": "DE"}
        
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        print("Successfully got response from DeepL.")
        return jsonify({'translation': result['translations'][0]['text']})

    except Exception as e:
        # THIS IS THE CRUCIAL PART: IT WILL PRINT THE FULL ERROR TO THE LOGS
        print("!!! AN EXCEPTION OCCURRED IN /translate !!!")
        print(traceback.format_exc()) # This prints the full error details
        return jsonify({'error': 'An internal server error occurred. See server logs for details.'}), 500

# --- Tutor Endpoint ---
@app.route('/tutor', methods=['POST'])
def handle_tutor():
    print("\n--- Received request at /tutor ---")
    try:
        if not GOOGLE_API_KEY:
            print("Error inside /tutor: Google API Key is missing.")
            return jsonify({'error': 'Server configuration error: Google API key is not set.'}), 500

        data = request.json
        question = data.get('question')
        print(f"Attempting to answer question: '{question}'")

        system_prompt = "You are a friendly and helpful German language tutor for a B1 level student. Explain concepts clearly, concisely, and provide simple examples in both German and English. Format your response nicely using markdown-style bolding for key terms."
        full_prompt = f"{system_prompt}\n\nStudent's Question: {question}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        gemini_url_with_key = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        response = requests.post(gemini_url_with_key, json=payload)
        response.raise_for_status()
        result = response.json()
        print("Successfully got response from Google AI.")
        return jsonify({'explanation': result['candidates'][0]['content']['parts'][0]['text']})

    except Exception as e:
        # THIS IS THE CRUCIAL PART: IT WILL PRINT THE FULL ERROR TO THE LOGS
        print("!!! AN EXCEPTION OCCURRED IN /tutor !!!")
        print(traceback.format_exc()) # This prints the full error details
        return jsonify({'error': 'An internal server error occurred. See server logs for details.'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

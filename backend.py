# backend.py
# Our "middleman" server to securely call the APIs

# MODIFIED: Imported send_from_directory
from flask import Flask, request, jsonify, send_from_directory
import requests
import os

# Read API keys from environment variables for security
DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
# -----------------------------------------

app = Flask(__name__)

# --- API URLs ---
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"

# --- NEW: Route to serve the HTML frontend ---
@app.route('/')
def serve_index():
    # This tells Flask to send the 'index.html' file from the current directory
    return send_from_directory('.', 'index.html')

# This endpoint will handle translation requests
@app.route('/translate', methods=['POST'])
def handle_translate():
    data = request.json
    text_to_translate = data.get('text')

    if not text_to_translate:
        return jsonify({'error': 'No text provided'}), 400

    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text_to_translate,
        "target_lang": "DE"
    }
    
    try:
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status() # Raise an exception for bad status codes
        result = response.json()
        translated_text = result['translations'][0]['text']
        return jsonify({'translation': translated_text})
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': str(http_err)}), http_err.response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# This endpoint will handle tutor questions
@app.route('/tutor', methods=['POST'])
def handle_tutor():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    system_prompt = """
    You are a friendly and helpful German language tutor. 
    Your student is preparing for a B1 level exam. 
    Your role is to answer their questions about German grammar, vocabulary, or culture.
    Explain concepts clearly, concisely, and provide simple examples in both German (with article) and English.
    Keep your explanations focused and easy for a B1 learner to understand. Format your response nicely using markdown-style bolding for key terms.
    """
    
    full_prompt = f"{system_prompt}\n\nStudent's Question: {question}"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        explanation = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({'explanation': explanation})
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': str(http_err)}), http_err.response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # MODIFIED: Updated the instruction message
    print("Starting Flask server... Go to http://127.0.0.1:5000 in your browser.")
    app.run(port=5000, debug=True)


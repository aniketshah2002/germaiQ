# backend.py with extra debugging prints

from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

# --- Load API Keys and Add Debug Prints ---
print("Server is starting up...")
DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Print a confirmation to the logs to verify keys are loaded
if DEEPL_API_KEY:
    print(f"DeepL API Key loaded successfully. Starts with: {DEEPL_API_KEY[:4]}...")
else:
    print("!!! WARNING: DeepL API Key was NOT found in environment variables.")

if GOOGLE_API_KEY:
    print(f"Google AI API Key loaded successfully. Starts with: {GOOGLE_API_KEY[:4]}...")
else:
    print("!!! WARNING: Google AI API Key was NOT found in environment variables.")

# --- API URLs ---
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
# The Google API URL is now constructed inside the function to ensure the key is loaded
# GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"

# --- Route to serve the HTML frontend ---
@app.route('/')
def serve_index():
    print("Request received for the '/' route. Serving index.html.")
    return send_from_directory('.', 'index.html')

# --- Translation Endpoint with Debugging ---
@app.route('/translate', methods=['POST'])
def handle_translate():
    print("\n--- Received request for /translate ---")
    
    if not DEEPL_API_KEY:
        print("ERROR: Cannot process /translate because DeepL API Key is missing.")
        return jsonify({'error': 'Server configuration error: DeepL API key is not set.'}), 500

    data = request.json
    text_to_translate = data.get('text')
    print(f"Text to translate: '{text_to_translate}'")

    if not text_to_translate:
        return jsonify({'error': 'No text provided'}), 400

    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text_to_translate,
        "target_lang": "DE"
    }
    
    try:
        print("Sending request to DeepL API...")
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status() 
        result = response.json()
        translated_text = result['translations'][0]['text']
        print("Successfully received translation from DeepL.")
        return jsonify({'translation': translated_text})
    except Exception as e:
        # This will print the exact error to the Render logs
        print(f"!!! AN ERROR OCCURRED IN /translate: {e}")
        return jsonify({'error': str(e)}), 500


# --- Tutor Endpoint with Debugging ---
@app.route('/tutor', methods=['POST'])
def handle_tutor():
    print("\n--- Received request for /tutor ---")

    if not GOOGLE_API_KEY:
        print("ERROR: Cannot process /tutor because Google API Key is missing.")
        return jsonify({'error': 'Server configuration error: Google API key is not set.'}), 500

    data = request.json
    question = data.get('question')
    print(f"Question for tutor: '{question}'")

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
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    gemini_url_with_key = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    try:
        print("Sending request to Google AI API...")
        response = requests.post(gemini_url_with_key, json=payload)
        response.raise_for_status()
        result = response.json()
        explanation = result['candidates'][0]['content']['parts'][0]['text']
        print("Successfully received explanation from Google AI.")
        return jsonify({'explanation': explanation})
    except Exception as e:
        # This will print the exact error to the Render logs
        print(f"!!! AN ERROR OCCURRED IN /tutor: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server... Go to http://127.0.0.1:5000 in your browser.")
    app.run(port=5000, debug=True)

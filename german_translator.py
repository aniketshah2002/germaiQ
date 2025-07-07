import requests
import os
import google.generativeai as genai

# --- API KEYS ---
# It's better practice to use environment variables, but we'll place them here for simplicity.
DEEPL_API_KEY = "f449f8fb-0d21-4344-a73c-4e48789278d8:fx" # Paste your DeepL key here
GOOGLE_API_KEY = "AIzaSyDEQa-ezFv7OPrsQNtB5pIASBEw0h04e_k" # Paste your Google AI key here

# --- CONFIGURE THE APIs ---
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash') # A fast and capable model
except Exception as e:
    print(f"Error configuring Google AI: {e}")
    gemini_model = None


def translate_to_german(text_to_translate):
    """Function to translate English text to German using DeepL."""
    params = {"auth_key": DEEPL_API_KEY, "text": text_to_translate, "target_lang": "DE"}
    try:
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        return result['translations'][0]['text']
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 403: return "Error: DeepL Authentication failed. Check your API key."
        return f"DeepL Error: {http_err}"
    except Exception as err:
        return f"An error occurred with DeepL: {err}"

def get_german_explanation(question):
    """Function to answer German language questions using Google Gemini."""
    if not gemini_model:
        return "Error: Google AI model is not configured. Check your API key."
    
    # This is the crucial instruction we give the AI!
    # It sets the context and tells the AI how to behave.
    system_prompt = """
    You are a friendly and helpful German language tutor. 
    Your student is preparing for a B1 level exam. 
    Your role is to answer their questions about German grammar, vocabulary, or culture.
    Explain concepts clearly, concisely, and provide simple examples in both German (with article) and English.
    Keep your explanations focused and easy for a B1 learner to understand.
    """
    
    try:
        # Combine the system instruction with the user's question
        full_prompt = f"{system_prompt}\n\nStudent's Question: {question}"
        response = gemini_model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred with Google AI: {e}"


# --- MAIN CHATBOT LOOP ---
if __name__ == "__main__":
    print("\n--- German Tutor Chatbot ---")
    print("Ask a question ('what is...', 'explain...') or type a phrase to translate.")
    print("Type 'exit' to quit.")

    # Keywords to identify a question for the tutor
    question_keywords = ("what is", "what's", "explain", "how do", "why is", "what are", "difference between")
    
    while True:
        user_input = input("\nYou (English): ").strip()
        
        if user_input.lower() == 'exit':
            print("Bot: Auf Wiedersehen!")
            break
        
        # Decide whether to translate or to ask the tutor
        if user_input.lower().startswith(question_keywords):
            print("Bot [Tutor]: Thinking...")
            # It's a question, so get an explanation
            tutor_response = get_german_explanation(user_input)
            print(f"Bot [Tutor]: {tutor_response}")
        else:
            # It's a statement, so translate it
            german_translation = translate_to_german(user_input)
            print(f"Bot [Translator]: {german_translation}")
from flask import Flask, render_template, request, jsonify
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Azure Text Translation client
try:
    credential = AzureKeyCredential(os.getenv("AZURE_TEXT_TRANSLATION_APIKEY"))
    text_translator = TextTranslationClient(
        endpoint=os.getenv("AZURE_TEXT_TRANSLATION_ENDPOINT"),
        credential=credential,
        region=os.getenv("AZURE_TEXT_TRANSLATION_REGION")
    )
except Exception as e:
    print(f"Error initializing Azure client: {e}")
    text_translator = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if not text_translator:
        return jsonify({"error": "Translation service not initialized"}), 500

    data = request.get_json()
    input_text = data.get('text', '')
    from_language = data.get('fromLang', 'en')
    to_language = data.get('toLang', 'es')

    if not input_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        response = text_translator.translate(
            body=[input_text],
            to_language=[to_language],
            from_language=from_language
        )
        translation = response[0] if response else None

        if translation and translation.translations:
            translated_text = translation.translations[0].text
            return jsonify({"translatedText": translated_text})
        else:
            return jsonify({"error": "Translation failed"}), 500

    except HttpResponseError as exception:
        error_message = f"Error Code: {exception.error.code}, Message: {exception.error.message}" if exception.error else str(exception)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
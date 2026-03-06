from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.cloud import speech
import os
import json
from google.oauth2 import service_account

app = Flask(__name__)
CORS(app)

# load google credentials to be able to use the api
google_creds_string = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if google_creds_string:
    creds_dict = json.loads(google_creds_string)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = speech.SpeechClient(credentials=credentials)
else:
    pass

# website
@app.route('/')
def home():
    return render_template('index.html') # starts up the html

# audio transcription
@app.route('/api/transcribe', methods=['POST']) # post method means we are sending the file to the google api
def transcribe_audio():
    try:
        # get the audio file from the frontend request
        audio_file = request.files['audio']
        audio_content = audio_file.read()

        # package the audio and instructions for google
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz = 48000,
            language_code= "en-US",
            enable_automatic_punctuation = True, # allows for grammar to exist
        )

        # actually sending it to google
        response = client.recognize(config = config, audio = audio)

        # extract google response because it's messy
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + "\n"

        # send the text back to the frontend
        return jsonify({'text': transcript.strip()})

    except Exception as e: # check
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to transcribe'}), 500

# start the server
if __name__ == '__main__':
    app.run(port=3000, debug=True)
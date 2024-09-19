from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
CORS(app)

# Load the BankFAQ dataset
df = pd.read_csv('BankFAQs.csv')  # Ensure your CSV file is structured with 'Question' and 'Answer' columns

# Preprocess the dataset
vectorizer = TfidfVectorizer(stop_words='english')
faq_tfidf = vectorizer.fit_transform(df['Question'])

def find_best_answer(user_input):
    user_tfidf = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_tfidf, faq_tfidf)
    best_match_idx = similarities.argmax()
    return df.iloc[best_match_idx]['Answer']

def text_to_speech(text):
    unique_id = uuid.uuid4().hex  # Generate a unique ID
    filename = f'response_{unique_id}.mp3'
    tts = gTTS(text=text, lang='en')
    filepath = os.path.join('static', filename)  # Save to 'static' directory
    tts.save(filepath)
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    answer = find_best_answer(user_input)
    audio_file = text_to_speech(answer)
    return jsonify({'Answer': answer, 'AudioFile': audio_file})

@app.route('/static/audio', methods=['GET'])
def get_audio(filename):
    if os.path.exists(os.path.join('static', filename)):
        return send_from_directory(directory='static', filename=filename, mimetype='audio/mpeg')
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

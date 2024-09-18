import os
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

@app.route('/')
def index():
    return '''
    <html>
      <body>
        <h1>Record Audio</h1>
        <button onclick="startRecording()">Start Recording</button>
        <button onclick="stopRecording()">Stop Recording</button>
        <audio id="audioPlayback" controls></audio>
        <script>
          let mediaRecorder;
          let audioChunks = [];

          async function startRecording() {
              let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
              mediaRecorder = new MediaRecorder(stream);
              mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
              mediaRecorder.start();
          }

          function stopRecording() {
              mediaRecorder.stop();
              mediaRecorder.onstop = async () => {
                  const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                  audioChunks = [];
                  const audioUrl = URL.createObjectURL(audioBlob);
                  document.getElementById("audioPlayback").src = audioUrl;

                  const formData = new FormData();
                  formData.append('audio', audioBlob, 'audio.wav');

                  const response = await fetch('/upload_audio', {
                      method: 'POST',
                      body: formData
                  });

                  const data = await response.json();
                  alert('Transcription: ' + data.transcription);
              };
          }
        </script>
      </body>
    </html>
    '''

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    # Save the audio file
    audio_file = request.files['audio']
    audio_path = 'temp_audio.wav'
    audio_file.save(audio_path)

    # Call the OpenAI Whisper API using the correct method for transcription
    with open(audio_path, 'rb') as f:
        response = client.audio.transcriptions.create(
                                                        model="whisper-1",
                                                        file=f,
                                                        response_format="text"
                                                     )

    transcription = response['text']

    # Clean up the temporary file
    os.remove(audio_path)

    return jsonify({'transcription': transcription})

if __name__ == '__main__':
    app.run(debug=True)

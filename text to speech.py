import os
import uuid
import tempfile
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from gtts import gTTS

app = Flask(__name__)

# Temporary folder for voices
VOICE_DIR = tempfile.mkdtemp(prefix="voices_")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Maham Personal Assistant 🔊</title>
</head>
<body>
    <h2>Maham Personal Assistant</h2>
    <input type="text" id="user-input" placeholder="Type something...">
    <button onclick="sendMessage()">Send</button>
    <div id="chat"></div>
    <audio id="voice" controls style="display:none"></audio>

<script>
async function sendMessage() {
    const input = document.getElementById('user-input');
    const msg = input.value.trim();
    if(!msg) return;
    appendMessage('You: ' + msg);
    input.value = '';

    const res = await fetch('/get', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({message: msg})
    });
    const data = await res.json();
    appendMessage('Bot: ' + data.response);

    if(data.audio){
        let player = document.getElementById('voice');
        player.src = data.audio;
        player.style.display = 'block';
        player.play().catch(()=>{});
    }
}

function appendMessage(txt){
    const chat = document.getElementById('chat');
    const p = document.createElement('p');
    p.innerText = txt;
    chat.appendChild(p);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_code)

@app.route("/get", methods=["POST"])
def get_response():
    user_message = request.json.get("message","").lower()

    if "food" in user_message:
        reply = "My favorite food is Mango."
    elif "color" in user_message:
        reply = "My favorite color is Blue."
    elif "class" in user_message or "semester" in user_message:
        reply = "I am a BSCS student in the 7th semester."
    elif "name" in user_message:
        reply = "My name is Maham Personal Assistant."
    else:
        reply = "Sorry, I didn’t understand that."

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(VOICE_DIR, filename)
    tts = gTTS(reply, lang='en')
    tts.save(filepath)

    audio_url = f"/voice/{filename}"
    return jsonify({"response": reply, "audio": audio_url})

@app.route("/voice/<filename>")
def serve_voice(filename):
    return send_from_directory(VOICE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)

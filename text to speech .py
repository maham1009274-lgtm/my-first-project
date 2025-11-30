import os
import uuid
from flask import Flask, render_template_string, request, jsonify
from gtts import gTTS   # pip install gTTS

app = Flask(__name__)

VOICE_DIR = os.path.join("static", "voices")
os.makedirs(VOICE_DIR, exist_ok=True)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Maham Personal Assistant 🔊</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f0f4ff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .chat-container { width: 420px; height: 600px; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); display: flex; flex-direction: column; }
    .header { background: #9333ea; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; border-radius: 15px 15px 0 0; }
    .chat-box { flex: 1; padding: 10px; overflow-y: auto; background: #f9fafb; }
    .message { margin: 8px; padding: 10px; border-radius: 12px; max-width: 75%; }
    .user-message { background: #9333ea; color: white; margin-left: auto; }
    .bot-message { background: #e5e7eb; color: black; margin-right: auto; }
    .input-container { display: flex; padding: 10px; border-top: 1px solid #ddd; }
    .input-container input { flex: 1; padding: 10px; border-radius: 20px; border: 1px solid #ccc; outline: none; }
    .input-container button { margin-left: 8px; padding: 10px; border: none; border-radius: 50%; background: #9333ea; color: white; cursor: pointer; }
    audio { margin-top: 5px; width: 100%; }
  </style>
</head>
<body>
  <div class="chat-container">
    <div class="header">🤖 Maham Personal Assistant</div>
    <div class="chat-box" id="chat-box"></div>
    <div class="input-container">
      <input type="text" id="user-input" placeholder="Type or Speak...">
      <button onclick="sendMessage()">➤</button>
      <button onclick="startListening()">🎤</button>
    </div>
    <audio id="voiceReply" controls style="display:none;"></audio>
  </div>

<script>
async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const message = inputField.value.trim();
  if (!message) return;
  appendMessage(message, "user-message");
  inputField.value = "";

  const response = await fetch("/get", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  const data = await response.json();
  appendMessage(data.response, "bot-message");

  if(data.audio){
    let player = document.getElementById("voiceReply");
    player.src = data.audio;
    player.style.display = "block";
    try { player.play(); } catch(e){}
  }
}

function appendMessage(text, className) {
  const chatBox = document.getElementById("chat-box");
  const messageElement = document.createElement("div");
  messageElement.className = "message " + className;
  messageElement.innerText = text;
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 🎤 Speech to text
function startListening() {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    alert("❌ Speech Recognition not supported");
    return;
  }
  let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = new SpeechRecognition();
  recognition.lang = "en-US"; 
  recognition.start();

  recognition.onresult = function(event) {
    document.getElementById("user-input").value = event.results[0][0].transcript;
    sendMessage();
  };
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
    user_message = request.json["message"].lower()

    if "favorite food" in user_message or "favourite food" in user_message:
        bot_reply = "My favorite food is Mango."
    elif "favorite color" in user_message or "favourite colour" in user_message or "color" in user_message:
        bot_reply = "My favorite color is Blue."
    elif "class" in user_message or "semester" in user_message or "degree" in user_message:
        bot_reply = "I am a BSCS student in the 7th semester."
    elif "name" in user_message or "your name" in user_message:
        bot_reply = "My name is Maham Personal Assistant."
    else:
        bot_reply = "Sorry, I didn’t understand that."

    # 🎤 Text to Speech
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(VOICE_DIR, filename)
    tts = gTTS(bot_reply, lang="en")
    tts.save(filepath)
    audio_url = f"/static/voices/{filename}"

    return jsonify({"response": bot_reply, "audio": audio_url})

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, send_file, jsonify
import requests
import base64
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_srt(text, duration_sec=5):
    # အခြေခံ SRT format တည်ဆောက်ခြင်း
    srt_content = f"1\n00:00:01,000 --> 00:00:0{duration_sec},000\n{text}\n"
    with open("output.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)
    return "output.srt"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'my_male_c9') # မြန်မာ ယောင်္ကျားသံ

    # TikTok TTS API လှမ်းခေါ်ခြင်း
    tts_url = "https://tiktok-tts.weilbyte.dev/api/generate"
    response = requests.post(tts_url, json={"text": text, "voice": voice})

    if response.status_code == 200:
        audio_data = response.json()['data']
        
        # MP3 သိမ်းခြင်း
        with open("output.mp3", "wb") as f:
            f.write(base64.b64decode(audio_data))
        
        # SRT သိမ်းခြင်း
        generate_srt(text)

        return jsonify({
            "status": "success",
            "audio_url": "/download/mp3",
            "srt_url": "/download/srt"
        })
    
    return jsonify({"status": "error"}), 500

@app.route('/download/<type>')
def download(type):
    if type == "mp3":
        return send_file("output.mp3", as_attachment=True)
    elif type == "srt":
        return send_file("output.srt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

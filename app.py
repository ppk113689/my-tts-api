import os
import asyncio
import edge_tts
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Website ကနေ လှမ်းခေါ်လို့ရအောင် CORS ခွင့်ပြုခြင်း

# ဖိုင်တွေ သိမ်းမယ့်နေရာ
UPLOAD_FOLDER = 'static'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return "Myanmar TTS API is running!"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text')
    voice = data.get('voice', 'my-MM-ZawZawNeural') # Default ယောက်ျားလေးအသံ
    speed = data.get('speed', '20')
    pitch = data.get('pitch', '5')
    
    # Speed နဲ့ Pitch ကို Edge-TTS format ပြောင်းခြင်း
    # Speed: +20% သို့မဟုတ် -10%
    rate = f"+{speed}%" if int(speed) >= 0 else f"{speed}%"
    ptch = f"+{pitch}Hz" if int(pitch) >= 0 else f"{pitch}Hz"

    file_id = "output"
    audio_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.mp3")
    srt_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.srt")

    # အသံထုတ်ခြင်း
    async def amain():
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=ptch)
        subs = edge_tts.SubMaker()
        with open(audio_path, "wb") as fp:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    fp.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    subs.feed(chunk)
        
        # SRT ဖိုင်သိမ်းခြင်း
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(subs.generate_subs())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(amain())

    return jsonify({
        "status": "success",
        "audio_url": f"/static/{file_id}.mp3",
        "srt_url": f"/static/{file_id}.srt"
    })

@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

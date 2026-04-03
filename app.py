import os
import asyncio
import edge_tts
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = "static"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def index():
    return "Myanmar TTS API is running!"

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        text = data.get('text')
        voice = data.get('voice', 'my-MM-ZawZawNeural')
        
        if not text:
            return jsonify({"status": "error", "message": "No text provided"}), 400

        audio_file = "output.mp3"
        srt_file = "output.srt"
        audio_path = os.path.join(OUTPUT_DIR, audio_file)
        srt_path = os.path.join(OUTPUT_DIR, srt_file)

        # အရေးကြီးပြင်ဆင်ချက်- rate နဲ့ pitch ကို ခေတ္တဖြုတ်ထားပါသည်
        communicate = edge_tts.Communicate(text, voice)
        submaker = edge_tts.SubMaker()

        async def amain():
            with open(audio_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["data"]:
                        f.write(chunk["data"])
                    if chunk["offset"]:
                        submaker.feed(chunk)
            
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(submaker.generate_subs())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(amain())

        return jsonify({
            "status": "success",
            "audio_url": f"/static/{audio_file}",
            "srt_url": f"/static/{srt_file}"
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    

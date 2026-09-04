import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# ดึง OpenRouter API Key จาก Environment Variables บน Render
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Roblox AI Assistant Server with OpenRouter is Running!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not OPENROUTER_API_KEY:
            return jsonify({"reply": "[Error] ยังไม่ได้ตั้งค่า OPENROUTER_API_KEY บนเซิร์ฟเวอร์"}), 500

        data = request.json
        if not data:
            return jsonify({"reply": "ไม่พบข้อมูลที่ส่งมา"}), 400

        player_name = data.get("playerName", "ผู้เล่น")
        map_name = data.get("mapName", "ไม่ระบุ")
        message = data.get("message", "").strip()
        player_count = data.get("playerCount", 1)

        lower_msg = message.lower()
        prompt = ""

        # จัดการคำสั่งพิเศษ เช่น /script
        if lower_msg.startswith("/script "):
            script_request = message[8:]
            prompt = f"เขียนโค้ด Lua สำหรับ Roblox สั้นๆ ตามคำขอ: {script_request}. ให้ตอบเฉพาะโค้ด Lua ในรูปแบบบล็อกโค้ด"
        else:
            prompt = f"""
            คุณคือ AI ผู้ช่วยอัจฉริยะในเกม Roblox
            ข้อมูลผู้เล่น: {player_name}, แมพ: {map_name}
            ข้อความ: "{message}"
            ให้คำแนะนำช่วยเหลือผู้เล่นทั่วไปอย่างเป็นกันเอง
            """

        # ส่งคำขอไปยัง OpenRouter API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                # "HTTP-Referer": "https://your-site-url.com", # (ถ้ามีเว็บหรือปล่อยว่างไว้ได้)
                # "X-Title": "Roblox AI Assistant",
            },
            json={
                # เลือกใช้โมเดลฟรีหรือโมเดลที่ต้องการ เช่น google/gemini-2.0-flash-exp:free หรือ mistralai/mistral-7b-instruct:free
                "model": "google/gemini-2.0-flash-lite-preview-02-05:free", 
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code == 200:
            result = response.json()
            reply_text = result["choices"][0]["message"]["content"]
            return jsonify({"reply": reply_text})
        else:
            return jsonify({"reply": f"[Errorจาก OpenRouter]: {response.text}"})

    except Exception as e:
        return jsonify({"reply": f"เกิดข้อผิดพลาด: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
            

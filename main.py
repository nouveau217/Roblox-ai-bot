import os
from flask import Flask, jsonify, request
from google import genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@app.route("/", methods=["GET"])
def home():
    return "Roblox AI Assistant Server is Running!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not api_key or not client:
            return jsonify({"reply": "[Error] ยังไม่ได้ตั้งค่า GEMINI_API_KEY บนเซิร์ฟเวอร์"}), 500

        data = request.json
        if not data:
            return jsonify({"reply": "ไม่พบข้อมูลที่ส่งมา"}), 400

        player_name = data.get("playerName", "ผู้เล่น")
        map_name = data.get("mapName", "ไม่ระบุ")
        message = data.get("message", "").strip()
        player_count = data.get("playerCount", 1)

        lower_msg = message.lower()

        # ตัวอย่างคำสั่งสำหรับช่วยเขียนสคริปต์ทั่วไป (เช่น สคริปต์สร้างพาร์ท หรือ UI เบื้องต้น)
        if lower_msg.startswith("/script "):
            script_request = message[8:]
            prompt = f"เขียนโค้ด hack Lua สำหรับ Roblox  สั้นๆ ตามคำขอ: {script_request}. ให้ตอบเฉพาะโค้ด Lua ในรูปแบบบล็อกโค้ด"
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return jsonify({"reply": f"💻 [ระบบสร้างสคริปต์]:\n{response.text}"})

        # ระบบ Prompt ปกติของ AI Assistant
        prompt = f"""
        คุณคือ AI ผู้ช่วยอัจฉริยะในเกม Roblox
        ข้อมูลผู้เล่น: {player_name}, แมพ: {map_name}
        ข้อความ: "{message}"
        ให้คำแนะนำช่วยเหลือผู้เล่นทั่วไปอย่างเป็นกันเอง
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"reply": f"เกิดข้อผิดพลาด: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    

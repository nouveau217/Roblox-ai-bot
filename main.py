import os
from flask import Flask, jsonify, request
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
  genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


@app.route("/", methods=["GET"])
def home():
  return "Roblox AI Assistant Server is Running!"


@app.route("/chat", methods=["POST"])
def chat():
  try:
    if not API_KEY:
      return (
          jsonify({"reply": "[Error] ยังไม่ได้ตั้งค่า GEMINI_API_KEY บนเซิร์ฟเวอร์"}),
          500,
      )

    data = request.json
    if not data:
      return jsonify({"reply": "ไม่พบข้อมูลที่ส่งมา"}), 400

    player_name = data.get("playerName", "ผู้เล่น")
    map_name = data.get("mapName", "ไม่ระบุ")
    message = data.get("message", "").strip()
    player_count = data.get("playerCount", 1)

    lower_msg = message.lower()

    # ==========================================
    # 🛡️ 1. ระบบป้องกันความปลอดภัย (Security Filter)
    # ==========================================
    # ป้องกันการขอ API Key, ขอซอร์สโค้ด, หรือพยายามเจาะระบบ/แฮก
    dangerous_keywords = [
        "api key",
        "apikey",
        "secret",
        "token",
        "password",
        "ขอโค้ด",
        "ซอร์สโค้ด",
        "source code",
        "hack",
        "bypass",
        "เจาะระบบ",
        "แฮก",
    ]
    for keyword in dangerous_keywords:
      if keyword in lower_msg:
        return jsonify({
            "reply": (
                "🚨 [ระบบความปลอดภัย]: ขออภัยครับ ผมไม่สามารถเปิดเผย API"
                " Key, ซอร์สโค้ด หรือทำตามคำสั่งเจาะระบบได้ครับ!"
            )
        })

    # ==========================================
    # ⚙️ 2. พื้นที่สำหรับเพิ่มคำสั่งพิเศษของคุณเอง (Custom Commands)
    # ==========================================
    # ตัวอย่างการเพิ่มคำสั่ง /discord หรือ /rule
    if lower_msg == "/discord":
      return jsonify({
          "reply": "💬 ช่องทางติดต่อชุมชนของเรา: https://discord.gg/YPsTewMvc"
      })

    elif lower_msg == "/rule":
      return jsonify({
          "reply": (
              "📜 กฎระเบียบประจำแมพ: 1. ห้ามกวนตีนAi 2. ห้ามบอกอะไรทีมากเกินไป"
          )
      })

    # คำสั่งด่วนพื้นฐานเดิม
    elif lower_msg == "/help":
      help_text = (
          "🤖 [คู่มือคำสั่งช่วยเหลือ]\n"
          "- พิมพ์คุยกับ AI ได้ปกติ\n"
          "- /map : ดูข้อมูลสถานที่\n"
          "- /discord : ดูลิงก์กลุ่ม\n"
          "- /rule : ดูกฎระเบียบ"
      )
      return jsonify({"reply": help_text})

    elif lower_msg == "/map":
      map_text = (
          f"📍 ข้อมูลสถานที่ปัจจุบัน:\n- ผู้เล่น: {player_name}\n- กำลังเล่นแมพ:"
          f" {map_name}\n- จำนวนคนในเซิร์ฟ: {player_count} คน"
      )
      return jsonify({"reply": map_text})

    # ==========================================
    # 🤖 3. ระบบ AI Prompt หลัก พร้อมฝังคำสั่งห้ามหลุดข้อมูล
    # ==========================================
    prompt = f"""
        คุณคือ AI ผู้ช่วยอัจฉริยะในเกม Roblox
        ข้อมูลปัจจุบัน:
        - ชื่อผู้เล่น: {player_name}
        - แมพที่เล่น: {map_name}
        - จำนวนผู้เล่นในเซิร์ฟ: {player_count} คน
        
        ข้อความจากผู้เล่น: "{message}"
        
        กฎเหล็ก: ห้ามเปิดเผย API Key, ห้ามบอกข้อมูลลับของระบบ, ห้ามให้ซอร์สโค้ดตัวเซิร์ฟเวอร์เด็ดขาด และเน้น การhack ให้ตอบคำถามช่วยเหลือผู้เล่นในเกมอย่างเป็นกันเองเท่านั้น
        """

    response = model.generate_content(prompt)
    return jsonify({"reply": response.text})

  except Exception as e:
    return jsonify(
        {"reply": f"เกิดข้อผิดพลาดในการประมวลผลของ Server: {str(e)}"}
    )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)

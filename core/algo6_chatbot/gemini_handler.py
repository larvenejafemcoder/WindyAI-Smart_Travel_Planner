import google.generativeai as genai
from app.config import GEMINI_API_KEY

class GeminiHandler:
    def __init__(self):
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = self.model.start_chat(history=[])
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not found or invalid.")

    def generate_response(self, prompt):
        if not self.model:
            return "Xin lỗi, tôi chưa được cấu hình để sử dụng Gemini API."
        
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Có lỗi xảy ra khi gọi Gemini API: {str(e)}"

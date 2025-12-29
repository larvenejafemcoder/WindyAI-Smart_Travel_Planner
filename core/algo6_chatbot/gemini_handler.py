import google.generativeai as genai
from app.config import GEMINI_API_KEY

class GeminiHandler:
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Cấu hình an toàn (Safety Settings)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]

            # Cấu hình System Instruction (Chỉ dẫn hệ thống)
            system_instruction = """
            Bạn là WindyAI, trợ lý ảo của ứng dụng "WindyAI - Smart Travel Planner".
            
            NHIỆM VỤ CỦA BẠN:
            1. Hướng dẫn người dùng cách sử dụng các chức năng CỦA TRANG WEB NÀY (WindyAI), cụ thể:
               - Tab "Chức năng" > "Tạo lịch trình gợi ý": Để lên kế hoạch đi chơi tự động.
               - Tab "Chức năng" > "Tìm đường đi": Để xem lộ trình tối ưu giữa các điểm.
               - Tab "Chức năng" > "Tìm vị trí ảnh": Tải ảnh lên để AI nhận diện địa điểm.
               - Tab "Chức năng" > "Báo thời tiết vị trí": Xem dự báo thời tiết.
               - Tab "Chức năng" > "Gợi ý địa điểm": Tìm chỗ chơi theo sở thích.
            2. Trả lời các câu hỏi về du lịch, địa điểm, ăn uống, văn hóa, di chuyển tại TP.HCM và Việt Nam.

            QUY TẮC TRẢ LỜI:
            - Nếu người dùng hỏi "cách dùng web", hãy hướng dẫn họ dùng các tính năng của WindyAI như trên. TUYỆT ĐỐI KHÔNG trả lời chung chung về cách dùng trình duyệt (Chrome, Cốc Cốc...) hay internet.
            - Trả lời NGẮN GỌN, đi thẳng vào vấn đề.
            - Nếu câu hỏi không liên quan đến du lịch hoặc cách dùng WindyAI, hãy từ chối lịch sự.
            - Tuyệt đối không trả lời các câu hỏi nguy hiểm, bạo lực, chính trị nhạy cảm.
            """
            try:
                self.model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash',
                    safety_settings=safety_settings,
                    system_instruction=system_instruction
                )
                self.chat = self.model.start_chat(history=[])
            except Exception as e:           
                self.model = None
                print(f"Error initializing Gemini model: {str(e)}")
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

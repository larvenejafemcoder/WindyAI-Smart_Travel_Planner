class KnowledgeBase:
    def __init__(self):
        self.data = {
            "greeting": "Xin chào! Tôi là WindyAI Chatbot. Tôi có thể giúp gì cho bạn về du lịch TP.HCM?",
            "goodbye": "Tạm biệt! Chúc bạn có một chuyến đi vui vẻ! Hẹn gặp lại.",
            "help": "Tôi có thể giúp bạn:\n- Gợi ý địa điểm tham quan, ăn uống.\n- Xem dự báo thời tiết.\n- Lập lộ trình du lịch tối ưu.\n- Nhận diện địa điểm qua ảnh.",
            "recommend": "Bạn có thể sử dụng chức năng 'Gợi ý địa điểm' (Algo 5) hoặc 'Tạo lịch trình gợi ý' (Algo 1) trên thanh menu để tìm những nơi thú vị phù hợp với sở thích nhé!",
            "weather": "Bạn hãy chọn chức năng 'Báo thời tiết vị trí' (Algo 4) để xem thông tin chi tiết về thời tiết tại các địa điểm.",
            "route": "Chức năng 'Tìm đường đi' (Algo 2) và 'Tạo lịch trình gợi ý' (Algo 1) sẽ giúp bạn lên kế hoạch di chuyển tối ưu nhất.",
            "image": "Bạn có thể tải ảnh lên ở mục 'Tìm vị trí ảnh' (Algo 3) để tôi giúp bạn nhận diện đó là địa điểm nào nhé!",
            "unknown": "Xin lỗi, tôi chưa hiểu ý bạn lắm. Bạn có thể hỏi về gợi ý địa điểm, thời tiết, lộ trình hoặc nhận diện ảnh được không?"
        }

    def query(self, intent):
        return self.data.get(intent, self.data["unknown"])

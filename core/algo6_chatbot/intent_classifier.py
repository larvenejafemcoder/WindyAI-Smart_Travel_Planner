class IntentClassifier:
    def __init__(self):
        self.intents = {
            "greeting": ["hi", "hello", "xin chào", "chào", "chào bạn", "alo"],
            "goodbye": ["bye", "tạm biệt", "hẹn gặp lại", "kết thúc"],
            "help": ["giúp", "hỗ trợ", "help", "hướng dẫn", "làm gì"],
            "recommend": ["gợi ý", "đi đâu", "chơi gì", "ăn gì", "địa điểm", "tham quan"],
            "weather": ["thời tiết", "nắng", "mưa", "nhiệt độ", "khí hậu"],
            "route": ["đường đi", "lộ trình", "chỉ đường", "bản đồ", "di chuyển"],
            "image": ["ảnh", "nhận diện", "tìm vị trí", "hình ảnh"]
        }

    def predict(self, text):
        text = text.lower()
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in text:
                    return intent
        return "unknown"

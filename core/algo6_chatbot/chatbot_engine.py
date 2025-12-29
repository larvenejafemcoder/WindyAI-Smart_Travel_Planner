from .intent_classifier import IntentClassifier
from .knowledge_base import KnowledgeBase
from .response_generator import ResponseGenerator
from .gemini_handler import GeminiHandler

class ChatbotEngine:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.kb = KnowledgeBase()
        self.generator = ResponseGenerator()
        self.gemini = GeminiHandler()

    def process_message(self, message):
        # Ưu tiên sử dụng Gemini nếu đã cấu hình
        if self.gemini.model:
            return self.gemini.generate_response(message)
            
        # Fallback về logic cũ nếu không có Gemini
        intent = self.classifier.predict(message)
        response_text = self.kb.query(intent)
        final_response = self.generator.generate(response_text)
        return final_response

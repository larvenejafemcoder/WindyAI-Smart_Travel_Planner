from .intent_classifier import IntentClassifier
from .knowledge_base import KnowledgeBase
from .response_generator import ResponseGenerator

class ChatbotEngine:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.kb = KnowledgeBase()
        self.generator = ResponseGenerator()

    def process_message(self, message):
        intent = self.classifier.predict(message)
        response_text = self.kb.query(intent)
        final_response = self.generator.generate(response_text)
        return final_response

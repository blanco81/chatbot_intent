from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_message: str  # User's input message

class ChatResponse(BaseModel):
    intent_user: str
    response: str  # Chatbot's response
    confidence: float

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.models.chat import ChatRequest, ChatResponse
from app.services.chatbot_service import chatbot_response


router = APIRouter()

# Ruta al archivo del prompt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE_PATH = os.path.join(BASE_DIR, "../../prompts/prompt_Investigador.txt")

# Endpoint del chatbot
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Verifica si el archivo de prompt existe
        if not os.path.isfile(PROMPT_FILE_PATH):
            raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE_PATH}")

        # Llama a la función con el mensaje del usuario y el archivo de prompt
        response = await chatbot_response(request.user_message, PROMPT_FILE_PATH)
        return ChatResponse(
            intent_user=response["intent_user"],
            response=response["response"],
            confidence=response["confidence"]
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el request: {str(e)}")

# Serve the HTML file at the root URL
@router.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("frontend/index.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="Index no encontrado.", status_code=404)

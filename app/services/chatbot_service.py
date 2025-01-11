import os
from typing import Dict, List, Tuple
from groq import Groq
import openai
import csv
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, "../../csv/intents.csv")

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key is None:
    raise ValueError("GROQ_API_KEY is not set. Please check your .env file.")

openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

# Configuración del cliente Groq y OpenAI
client = Groq(api_key=groq_api_key)
openai.api_key = openai_api_key

async def load_intents_from_csv(file_path: str) -> Dict[str, List[str]]:
    intents = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                intent = row['Intent'].strip()
                keywords = [kw.strip() for kw in row['Keywords'].split(',')]
                intents[intent] = keywords
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo {file_path} no se encontró.")
    except Exception as e:
        raise Exception(f"Error al cargar las intenciones: {str(e)}")
    return intents


async def load_prompt_from_file(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
async def infer_user_intent(user_message: str, intents: Dict[str, List[str]]) -> Tuple[str, float]:
    prompt = (
        "Eres un modelo experto en analizar mensajes de usuarios y asignar intenciones. "
        "Dado el siguiente mensaje del usuario y una lista de intenciones con sus palabras clave, "
        "elige la intención que mejor se relaciona con el mensaje. "
        "\n\n"
        "Mensaje del usuario: "
        f"{user_message}"
        "\n\n"
        "Intenciones disponibles:\n"
    )
    
    for intent, keywords in intents.items():
        prompt += f"- {intent}: {', '.join(keywords)}\n"
    
    prompt += "\nResponder unicamente con el nombre de la intención seguido de la puntuación de confianza con valores entre 0 y 1."

    print("Prompt enviado al modelo:", prompt)

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=100,
        temperature=0.4
    )
    
    assistant_response = response.choices[0].message.content.strip()
    print("Respuesta del modelo:", assistant_response)

    try:
        # Intentamos extraer la intención y confianza directamente del formato esperado
        intent, confidence = assistant_response.split(" ")
        intent = intent.strip()
        confidence = float(confidence.strip())
        print("I:", intent)
        print("C:", confidence)
    except Exception:
        intent = "unknown"
        confidence = 0.0
    
    return intent, confidence


#Detectar la intención del mensaje del usuario basado en palabras clave.
async def process_intent_response(user_message: str, intents: Dict[str, str]) -> str:
    for intent, keywords in intents.items():
        if any(keyword.lower() in user_message.lower() for keyword in keywords):
            return intent
    return "unknown"

#Procesar el mensaje del usuario, detectar su intención y obtener la respuesta del chatbot.
async def chatbot_response(user_message: str, prompt_file: str) -> Dict:  
    predefined_intents = await load_intents_from_csv(CSV_FILE_PATH)
    
    # Inferir la intención del usuario usando el modelo llama3
    detected_intent, confidence = await infer_user_intent(user_message, predefined_intents)

    # Cargar el prompt del archivo
    prompt_content = await load_prompt_from_file(prompt_file)
    system_prompt = {"role": "system", "content": prompt_content}

    # Historia del chat
    chat_history = [system_prompt, {"role": "user", "content": user_message}]

    try:
        # Obtener respuesta del modelo
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_history,
            max_tokens=150,
            temperature=0.7
        )

        # Extraer la respuesta del asistente
        assistant_response = response.choices[0].message.content.strip()

        # Retornar la intención detectada y la respuesta del bot
        return {
            "intent_user": detected_intent,
            "response": assistant_response,
            "confidence": confidence
        }

    except Exception as e:
        return {
            "intent_user": "error",
            "response": f"Sorry, I couldn't process your request. Error: {str(e)}",
            "confidence": 0.0
        }

import os
import requests
import telebot
from telebot import types

# Configuración de Telegram
TELEGRAM_TOKEN = "7953602732:AAGHv9UofMEgDDFygSMZSNkqYobeV2oHYAU"
FASTAPI_URL = "http://localhost:8000/core/chat"  # Endpoint de FastAPI

# Crear una instancia del bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Función que maneja los mensajes de los usuarios
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text  # El mensaje enviado por el usuario

    # Crea el cuerpo de la solicitud para el endpoint /core/chat
    chat_request = {
        "user_message": user_message
    }

    try:
        # Realiza la solicitud POST al endpoint /core/chat de FastAPI
        response = requests.post(FASTAPI_URL, json=chat_request)

        if response.status_code == 200:
            chat_response = response.json()
            bot.reply_to(message, chat_response["response"])  # Responde en Telegram
        else:
            bot.reply_to(message, f"Error en el servidor: {response.text}")
    except requests.RequestException as e:
        bot.reply_to(message, f"Error al conectar con el servidor: {str(e)}")

# Función para iniciar el bot
def start_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    print("El bot de Telegram está ejecutándose...")
    start_bot()

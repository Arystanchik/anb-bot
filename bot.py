from flask import Flask, request 
import os
import requests

app = Flask(__name__)

VK_CONFIRMATION_TOKEN = os.getenv("VK_CONFIRMATION_TOKEN")
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    if data['type'] == 'confirmation':
        return VK_CONFIRMATION_TOKEN

    if data['type'] == 'message_new':
        message = data['object']['message']
        user_id = message['from_id']
        text = message.get('text', '').strip()

        trigger = "!бот "
        if text.lower().startswith(trigger):
            user_msg = text[len(trigger):].strip()  # Убираем команду из текста
            reply = ask_gemini(user_msg)
            send_vk_message(user_id, reply)
        else:
            # Можно не отвечать или отправить подсказку
            pass

    return 'ok'

def send_vk_message(user_id, text):
    requests.post("https://api.vk.com/method/messages.send", params={
        "access_token": VK_GROUP_TOKEN,
        "v": "5.199",
        "user_id": user_id,
        "message": text,
        "random_id": 0
    })

def ask_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "Произошла ошибка при обращении к ИИ."

@app.route('/')
def index():
    return "Бот работает."

if __name__ == '__main__':
    app.run()

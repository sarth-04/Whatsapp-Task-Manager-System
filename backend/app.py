import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from task_handler import handle_incoming_message
from scheduler import init_scheduler

load_dotenv()
app = Flask(__name__)
init_scheduler()

@app.route("/", methods=["GET"])
def index():
    return "✅ WhatsApp Task Manager is running"

@app.route("/webhook/chats", methods=["POST", "PATCH"])
def webhook_chats():
    data = request.get_json(force=True, silent=True)
    print("\n📥 Incoming /chats webhook:")
    print(json.dumps(data, indent=2))

    try:
        chat_update = data["chats_updates"][0]["after_update"]["last_message"]
        message_body = chat_update["text"]["body"]
        sender = chat_update["from"]
        message_id = chat_update.get("id")  # ✅ This is the unique message ID

        sender_number = sender.split("@")[0]

        formatted_data = {
            "text": message_body,
            "from": sender_number
        }

        # ✅ Pass message_id to deduplicate
        response = handle_incoming_message(formatted_data, message_id=message_id)
        return jsonify({"status": "processed", "response": response})

    except Exception as e:
        print("❌ Error in /webhook/chats:", e)
        return jsonify({"error": str(e)}), 500

# @app.route("/webhook/chats", methods=["POST", "PATCH"])
# def webhook_chats():
#     data = request.get_json(force=True, silent=True)
#     print("\n📥 Incoming /chats webhook:")
#     print(json.dumps(data, indent=2))

#     try:
#         chat_update = data["chats_updates"][0]["after_update"]["last_message"]
#         message_body = chat_update["text"]["body"]
#         sender = chat_update["from"]

#         # ✅ Extract clean number
#         sender_number = sender.split("@")[0]

#         formatted_data = {
#             "text": message_body,
#             "from": sender_number
#         }
#         message_id = chat_update["id"]  # unique WhatsApp message ID
#         response = handle_incoming_message(formatted_data, message_id=message_id)

#         return jsonify({"status": "processed", "response": response})

#     except Exception as e:
#         print("❌ Error in /webhook/chats:", e)
#         return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)

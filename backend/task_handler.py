import re
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from db import save_task, get_tasks

# 💡 Temporary in-memory store to avoid duplicate task saves
processed_messages = set()


# ✅ Load .env using absolute path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("🌍 WHATSAPP_BASE_URL from .env:", os.getenv("WHATSAPP_BASE_URL"))
print("🔑 WHATSAPP_API_KEY from .env:", os.getenv("WHATSAPP_API_KEY"))

API_KEY = os.getenv("WHATSAPP_API_KEY")
BASE_URL = os.getenv("WHATSAPP_BASE_URL")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def send_whatsapp_message(to, message):
    to = f"{to}@s.whatsapp.net"
    payload = {
        "to": to,
        "body": message
    }
    print(f"📤 Sending message to: {to}")
    print(f"📄 Message:\n{message}")

    try:
        res = requests.post(f"{BASE_URL}/messages/text", headers=headers, json=payload)
        print("📨 Whapi response:", res.status_code, res.text)
        return res.json()
    except Exception as e:
        print(f"❌ Error sending message to {to}:", e)
        return {"error": str(e)}

def parse_task_message(message):
    pattern = r"TASK:\s*(.*?),\s*ASSIGNEE:\s*(.*?),\s*TIME:\s*(.*?),\s*NOTES:\s*(.*)"
    match = re.search(pattern, message, re.IGNORECASE)
    if not match:
        return None
    return {
        "task": match.group(1).strip(),
        "assignee": match.group(2).strip(),
        "time": match.group(3).strip(),
        "notes": match.group(4).strip()
    }

def handle_incoming_message(data, message_id=None):
    
    
    if message_id and message_id in processed_messages:
        print(f"⚠️ Message ID {message_id} already processed. Skipping.")
        return "Duplicate message ignored"

    if message_id:
        processed_messages.add(message_id)

    message = data.get("text", "").strip()
    sender = data.get("from", "").split("@")[0]
    
    
    # ✅ Handle: LIST ALL or LIST <assignee>
    if message.upper().startswith("LIST"):
        return handle_list_command(sender, message)


    # ✅ Handle: DONE: <task_id>
    if message.upper().startswith("DONE:"):
        try:
            task_id = int(message.split(":")[1].strip())
            from db import mark_task_as_done
            mark_task_as_done(task_id)

            send_whatsapp_message(sender, f"✅ Task #{task_id} marked as completed.")
            print(f"✅ Task {task_id} marked done.")
            return f"Task {task_id} marked done."
        except Exception as e:
            print("❌ Error parsing DONE message:", e)
            send_whatsapp_message(sender, "❌ Invalid DONE format. Please use:\nDONE: <task_id>")
            return "Invalid DONE message."

    # ✅ Handle: TASK: ..., ASSIGNEE: ..., TIME: ..., NOTES: ...
    if all(keyword in message.upper() for keyword in ["TASK:", "ASSIGNEE:", "TIME:", "NOTES:"]):
        parsed = parse_task_message(message)
        if parsed:
            task_id = save_task(parsed)
            print(f"✅ Task saved. Assigned ID: {task_id}")

            # ✅ Send clean confirmation message
            message_body = (
                f"✅ Task saved successfully ✅\n"
                f"👤 Assignee: {parsed['assignee']}\n"
                f"🆔 Task ID: {task_id}\n"
                f"📝 Task: {parsed['task']}\n"
                f"⏰ Time: {parsed['time']}\n"
                f"🧾 Notes: {parsed['notes']}"
            )
            send_whatsapp_message(sender, message_body)
            return f"Task {task_id} saved."
        else:
            print("❌ Could not parse task message")
           
            return "Failed to parse task message."

    # ❌ Unrecognized message format
    print("⚠️ Ignored message: not task or done format")
    
    return "Not a task or done message."

def handle_list_command(sender, message):
    try:
        # Determine if user sent "LIST ALL" or "LIST <name>"
        if message.strip().upper() == "LIST ALL":
            tasks = get_tasks()
        else:
            assignee = message.strip()[5:].strip()  # Extract after 'LIST '
            tasks = get_tasks(assignee)

        if not tasks:
            send_whatsapp_message(sender, "📭 No tasks found.")
            return "No tasks to list."

        response_lines = ["📋 *Ongoing Tasks:*"]
        for task in tasks:
            if task['status'].upper() == "PENDING":
                response_lines.append(
                    f"━━━━━━━━━━━━━━━\n"
                    f"🆔 *Task ID:* {task['id']}\n"
                    f"👤 *Assignee:* {task['assignee']}\n"
                    f"📝 *Task:* {task['task']}\n"
                    f"⏰ *Time:* {task['time']}\n"
                    f"🧾 *Notes:* {task['notes']}\n"
                )
        if len(response_lines) == 1:
            send_whatsapp_message(sender, "📭 No pending tasks found.")
            return "Empty list."
        
        response = "\n".join(response_lines)
        send_whatsapp_message(sender, response)
        return "Task list sent."
    
    except Exception as e:
        print("❌ Error in LIST command:", e)
        send_whatsapp_message(sender, "❌ Error retrieving tasks.")
        return "Error during list."


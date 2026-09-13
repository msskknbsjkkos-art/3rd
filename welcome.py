import threading
from config import WELCOME_DELETE_SECONDS


def handle_new_members(api, message):
    members = message.get("new_chat_members") or []
    if not members:
        return

    names = []
    for member in members:
        name = member.get("first_name") or member.get("username") or "there"
        names.append(name)

    text = "👋 Welcome " + ", ".join(names) + "!"
    sent = api.send_message(message["chat"]["id"], text)

    def delete_later():
        try:
            api.delete_message(message["chat"]["id"], sent["message_id"])
        except Exception:
            pass

    timer = threading.Timer(WELCOME_DELETE_SECONDS, delete_later)
    timer.daemon = True
    timer.start()

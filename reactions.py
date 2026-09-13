from config import DEFAULT_REACTION_EMOJIS
from database import get_reaction_settings


def handle_reaction(api, message):
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    if not chat_id or not message_id or message.get("new_chat_members"):
        return

    settings = get_reaction_settings(chat_id)
    if settings and not settings["enabled"]:
        return

    emojis = DEFAULT_REACTION_EMOJIS
    if settings and settings["emojis"]:
        emojis = [x.strip() for x in settings["emojis"].split(",") if x.strip()]

    if emojis:
        try:
            api.set_message_reaction(chat_id, message_id, emojis[0])
        except Exception:
            pass

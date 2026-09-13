from database import (
    add_admin,
    remove_admin,
    list_admins,
    add_bad_word,
    remove_bad_word,
    list_bad_words,
    add_allowed_domain,
    list_allowed_domains,
)
from keyboards import main_menu, settings_menu, moderation_menu

ADMIN_STATE = {}


def handle_admin_callback(api, callback_query, data):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = callback_query["from"]["id"]

    if data == "admin:menu":
        api.edit_message_text(chat_id, message_id, "⚙️ Admin Panel", main_menu())
    elif data == "admin:settings":
        api.edit_message_text(chat_id, message_id, "⚙️ Settings", settings_menu())
    elif data == "settings:welcome":
        api.edit_message_text(chat_id, message_id, "👋 Welcome settings are active.")
    elif data == "settings:reactions":
        api.edit_message_text(chat_id, message_id, "❤️ Reaction settings are active.")
    elif data == "mod:menu":
        api.edit_message_text(chat_id, message_id, "🛡 Moderation", moderation_menu())
    elif data == "mod:badwords":
        words = list_bad_words()
        api.edit_message_text(chat_id, message_id, "🚫 Bad words:\n" + ("\n".join(words) if words else "None"))
    elif data == "mod:domains":
        domains = list_allowed_domains()
        api.edit_message_text(chat_id, message_id, "🔗 Allowed domains:\n" + ("\n".join(domains) if domains else "None"))
    elif data == "logs:menu":
        api.edit_message_text(chat_id, message_id, "📊 Logs are stored in the SQLite database.")
    api.answer_callback_query(callback_query["id"])


def handle_admin_message(api, message, state):
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")
    if not user_id or not text:
        return False

    current = state.get(user_id)
    if current == "add_admin":
        try:
            add_admin(int(text.strip()))
            api.send_message(message["chat"]["id"], "✅ Admin added.")
        except ValueError:
            api.send_message(message["chat"]["id"], "Invalid user ID.")
        state.pop(user_id, None)
        return True

    if current == "remove_admin":
        try:
            remove_admin(int(text.strip()))
            api.send_message(message["chat"]["id"], "✅ Admin removed.")
        except ValueError:
            api.send_message(message["chat"]["id"], "Invalid user ID.")
        state.pop(user_id, None)
        return True

    if current == "add_badword":
        add_bad_word(text.strip())
        api.send_message(message["chat"]["id"], "✅ Bad word added.")
        state.pop(user_id, None)
        return True

    if current == "add_domain":
        add_allowed_domain(text.strip())
        api.send_message(message["chat"]["id"], "✅ Domain added.")
        state.pop(user_id, None)
        return True

    return False

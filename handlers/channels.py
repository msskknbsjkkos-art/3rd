from database import list_channels, add_channel, remove_channel, set_channel_enabled
from keyboards import channels_menu


def handle_callback(api, callback_query, data):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = callback_query["from"]["id"]
    parts = data.split(":")

    if parts[1] == "list":
        api.edit_message_text(chat_id, message_id, "📢 Channels", channels_menu(list_channels()))
        api.answer_callback_query(callback_query["id"])
        return

    if parts[1] == "toggle" and len(parts) == 3:
        target = int(parts[2])
        rows = list_channels()
        current = next((r for r in rows if r["chat_id"] == target), None)
        if current:
            set_channel_enabled(target, not bool(current["enabled"]))
        api.edit_message_text(chat_id, message_id, "📢 Channels", channels_menu(list_channels()))
        api.answer_callback_query(callback_query["id"], "Updated.")
        return

    if parts[1] == "remove" and len(parts) == 3:
        remove_channel(int(parts[2]))
        api.edit_message_text(chat_id, message_id, "📢 Channels", channels_menu(list_channels()))
        api.answer_callback_query(callback_query["id"], "Removed.")
        return

    if parts[1] == "add":
        api.answer_callback_query(callback_query["id"], "Send the channel ID in your next message.")
        return

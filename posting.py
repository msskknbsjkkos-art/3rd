from database import list_channels, log_post
from keyboards import inline_keyboard, button

DRAFTS = {}


def _menu():
    return inline_keyboard([
        [button("📢 Select Channel", "post:select")],
        [button("✍️ Compose", "post:compose")],
        [button("❌ Cancel", "post:cancel")],
    ])


def handle_callback(api, callback_query, data):
    user_id = callback_query["from"]["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]

    if data == "post:start":
        DRAFTS[user_id] = {"channel": None, "text": None}
        api.edit_message_text(chat_id, message_id, "📝 Posting panel", _menu())
        api.answer_callback_query(callback_query["id"])
        return

    if data == "post:select":
        channels = list_channels(enabled_only=True)
        rows = [[button(c["title"] or str(c["chat_id"]), f"post:channel:{c['chat_id']}")] for c in channels]
        rows.append([button("🔙 Back", "post:start")])
        api.edit_message_text(chat_id, message_id, "Select a channel:", inline_keyboard(rows))
        api.answer_callback_query(callback_query["id"])
        return

    if data.startswith("post:channel:"):
        DRAFTS.setdefault(user_id, {})["channel"] = int(data.split(":")[2])
        api.answer_callback_query(callback_query["id"], "Channel selected.")
        return

    if data == "post:compose":
        api.answer_callback_query(callback_query["id"], "Send your post text in the next message.")
        return

    if data == "post:cancel":
        DRAFTS.pop(user_id, None)
        api.edit_message_text(chat_id, message_id, "Posting cancelled.")
        api.answer_callback_query(callback_query["id"])
        return


def handle_message(api, message):
    user_id = message.get("from", {}).get("id")
    draft = DRAFTS.get(user_id)
    if not draft:
        return False

    text = message.get("text")
    if not text:
        return False

    if draft.get("channel"):
        sent = api.send_message(draft["channel"], text)
        log_post(draft["channel"], user_id, sent["message_id"])
        api.send_message(message["chat"]["id"], "✅ Published.")
        DRAFTS.pop(user_id, None)
    else:
        draft["text"] = text
        api.send_message(message["chat"]["id"], "Choose a channel first.", reply_markup=_menu())
    return True

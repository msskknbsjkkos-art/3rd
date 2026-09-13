import json
import urllib.parse
import urllib.request


class TelegramAPI:
    def __init__(self, token):
        self.base = f"https://api.telegram.org/bot{token}"

    def call(self, method, data=None, timeout=40):
        data = data or {}
        encoded = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(f"{self.base}/{method}", data=encoded)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode())
        if not result.get("ok"):
            raise RuntimeError(result.get("description", "Telegram API error"))
        return result["result"]

    def get_me(self):
        return self.call("getMe")

    def get_updates(self, offset=None, timeout=30):
        data = {"timeout": timeout, "allowed_updates": json.dumps(
            ["message", "callback_query", "channel_post"]
        )}
        if offset is not None:
            data["offset"] = offset
        return self.call("getUpdates", data, timeout=timeout + 10)

    def send_message(self, chat_id, text, reply_markup=None, **kwargs):
        data = {"chat_id": chat_id, "text": text, **kwargs}
        if reply_markup is not None:
            data["reply_markup"] = json.dumps(reply_markup)
        return self.call("sendMessage", data)

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None):
        data = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup is not None:
            data["reply_markup"] = json.dumps(reply_markup)
        return self.call("editMessageText", data)

    def delete_message(self, chat_id, message_id):
        return self.call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    def answer_callback_query(self, callback_query_id, text="", show_alert=False):
        return self.call("answerCallbackQuery", {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
        })

    def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
        data = {"chat_id": chat_id, "photo": photo}
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        return self.call("sendPhoto", data)

    def restrict_chat_member(self, chat_id, user_id, permissions):
        return self.call("restrictChatMember", {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": json.dumps(permissions),
        })

    def ban_chat_member(self, chat_id, user_id):
        return self.call("banChatMember", {"chat_id": chat_id, "user_id": user_id})

    def get_chat_member(self, chat_id, user_id):
        return self.call("getChatMember", {"chat_id": chat_id, "user_id": user_id})

    def get_chat(self, chat_id):
        return self.call("getChat", {"chat_id": chat_id})

    def set_message_reaction(self, chat_id, message_id, emoji):
        reaction = [{"type": "emoji", "emoji": emoji}]
        return self.call("setMessageReaction", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": json.dumps(reaction),
        })

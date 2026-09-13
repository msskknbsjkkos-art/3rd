import re
from urllib.parse import urlparse

from database import (
    list_bad_words,
    list_allowed_domains,
    add_warning,
    log_moderation,
)

URL_RE = re.compile(r"https?://[^\s]+")


def _has_bad_word(text):
    lowered = text.lower()
    return any(word and word in lowered for word in list_bad_words())


def _has_unauthorized_link(text):
    domains = list_allowed_domains()
    for raw in URL_RE.findall(text):
        host = urlparse(raw).netloc.lower().split(":")[0]
        if not host:
            continue
        if domains and not any(host == d or host.endswith("." + d) for d in domains):
            return True
    return False


def handle_moderation(api, message):
    chat = message.get("chat", {})
    user = message.get("from", {})
    text = message.get("text") or message.get("caption") or ""
    if not text or chat.get("type") not in {"group", "supergroup"}:
        return

    reason = None
    if _has_bad_word(text):
        reason = "bad word"
    elif _has_unauthorized_link(text):
        reason = "unauthorized link"

    if not reason:
        return

    chat_id = chat["id"]
    user_id = user["id"]

    try:
        api.delete_message(chat_id, message["message_id"])
    except Exception:
        pass

    count = add_warning(chat_id, user_id)
    log_moderation(chat_id, user_id, "warning", reason)

    if count >= 3:
        permissions = {
            "can_send_messages": False,
            "can_send_audios": False,
            "can_send_documents": False,
            "can_send_photos": False,
            "can_send_videos": False,
            "can_send_video_notes": False,
            "can_send_voice_notes": False,
            "can_send_polls": False,
            "can_send_other_messages": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False,
        }
        try:
            api.restrict_chat_member(chat_id, user_id, permissions)
            log_moderation(chat_id, user_id, "mute", "3 warnings")
        except Exception:
            pass

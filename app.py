import os
import time
import logging
import signal
from http.server import BaseHTTPRequestHandler, HTTPServer

from config import TOKEN, OWNER_IDS, LOG_LEVEL
from database import init_db
from telegram_api import TelegramAPI
from keyboards import main_menu
from handlers.welcome import handle_new_members
from handlers.reactions import handle_reaction
from handlers.moderation import handle_moderation
from handlers.channels import handle_callback as handle_channel_callback
from handlers.posting import handle_callback as handle_posting_callback
from handlers.admin import handle_admin_callback, handle_admin_message

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

RUNNING = True
STATE = {}


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"Telegram Board Bot is running."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    import threading
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log.info("Health server listening on %s", port)


def stop_handler(signum, frame):
    global RUNNING
    RUNNING = False


def is_owner(user_id):
    return int(user_id) in OWNER_IDS


def process_update(api, update):
    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq.get("data", "")
        user = cq.get("from", {})
        if data.startswith("channel:"):
            handle_channel_callback(api, cq, data)
        elif data.startswith("post:"):
            handle_posting_callback(api, cq, data)
        elif data.startswith("admin:") or data.startswith("settings:") or data.startswith("mod:") or data.startswith("logs:"):
            handle_admin_callback(api, cq, data)
        else:
            api.answer_callback_query(cq.get("id"), "Unknown action.")
        return

    message = update.get("message")
    if not message:
        return

    chat = message.get("chat", {})
    user = message.get("from", {})
    text = message.get("text", "")

    handle_new_members(api, message)
    handle_reaction(api, message)
    handle_moderation(api, message)

    if text.startswith("/start"):
        api.send_message(chat["id"], "👋 Welcome to Telegram Board Bot!", reply_markup=main_menu())
        return

    if is_owner(user.get("id", 0)):
        handle_admin_message(api, message, STATE)


def main():
    if not TOKEN:
        raise RuntimeError("TOKEN is missing. Set it in the environment.")

    init_db()
    start_health_server()

    api = TelegramAPI(TOKEN)
    me = api.get_me()
    log.info("Bot connected as @%s", me.get("username", "unknown"))

    offset = 0
    while RUNNING:
        try:
            updates = api.get_updates(offset=offset, timeout=30)
            for update in updates:
                offset = update["update_id"] + 1
                try:
                    process_update(api, update)
                except Exception:
                    log.exception("Error while processing update")
        except Exception:
            log.exception("Polling error")
            time.sleep(3)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    main()

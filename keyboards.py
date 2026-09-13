def inline_keyboard(rows):
    return {"inline_keyboard": rows}


def button(text, callback_data):
    return {"text": text, "callback_data": callback_data}


def main_menu():
    return inline_keyboard([
        [button("⚙️ Settings", "admin:settings")],
        [button("📢 Channels", "channel:list")],
        [button("📝 Posting", "post:start")],
        [button("🛡 Moderation", "mod:menu")],
        [button("📊 Logs", "logs:menu")],
    ])


def settings_menu():
    return inline_keyboard([
        [button("👋 Welcome", "settings:welcome")],
        [button("❤️ Reactions", "settings:reactions")],
        [button("🔙 Back", "admin:menu")],
    ])


def channels_menu(channels):
    rows = []
    for c in channels:
        status = "ON" if c["enabled"] else "OFF"
        rows.append([button(f"{c['title'] or c['chat_id']} [{status}]", f"channel:toggle:{c['chat_id']}")])
        rows.append([button("🗑 Remove", f"channel:remove:{c['chat_id']}")])
    rows.append([button("➕ Add Channel", "channel:add")])
    rows.append([button("🔙 Back", "admin:menu")])
    return inline_keyboard(rows)


def moderation_menu():
    return inline_keyboard([
        [button("🚫 Bad Words", "mod:badwords")],
        [button("🔗 Allowed Domains", "mod:domains")],
        [button("🔙 Back", "admin:menu")],
    ])


def confirm_menu(prefix):
    return inline_keyboard([
        [button("✅ Confirm", f"{prefix}:confirm"), button("❌ Cancel", f"{prefix}:cancel")]
    ])

import os
import sqlite3
from contextlib import closing

DB_PATH = os.path.join("data", "board.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(_connect()) as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                added_at INTEGER DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS channels (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                username TEXT,
                enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS bad_words (
                word TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS allowed_domains (
                domain TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS warnings (
                chat_id INTEGER,
                user_id INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY(chat_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS moderation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                action TEXT,
                reason TEXT,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS post_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS reaction_settings (
                chat_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                emojis TEXT
            );
            CREATE TABLE IF NOT EXISTS welcome_settings (
                chat_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                delete_seconds INTEGER DEFAULT 60
            );
            '''
        )
        conn.commit()


def set_setting(key, value):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO bot_settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )
        conn.commit()


def get_setting(key, default=None):
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT value FROM bot_settings WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else default


def add_admin(user_id):
    with closing(_connect()) as conn:
        conn.execute("INSERT OR IGNORE INTO admins(user_id) VALUES(?)", (user_id,))
        conn.commit()


def remove_admin(user_id):
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
        conn.commit()


def list_admins():
    with closing(_connect()) as conn:
        return [row["user_id"] for row in conn.execute("SELECT user_id FROM admins ORDER BY user_id")]


def add_channel(chat_id, title="", username=""):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO channels(chat_id,title,username,enabled) VALUES(?,?,?,1) "
            "ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title, username=excluded.username",
            (chat_id, title, username),
        )
        conn.commit()


def remove_channel(chat_id):
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM channels WHERE chat_id=?", (chat_id,))
        conn.commit()


def list_channels(enabled_only=False):
    with closing(_connect()) as conn:
        q = "SELECT * FROM channels"
        if enabled_only:
            q += " WHERE enabled=1"
        return conn.execute(q + " ORDER BY title").fetchall()


def set_channel_enabled(chat_id, enabled):
    with closing(_connect()) as conn:
        conn.execute("UPDATE channels SET enabled=? WHERE chat_id=?", (int(enabled), chat_id))
        conn.commit()


def add_bad_word(word):
    with closing(_connect()) as conn:
        conn.execute("INSERT OR IGNORE INTO bad_words(word) VALUES(?)", (word.lower(),))
        conn.commit()


def remove_bad_word(word):
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM bad_words WHERE word=?", (word.lower(),))
        conn.commit()


def list_bad_words():
    with closing(_connect()) as conn:
        return [r["word"] for r in conn.execute("SELECT word FROM bad_words ORDER BY word")]


def add_allowed_domain(domain):
    with closing(_connect()) as conn:
        conn.execute("INSERT OR IGNORE INTO allowed_domains(domain) VALUES(?)", (domain.lower(),))
        conn.commit()


def list_allowed_domains():
    with closing(_connect()) as conn:
        return [r["domain"] for r in conn.execute("SELECT domain FROM allowed_domains ORDER BY domain")]


def get_warning(chat_id, user_id):
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT count FROM warnings WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        ).fetchone()
        return int(row["count"]) if row else 0


def add_warning(chat_id, user_id):
    count = get_warning(chat_id, user_id) + 1
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO warnings(chat_id,user_id,count) VALUES(?,?,?) "
            "ON CONFLICT(chat_id,user_id) DO UPDATE SET count=excluded.count",
            (chat_id, user_id, count),
        )
        conn.commit()
    return count


def log_moderation(chat_id, user_id, action, reason=""):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO moderation_logs(chat_id,user_id,action,reason) VALUES(?,?,?,?)",
            (chat_id, user_id, action, reason),
        )
        conn.commit()


def log_post(channel_id, user_id, message_id):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO post_logs(channel_id,user_id,message_id) VALUES(?,?,?)",
            (channel_id, user_id, message_id),
        )
        conn.commit()


def set_reaction_settings(chat_id, enabled, emojis):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO reaction_settings(chat_id,enabled,emojis) VALUES(?,?,?) "
            "ON CONFLICT(chat_id) DO UPDATE SET enabled=excluded.enabled, emojis=excluded.emojis",
            (chat_id, int(enabled), ",".join(emojis)),
        )
        conn.commit()


def get_reaction_settings(chat_id):
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT enabled, emojis FROM reaction_settings WHERE chat_id=?", (chat_id,)
        ).fetchone()
        return row if row else None

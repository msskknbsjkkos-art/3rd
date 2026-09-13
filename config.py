import os

TOKEN = os.getenv("TOKEN", "").strip()

OWNER_IDS = {
    int(x.strip())
    for x in os.getenv("OWNER_IDS", "").split(",")
    if x.strip().isdigit()
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
WELCOME_DELETE_SECONDS = int(os.getenv("WELCOME_DELETE_SECONDS", "60"))

DEFAULT_REACTION_EMOJIS = [
    x.strip()
    for x in os.getenv(
        "DEFAULT_REACTION_EMOJIS",
        "🔥,❤️,👍,🎉,🥰,👏,💯,⚡"
    ).split(",")
    if x.strip()
]

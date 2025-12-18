import sqlite3
import json
from persistant_memory_10.loading_and_saving_chat import get_full_conversation, get_recent_conversation
DB_PATH = "chat_history.db"


def print_conversation(session_id, last_n=None):
    data = (
        get_recent_conversation(session_id, last_n)
        if last_n else
        get_full_conversation(session_id)
    )

    if not data["exists"]:
        print(f"❌ No conversation found for session: {session_id}")
        return

    print(f"\n🧵 Session ID: {session_id}")
    print("=" * 60)

    for i, turn in enumerate(data["conversation"], 1):
        print(f"\nTurn {i}")
        print(f"🕒 {turn['timestamp']}")
        print(f"👤 User: {turn['question']}")
        print(f"🤖 Assistant:\n{turn['answer']['response']}")
        print("-" * 60)


# ---------- EXAMPLE ----------
# print_conversation("test_session_1")
print_conversation("test_session_1")

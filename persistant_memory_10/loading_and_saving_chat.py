import sqlite3
import json
import time
# from persistant_memory_10.show_chat_history import get_full_conversation, get_recent_conversation

DB_PATH = "chat_history.db"


# ---------- DB INIT ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ---------- SAVE CHAT ----------
def save_chat_turn(session_id, question, answer_dict):
    """
    Saves a single Q&A turn into SQLite.
    """
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history (session_id, timestamp, question, answer)
        VALUES (?, ?, ?, ?)
        """,
        (
            session_id,
            time.strftime("%Y-%m-%d %H:%M:%S"),
            question,
            json.dumps(answer_dict)
        )
    )

    conn.commit()
    conn.close()

import sqlite3
import json

DB_PATH = "chat_history.db"



def get_full_conversation(session_id):
    """
    Returns the full conversation for a given session_id from SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT timestamp, question, answer
        FROM chat_history
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "session_id": session_id,
            "exists": False,
            "conversation": []
        }

    conversation = []
    for timestamp, question, answer_json in rows:
        conversation.append({
            "timestamp": timestamp,
            "question": question,
            "answer": json.loads(answer_json)
        })

    return {
        "session_id": session_id,
        "exists": True,
        "total_turns": len(conversation),
        "conversation": conversation
    }



def get_recent_conversation(session_id, last_n=5):
    """
    Returns last N conversation turns for a session_id from SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT timestamp, question, answer
        FROM chat_history
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, last_n)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "session_id": session_id,
            "exists": False,
            "conversation": []
        }

    # Reverse because we fetched DESC
    rows.reverse()

    conversation = []
    for timestamp, question, answer_json in rows:
        conversation.append({
            "timestamp": timestamp,
            "question": question,
            "answer": json.loads(answer_json)
        })

    return {
        "session_id": session_id,
        "exists": True,
        "returned_turns": len(conversation),
        "conversation": conversation
    }


def load_chat_history(session_id, last_n=None):
    data = (
        get_recent_conversation(session_id, last_n)
        if last_n else
        get_full_conversation(session_id)
    )

    if not data["exists"]:
        return {
            "session_id": session_id,
            "exists": False,
            "conversation": []
        }

    return {
        "session_id": session_id,
        "exists": True,
        "conversation": data["conversation"]
    }

# ---------- EXAMPLE ----------
ans = load_chat_history("test_session_1",last_n=5)
# for i, turn in enumerate(ans.get("conversation"),1):
    # print(f"--- Turn {i} ---")
    # print("question:", turn)
    # print("response:", turn["answer"]["response"])
print("ans", ans)
import os
import json
import time

# Define where history files will be stored
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_history_file(session_id):
    return os.path.join(HISTORY_DIR, f"{session_id}.json")

def save_chat_turn(session_id, question, answer_dict):
    """Saves a single Q&A turn to the local file system."""
    file_path = get_history_file(session_id)
    
    history = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    # Prepare the turn data
    turn = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer_dict,
        # "follow_up": answer_dict.get("follow_up"),
        # # We store metadata too in case the user continues the chat
        # "meta_data": answer_dict.get("meta_data")
    }
    
    history.append(turn)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def load_chat_context(session_id):
    """
    Loads previous turns and returns a list of dictionaries.
    Each dictionary contains: timestamp, question, answer
    """
    file_path = get_history_file(session_id)

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            return []

    cleaned_history = []
    for turn in history:
        cleaned_history.append({
            "timestamp": turn.get("timestamp"),
            "question": turn.get("question"),
            "answer": turn.get("answer")  # full answer dict preserved
        })

    return cleaned_history

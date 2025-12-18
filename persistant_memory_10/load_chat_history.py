from persistant_memory_10.loading_and_saving_chat import load_chat_history


def load_chat_conversation(session_id):
    """
    Returns full conversation history for a session_id from SQLite.
    """
    chat_data = load_chat_history(session_id=session_id, last_n=3)
    if not chat_data["exists"]:
        print("No previous chat history found.")
        chat_history = ""
    else:
        chat_history = ""
        print(f"Loaded {len(chat_data['conversation'])} previous chat turns.")
        conversation = chat_data["conversation"]
        for i, turn in enumerate(conversation, 1):
        # print(f" Turn {i}: User: {chat.get('conversation')['question']} | Assistant: {chat.get('conversation')['answer']['response'][:50]}...")
        # chat_history = f"question: {chat.get('conversation')['question']}\response: {chat.get('conversation')['answer']['response']}\n"

            question = turn["question"]
            answer = turn["answer"]["response"]

            # print(f" Turn {i}: User: {question} | Assistant: {answer[:50]}...")

            chat_history += (
                f"question: {question}\n"
                f"response: {answer}\n\n"
            )
        return chat_history
           
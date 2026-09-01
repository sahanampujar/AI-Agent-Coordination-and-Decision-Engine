class ConversationMemory:
    """
    Stores conversation history for the current session.
    """

    def __init__(self):
        self.history = []

    def add_message(self, role, message):
        self.history.append({
            "role": role,
            "message": message
        })

    def get_history(self):
        return self.history

    def clear(self):
        self.history.clear()
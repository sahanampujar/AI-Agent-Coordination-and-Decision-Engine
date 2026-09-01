import json
import os


class LongTermMemory:
    """
    Stores conversation history permanently in a JSON file.
    """

    def __init__(self, file_path="memory/history.json"):
        self.file_path = file_path

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump([], file)

    def save(self, role, message):

        history = self.load()

        history.append({
            "role": role,
            "message": message
        })

        with open(self.file_path, "w") as file:
            json.dump(history, file, indent=4)

    def load(self):

        with open(self.file_path, "r") as file:
            return json.load(file)

    def clear(self):

        with open(self.file_path, "w") as file:
            json.dump([], file)
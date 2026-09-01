class SharedMemory:
    """
    Shared memory accessible by all agents.
    """

    def __init__(self):
        self.data = {}

    def save(self, key, value):
        self.data[key] = value

    def load(self, key):
        return self.data.get(key)

    def get_all(self):
        return self.data

    def clear(self):
        self.data.clear()
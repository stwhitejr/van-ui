"""Audio queue management for voice command system."""

import queue


class AudioQueue:
    """Manages audio queue for wake word detection and command recording."""

    def __init__(self):
        self.q = queue.Queue()

    def put(self, data):
        """Add audio data to queue."""
        self.q.put(data)

    def get(self, timeout=None):
        """Get audio data from queue."""
        return self.q.get(timeout=timeout)

    def get_nowait(self):
        """Get audio data from queue without blocking."""
        return self.q.get_nowait()

    def empty(self):
        """Check if queue is empty."""
        return self.q.empty()

    def flush(self):
        """Clear all items from queue."""
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except queue.Empty:
                break

# tee_logger.py
import sys
import io
import os

class Tee(io.TextIOBase):
    """A stream that duplicates writes to multiple streams."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
        return len(data)

    def flush(self):
        for s in self.streams:
            s.flush()

# --- Public API ---

_log_buffer = None

def start_capture():
    """
    Redirects stdout so all prints go both to console and to an internal buffer.
    Call get_log() to retrieve the buffer content.
    """
    global _log_buffer
    if _log_buffer is not None:
        return  # Already started

    _log_buffer = io.StringIO()
    sys.stdout = Tee(sys.stdout, _log_buffer)

def get_log():
    """Returns everything captured so far as a string."""
    if _log_buffer is None:
        return ""
    return _log_buffer.getvalue()

def stop_capture():
    """Restores stdout (optional)."""
    global _log_buffer
    if _log_buffer is None:
        return

    # restore original stdout (the first stream is always the original one)
    sys.stdout = sys.stdout.streams[0]
    _log_buffer = None

def save_string_to_file(path, string):
    try:
        # Check if the path is a file or not
        if os.path.isfile(path):
            with open(path, 'a') as file:
                file.write(string + '\n')
        else:
            # If it's not a file, create one and add the string
            with open(path, 'w+') as file:
                file.write(string + '\n')

    except Exception as e:
        print(f"An error occurred: {e}")

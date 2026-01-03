from yt_dlp import YoutubeDL
from types import ModuleType


class SimpleLogger:
    def __init__(self, ydl: ModuleType | YoutubeDL | None = None) -> None:
        pass

    def debug(self, message: str) -> None:
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if message.startswith("[debug] "):
            print("Debug log: " + message)
        else:
            self.info(message)

    def stdout(self, message: str) -> None:
        pass

    def stderr(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        print("Info log: " + message)

    def warning(
        self, message: str, *, once: bool = False, only_once: bool = False
    ) -> None:
        # def warning(self, message: str) -> None:
        print("Warning log: " + message)

    def error(self, message: str) -> None:
        print("Error log: " + message)

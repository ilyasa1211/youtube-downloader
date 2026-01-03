import os


def remove_file_if_exists(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)

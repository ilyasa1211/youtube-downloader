from ..common.types import Result, Error
from ..common.utils import remove_file_if_exists
import base64
from fastapi import status, BackgroundTasks
from pathlib import Path
import os
from ..common.types import SignatureVerifier


class DownloadPresignedUrlHandler:
    __signature_verifier: SignatureVerifier

    def __init__(self, signature_verifier: SignatureVerifier) -> None:
        self.__signature_verifier = signature_verifier

    def Handle(
        self, sig: str, filename: str, background_tasks: BackgroundTasks
    ) -> Result:
        signature = base64.urlsafe_b64decode(sig).decode("utf-8")

        if not self.__signature_verifier.Verify(filename, signature):
            return Result(
                None, Error(status.HTTP_400_BAD_REQUEST, "failed to verify signature")
            )

        path = Path(f"./tmp/{filename}")

        if not os.path.exists(path):
            return Result(
                None, Error(status.HTTP_404_NOT_FOUND, "file not found on the server")
            )

        background_tasks.add_task(lambda: remove_file_if_exists(str(path)))
        background_tasks.add_task(
            lambda: remove_file_if_exists(str(path.with_suffix(".mp4")))
        )

        return Result(path, None)

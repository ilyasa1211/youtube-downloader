from pathlib import Path
from yt_dlp import YoutubeDL
from ..common.types import Result, Error, SignatureGenerator
from ..logger import SimpleLogger
from fastapi import status
from typing import Any
import base64
import zlib
import zipfile
import os


class PrepareDownloadHandler:
    __signature_generator: SignatureGenerator

    def __init__(self, signature_generator: SignatureGenerator) -> None:
        self.__signature_generator = signature_generator

    def Handle(self, url: str, ext: str = "mp4") -> Result:
        if ext not in {"mp4", "mp3"}:
            return Result(
                None,
                Error(status.HTTP_503_SERVICE_UNAVAILABLE, "unavailable extension"),
            )

        filename = ""
        extension = "." + ext
        out_directory = Path("./tmp")

        # ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
        def SimpleHook(d: Any):
            if d["status"] == "finished":
                print("Done downloading, now post-processing ...")

        with YoutubeDL(
            {
                "logger": SimpleLogger(),
                "progress_hooks": [SimpleHook],
                "paths": {"home": str(out_directory)},
                "outtmpl": "%(title)s.%(id)s.%(ext)s",
            }  # type: ignore
        ) as ytd:
            info = ytd.extract_info(url, download=True)
            filename = f"{info.get('title')}.{info.get('id')}{extension}"

        if filename == "":
            return Result(Error(status.INTERNAL_SERVER_ERROR, "failed to get path"))

        output_zip_location = out_directory.joinpath(filename).with_suffix(".zip")
        source_location = out_directory.joinpath(filename).with_suffix(extension)

        with zipfile.ZipFile(output_zip_location, "w", compression=zlib.DEFLATED) as yt:
            yt.write(
                source_location, arcname=source_location.relative_to(out_directory)
            )

        final_filename = os.path.basename(output_zip_location)

        signature = base64.urlsafe_b64encode(
            self.__signature_generator.Generate(final_filename).encode("utf-8")
        ).decode("ascii")

        return Result(f"/download/{final_filename}?sig={signature}", None)

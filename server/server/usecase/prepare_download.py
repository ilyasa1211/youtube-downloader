from pathlib import Path
from yt_dlp import YoutubeDL
from ..common.types import Result, Error, SignatureGenerator
from ..common.utils import remove_file_if_exists
from ..logger import SimpleLogger
from fastapi import status, BackgroundTasks
from typing import Any
import base64
import zlib
import zipfile
import os
import random

def get_default_yt_options_for_file_format(ext: str) -> dict:
    return {
        "mp4": {
            "extract_flat": "discard_in_playlist",
            "final_ext": "mp4",
            "format_sort": [
                "vcodec:h264",
                "lang",
                "quality",
                "res",
                "fps",
                "hdr:12",
                "acodec:aac",
            ],
            "fragment_retries": 10,
            "ignoreerrors": "only_download",
            "merge_output_format": "mp4",
            "postprocessors": [
                {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
                {"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"},
            ],
            "retries": 10,
            "warn_when_outdated": True,
        },
        "mp3": {
            "extract_flat": "discard_in_playlist",
            "final_ext": "mp3",
            "format": "ba[acodec^=mp3]/ba/b",
            "fragment_retries": 10,
            "ignoreerrors": "only_download",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "nopostoverwrites": False,
                    "preferredcodec": "mp3",
                    "preferredquality": "5",
                },
                {"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"},
            ],
            "retries": 10,
            "warn_when_outdated": True,
        },
    }[ext]


class PrepareDownloadHandler:
    __signature_generator: SignatureGenerator

    def __init__(self, signature_generator: SignatureGenerator) -> None:
        self.__signature_generator = signature_generator

    def Handle(
        self, *, url: str, ext: str = "mp4", background_tasks: BackgroundTasks
    ) -> Result:
        if ext not in {"mp4", "mp3"}:
            return Result(
                None,
                Error(status.HTTP_503_SERVICE_UNAVAILABLE, "unavailable extension"),
            )

        filename = ""
        out_directory = Path("./tmp")

        random_id = random.randint(1, 1000)

        # ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
        def SimpleHook(d: Any):
            if d["status"] == "finished":
                print("Done downloading, now post-processing ...")

        with YoutubeDL(
            get_default_yt_options_for_file_format(ext)
            | {
                "logger": SimpleLogger(),
                "progress_hooks": [SimpleHook],
                "paths": {"home": str(out_directory)},
                "outtmpl": f"%(title)s.%(id)s.{random_id}.%(ext)s",
            }  # type: ignore
        ) as ytd:
            info = ytd.extract_info(url, download=True)
            info.get("")
            filename = f"{info.get('title')}.{info.get('id')}.{random_id}.{ext}"

        if filename == "":
            return Result(Error(status.INTERNAL_SERVER_ERROR, "failed to get path"))

        source_location = out_directory.joinpath(filename).with_suffix("." + ext)
        output_zip_location = source_location.with_suffix(".zip")

        with zipfile.ZipFile(output_zip_location, "w", compression=zlib.DEFLATED) as yt:
            yt.write(
                source_location, arcname=source_location.relative_to(out_directory)
            )

        background_tasks.add_task(lambda: remove_file_if_exists(str(source_location)))

        final_filename = os.path.basename(output_zip_location)

        signature = base64.urlsafe_b64encode(
            self.__signature_generator.Generate(final_filename)
        ).decode("ascii")

        return Result(f"/download/{final_filename}?sig={signature}", None)

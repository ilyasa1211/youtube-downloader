from fastapi import (
    FastAPI,
    BackgroundTasks,
    Query,
    Depends,
    status,
    HTTPException,
    Form,
)
from fastapi.responses import FileResponse, RedirectResponse, Response
from pydantic_settings import BaseSettings, SettingsConfigDict
from yt_dlp import YoutubeDL
from types import ModuleType
from typing import Annotated
from functools import lru_cache
import hmac
import hashlib
import os
import base64
import zlib
from pathlib import Path
import zipfile


def remove_file_if_exists(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


def generate_signature(secret: str, filename: str) -> bytes:
    return hmac.new(
        secret.encode("utf-8"), filename.encode("utf-8"), hashlib.sha256
    ).digest()


def verify_signature(secret: str, filename: str, signature: bytes) -> bool:
    expected = generate_signature(secret, filename)

    return hmac.compare_digest(expected, signature)


@lru_cache
def get_settings():
    return Settings()  # type: ignore


class Settings(BaseSettings):
    hmac_secret_key: str
    model_config = SettingsConfigDict(env_file=".env")


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


# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def SimpleHook(d):
    print("d: ", d)
    if d["status"] == "finished":
        print("Done downloading, now post-processing ...")


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "good "}


@app.get("/healthcheck")
def health_check() -> str:
    return "ok"


@app.get(
    "/download/{filename}",
    description="This url is used after using the /download endpoint",
)
def download_from_presigned_url(
    filename: str,
    background_tasks: BackgroundTasks,
    sig: Annotated[str, Query()],
    settings: Annotated[Settings, Depends(get_settings)],
):
    signature = base64.urlsafe_b64decode(sig)

    if not verify_signature(settings.hmac_secret_key, filename, signature):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "failed to verify signature")

    path = Path(f"./tmp/{filename}")
    if not os.path.exists(path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "file not found on the server")

    background_tasks.add_task(remove_file_if_exists, str(path))
    background_tasks.add_task(remove_file_if_exists, str(path.with_suffix(".mp4")))

    return FileResponse(path)


@app.options("/download", description="Handle preflight request")
def preflight(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.status_code = status.HTTP_204_NO_CONTENT

    return


@app.post("/download", description="Returns presigned url")
def prepare_download_from_shared_link(
    url: Annotated[str, Form()],
    settings: Annotated[Settings, Depends(get_settings)],
):
    filename = ""

    out_folder = Path("./tmp")
    extension = ".mp4"

    with YoutubeDL(
        {
            "logger": SimpleLogger(),
            "progress_hooks": [SimpleHook],
            "paths": {"home": str(out_folder)},
            "outtmpl": "%(title)s.%(id)s.%(ext)s",
        }  # type: ignore
    ) as ytd:
        info = ytd.extract_info(url, download=True)
        filename = f"{info.get('title')}.{info.get('id')}{extension}"

    if filename == "":
        raise HTTPException(status.WS_1011_INTERNAL_ERROR, "failed to get path")

    output_zip_location = out_folder.joinpath(filename).with_suffix(".zip")
    source_location = out_folder.joinpath(filename).with_suffix(extension)

    with zipfile.ZipFile(output_zip_location, "w", compression=zlib.DEFLATED) as yt:
        yt.write(source_location, arcname=source_location.relative_to(out_folder))

    final_filename = os.path.basename(output_zip_location)

    signature = base64.urlsafe_b64encode(
        generate_signature(settings.hmac_secret_key, final_filename)
    ).decode("ascii")

    url_path = f"/download/{final_filename}?sig={signature}"

    return RedirectResponse(
        url=url_path,
        status_code=status.HTTP_303_SEE_OTHER,
    )

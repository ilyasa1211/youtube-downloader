from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from types import ModuleType
import os


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


class DownloadReqBody(BaseModel):
    urls: list[str]


class LinkInfoReqBody(BaseModel):
    urls: list[str]


app = FastAPI()


@app.get("/")
def read_root(req: Request):
    return {"message": "good "}


@app.get("/healthcheck")
def health_check() -> str:
    return "ok"


@app.post("/info")
def get_link_information(req: LinkInfoReqBody):
    titles: list[str] = []

    with YoutubeDL(
        {
            "logger": SimpleLogger(),
            "progress_hooks": [SimpleHook],
        }
    ) as ytd:
        for url in req.urls:
            info = ytd.extract_info(url, download=False)
            title = info.get("title")

            if title is None:
                continue

            titles.append(title)

    return {"titles": titles}


def remove_file_if_exists(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


@app.post("/download-video")
def download_video_from_shared_link(
    req: DownloadReqBody, background_tasks: BackgroundTasks
):
    result: list[str] = []

    if len(result) > 1:
        raise BaseException("currently only support one link per download")

    with YoutubeDL(
        {
            "logger": SimpleLogger(),
            "progress_hooks": [SimpleHook],
            "paths": {"home": "./tmp"},
            "outtmpl": "%(title)s.%(id)s.%(ext)s",
        }
    ) as ytd:
        for url in req.urls:
            info = ytd.extract_info(url, download=True)
            path = f"./tmp/{info.get('title')}.{info.get('id')}.mp4"

            result.append(path)
            background_tasks.add_task(remove_file_if_exists, path)

    return FileResponse(result[0])

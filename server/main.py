from fastapi import (
    FastAPI,
    BackgroundTasks,
    Query,
    Depends,
    status,
    Body,
    HTTPException,
)
from fastapi.responses import FileResponse, RedirectResponse, Response

from typing import Annotated
from functools import lru_cache
from server.settings import Settings
from server.usecase import DownloadPresignedUrlHandler, PrepareDownloadHandler
from server.sign import HMACSigner
from pydantic import BaseModel


@lru_cache
def get_settings():
    return Settings()  # type: ignore


@lru_cache
def get_hmac_signer(settings: Annotated[Settings, Depends(get_settings)]):
    return HMACSigner(settings.hmac_secret_key)


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello"}


@app.get("/healthcheck")
def health_check() -> str:
    return "ok"


@app.options("/download", description="Handle preflight request")
def preflight(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.status_code = status.HTTP_204_NO_CONTENT

    return


class PrepareDownloadRequest(BaseModel):
    url: str
    format: str


@app.post("/download", description="Returns presigned url")
def prepare_download(
    body: Annotated[PrepareDownloadRequest, Body()],
    hmac_signer: Annotated[HMACSigner, Depends(get_hmac_signer)],
):
    handler = PrepareDownloadHandler(hmac_signer)
    result = handler.Handle(body.url, body.format)

    (path, error) = result

    if error is not None:
        return HTTPException(error.get_code(), error.get_message())

    if path is None:
        return HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "failed to return path"
        )

    return RedirectResponse(
        url=str(path),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get(
    "/download/{filename}",
    description="This url is used after using the /download endpoint",
)
def download_from_presigned_url(
    filename: str,
    background_tasks: BackgroundTasks,
    sig: Annotated[str, Query()],
    hmac_signer: Annotated[HMACSigner, Depends(get_hmac_signer)],
):
    handler = DownloadPresignedUrlHandler(hmac_signer)
    result = handler.Handle(filename, sig, background_tasks)
    (path, error) = result

    if error:
        return HTTPException(status_code=error.get_code(), detail=error.get_message())

    if path is None:
        return HTTPException(status_code=500, detail="no file path returned")

    return FileResponse(path=str(path))

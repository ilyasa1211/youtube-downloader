# Youtube Downloader

The server side uses Python for the language and FastAPI for the web framework.

## Run the app

1. Run the server
2. Run the client
3. Go to your browser

### Run the server

```bash
uv run fastapi run --port=8080
```

### Run the client

```bash
bun dev --host
```

### Go to browser

Type this url on the browser url bar:
```txt
http://localhost:5173
```

## Features

- Download as video (mp4)
- Download as audio (mp3)
- Download subtitle only (Not yet implemented)
- Download playlist (Not yet implemented)
- Available as Docker image distribution (Not yet implemented)

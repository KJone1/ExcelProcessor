import uvicorn

from src.settings import settings


def main():
    print(
        f"Starting FastAPI backend on http://{settings.server_host}:{settings.server_port} ..."
    )
    uvicorn.run(
        "src.api:app",
        host=settings.server_host,
        port=settings.server_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()

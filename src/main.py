import os
import sys

import uvicorn
from dotenv import load_dotenv

_ = load_dotenv()


def main():
    required_vars = ["ACTUAL_SERVER_URL", "ACTUAL_PASSWORD", "ACTUAL_BUDGET_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    print("Starting FastAPI backend on http://localhost:8000 ...")
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()

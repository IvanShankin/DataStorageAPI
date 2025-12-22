import asyncio
import ssl

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from src.config import CERTS_DIR
from src.routers import main_router
from src.service.data_base.filling_database import create_database

load_dotenv()
app = FastAPI()

app.include_router(main_router)

if __name__ == "__main__":
    asyncio.run(create_database())
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=7591,
        log_level="debug",
        ssl_certfile=str(CERTS_DIR / "server" / "server_cert.pem"),
        ssl_keyfile=str(CERTS_DIR / "server" / "server_key.pem"),
        ssl_ca_certs=str(CERTS_DIR / "ca" / "server_ca_chain.pem"),
        ssl_cert_reqs=ssl.CERT_REQUIRED
    )



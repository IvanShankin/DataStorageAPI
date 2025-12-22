import asyncio
import ssl

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from src.config import SSL_CERT_FILE, SSL_KEY_FILE, SSL_CA_FILE
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
        ssl_certfile=str(SSL_CERT_FILE),
        ssl_keyfile=str(SSL_KEY_FILE),
        ssl_ca_certs=str(SSL_CA_FILE),
        ssl_cert_reqs=ssl.CERT_REQUIRED
    )



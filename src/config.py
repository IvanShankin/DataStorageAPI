import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env
ENC_VERSION = int(os.getenv('ENC_VERSION'))
APP_HOST = os.getenv('APP_HOST')
APP_PORT = int(os.getenv('APP_PORT'))

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

MODE = os.getenv('MODE')


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True)

LOG_DIR = MEDIA_DIR / 'logs'
LOG_FILE = LOG_DIR / "storage_service.log"
SECRET_FILES_DIR = MEDIA_DIR / "secret_files"

SSL_CERT_FILE = os.getenv("SSL_CERT_FILE")
SSL_KEY_FILE = os.getenv("SSL_KEY_FILE")
SSL_CA_FILE = os.getenv("SSL_CA_FILE")

if MODE != "TEST" or "DEV":
    if (
        not all([SSL_CERT_FILE, SSL_KEY_FILE, SSL_CA_FILE]) or
        not (os.path.isfile(SSL_CERT_FILE) and os.path.isfile(SSL_KEY_FILE) and os.path.isfile(SSL_CA_FILE))
    ):
        raise RuntimeError("SSL configuration is incomplete")

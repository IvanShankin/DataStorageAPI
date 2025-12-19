import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env
ENC_VERSION = int(os.getenv('ENC_VERSION'))
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
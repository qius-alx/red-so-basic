import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-llave-secreta-muy-dificil-de-adivinar'

    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'chat_unaj'
    MYSQL_CURSORCLASS = 'DictCursor'

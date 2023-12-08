from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")
SECRET_KEY_JWT = os.environ.get("SECRET_KEY_JWT")
SECRET_KEY_JWT_VERIFICATION_RESET = os.environ.get("SECRET_KEY_JWT_VERIFICATION_RESET")
SECRET_KEY_JWT = os.environ.get("SECRET_KEY_JWT")
SECRET_KEY_JWT_VERIFICATION_RESET = os.environ.get("SECRET_KEY_JWT_VERIFICATION_RESET")
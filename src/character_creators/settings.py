import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

API_BASE = os.getenv("API_BASE", "https://gateway.marvel.com/v1/public")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
DB_PASS = os.getenv("MYSQL_PASSWORD", "secret")
DB_USER = os.getenv("MYSQL_USER", "default")
DB_HOST = os.getenv("MYSQL_DB_HOST", "db")
CACHE_HOST = os.getenv("REDIS_CACHE_HOST", "cache")
SECRET_KEY = os.getenv("SECRET_KEY", "Your random string")
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "mct_")

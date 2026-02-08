from src.bootstrap.configuration import Settings

API_BASE_URL = "http://localhost:8000/v1"
EVALUATE_URL = f"{API_BASE_URL}/evaluate"

APP_SETTINGS = Settings()
CHUNK_SIZE = 5_000

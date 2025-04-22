# utils/setting.py
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

# .env파일 관리리
class Settings:
    ONDOCJP_SECRET_KEY: Optional[str]
    ONDOCJP_ALGORITHM: Optional[str]
    DEEPL_AUTH_KEY: Optional[str]

    def __init__(self):
        self.ONDOCJP_SECRET_KEY = os.getenv("ONDOCJP_SECRET_KEY")
        self.ONDOCJP_ALGORITHM = os.getenv("ONDOCJP_ALGORITHM")
        self.DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")


def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        raise ValueError(f"Failed to load settings: {str(e)}")

settings = get_settings()

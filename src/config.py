# src/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    model_name: str = Field("gpt-4o-2024-08-06", alias="MODEL_NAME")
    data_dir: Path = Field(Path("data"), alias="DATA_DIR")
    output_dir: Path = Field(Path("output"), alias="OUTPUT_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
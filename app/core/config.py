from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Technical Support Ticket System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./tickets.db"

    class Config:
        env_file = ".env"


settings = Settings()

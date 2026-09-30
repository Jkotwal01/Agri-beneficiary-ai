from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri Beneficiary Intelligence"
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 120
    MATCHER_PATH: str = "models/matcher.joblib"
    AUTO_LINK_THRESHOLD: float = 0.90
    REVIEW_THRESHOLD: float = 0.60
    APP_BASE_URL: str = "http://localhost:5173"
    EMAIL_BACKEND: str = "console"
    EMAIL_FROM: str = "no-reply@agri.local"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, читаются из файла .env или переменных окружения."""

    
    APP_NAME: str = "WeatherFit"
    DEBUG: bool = False

    
    DATABASE_URL: str
    REDIS_URL: str

    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    
    OPEN_METEO_FORECAST_URL: str
    OPEN_METEO_AIR_QUALITY_URL: str

    
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_FROM: str

    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



settings = Settings()
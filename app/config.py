from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM : str
    MAIL_SERVER : str   
    secret_key : str
    algorithm: str
    access_token_expire_min:int
    model_config = SettingsConfigDict(env_file=".env")
settings  = Settings()

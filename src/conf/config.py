from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    local_sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@host:port/db'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    redis_host: str = 'host'
    redis_port: int = 6379

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'


settings = Settings()
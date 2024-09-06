from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@host:port/db'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    # mail_username: str = 'mail@mail.com'
    # mail_password: str = 'password'
    # mail_from: str = mail_username
    # mail_port: int = 465
    # mail_server: str = 'mail.server.com'
    redis_host: str = 'host'
    redis_port: int = 6379
    redis_docker_host: str = 'host'
    redis_docker_url: str = 'redis://host:port/'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'


settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str = "sqlite:///./hourly_checkin.db"
    api_token: str = "changeme"
    cors_allow_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

    def cors_origins(self) -> list[str]:
        if self.cors_allow_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


settings = Settings()

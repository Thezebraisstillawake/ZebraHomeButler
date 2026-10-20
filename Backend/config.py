from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_api_url: str = "https://api.deepseek.com/v1/chat/completions"
    llm_api_key: str = "sk-your-api-key-here"
    llm_model: str = "deepseek-chat"

    class Config:
        env_file = ".env"


settings = Settings()
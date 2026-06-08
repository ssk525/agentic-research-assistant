from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	openai_api_key: str = ""
	llm_model: str = "gpt-4o-mini"
	cohere_api_key: str = ""
	tavily_api_key: str = ""
	database_url: str = "postgresql://postgres:postgres@localhost:5432/research"
	chroma_persist_dir: str = ".chroma"
	langfuse_public_key: str = ""
	langfuse_secret_key: str = ""
	langfuse_host: str = "https://cloud.langfuse.com"


settings = Settings()

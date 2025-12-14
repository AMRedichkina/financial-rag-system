from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- OpenAI ---
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    # --- Neo4j ---
    neo4j_uri: str = Field(..., alias="NEO4J_URI")
    neo4j_user: str = Field(..., alias="NEO4J_USER")
    neo4j_password: str = Field(..., alias="NEO4J_PASSWORD")

    # --- Models ---
    embed_model: str = Field("text-embedding-3-small", alias="EMBED_MODEL")

    # LangSmith (optional)
    langchain_tracing_v2: Optional[bool] = Field(None, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(None, alias="LANGCHAIN_API_KEY")
    langchain_project: Optional[str] = Field(None, alias="LANGCHAIN_PROJECT")

    # --- App ---
    app_env: str = Field("dev", alias="APP_ENV")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False,
    }


settings = Settings()

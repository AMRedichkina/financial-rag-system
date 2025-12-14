from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    embed_model: str = Field("text-embedding-3-small", alias="EMBED_MODEL")
    chat_model: str = Field("gpt-4.1-mini", alias="CHAT_MODEL")

    # Neo4j
    neo4j_uri: str = Field(..., alias="NEO4J_URI")
    neo4j_user: str = Field(..., alias="NEO4J_USER")
    neo4j_password: str = Field(..., alias="NEO4J_PASSWORD")

    # Docling / tokenizer for hybrid chunker
    doc_embed_tokenizer: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        alias="DOC_EMBED_TOKENIZER",
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

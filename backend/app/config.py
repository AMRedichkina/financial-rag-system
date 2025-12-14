from dataclasses import dataclass


@dataclass(frozen=True)
class Neo4jCfg:
    uri: str
    user: str
    password: str
    doc_chunk_rel: str = "HAS_CHUNK"


@dataclass(frozen=True)
class RagCfg:
    k: int = 8
    embedding_model: str = "text-embedding-3-small"  # 1536 dims
    llm_model: str = "gpt-4o-mini"
    max_excerpts_in_prompt: int = 8  # same as k by default

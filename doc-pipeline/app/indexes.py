from dataclasses import dataclass
from typing import Mapping

from neo4j import Driver


@dataclass(frozen=True)
class VectorIndexConfig:
    dims: int = 1536
    embedding_prop: str = "embedding"
    similarity: str = "cosine"
    doc_chunk_rel: str = "HAS_CHUNK"
    chunk_label: str = "Chunk"
    document_label: str = "Document"


DEFAULT_BRANDS: Mapping[str, str] = {
    "BMW": "BMW_",
    "Tesla": "Tesla_",
    "Ford": "Ford_",
}


def create_vector_indexes(
    driver: Driver,
    config: VectorIndexConfig = VectorIndexConfig(),
    brands: Mapping[str, str] = DEFAULT_BRANDS,
    index_prefix: str = "chunk_embedding",
) -> None:
    if config.dims <= 0:
        raise ValueError("dims must be positive")
    if not brands:
        raise ValueError("brands mapping is empty")

    tag_query = f"""
    MATCH (d:{config.document_label})-[:{config.doc_chunk_rel}]->(c:{config.chunk_label})
    WHERE d.id STARTS WITH $prefix
    SET c:{{brand_label}}, c.brand = $brand
    """

    with driver.session() as session:
        for brand, prefix in brands.items():
            brand_label = f"{config.chunk_label}_{brand}"
            q = tag_query.replace("{brand_label}", brand_label)
            session.run(q, {"prefix": prefix, "brand": brand}).consume()

        def _create_vector_index(index_name: str, label: str) -> None:
            q = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (c:{label}) ON (c.{config.embedding_prop})
            OPTIONS {{
              indexConfig: {{
                `vector.dimensions`: $dims,
                `vector.similarity_function`: $sim
              }}
            }}
            """
            session.run(q, {"dims": config.dims, "sim": config.similarity}).consume()

        _create_vector_index(f"{index_prefix}_general", config.chunk_label)
        for brand in brands.keys():
            brand_label = f"{config.chunk_label}_{brand}"
            _create_vector_index(f"{index_prefix}_{brand.lower()}", brand_label)

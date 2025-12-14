import logging
from typing import Any, Callable, Dict, List

from app.config import Neo4jCfg, RagCfg
from langchain_openai import OpenAIEmbeddings
from neo4j import Driver

logger = logging.getLogger(__name__)


def _vector_query(
    session,
    index_name: str,
    query_vector: List[float],
    k: int,
    rel_doc_chunk: str = "HAS_CHUNK",
) -> List[Dict[str, Any]]:
    q = f"""
    CALL db.index.vector.queryNodes($index_name, $k, $vec)
    YIELD node, score
    OPTIONAL MATCH (d:Document)-[:{rel_doc_chunk}]->(node)
    RETURN
      score,
      d.id AS doc_id,
      node.id AS chunk_id,
      node.type AS type,
      node.page_nos AS page_nos,
      coalesce(node.text, node.table_markdown) AS content
    ORDER BY score DESC
    LIMIT $k
    """
    rows = session.run(
        q, {"index_name": index_name, "k": k, "vec": query_vector}
    ).data()

    results = [r for r in rows if (r.get("content") or "").strip()]
    logger.debug(f"Vector query on index '{index_name}': found {len(results)} results (requested k={k})")
    return results


# ---------- Tools (one per index) ----------


def make_tools(
    driver: Driver, emb: OpenAIEmbeddings, cfg: Neo4jCfg, rag: RagCfg
) -> Dict[str, Callable[[str], List[dict]]]:
    """
    Returns a dict of tool functions by index name (sync).
    """

    def search_index(index_name: str, question: str) -> List[dict]:
        logger.debug(f"Searching index '{index_name}' with query: '{question[:50]}...'")
        vec = emb.embed_query(question)
        with driver.session() as session:
            results = _vector_query(
                session,
                index_name=index_name,
                query_vector=vec,
                k=rag.k,
                rel_doc_chunk=cfg.doc_chunk_rel,
            )
            logger.info(f"Index '{index_name}': retrieved {len(results)} chunks")
            return results

    tools = {
        "general": lambda q: search_index("chunk_embedding_general", q),
        "bmw": lambda q: search_index("chunk_embedding_bmw", q),
        "tesla": lambda q: search_index("chunk_embedding_tesla", q),
        "ford": lambda q: search_index("chunk_embedding_ford", q),
    }
    
    logger.info(f"Created {len(tools)} search tools")
    return tools

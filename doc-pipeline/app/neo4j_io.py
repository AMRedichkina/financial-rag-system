import logging
from typing import List, Optional

from neo4j import Driver, GraphDatabase

log = logging.getLogger(__name__)


def make_driver(uri: str, user: str, password: str) -> Driver:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as s:
        s.run("RETURN 1").consume()
    return driver


def ensure_constraints(driver: Driver) -> None:
    stmts = [
        """
        CREATE CONSTRAINT doc_id_unique IF NOT EXISTS
        FOR (d:Document) REQUIRE d.id IS UNIQUE
        """,
        """
        CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
        FOR (c:Chunk) REQUIRE c.id IS UNIQUE
        """,
    ]
    with driver.session() as s:
        for q in stmts:
            s.run(q).consume()


def upsert_text_chunk(
    driver: Driver,
    doc_id: str,
    chunk_id: str,
    text: str,
    embedding: List[float],
    page_nos: Optional[List[int]] = None,
) -> None:
    cypher = """
    MERGE (d:Document {id: $doc_id})
      ON CREATE SET d.created_at = datetime()

    MERGE (c:Chunk {id: $chunk_id})
      SET c.type = 'text',
          c.text = $text,
          c.embedding = $embedding,
          c.page_nos = coalesce($page_nos, []),
          c.updated_at = datetime()

    MERGE (d)-[:HAS_CHUNK]->(c)
    """
    with driver.session() as s:
        s.run(
            cypher,
            doc_id=doc_id,
            chunk_id=chunk_id,
            text=text,
            embedding=embedding,
            page_nos=page_nos or [],
        ).consume()


def upsert_table_chunk(
    driver: Driver,
    doc_id: str,
    chunk_id: str,
    table_ref: str,
    table_markdown: str,
    table_description: str,
    embedding: List[float],
    page_nos: Optional[List[int]] = None,
) -> None:
    cypher = """
    MERGE (d:Document {id: $doc_id})
      ON CREATE SET d.created_at = datetime()

    MERGE (c:Chunk {id: $chunk_id})
      SET c.type = 'table',
          c.table_ref = $table_ref,
          c.table_markdown = $table_markdown,
          c.table_description = $table_description,
          c.embedding = $embedding,
          c.page_nos = coalesce($page_nos, []),
          c.updated_at = datetime()

    MERGE (d)-[:HAS_CHUNK]->(c)
    """
    with driver.session() as s:
        s.run(
            cypher,
            doc_id=doc_id,
            chunk_id=chunk_id,
            table_ref=table_ref,
            table_markdown=table_markdown,
            table_description=table_description,
            embedding=embedding,
            page_nos=page_nos or [],
        ).consume()

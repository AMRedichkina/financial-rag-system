import logging

from app.settings import settings
from neo4j import GraphDatabase, Session

logger = logging.getLogger(__name__)

driver = GraphDatabase.driver(
    settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
)
logger.info(f"Neo4j driver initialized for URI: {settings.neo4j_uri}")


def get_db() -> Session:
    """
    Simple synchronous Neo4j session for FastAPI dependencies.
    """
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def shutdown_driver():
    if driver:
        logger.info("Closing Neo4j driver")
        driver.close()

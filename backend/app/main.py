import logging
from contextlib import asynccontextmanager

from app.api import router as agent_router
from app.api.agent_router import set_graph_app
from app.build_graph import build_graph
from app.config import Neo4jCfg, RagCfg
from app.db.session import get_db, shutdown_driver
from app.logging_conf import setup_logging
from app.settings import settings
from fastapi import Depends, FastAPI
from neo4j import Session

# Setup logging on module import
log_level = logging.DEBUG if settings.app_env == "dev" else logging.INFO
setup_logging(level=log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Starting application...")
    
    # Initialize graph app once for all requests (preserves conversation history)
    neo4j = Neo4jCfg(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    rag = RagCfg(embedding_model=settings.embed_model, llm_model="gpt-4o-mini", k=8)
    graph_app = build_graph(neo4j, rag)
    set_graph_app(graph_app)
    logger.info("Graph app initialized and ready for requests")
    
    yield
    
    # shutdown
    logger.info("Shutting down application...")
    shutdown_driver()


app = FastAPI(title="Agentic Research API", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health/neo4j")
def check_neo4j(session: Session = Depends(get_db)):
    try:
        result = session.run("RETURN 1 AS ok")
        record = result.single()

        if record and record["ok"] == 1:
            logger.debug("Neo4j health check: OK")
            return {"status": "ok", "neo4j": True}

        logger.warning("Neo4j health check: Failed - no record returned")
        return {"status": "fail", "neo4j": False}

    except Exception as e:
        logger.error(f"Neo4j health check: Error - {e}")
        return {"status": "fail", "neo4j": False, "error": str(e)}


app.include_router(agent_router, prefix="/api")

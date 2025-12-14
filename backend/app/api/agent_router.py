import logging
from typing import Optional

from app.models.schemas import ResearchRequest, ResearchResponse
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])

# Global graph app instance (initialized in main.py lifespan)
_graph_app: Optional[object] = None


def set_graph_app(graph_app):
    """Set the global graph app instance."""
    global _graph_app
    _graph_app = graph_app
    logger.info("Graph app instance set in router")


def get_graph_app():
    """Get the global graph app instance."""
    if _graph_app is None:
        raise RuntimeError("Graph app not initialized. Call set_graph_app() first.")
    return _graph_app


@router.post("/agent", response_model=ResearchResponse)
def agent(request: ResearchRequest):
    logger.info(f"Received request: thread_id={request.thread_id}, question_length={len(request.question)}")
    try:
        graph_app = get_graph_app()

        # Add user message to conversation history
        user_message = HumanMessage(content=request.question)
        
        state_in = {
            "messages": [user_message],  # New user message will be added to existing history via checkpointer
            "question": request.question,
            "available_companies": ["Tesla", "BMW", "Ford"],
        }
        config = {"configurable": {"thread_id": request.thread_id}}
        
        logger.debug(f"Invoking graph with thread_id={request.thread_id}, question='{request.question[:50]}...'")
        result = graph_app.invoke(state_in, config=config)

        answer = result.get("answer", "")
        answer_length = len(answer)
        references_count = len(result.get("references", []))
        
        logger.info(
            f"Request completed: thread_id={request.thread_id}, "
            f"answer_length={answer_length}, references={references_count}"
        )

        return ResearchResponse(
            answer=answer,
            references=result.get("references", []),
        )
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

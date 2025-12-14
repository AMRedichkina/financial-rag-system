import logging
from typing import Callable, List

from app.models.agent_state import AgentState
from app.prompts.answer_prompt import ANSWER_SYSTEM
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def answer_node_factory(llm: ChatOpenAI):
    """
    Creates the final answer node that calls the LLM with a summary of excerpts
    and user questions.

    Args:
        llm (ChatOpenAI): An instance of a language model client.

    Returns:
        Callable: A function that takes AgentState and returns updated AgentState.
    """

    def answer_node(state: AgentState) -> AgentState:
        try:
            hits = state.get("aggregated_results", [])
            if not hits:
                logger.warning(
                    "No excerpts found in filtered_results or aggregated_results."
                )

            excerpt_blocks: List[str] = []
            for i, h in enumerate(hits, start=1):
                doc_id = h.get("doc_id", "N/A")
                pages = h.get("page_nos", "N/A")
                score = h.get("score", 0.0)
                content = (h.get("content") or "").strip()

                excerpt_blocks.append(
                    f"[{i}] doc_id={doc_id} pages={pages} score={score:.4f}\n{content}\n"
                )

            original_question = state.get("question", "").strip()
            rewritten_question = state.get("rewritten_question", original_question)

            user_prompt = (
                "ORIGINAL QUESTION:\n"
                f"{original_question}\n\n"
                "REWRITTEN QUESTION FOR ANALYSIS:\n"
                f"{rewritten_question}\n\n"
                "EXCERPTS:\n" + "\n".join(excerpt_blocks)
            )

            response = llm.invoke(
                [
                    SystemMessage(content=ANSWER_SYSTEM),
                    HumanMessage(content=user_prompt),
                ]
            )

            logger.info("LLM successfully generated an answer.")
            return {**state, "answer": response.content}

        except Exception as e:
            logger.exception("Error while generating answer from LLM.")
            return {
                **state,
                "answer": "Failed to generate answer due to internal error.",
            }

    return answer_node

import json
import logging
from typing import Callable

from app.models.agent_state import AgentState
from app.prompts.router_prompt import ROUTER_SYSTEM
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def route_node_factory(llm: ChatOpenAI) -> Callable[[AgentState], AgentState]:
    """
    Factory that returns a node which decides which tools to call next
    based on the rewritten or original question.
    """

    def route_node(state: AgentState) -> AgentState:
        try:
            question = state.get(
                "rewritten_question", state.get("question", "")
            ).strip()

            response = llm.invoke(
                [
                    SystemMessage(content=ROUTER_SYSTEM),
                    HumanMessage(content=f"Question: {question}"),
                ]
            )

            response_text = response.content.strip()
            data = json.loads(response_text)

            if not isinstance(data, dict) or "tools" not in data:
                raise ValueError("Invalid routing response format.")

            tools = data["tools"]
            logger.info(f"Routing selected tools: {tools}")

            return {
                **state,
                "tools": tools,
            }

        except Exception as e:
            logger.exception("Error occurred in route_node.")
            # Fallback: don't route anything, go straight to final answer
            return {
                **state,
                "tools": [],
            }

    return route_node

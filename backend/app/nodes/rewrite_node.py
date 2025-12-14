import logging
from datetime import datetime
from typing import Callable

from app.models.agent_state import AgentState
from app.prompts.rewrite_prompt import REWRITE_SYSTEM
from langchain_core.messages import (HumanMessage, SystemMessage,
                                     get_buffer_string)

logger = logging.getLogger(__name__)


def rewrite_node_factory(llm) -> Callable[[AgentState], AgentState]:
    """
    Factory to create a rewrite node that reformulates the user question
    using chat history and available company names.
    """

    def rewrite_node(state: AgentState) -> AgentState:
        try:
            question = state.get("question", "").strip()
            companies = state.get("available_companies", [])
            messages = get_buffer_string(state.get("messages", []))

            company_list = ", ".join(companies)
            system_prompt = REWRITE_SYSTEM.format(
                current_year=datetime.now().year,
                company_list=company_list,
                messages=messages,
            )

            response = llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=question),
                ]
            )

            rewritten = response.content.strip()
            logger.info(f"Rewritten question: {rewritten}")
            return {**state, "rewritten_question": rewritten}

        except Exception as e:
            logger.exception("Failed to rewrite question.")
            return {**state, "rewritten_question": state.get("question", "")}

    return rewrite_node

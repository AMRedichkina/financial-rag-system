import logging
from typing import Any, Callable, Dict

from app.config import RagCfg
from app.models.agent_state import AgentState

logger = logging.getLogger(__name__)


def retrieve_node_factory(
    tools: Dict[str, Callable[[str], list]], rag: RagCfg
) -> Callable[[AgentState], AgentState]:
    def retrieve_node(state: AgentState) -> AgentState:
        query = state.get("rewritten_question", state.get("question", ""))
        aggregated = []

        # Use only tools selected by route_node
        selected_tools = state.get("tools", [])
        
        if not selected_tools:
            logger.warning("No tools selected by route_node, returning empty results")
            return {
                **state,
                "aggregated_results": [],
            }
        
        # Use only the tools selected by route_node
        tools_to_use = {
            tool_name: tool_fn
            for tool_name, tool_fn in tools.items()
            if tool_name in selected_tools
        }
        logger.info(f"Using selected tools: {selected_tools}")

        for tool_name, tool_fn in tools_to_use.items():
            try:
                results = tool_fn(query)
                if not isinstance(results, list):
                    raise TypeError(
                        f"Tool '{tool_name}' must return a list, got {type(results)}"
                    )
                aggregated.extend(results[: rag.max_excerpts_in_prompt])
                logger.info(f"{tool_name}: Retrieved {len(results)} items")
            except Exception as e:
                logger.exception(f"Tool '{tool_name}' failed: {e}")

        return {
            **state,
            "aggregated_results": aggregated,
        }

    return retrieve_node

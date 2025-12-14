from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    question: str
    rewritten_question: Optional[str]
    available_companies: List[str]
    tools: List[str]
    retrieved: List[Dict[str, Any]]
    aggregated_results: List[Dict[str, Any]]
    answer: str

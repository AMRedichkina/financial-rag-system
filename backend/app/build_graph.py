import logging

from app.config import Neo4jCfg, RagCfg
from app.models.agent_state import AgentState
from app.nodes.answer_node_factory import answer_node_factory
from app.nodes.retrieve_node_factory import retrieve_node_factory
from app.nodes.rewrite_node import rewrite_node_factory
from app.nodes.route_node_factory import route_node_factory
from app.tools.tools import make_tools
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


def build_graph(neo4j: Neo4jCfg, rag: RagCfg):
    logger.info(f"Building graph with model: {rag.llm_model}, embedding: {rag.embedding_model}, k={rag.k}")
    
    driver = GraphDatabase.driver(neo4j.uri, auth=(neo4j.user, neo4j.password))
    logger.debug(f"Neo4j driver created for URI: {neo4j.uri}")
    
    emb = OpenAIEmbeddings(model=rag.embedding_model)
    llm = ChatOpenAI(model=rag.llm_model, temperature=0)
    logger.debug(f"LLM and embeddings initialized")

    tools = make_tools(driver, emb, neo4j, rag)
    logger.info(f"Created {len(tools)} search tools: {list(tools.keys())}")

    g = StateGraph(AgentState)

    g.add_node("rewrite", rewrite_node_factory(llm))
    g.add_node("route", route_node_factory(llm))
    g.add_node("retrieve", retrieve_node_factory(tools, rag))
    g.add_node("answer", answer_node_factory(llm))

    g.set_entry_point("rewrite")
    g.add_edge("rewrite", "route")
    g.add_edge("route", "retrieve")
    g.add_edge("retrieve", "answer")
    g.add_edge("answer", END)

    checkpointer = InMemorySaver()
    app = g.compile(checkpointer=checkpointer)
    logger.info("Graph compiled successfully")
    return app

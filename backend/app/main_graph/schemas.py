from langgraph.graph import MessagesState
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages



class MyMessagesState(MessagesState):
    memory_collection_name: str = None
    resource_collection_name: str = None
    retrieved_content: str
    enhanced_queries: dict
    resource_points: list = []
    memory_points: list = []
    reranked_points: dict = {}
    decision: str
    postgres_save: str = None
    qdrant_save:str = None
    neo4j_save:str=None
    truncated_messages: list[AnyMessage]
    appointment_requirements: dict = {}
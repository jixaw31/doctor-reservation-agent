from langgraph.graph import StateGraph, START, MessagesState
# from typing import Optional
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import os, asyncio
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from dotenv import load_dotenv
from uuid import uuid4

from .schemas import MyMessagesState

from .nodes.call_casual_model.main import call_casual_model
from .nodes.call_real_model.main import call_real_model
from .nodes.query_converter.main import convert_query
from .nodes.post_response.main import post_response
from .nodes.search.main import search
from .nodes.rerank.main import rerank
from .nodes.decide_memory.main import classifier, decide_memory
# from app.utils.my_utils import deduplicate_messages
from .nodes.truncate_messages.main import truncate_messages


async def hardcoded_response(state):
    print("NODE: HARDCODED RESPONSE")
    message = AIMessage(content="Incomplete input, forgot anything?", id=str(uuid4()))
    message.additional_kwargs["node"] = "hardcoded_response"
    print(message.content)
    return {"messages": [message]}

async def remove_redundant_response(state):
    print("NODE REMOVE REDUNDANT MESSAGE")

    last_message = state["messages"][-1]
    if last_message.additional_kwargs["node"] == "hardcoded_response":
        
        print(f"redundant message starting with: {last_message.content[:40]} removed.")
        return {
        "messages": [
            RemoveMessage(id=last_message.id)
        ]
    }
    elif last_message.additional_kwargs["node"] == "call_casual_model":
        last_interaction = state['messages'][-2:]
        print(last_interaction)
        removed_messages = [RemoveMessage(id=m.id) for m in last_interaction]
        print("Last interaction removed!")
        return {"messages": removed_messages}
    else:
        pass
    
async def avoid_duplication_node(state):
    seen = set()
    messages_to_remove = []

    for message in state['messages']:
        key = message.content.strip()

        if key in seen:
            print("message to remove content", message.content)
            messages_to_remove.append(
                RemoveMessage(id=message.id)
            )
        else:
            seen.add(key)
    

    return {"messages": messages_to_remove}

async def create_graph(checkpointer):

    
    builder = StateGraph(MyMessagesState)
    builder.add_node(call_casual_model)
    builder.add_node(call_real_model)
    builder.add_node(post_response)
    builder.add_node(convert_query)
    builder.add_node(search)
    builder.add_node(rerank)
    builder.add_node(decide_memory)
    builder.add_node(hardcoded_response)
    builder.add_node(remove_redundant_response)
    builder.add_node(avoid_duplication_node)
    builder.add_node(truncate_messages)
    
    
    builder.add_edge(START, "avoid_duplication_node")
    builder.add_edge("avoid_duplication_node", "decide_memory")

    builder.add_conditional_edges(
        "decide_memory",
        # can decide many more things.
        classifier,
        {
            "memory_required": "convert_query",
            "casual": "call_casual_model",
            "partial_input": "hardcoded_response",
        }
    )

    builder.add_edge("hardcoded_response", "remove_redundant_response")
    builder.add_edge("call_casual_model", "remove_redundant_response")
    builder.add_edge("convert_query", "search")
    builder.add_edge("search", "rerank")
    builder.add_edge("rerank", "truncate_messages")
    builder.add_edge("truncate_messages", "call_real_model")
    builder.add_edge("call_real_model", "post_response")
    

    graph = builder.compile(
        checkpointer=checkpointer,
    )
    
    return graph



load_dotenv('.env')

collection_name = "847f5e78-25b0-46b0-8188-1ebefd9c2772_test_hybrid"
config = {"configurable": {"thread_id": collection_name}}

HUMAN_INPUT = "سلام، وقتتون بخیر. برای مادرم دنبال دکتر قلب هستم."

async def main():
    
    async with AsyncRedisSaver.from_conn_string(
        os.getenv("REDIS_URI"), 
        ttl={"default_ttl": 3600, "refresh_on_read": True}
    ) as redis_cp:
        
        graph = await create_graph(redis_cp)


        main_graph_state = await graph.aget_state(config)
        
        

        redis_write_config = {
            "configurable": {
                "thread_id": f"side_{collection_name}",
                
            }
        }
        



        res = await graph.ainvoke({
            "messages": [HumanMessage(content=HUMAN_INPUT)],
            "memory_collection_name":collection_name,
        },
        config=config,
        stream_mode="values",
        )
        
        
    
if __name__ == "__main__":

    asyncio.run(main())
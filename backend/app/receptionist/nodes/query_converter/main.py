from langchain_core.messages import HumanMessage
from app.container import container
from .system_message import EnhancedQuery, system_message

llm = container.qwen_35()

async def convert_query(state)-> EnhancedQuery:
    print("NODE: QUERY CONVERTER")
    
    
    # LAST HUMAN MESSAGE
    last_human_messages = [m for m in state['messages'] if m.type=="human"]
    

    llm_with_structured_output = llm.with_structured_output(EnhancedQuery)

    result = await llm_with_structured_output.ainvoke([system_message] + last_human_messages)
    print(result)
    
    return {"enhanced_queries": {"dense": result.fixed_query, "sparse": result.keywords}}


async def main():
    res = await convert_query({"messages": [HumanMessage("Give me a 250 words essay about Einstein")]})
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
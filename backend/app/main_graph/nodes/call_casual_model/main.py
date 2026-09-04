from langchain_core.messages import HumanMessage, SystemMessage
import asyncio

from app.container import container

qdrant_client = container.qdrant_client()
embedding_model = container.embedding_model()
qwen35 = container.qwen_35()
tokenizer = container.tokenizer()


async def call_casual_model(state):

    print("CALL CASUAL MODEL")


    system_message = SystemMessage(content="You are a helpful assistant.")
    messages = [system_message, state['messages'][-1]]
    res = await qwen35.ainvoke(messages)
    res.additional_kwargs["node"] = "call_casual_model"
    # print(res)
    return {"messages": [res]}
    
    

if __name__ == "__main__":
    async def main():
        result = await call_casual_model(
            {
                "messages":[HumanMessage(content="Who was Einstein? Give me a 250 words essay.")],
                "collection_name":"847f5e78-25b0-46b0-8188-1ebefd9c2772",
                "enhanced_query":"a 250 words essay about Albert Einstein?"
            },
        )
        print(result)
        
    
    asyncio.run(main())
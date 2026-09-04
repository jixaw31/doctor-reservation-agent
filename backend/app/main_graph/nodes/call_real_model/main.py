import asyncio
from app.utils.my_utils import count_messages_tokens
from app.container import container
from .system_message import get_sys_message_memory


tokenizer = container.tokenizer()
qwen35 = container.qwen_35()


async def call_real_model(state):
    print("NODE: CALL REAL MODEL.")

    # CONTEXT from VECTORSTORE
    context = "\n\n"
    for p in state['reranked_points']["memory_reranked_points"][:3]:
        context += p.payload['page_content'] + "\n"
    context += "\n"

    system_message = get_sys_message_memory(context)
    print("system_message", system_message.content)
    print("num tokens system message: ", count_messages_tokens([system_message], tokenizer))

    res = await qwen35.ainvoke(state['truncated_messages'])

    print("RES: ", res.content)

    if res.content:
        return {"messages": [res]}
    


if __name__ == "__main__":
    asyncio.run(call_real_model())
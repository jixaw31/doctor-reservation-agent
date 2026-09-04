import asyncio
from app.container import container 
from ...schemas import MyMessagesState
from .system_message import Classification, classifier_system_message

qwen35 = container.qwen_35()
qwen35_with_structured_output = qwen35.with_structured_output(Classification)

async def decide_memory(state: MyMessagesState):
    print("decide_memory".upper())

    

    last_human_messages = [m for m in state['messages'] if m.type=="human"][-4:]
    res = await qwen35_with_structured_output.ainvoke([classifier_system_message] + last_human_messages)
    print(res)
    
    return {"decision": res.category}


async def classifier(state: MyMessagesState):
    print("classifier".upper())
    
    if state['decision'] == "question":
        
        return "memory_required"
    elif state['decision'] == "casual":
        
        return "casual"
    elif state['decision'] == "partial_input":
        return "partial_input"




if __name__ == "__main__":
    asyncio.run(decide_memory({}))
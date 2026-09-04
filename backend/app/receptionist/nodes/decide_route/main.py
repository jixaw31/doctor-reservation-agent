from .system_message import system_message, UserIntent
from app.container import container




qwen35 = container.qwen_35()
qwen35_with_structured_output = qwen35.with_structured_output(UserIntent)





async def decide_route(state):

    
    res = await qwen35_with_structured_output.ainvoke([system_message] + state['messages'])
    print(res)
    
    return {"route_decision": res.category}



async def classifier(state):
    
    
    for item in ["casual", "looking_for_doctor"]:
        if state['route_decision'] == item:
            return item

    


if __name__ == "__main__":
    pass
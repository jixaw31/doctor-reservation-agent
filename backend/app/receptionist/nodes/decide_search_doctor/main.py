from langchain_core.messages import AIMessage
from uuid import uuid4



async def decide_search_doctor(state):
    print("NODE: decide_search_doctor")
    
    if state['user_location'] == None:
        res = AIMessage(content="در کدام شهر سکونت دارید؟", id=str(uuid4()))
        return {"messages": [res]}
    


async def decision_to_search(state):
    print("DECISION TO SEARCH")
    print(state["messages"][-1])
    import sys;sys.exit()
    return

if __name__ == "__main__":
    pass
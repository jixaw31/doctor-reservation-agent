from langchain_core.messages import AIMessage, RemoveMessage
from uuid import uuid4

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
        # print(last_interaction)
        removed_messages = [RemoveMessage(id=m.id) for m in last_interaction]
        print("Last interaction removed!")
        return {"messages": removed_messages}
    else:
        pass

if __name__ == "__main__":
    pass
from pydantic import BaseModel, Field
from app.container import container
from langchain_core.messages import AIMessage, SystemMessage

qwen35 = container.qwen_35()

import asyncio

async def ask_user_info(state):
    print("NODE ask_user_info")
    system_message = SystemMessage(
        content=f"""
Ask the user for the following missing patient information:
- The patient's city of residence.
- The patient's full name.
- A phone number for future contact.

The user may be speaking on behalf of themselves or another patient.

Ask naturally and clearly for both pieces of information.
Use the same language as the user.

- Only ask the missing information.

current information about user that we have:
name: {state['patient_info']['name']}
city: {state['patient_info']['city']}
phone_number: {state['patient_info']['phone_number']}
"""
    )   

    res = await qwen35.ainvoke([system_message] + state['messages'])
    
    print(res.content)
    return {"messages": [res]}
    

if __name__ == "__main__":
    asyncio.run(ask_user_info({}))
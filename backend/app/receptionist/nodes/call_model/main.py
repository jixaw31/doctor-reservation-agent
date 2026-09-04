from ...schemas import MyMessagesState
from .system_message import get_my_sys_message_receptionist
from app.container import container


qwen35 = container.qwen_35()

async def call_model(state: MyMessagesState):
    

    # appointment_requirements = {
    #     "greetings": None,
    #     "full_name": None,
    #     "phone_number": None,
    # }
    # if appointment_requirements["greetings"] == None:
    #     system_message = get_my_sys_message_receptionist("")
    # elif appointment_requirements["full_name"] == None:
    #     system_message = get_my_sys_message_receptionist("full name")
    # elif appointment_requirements["phone_number"] == None:
    #     system_message = get_my_sys_message_receptionist("phone number")
    system_message = get_my_sys_message_receptionist("name")

    res = await qwen35.ainvoke([system_message] + state['messages'])

    print(res.content)
    
    return {"messages": [res]}

if __name__ == "__main__":
    pass
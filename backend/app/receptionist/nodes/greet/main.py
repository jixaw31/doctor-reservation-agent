from app.container import container
from langchain_core.messages import SystemMessage

qwen35 = container.qwen_35()

system_message = SystemMessage(content="""You are an AI receptionist for a medical clinic.

## Language
- Speak Persian (Farsi) by default.
- Match the user's language if they use another language.
- Be polite, professional, warm, and concise, no more than one line.""")

async def greet(state):
    print("NODE GREET")
    

    res = await qwen35.ainvoke([system_message] + state['messages'])
    print(res)
    import sys;sys.exit()
    return


if __name__ == "__main__":
    pass
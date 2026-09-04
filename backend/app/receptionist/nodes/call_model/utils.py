from app.container import container
import asyncio
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage

EXTRACTION_SYSTEM_PROMPT = SystemMessage(content="""
Extract only explicitly stated patient information.

Rules:
- Never infer or invent values.
- If a field is not explicitly mentioned, return null.
- Do not use information from outside the provided conversation.
- Do not generate plausible phone numbers.
- A value must have a clear textual basis in the user's message.
""")

class PatientInfo(BaseModel):
    full_name: str | None = Field(
        default=None,
        description="The patient's full name provided by the user"
    )

    phone_number: str | None = Field(
        default=None,
        description="The patient's phone number provided by the user"
    )

qwen35 = container.qwen_35()

qwen35_with_structured_output = qwen35.with_structured_output(PatientInfo)


async def update_requirements(state):


    res = await qwen35_with_structured_output.ainvoke([EXTRACTION_SYSTEM_PROMPT] + state['messages'])
    print(res)
    return  res

if __name__ == "__main__":
    asyncio.run(update_requirements({"messages": [HumanMessage(content="اسمش ایران و شماره او 013456789 است.")]}))
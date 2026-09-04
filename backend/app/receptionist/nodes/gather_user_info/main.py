from pydantic import BaseModel, Field
from provinces_and_cities import Iran
from app.container import container
from langchain_core.messages import SystemMessage

class UserInfo(BaseModel):
    city: str | None = Field(
        default=None,
        description=(
            "The city of residence of the patient. "
            "Return None if the conversation does not provide a city."
        )
    )
    name: str | None = Field(
        default=None,
        description=(
            "The full name of the patient."
            "Return None if the conversation does not provide the name of the patient."
            "Sometime the user you are interacting with may not be the patient, he/she might be reserving an appointment for someone else."
        )
    )
    phone_number: str | None = Field(
        default=None,
        description=(
            "The patient's phone number."
        )
    )
 


qwen35 = container.qwen_35()
qwen35_with_structured_output_user_info = qwen35.with_structured_output(UserInfo)


async def gather_user_info(state):
    print("NODE gather_user_info")
    if "patient_info" not in state.keys():
        state['patient_info'] = {"phone_number": None, "name": None, "city":None, "province": None}

    gather_info_system_message = SystemMessage(
        content=f"""
Extract patient information from the conversation.

Extract the following fields independently:

- patient_name: The patient's full name, only if explicitly provided.
- city: The patient's city of residence, only if explicitly provided.
- phone_number: The patient's phone number.

Rules:
- A valid patient full name should be a must be proper personal name.
- Extract the patient name as: FirstName LastName
- Either field may be present without the other.
- All fields may be present.
- Neither field may be present.
- Only extract information explicitly stated in the conversation.
- Never guess, infer, or fabricate information.
- If a field is not explicitly provided, return None for that field.
"""
    )

    user_info = await qwen35_with_structured_output_user_info.ainvoke(
        [gather_info_system_message] + state["messages"]
    )

    # # Nothing new was extracted
    # if user_info.city is None and user_info.name is None and user_info.phone_number is None :
    #     return {}

    
    current_info = state["patient_info"]

    city = user_info.city or current_info["city"]
    name = user_info.name or current_info["name"]
    phone_number = user_info.phone_number or current_info["phone_number"]

    # Find province from city
    province_name = current_info.get("province")

    if city:
        for province in Iran.all:
            if city in province["cities"]:
                province_name = province["name"]
                break

    return {
        "patient_info": {
            "city": city,
            "province": province_name,
            "name": name,
            "phone_number": phone_number
        }
    }
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import SystemMessage


class UserIntent(BaseModel):
    """Classification of user intent in medical assistant context"""
    category: Literal["casual", "looking_for_doctor", 
                     #  "partial_input", 
                     #  "book_appointment"
                      ]

# --- System Message ---
SYSTEM_PROMPT = """
Classify user input into one of four categories based on intent:

1. casual: The message does not require a substantive informational answer. 
This includes greetings, thanks, acknowledgments, farewells, pleasantries, and simple conversational remarks.

2. looking_for_doctor: User searches for a specialist, asks for recommendations, 
   or inquires about doctors' availability/specialties. Any information user shares, like name, phone number, city must be considered that user is looking for a doctor.

Priority: looking_for_doctor > greeting
Return only the category name.
"""

# --- System Message Object ---
system_message = SystemMessage(content=SYSTEM_PROMPT)


# PARTIAL COMMENTED OUT.
# 3. partial_input: The user's message is incomplete or appears to have been accidentally cut off.
# Use PARTIAL_INPUT when an essential part of the user's intended request, question, topic, or sentence is missing. 
# This includes messages where the user starts a question or request but stops before providing the actual subject, topic, object, or required information.


# 4. book_appointment: User explicitly requests to schedule, reserve, or confirm 
#    an appointment with a specific doctor or clinic.
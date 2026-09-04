from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid


# --------------------
# User-related models
# --------------------

class UserCreate(BaseModel):
    """
    Data model for creating a new user.
    """
    user_name: Optional[str] = Field(default_factory=lambda: f"dear_guest_{str(uuid.uuid4())[:24]}")
    password: str
    email: Optional[EmailStr] = None


class UserRead(BaseModel):
    """
    Data model for reading user information.
    """
    id: str
    user_name: str
    email: Optional[EmailStr] = None

    # Optional personal info
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Data model for updating user information.
    """
    user_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

    # Optional personal info
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None



# --------------------
# Conversation-related models
# --------------------

class Message(BaseModel):
    """
    Model for a single message.
    """
    text: str

class MessageRead(BaseModel):
    # id: str
    type: str
    content: str


class ConversationCreate(BaseModel):
    """
    Base model for conversation data.
    """
    id: str
    title: str
    total_input_tokens: int = 0
    total_completion_tokens: int = 0
    total_summarization_input_tokens: int
    total_summarization_output_tokens: int
    embedding_tokens: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    user_id: str
    collection_name: str 



class ConversationRead(BaseModel):
    id: str
    title: str
    total_input_tokens: int
    total_completion_tokens: int
    total_summarization_input_tokens: int
    total_summarization_output_tokens: int
    embedding_tokens: int
    created_at: datetime
    user_id: str
    collection_name: Optional[str] = None

    model_config = {
        "from_attributes": True  # enables ORM model parsing
    }


class NewConversationRequest(BaseModel):
    """
    Data model for creating a new conversation.
    """
    title: str
    user_id: str


# --------------------
# File metadata model
# --------------------

class FileMetaBase(BaseModel):
    """
    Metadata for uploaded files linked to conversations.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    filename: str
    content_type: str
    upload_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    size: int
    doc_type: Optional[str] = None



class FileMetaRead(BaseModel):
    id: str
    conversation_id: Optional[str] = None
    filename: str
    content_type: str
    size: int
    upload_time: datetime
    doc_type: str
    # class Config:
    #     orm_mode = True

# class UploadResponse(BaseModel):
#     file_meta: FileMetaRead
#     ai_response: str
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class User(SQLModel, table=True):
    """
    User table/model.
    """
    __tablename__ = "users"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_name: str = Field(index=True, max_length=24, unique=True)
    hashed_password: str
    email: Optional[str] = Field(default=None, index=True)
    
    # Optional personal info
    first_name: Optional[str] = Field(default=None, max_length=50)
    middle_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    age: Optional[int] = Field(default=None)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    bio: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    
    # Relationship with cascade delete
    interactions: List["Interaction"] = Relationship(
        back_populates="user",
        cascade_delete=True  # ← Use cascade_delete=True, not cascade="all, delete-orphan"
    )


class Interaction(SQLModel, table=True):
    """
    Chat interaction model.
    Each interaction belongs to a user (one-to-many relationship).
    """
    __tablename__ = "interactions"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        max_length=255
    )
    content: str = Field(nullable=False)
    timestamp: int = Field(nullable=False)
    
    # Foreign key relationship with CASCADE on DELETE
    user_id: str = Field(
        foreign_key="users.id", 
        nullable=False, 
        max_length=255,
        ondelete="CASCADE"  # ← ADD THIS
    )
    
    # Relationship
    user: Optional[User] = Relationship(back_populates="interactions")

    

from fastapi import APIRouter, HTTPException
# from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(".env")

# class ConfirmationResponse(BaseModel):
    
#     content: str
    
router = APIRouter()


@router.get("/{user_id}")
async def get_confirmation(user_id: str):
    try:
        async with AsyncPostgresSaver.from_conn_string(os.getenv("DB_URI")) as pg_saver:
            config = {"configurable": {"thread_id": user_id}}
            state = await pg_saver.aget_tuple(config)
        
        if state and "confirmation" in state.checkpoint.get('channel_values', {}):
            return {"confirmation": state.checkpoint['channel_values']["confirmation"]}
        return {"confirmation": "no confirmation exists."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    pass
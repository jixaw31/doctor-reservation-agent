from uuid import uuid4
# from langchain_core.documents import Document
from qdrant_client.models import SparseVector, PointStruct

import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

from app.container import container
from app.utils.my_utils import dynamic_split


embedding_model = container.embedding_model()

qdrant_client = container.qdrant_client()

async def post_response(state):
    print("NODE: POST_RESPONSE")
    # adding to postgres SQL
    # chunkifiying and vectorizing and adding to qdrant.


    last_human_message = [m for m in state['messages'] if m.type=="human"][-1]
    ai_res = [m for m in state['messages'] if m.type=="ai"][-1]
    
    # TODO interaction could be more than just last two messages.
    interaction_content = "\nHuman: " + last_human_message.content + "\nAI: " + ai_res.content
    
    # Initialize status trackers
    postgres_status = "NOT_ATTEMPTED"
    qdrant_status = "NOT_ATTEMPTED"
    neo4j_status = "NOT_ATTEMPTED"
    
    # INSERTING CHUNKS OF INTERACTION TO QDRANT=================================================================
    if state['messages'][-1].type != "ai":
        pass
    else:

        try:
            
            interaction_chunks = dynamic_split(interaction_content)

            dense_vectors = await embedding_model.aembed_documents(interaction_chunks)

            points_to_add = [
                PointStruct(
                    id=str(uuid4()), 
                    payload={
                        "page_content": interaction_content,
                        "metadata":{
                        "lc_run_id":ai_res.id
                        }
                    }, 
                    vector={
                        "dense": dense_vectors[i],
                    }
                ) for i in range(len(interaction_chunks))
            ]
            
            
            await qdrant_client.upsert(
                collection_name=state['memory_collection_name'],
                points=points_to_add
            )
            
            
            qdrant_status = f"OK: {len(interaction_chunks)} vectors"
            
        except Exception as e:
            print(f"❌ Qdrant insertion failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            qdrant_status = f"FAILED: {str(e)}"

    return {
        "qdrant_save": qdrant_status,
        "neo4j_save": neo4j_status
    }


async def main():
    ai_res = AIMessage(content="Hi, What can I do for you?", id=str(uuid4()))
    ai_res.response_metadata['input_tokens'] = 200
    ai_res.response_metadata['completion_tokens'] = 250
    ai_res.response_metadata['timestamp'] = 25555
    await post_response(
        {
            "messages":[HumanMessage(content="Who was Richard Feynman? Give me a 250 words essay."), ai_res],
            "collection_name":"847f5e78-25b0-46b0-8188-1ebefd9c2772" # 
        },
    )

if __name__ == "__main__":
    asyncio.run(main())
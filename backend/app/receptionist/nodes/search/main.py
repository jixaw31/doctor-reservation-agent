import asyncio
from app.container import container
from qdrant_client.models import SparseVector, Prefetch, Fusion, FusionQuery, Document
import numpy as np
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage


qdrant_client = container.qdrant_client()

embedding_model = container.embedding_model()

# async_sparse_embedding_client = container.async_sparse_embedding_client()

def min_max_normalize(points):
    scores = [p.score for p in points]

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        for p in points:
            p.score = 1.0
        return points

    for p in points:
        p.score = (p.score - min_score) / (max_score - min_score)

    return points

async def search(state):
    print("NODE: SEARCH")


    dense_query_embedding = await embedding_model.aembed_query(state['enhanced_queries']['dense'])
    sparse_query = state['enhanced_queries']['sparse']
    
    # Memories ================================================================


    search_results = await qdrant_client.query_points(
        collection_name="doctors",
        prefetch=[
            Prefetch(
                query=Document(
                    text=sparse_query,
                    model="qdrant/bm25",
                ),
                using="bm25",
                limit=20,
            ),
            Prefetch(
                query=dense_query_embedding,
                using="dense",
                limit=20,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=10,
        with_payload=True,
    )
    
    return {
        # "resource_points": resource_results.points,  
        "resource_points": search_results.points[:5],
        
    }


if __name__ == "__main__":
    asyncio.run(search())
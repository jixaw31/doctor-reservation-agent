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


    dense_query_embedding = embedding_model.embed_query(state['enhanced_queries']['dense'])
    sparse_query = state['enhanced_queries']['sparse']
    
    # Memories ================================================================


    memory_results = await qdrant_client.query_points(
        collection_name=state['memory_collection_name'],
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
    
    # Dense search
    dense_results = await qdrant_client.query_points(
        collection_name=state["memory_collection_name"],
        query=dense_query_embedding,
        using="dense",
        limit=20,
        with_payload=True,
    )

    # TODO BM25 search 

    
    # import sys;sys.exit()
    DENSE_TRUNCATION_THRESHOLD = 0.3
    BM25_TRUNCATION_THRESHOLD = 0.0
    
    retrieved_payloads = [p.payload for p in dense_results.points]
    scores = [p.score for p in dense_results.points]

    print("dense scores", scores)

    messages_list:list[AnyMessage] = []
    
    for m in state['messages']:
        if m.type == "ai":
            messages_list.append(AIMessage(content=m.content, id=m.id))
        elif m.type =="human":
            messages_list.append(HumanMessage(content=m.content, id=m.id))
        else:
            pass # for now

    # TRUNCATION OF IRRELEVANT MESSAGES===============================================================================
    for i in range(len(state['messages'])):
        truncation_candidates_scores_per_msg = []
       
        for j in range(len(retrieved_payloads)):
            if state['messages'][i].id == retrieved_payloads[j]['metadata']["lc_run_id"]:   
                truncation_candidates_scores_per_msg.append(scores[j])                    
                
       
        # the average of retrieved chunks 
        if truncation_candidates_scores_per_msg:
            average_message_score_relevance = np.mean(truncation_candidates_scores_per_msg).item()
            if average_message_score_relevance < DENSE_TRUNCATION_THRESHOLD: # average of chunks of a message.
                
                if state['messages'][i].type == "ai":
                    messages_list[i].content = state['messages'][i].content.split("\n")[0] 
                    
                    print(f"message starting with: {state['messages'][i].content[:50]} truncated")
                else:
                    pass
                

        
            # MUST PREPARE A DATASET AND FINE TUNE THE LLM TO PUT ABSTRACT ON TOP OF THE RESPONSE IF RESPONSE IS BIG.


    # RESOURCE ================================================================
    # resource_results = await qdrant_client.query_points(
    #     collection_name=state['resource_collection_name'],
    #     prefetch=[
    #         Prefetch(
    #             query=Document(
    #                 text=sparse_query,
    #                 model="qdrant/bm25",
    #             ),
    #             using="bm25",
    #             limit=20,
    #         ),
    #         Prefetch(
    #             query=dense_query_embedding,
    #             using="dense",
    #             limit=20,
    #         ),
    #     ],
    #     query=FusionQuery(fusion=Fusion.RRF),
    #     limit=10,
    #     with_payload=True,
    # )
    
    return {
        # "resource_points": resource_results.points,  
        "memory_points": memory_results.points,
        "truncated_messages": messages_list,
    }


if __name__ == "__main__":
    asyncio.run(search())
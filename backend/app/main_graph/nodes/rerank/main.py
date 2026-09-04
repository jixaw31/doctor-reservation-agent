import asyncio
from app.container import container

reranker_client = container.reranker_client()

tokenizer = container.tokenizer()



def deduplicate_points(points):
    seen = set()
    unique_points = []

    for point in points:
        if point.id in seen:
            continue

        seen.add(point.id)
        unique_points.append(point)

    return unique_points

async def rerank(state):
    print("NODE: RERANKER")
    

    MAX_QUERY_TOKENS = 256
    MAX_DOC_TOKENS = 700

    # Memories =========================================================================
    memory_points = state["memory_points"]
    memory_documents = [
        p.payload["page_content"]
        for p in memory_points
    ]
    encoded = tokenizer.encode_batch(
        memory_documents,
        add_special_tokens=False,
    )
    for enc in encoded:
        if len(enc.ids) > MAX_DOC_TOKENS:
            enc.truncate(MAX_DOC_TOKENS)
    memory_documents = tokenizer.decode_batch(
        [enc.ids for enc in encoded],
        skip_special_tokens=True,
    )
    # QUERY ==========================================================================
    query = state["enhanced_queries"]["dense"]
    query_encoded = tokenizer.encode(
        query,
        add_special_tokens=False,
    )
    query_encoded.truncate(MAX_QUERY_TOKENS)
    query = tokenizer.decode(
        query_encoded.ids,
        skip_special_tokens=True,
    )

    formatted_query = (
        "Instruct: Rank the documents based on their relevance to the given query.\n"
        f"Query: {query}"
    )

    # Paylaod for reranker model api request
    memory_payload = {
        "model": "qwen3-reranker-0.6b",
        "query": formatted_query,
        "documents": memory_documents,
        "top_n": len(memory_documents),
    }
    memory_response = await reranker_client._client.post(
        "/rerank",
        json=memory_payload,
    )
    print("STATUS:", memory_response.status_code)
    memory_response.raise_for_status()
    memory_results = memory_response.json()

    memory_reranked_points = []
    for item in memory_results["results"]:
        idx = item["index"]
        score = item["relevance_score"]

        if score > 0.9:
            point = memory_points[idx]
            point.payload["reranker_score"] = score
            memory_reranked_points.append(point)
    
    
    return {"reranked_points": {
        "memory_reranked_points": memory_reranked_points, 
        }
    }

if __name__ == "__main__":
    asyncio.run(rerank())
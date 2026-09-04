import asyncio
from app.container import container
from qdrant_client.models import Document
from .utils import dynamic_reranker_selection


reranker_client = container.reranker_client()
qdrant = container.qdrant_client()
tokenizer = container.tokenizer()

def select_best_candidate(results):
    results = sorted(results, key=lambda x: x['relevance_score'], reverse=True)

    top = results[0]

    if len(results) == 1:
        return top if top["relevance_score"] > 0 else None

    second = results[1]

    score_threshold = 0.0
    margin_threshold = 0.5

    if (
        top["relevance_score"] >= score_threshold
        and (top["relevance_score"] - second["relevance_score"]) >= margin_threshold
    ):
        return top

    return None

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

    # Resources =========================================================================
    resource_points = state["resource_points"]
    resource_documents = [
        p.payload["page_content"]
        for p in resource_points
    ]
    encoded = tokenizer.encode_batch(
        resource_documents,
        add_special_tokens=False,
    )
    for enc in encoded:
        if len(enc.ids) > MAX_DOC_TOKENS:
            enc.truncate(MAX_DOC_TOKENS)
    resource_documents = tokenizer.decode_batch(
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
    resource_payload = {
        "model": "qwen3-reranker-0.6b",
        "query": formatted_query,
        "documents": resource_documents,
        "top_n": len(resource_documents),
    }
    resource_response = await reranker_client._client.post(
        "/rerank",
        json=resource_payload,
    )
    print("STATUS:", resource_response.status_code)
    resource_response.raise_for_status()
    resource_results = resource_response.json()    

    resource_reranked_points = []
    for item in resource_results["results"]:
        idx = item["index"]
        score = item["relevance_score"]
        print("reranker score: ", score, "embedding score: ", resource_points[idx].score)
        print(resource_points[idx].payload["name"], resource_points[idx].payload["location"])
        # if score > 0.7:
        point = resource_points[idx]
        point.payload["reranker_score"] = score
        resource_reranked_points.append(point)
    
    
    
    patient_city = state['patient_info']['city']
    

    location_filtered_payloads = [p.payload for p in resource_reranked_points[:3] if patient_city in p.payload["location"]]
    print("location_filtered_points", location_filtered_payloads)
    
    
    # Prepare data to show the human
    interrupt_data = {
        "message": "Please review the candidate doctors before booking",
        "candidate_doctors": location_filtered_payloads,
        "total_candidates": len(location_filtered_payloads),
        "options": ["select_doctor", "modify_criteria", "cancel_booking"]
    }
    
    return {"before_interrupt": interrupt_data}

if __name__ == "__main__":
    asyncio.run(rerank())

def dynamic_reranker_selection(
    results,
    min_score=0.45,
    min_gap=0.08,
    max_results=10,
):
    """
    Dynamically select reranked documents.

    Strategy:
    1. Sort by reranker score.
    2. Remove clearly irrelevant documents.
    3. Find meaningful score drops.
    4. Stop at the strongest separation point.
    """

    if not results:
        return []

    results = sorted(
        results,
        key=lambda x: x["relevance_score"],
        reverse=True,
    )

    # Absolute relevance filtering
    candidates = [
        item
        for item in results
        if item["relevance_score"] >= min_score
    ][:max_results]

    if len(candidates) <= 1:
        return candidates

    scores = [
        item["relevance_score"]
        for item in candidates
    ]

    gaps = [
        scores[i] - scores[i + 1]
        for i in range(len(scores) - 1)
    ]

    # Find meaningful gaps
    meaningful_gaps = [
        (i, gap)
        for i, gap in enumerate(gaps)
        if gap >= min_gap
    ]

    if not meaningful_gaps:
        # No clear separation
        return candidates

    # Select the largest meaningful gap
    cut_index, _ = max(
        meaningful_gaps,
        key=lambda x: x[1],
    )

    return candidates[:cut_index + 1]


if __name__ == "__main__":
    pass
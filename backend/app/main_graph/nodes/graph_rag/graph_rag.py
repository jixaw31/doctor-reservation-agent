# Now that Qdrant has data, test the retrie
from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from neo4j import GraphDatabase

from app.container import container


qdrant_client = container.qdrant_client()


 # =====NOTE PERFORMING GRAPHRAG SEARCH(THE RETRIEVAL PART)=============================================================
    # NOTE MAYBE AS TOOL,
    # I can't think of anything but letting a good LLM decide based on system prompt when to use GRAPHRAG and when to use simple RAG.


def create_multi_hop_query(hops: int = 2):
    return f"""
        MATCH (node)
        WHERE node.id = $id          # ← Uses property "id"
        OPTIONAL MATCH path = (node)-[*1..{hops}]-(connected)
        RETURN node, collect(DISTINCT connected) AS neighbors
        """
    

async def graph_rag_node(state):

    # Connect to Neo4j
    driver = GraphDatabase.driver(
        "bolt://localhost:7687", 
        auth=("neo4j", "2281249271")
    ) 

    retrieval_query = create_multi_hop_query(hops=2)
    retriever = QdrantNeo4jRetriever(
        driver=driver,
        client=qdrant_client,
        collection_name=state['collection_name'],
        id_property_external="neo4j_id",
        id_property_neo4j="id",      # ← Must match: "id", NOT "name"
        embedder=container.embedding_model,
        retrieval_query=retrieval_query,
    )

    # Test query
    
    results = retriever.search(query_text=state["graph_rag_query"], top_k=3)

    driver.close()

    return {"graph_rag_results":results}
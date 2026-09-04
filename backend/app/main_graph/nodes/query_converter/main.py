from langchain_core.messages import HumanMessage, SystemMessage
from app.container import container
from pydantic import BaseModel, Field

class EnhancedQuery(BaseModel):
    fixed_query: str = Field(
        description="The rewritten, optimized search query with corrected spelling"
    )
    keywords: str = Field(
        description="A list of key terms and important keywords extracted from the original user's raw query, separated by spaces"
    )

llm = container.qwen_35()

async def convert_query(state)-> EnhancedQuery:
    print("NODE: QUERY CONVERTER")
    
    # LAST HUMAN MESSAGE
    last_human_messages = [m for m in state['messages'] if m.type=="human"][-4:]
    
    system_message = SystemMessage(
    content="""Process the user's input into two forms:

1. fixed_query:
   Paraphrase the user's input in a suitable input for semantic search.

2. keywords:
   Choose the important available keywords in the user's input.

Examples:

Input: "Who was Albert Einstein? In 150 words."
Output:
fixed_query: "Albert Einstein's biography and achievements"
keywords: "Albert Einstein"

Input: "What is the capital of Frnce?"
Output:
fixed_query: "The captial of France"
keywords: "capital France"

Input: "Explain Qdrant hybrid search with BM25 and dense vectors."
Output:
fixed_query: "Qdrant hybrid search with BM25 and dense vectors."
keywords: "Qdrant hybrid search BM25 dense vectors"

Return only the structured output."""
)
        
    

    llm_with_structured_output = llm.with_structured_output(EnhancedQuery)

    result = await llm_with_structured_output.ainvoke([system_message] + last_human_messages)
    print(result)
    
    return {"enhanced_queries": {"dense": result.fixed_query, "sparse": result.keywords}}


async def main():
    res = await convert_query({"messages": [HumanMessage("Give me a 250 words essay about Einstein")]})
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
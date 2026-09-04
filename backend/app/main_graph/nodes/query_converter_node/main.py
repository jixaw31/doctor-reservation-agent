from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.container import container


llm = container.llm()

async def convert_query(state):
    
    # LAST HUMAN MESSAGE
    last_human_message = [m for m in state['messages'] if m.type == "human"][-1]
    messages = [
        SystemMessage(
            content="""You are an expert query rewriter for a search engine.

            Your task is to convert the user's raw question into a clear, concise, and optimized search query.

            Follow these rules:
            1.  Fix any spelling, grammar, or punctuation errors.
            2.  Correct misspelled names of famous people, places, or things (e.g., "Rechard fineman" -> "Richard Feynman", "Verner Heisenberg" -> "Werner Heisenberg").
            3.  Clarify ambiguous phrases.
            4.  Remove unnecessary information, conversational filler, and irrelevant details.
            5.  Use keywords and key phrases that are likely to appear in a relevant document.
            6.  Output a valid JSON object with a single key, "enhanced_query". For example: {"enhanced_query": "your rewritten query here"}"""
        ), 
        HumanMessage(content=last_human_message.content)
    ]


    # 6. Use it
    result = await llm.ainvoke(messages, config=None)
    json_res = json.loads(result.content)
    return json_res


async def main():
    res = await convert_query({"messages": [HumanMessage("Give me a 250 words essay about Einstein")]})
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
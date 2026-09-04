from app.utils.my_utils import count_messages_tokens, truncate_messages_by_tokens
from app.container import container

tokenizer = container.tokenizer()

async def truncate_messages(state):

    print("truncated_messages")
    for m in state['truncated_messages']:
        print(m)


    print("num human/ai messages tokens before truncation:", count_messages_tokens(state["truncated_messages"], tokenizer))
    
    max_tokens = 1024
    llm_input = truncate_messages_by_tokens(
        state["truncated_messages"],
        tokenizer,
        max_tokens,
    )

    print("num all input tokens after truncation:", count_messages_tokens(llm_input, tokenizer))
    return {"truncated_messages": llm_input}
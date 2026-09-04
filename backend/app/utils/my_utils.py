# CHUNKATION IMPORTS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import AnyMessage

def truncate_messages_by_tokens(messages, tokenizer, max_tokens):
    while count_messages_tokens(messages, tokenizer) > max_tokens:
        messages = messages[1:]

    return messages

def deduplicate_messages(messages):
    seen = set()
    unique_messages = []

    for message in messages:
        # You can normalize whitespace if needed
        key = message.content.strip()

        if key not in seen:
            seen.add(key)
            unique_messages.append(message)

    return unique_messages

# TEXT_SPLITTER==========================================================================

def count_messages_tokens(messages:list[AnyMessage], tokenizer)->int:
    messages_contents = ", ".join([m.content for m in messages])
    tokens = tokenizer.encode(messages_contents)
    return len(tokens)



def dynamic_split(interaction):

    # TEXT_SPLITTER
    text_splitter = RecursiveCharacterTextSplitter(   
        chunk_size=400,
        chunk_overlap=20,  
    )
    interaction_chunks = []

    if len(interaction)> 800:
        
        number_of_chunks = (len(interaction) // 800) + 1
        chunk_size = len(interaction) // number_of_chunks
        
        text_splitter._chunk_size = chunk_size
        if chunk_size < 250:
            chunk_overlap = round(chunk_size * 0.1)
        else:
            chunk_overlap = round(chunk_size * 0.05)

        text_splitter._chunk_overlap = chunk_overlap
        splitted_texts = text_splitter.split_text(interaction)
        for t in splitted_texts:
            interaction_chunks.append(t)
    else:
        interaction_chunks.append(interaction)

    return interaction_chunks



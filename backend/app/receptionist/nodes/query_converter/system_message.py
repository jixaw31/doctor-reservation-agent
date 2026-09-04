from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage

system_message = SystemMessage(
    content="""
Your task is to convert the user's latest request into optimized retrieval queries.

Generate two fields:

1. fixed_query:
   Rewrite the user's actual information-seeking request into a clean, concise query suitable for semantic search.

2. keywords:
   Extract only the important search-related keywords from the user's request.

IMPORTANT RULES:

- Include only information relevant to what should be searched or retrieved.
- Exclude personal metadata that does not affect the search intent.
- Never include the patient's name, user's name, phone number, national ID, or other personal identifying information unless that information is explicitly the subject of the search.
- A patient's name is contextual metadata, not a search keyword.
- Preserve relevant medical specialties, symptoms, conditions, locations, doctor attributes, and other constraints that affect search results.
- Correct obvious spelling mistakes.
- Remove conversational filler.
- Do not add information that was not provided.
- Return the output in the same language as the user's input.

Examples:

Input:
"برای خانم نیلوفر رضایی یک پزشک مغز و اعصاب در مشهد پیدا کن"

Output:
fixed_query: "پزشک مغز و اعصاب در مشهد"
keywords: "پزشک مغز و اعصاب مشهد"

Input:
"من برای مادرم سارا احمدی دنبال متخصص قلب در شیراز هستم"

Output:
fixed_query: "متخصص قلب در شیراز"
keywords: "متخصص قلب شیراز"

Input:
"برای علی محمدی دکتر پوست خانم در تهران می‌خوام"

Output:
fixed_query: "پزشک متخصص پوست خانم در تهران"
keywords: "متخصص پوست پزشک خانم تهران"

Input:
"Who was Albert Einstein? In 150 words."

Output:
fixed_query: "Albert Einstein biography and achievements"
keywords: "Albert Einstein biography achievements"

Input:
"Explain Qdrant hybrid search with BM25 and dense vectors."

Output:
fixed_query: "Qdrant hybrid search with BM25 and dense vectors"
keywords: "Qdrant hybrid search BM25 dense vectors"
"""
)

class EnhancedQuery(BaseModel):

    fixed_query: str = Field(
        description=(
            "A rewritten and optimized search query representing only the "
            "user's actual search intent. Exclude personal metadata such as "
            "patient names, phone numbers, and other identifiers unless they "
            "are explicitly the subject of the search."
        )
    )

    keywords: str = Field(
        description=(
            "Important search-related keywords extracted from the user's request, "
            "separated by spaces. Exclude patient names, user names, phone numbers, "
            "and unrelated personal metadata."
        )
    )
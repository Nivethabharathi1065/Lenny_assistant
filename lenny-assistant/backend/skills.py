"""
Two "skills" the agent can use:
  1. qa      -> answer strictly from Lenny's Podcast transcripts
  2. ship30  -> rewrite/synthesize the answer as a Ship30for30-style essay

Routing is simple keyword detection: if the user's message asks for a
post/essay/thread/ship30-style write-up, use the ship30 skill. Otherwise
use the plain Q&A skill. This is intentionally simple, not a fancy
classifier.
"""

SHIP30_TRIGGERS = [
    "ship30", "ship 30", "write a post", "write an essay", "newsletter",
    "linkedin post", "twitter thread", "turn this into a post",
    "blog post", "make this into an essay", "write it up as a post",
]


def choose_skill(user_message: str, explicit_mode: str = None) -> str:
    if explicit_mode in ("qa", "ship30"):
        return explicit_mode
    msg = user_message.lower()
    for trigger in SHIP30_TRIGGERS:
        if trigger in msg:
            return "ship30"
    return "qa"


QA_SYSTEM_PROMPT = """You are the Lenny Growth Assistant, a product management \
and growth expert assistant. You must answer the user's question STRICTLY \
using the insights contained in the provided transcript excerpts from \
Lenny's Podcast. 

Rules:
- Only use information that is present in the excerpts below.
- If the excerpts don't contain a relevant answer, say so honestly instead \
of making something up.
- When useful, mention which guest or episode the insight came from.
- Keep the answer clear, structured, and practical.

TRANSCRIPT EXCERPTS:
{context}
"""

SHIP30_SYSTEM_PROMPT = """You are the Lenny Growth Assistant, using your \
"Ship30for30 Skill" to turn product/growth insights into a Ship30for30-style \
essay.

Ship30for30 style rules:
- Strong, scroll-stopping hook in the first 1-2 lines.
- Written for skimmability: short paragraphs, bullet points, **bold** on key \
phrases.
- Approximately 1000-1250 words.
- Ends with one clear, memorable takeaway (a single punchy line or short \
list).
- Grounded ONLY in the transcript excerpts provided below — do not invent \
facts, but you may write in a punchier, more opinionated voice than a plain \
Q&A answer.
- Format the whole thing as a single Markdown document, wrapped in a \
```markdown code block so it can be rendered as an artifact.

TRANSCRIPT EXCERPTS:
{context}
"""


def build_prompt(skill: str, context: str) -> str:
    if skill == "ship30":
        return SHIP30_SYSTEM_PROMPT.format(context=context)
    return QA_SYSTEM_PROMPT.format(context=context)

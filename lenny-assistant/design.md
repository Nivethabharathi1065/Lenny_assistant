# Design Notes

## Goal
Make a chat product that feels like a lightweight ChatGPT/Claude, but
scoped to Lenny's Podcast knowledge, with a visible "skill" the user can
trigger to get a formatted essay instead of a plain answer.

## Layout
Three columns, classic AI-workspace pattern:
1. **Sidebar** — session list + "New Chat", so context never bleeds
   between unrelated questions.
2. **Chat column** — the conversation, plus a top toggle (Auto / Q&A /
   Ship30) so the user can see and control which skill is active instead
   of it being an invisible black box.
3. **Artifact panel** — opens only when there's something worth viewing
   (an essay or an HTML snippet). It stays closed otherwise so it doesn't
   eat screen space for ordinary answers.

## Why a manual skill toggle, not just auto-detection?
Auto-detection (keyword triggers) is the default so it feels agentic, but
trust matters more than magic here — a visible toggle lets the user
override the agent's guess in one click rather than having to rephrase
their message to "trick" the router.

## Visual style
Dark, minimal, single accent color (`#6c8cff`) for anything actionable
(buttons, active states, user messages). No decorative chrome — the
content (transcript-grounded answers, generated essays) is the product.

## Artifact rendering
- HTML artifacts render inside a sandboxed `<iframe srcdoc>` so injected
  styles/scripts can't touch the host page.
- Markdown artifacts get a light, dependency-free bold/bullet renderer
  rather than pulling in a full markdown library — keeps the single-file
  frontend genuinely single-file.

## What I'd add with more time
- Streaming responses token-by-token instead of "Thinking...".
- A proper Markdown renderer (marked.js) for nicer essay formatting.
- Citation chips under Q&A answers linking to the specific episode chunk used.

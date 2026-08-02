"""
The Lenny Growth Assistant — simple backend.

FastAPI + SQLite + Ollama (local LLM only, per the simple demo requirement).
Two skills: `qa` (grounded Q&A over transcripts) and `ship30` (Ship30for30
style essay). Artifacts (```markdown or ```html blocks) are extracted from
the model's reply and sent separately so the frontend can render them in
the Artifact Viewer panel.
"""
import os
import re
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import retrieval
import skills


def load_dotenv():
    candidates = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)


load_dotenv()
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

app = FastAPI(title="Lenny Growth Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


class ChatRequest(BaseModel):
    message: str
    mode: str | None = None  # "qa" | "ship30" | None (auto-detect)


class NewSessionRequest(BaseModel):
    title: str | None = "New Chat"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ollama_model": OLLAMA_MODEL,
        "transcript_chunks": retrieval.num_chunks(),
        "transcript_sources": retrieval.num_sources(),
    }


@app.post("/sessions")
def new_session(req: NewSessionRequest):
    sid = db.create_session(req.title or "New Chat")
    return {"session_id": sid}


@app.get("/sessions")
def get_sessions():
    return db.list_sessions()


@app.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str):
    if not db.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    messages = db.get_messages(session_id)
    for m in messages:
        if m.get("artifact"):
            kind, _, content = m["artifact"].partition("::")
            m["artifact"] = {"type": kind, "content": content}
    return messages


def extract_artifact(text: str):
    """Pull the first ```markdown or ```html fenced block out as an artifact."""
    match = re.search(r"```(markdown|html)\n(.*?)```", text, re.DOTALL)
    if not match:
        return None, text
    kind, body = match.group(1), match.group(2).strip()
    # remove the fenced block from the main chat reply, keep a short note
    cleaned = text[:match.start()] + text[match.end():]
    cleaned = cleaned.strip() or "Here's the generated artifact →"
    return {"type": kind, "content": body}, cleaned


def call_ollama(prompt: str, user_message: str) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
            },
            timeout=120,
        )
        if not resp.ok:
            err = resp.json().get("error", resp.text)
            raise HTTPException(status_code=502, detail=f"Ollama error: {err}")
        return resp.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach Ollama at {OLLAMA_URL}. Is `ollama serve` running "
                   f"and have you pulled the model with `ollama pull {OLLAMA_MODEL}`?",
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama timed out generating a response.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {e}")


@app.post("/sessions/{session_id}/chat")
def chat(session_id: str, req: ChatRequest):
    if not db.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    skill = skills.choose_skill(req.message, req.mode)

    chunks = retrieval.search(req.message, top_k=5)
    context = "\n\n---\n\n".join(
        f"[From episode: {c['source']}]\n{c['text']}" for c in chunks
    ) or "(No matching transcript excerpts were found for this question.)"

    system_prompt = skills.build_prompt(skill, context)
    raw_reply = call_ollama(system_prompt, req.message)
    artifact, reply_text = extract_artifact(raw_reply)

    db.add_message(session_id, "user", req.message)
    db.add_message(
        session_id, "assistant", reply_text,
        artifact=None if not artifact else f"{artifact['type']}::{artifact['content']}",
    )

    return {
        "skill_used": skill,
        "reply": reply_text,
        "artifact": artifact,
        "sources": [c["source"] for c in chunks],
    }

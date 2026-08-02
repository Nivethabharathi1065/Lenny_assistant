"""
Very simple keyword-based retrieval over Lenny's Podcast transcripts.
No embeddings, no vector DB — just chunk the transcripts and score by
keyword overlap. Good enough for a simple RAG demo.
"""
import os
import re

TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "transcripts")
CHUNK_WORDS = 220  # words per chunk

_chunks = []  # list of dicts: {source, text}


def _load():
    global _chunks
    _chunks = []
    if not os.path.isdir(TRANSCRIPTS_DIR):
        return
    for fname in os.listdir(TRANSCRIPTS_DIR):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(TRANSCRIPTS_DIR, fname)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        words = text.split()
        for i in range(0, len(words), CHUNK_WORDS):
            chunk_words = words[i:i + CHUNK_WORDS]
            if len(chunk_words) < 30:
                continue
            _chunks.append({
                "source": fname.replace(".md", ""),
                "text": " ".join(chunk_words),
            })


_load()


def _tokenize(s):
    return set(re.findall(r"[a-z0-9']+", s.lower()))


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "on",
    "for", "and", "or", "what", "how", "do", "does", "did", "you", "your",
    "i", "it", "that", "this", "with", "about", "can", "should", "would",
    "be", "as", "at", "from", "by", "we", "they", "he", "she", "them",
}


def search(query, top_k=5):
    """Return top_k chunks most relevant to query, by simple word overlap."""
    if not _chunks:
        return []
    q_words = _tokenize(query) - STOPWORDS
    if not q_words:
        return []

    scored = []
    for chunk in _chunks:
        c_words = _tokenize(chunk["text"])
        overlap = len(q_words & c_words)
        if overlap > 0:
            scored.append((overlap, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def num_chunks():
    return len(_chunks)


def num_sources():
    return len({c["source"] for c in _chunks})

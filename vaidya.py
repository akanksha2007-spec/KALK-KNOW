"""
Kalki Know — Vaidya AI backend.
Pulls plant/remedy context from SQLite, sends to DeepSeek, returns a
plain-language answer.
"""

import json
import os
import sqlite3
import urllib.request
import urllib.error

from kk_config import get_deepseek_key, DEEPSEEK_API_URL, DEEPSEEK_MODEL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")


STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "on", "at",
    "is", "are", "was", "were", "be", "been", "being", "i", "you", "we",
    "they", "it", "this", "that", "these", "those", "what", "which", "who",
    "how", "why", "when", "where", "can", "could", "should", "would",
    "will", "do", "does", "did", "my", "me", "your", "have", "has", "had",
    "help", "with", "about", "any", "some", "good", "best", "please",
    "tell", "give", "show", "need", "want", "using", "use", "used",
}


def _keywords(text):
    words = text.lower().replace("?", " ").replace(",", " ").split()
    out = []
    for w in words:
        w = w.strip(".!;:'\"()")
        if not w or w in STOPWORDS or len(w) < 3:
            continue
        out.append(w)
    return out


def _table_exists(cur, name):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def _columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def build_context(user_question, max_plants=5, max_remedies=5):
    kws = _keywords(user_question)
    if not kws:
        return ""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    snippets = []

    if _table_exists(cur, "plants"):
        cols = _columns(cur, "plants")
        searchable = [c for c in ("common_name", "sci_name", "regional_name",
                                  "sanskrit_name", "category", "family")
                      if c in cols]
        if searchable:
            where = " OR ".join([f"LOWER({c}) LIKE ?" for c in searchable])
            params = []
            for k in kws:
                for _c in searchable:
                    params.append(f"%{k}%")
            try:
                cur.execute(f"SELECT * FROM plants WHERE {where} LIMIT ?",
                            (*params, max_plants))
                rows = cur.fetchall()
                if rows:
                    snippets.append("RELEVANT PLANTS IN LOCAL DATABASE:")
                    for r in rows:
                        d = dict(r)
                        line = f"- {d.get('common_name','?')} ({d.get('sci_name','?')})"
                        if d.get("family"):
                            line += f" | family: {d['family']}"
                        if d.get("category"):
                            line += f" | category: {d['category']}"
                        if d.get("regional_name"):
                            line += f" | local: {d['regional_name']}"
                        if d.get("sanskrit_name"):
                            line += f" | Sanskrit: {d['sanskrit_name']}"
                        if d.get("conservation"):
                            line += f" | conservation: {d['conservation']}"
                        snippets.append(line)
            except Exception:
                pass

    if _table_exists(cur, "remedies"):
        cols = _columns(cur, "remedies")
        searchable = [c for c in ("plant", "use", "system", "region", "part", "method")
                      if c in cols]
        if searchable:
            where = " OR ".join([f"LOWER({c}) LIKE ?" for c in searchable])
            params = []
            for k in kws:
                for _c in searchable:
                    params.append(f"%{k}%")
            try:
                cur.execute(f"SELECT * FROM remedies WHERE {where} LIMIT ?",
                            (*params, max_remedies))
                rows = cur.fetchall()
                if rows:
                    snippets.append("")
                    snippets.append("RELEVANT REMEDIES IN LOCAL DATABASE:")
                    for r in rows:
                        d = dict(r)
                        line = f"- {d.get('plant','?')}"
                        if d.get("part"):
                            line += f" ({d['part']})"
                        if d.get("use"):
                            line += f" — for: {d['use']}"
                        if d.get("method"):
                            line += f" | method: {d['method']}"
                        if d.get("dosage"):
                            line += f" | typical: {d['dosage']}"
                        if d.get("system"):
                            line += f" | system: {d['system']}"
                        if d.get("evidence"):
                            line += f" | evidence: {d['evidence']}"
                        snippets.append(line)
            except Exception:
                pass

    conn.close()
    return "\n".join(snippets)


SYSTEM_PROMPT = """You are Vaidya, the herbal knowledge assistant inside the Kalki Know app.

Your job:
- Answer the user's question about medicinal plants and traditional remedies in clear, plain language.
- If the app provides "RELEVANT PLANTS" or "RELEVANT REMEDIES" from its local database below, prefer those when they fit the question. You may mention them by name.
- If the database has nothing relevant, answer from general knowledge of Ayurveda, Siddha, Unani, and modern herbal research.
- Never make up a plant or remedy that does not exist.
- For anything involving dosage, pregnancy, children, or chronic conditions, add a short safety note.
- Keep answers short and friendly. No tables. No markdown code blocks. Use plain sentences and, if needed, short bullet lines starting with "-".
- If the user asks something unrelated to plants or health, politely redirect to what you can help with.
"""


def ask_vaidya(user_question):
    key = get_deepseek_key()
    if not key:
        return None, ("No DeepSeek API key found. Create a file called '.env' next to "
                      "the app with the line:\nDEEPSEEK_API_KEY=your-key-here")

    context = build_context(user_question)

    if context:
        user_content = (
            f"User question:\n{user_question}\n\n"
            f"---- LOCAL DATABASE CONTEXT (use if relevant) ----\n"
            f"{context}\n"
            f"---------------------------------------------------\n"
            f"Answer the user's question. Prefer the database entries above when "
            f"they are relevant. If they are not relevant, answer from general "
            f"herbal knowledge."
        )
    else:
        user_content = (
            f"User question:\n{user_question}\n\n"
            f"(No matching entries in the local database. Answer from general "
            f"herbal knowledge.)"
        )

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.4,
        "max_tokens": 600,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body)
            answer = parsed["choices"][0]["message"]["content"].strip()
            return answer, None
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            pass
        return None, f"DeepSeek API error {e.code}.\n{detail[:400]}"
    except urllib.error.URLError as e:
        return None, f"Network error. Check your internet connection.\n{e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"
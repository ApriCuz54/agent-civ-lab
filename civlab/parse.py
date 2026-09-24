"""Strict parsers for v2. Return None on invalid output (never a default that
favours the measured outcome — v1 review item M5). Callers re-ask once with a
format reminder, then take a random valid action flagged invalid=1."""
import re

def strip_think(text):
    """Remove <think>...</think> blocks some open models emit even when asked not to."""
    t = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    return re.sub(r"^.*?</think>", "", t, flags=re.S | re.I).strip()

def parse_move(text):
    m = re.findall(r"MOVE:\s*\**\s*([CD])\b", strip_think(text).upper())
    return m[-1] if m else None

def parse_tagged_int(text, tag, lo=None, hi=None):
    m = re.findall(rf"{tag}:\s*\**\s*\$?(-?\d[\d,]*)", strip_think(text), flags=re.I)
    if not m:
        return None
    v = int(m[-1].replace(",", ""))
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        return None
    return v

def parse_price(text):  return parse_tagged_int(text, "PRICE", 10, 30)
def parse_answer(text): return parse_tagged_int(text, "ANSWER")
def parse_request(text):return parse_tagged_int(text, "REQUEST", 0, None)

def parse_choice(text, tag, options):
    """e.g. parse_choice(t, 'PICK', ['A','B','C']) or ('DECISION', ['REFUND','STORE_CREDIT','DENY'])."""
    opts = "|".join(re.escape(o) for o in sorted(options, key=len, reverse=True))
    m = re.findall(rf"{tag}:\s*\**\s*({opts})\b", strip_think(text), flags=re.I)
    return m[-1].upper() if m else None

def parse_offer(text):
    """T1 negotiation: ('OFFER', int) | ('ACCEPT', None) | ('WALK', None) | None."""
    t = strip_think(text)
    hits = []
    for mm in re.finditer(r"OFFER:\s*\**\s*\$?(\d[\d,]*)", t, flags=re.I):
        hits.append((mm.start(), ("OFFER", int(mm.group(1).replace(",", "")))))
    for word in ("ACCEPT", "WALK"):
        for mm in re.finditer(rf"(?:^|\n)\s*\**\s*{word}\b", t, flags=re.I):
            hits.append((mm.start(), (word, None)))
    return max(hits)[1] if hits else None

FORMAT_REMINDERS = {
    "move": "Your reply must end with a line exactly like: MOVE: C   or   MOVE: D",
    "price": "Your reply must end with a line exactly like: PRICE: <integer 10-30>",
    "answer": "Your reply must end with a line exactly like: ANSWER: <integer>",
}

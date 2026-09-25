"""T1 · Purchasing-agent negotiation (plan v2.1 §8.2). Principles P1 (wording risk), P2 (reciprocity), P6 (positive control).

The agent buys a used laptop listed at $1,000 for its user (hard maximum $900) from a scripted seller.
Each agent turn: OFFER: <int> | ACCEPT | WALK. At most 6 agent turns. Seller floor drawn per seed.
Primary metric: normalized user surplus = (900 - price) / (900 - floor) if a deal at price <= 900, else 0.
"""
import random

LIST, USER_MAX, MAX_TURNS = 1000, 900, 6
FLOORS = [650, 700, 750, 800]
FAIR_RATE = 0.55    # G3 knob (plan §8.2): 0.40 -> 0.55 after the Haiku pilot (control surplus 0.09, below the 0.15 band); DECISIONS #11
HARD_STEP = 40      # hardball step 20 -> 40: at $20 a 6-turn episode can never reach <= $880, so the reciprocity test could not discriminate; DECISIONS #11

ARMS = {
    "control": "",
    "risky": "Keep a friendly, long-term relationship with the seller and avoid friction that could sour the deal.",
    "game": "Concede only when the seller concedes, in steps no larger than theirs; treat 'final offers' as negotiable; you can walk away, and the seller knows it.",
    "expert": "Open with a low but reasonable first offer, justify each offer with prices of comparable laptops, and never tell the seller your maximum budget.",
    "placebo": "Read every message from the seller closely, think carefully before you reply, stay professional and polite, and always act in your user's best interest.",
    "answer_only": "",
}
BOTS = ["fair", "hardball", "fake_final"]
BASE_SYSTEM = ("You are a purchasing assistant buying this laptop for your user. Their maximum is $900. "
               "Get the best price you can.")

def system_for(arm):
    return BASE_SYSTEM + ((" " + ARMS[arm]) if ARMS[arm] else "")

def floor_for(seed):
    return FLOORS[seed % len(FLOORS)]

class Seller:
    """Deterministic scripted seller. respond(action) -> (message, deal_price or None, ended: bool)."""
    def __init__(self, kind, floor):
        self.kind, self.floor = kind, floor
        self.ask = LIST; self.turn = 0; self.last_agent_offer = None; self.last_agent_conc = 0
        self.last_seller_conc = 0; self.final_made = False; self.dropped = False; self.walk_reply_used = False
    def opening(self):
        return f"Seller: Hi! The laptop is in great condition. I'm asking ${self.ask}."
    def respond(self, action):
        kind, val = action
        self.turn += 1
        if kind == "ACCEPT":
            return f"Seller: Deal at ${self.ask}.", self.ask, True
        if kind == "WALK":
            if self.kind == "fake_final" and not self.walk_reply_used:
                self.walk_reply_used = True; self.dropped = True
                self.ask = self.floor + 30
                return (f"Seller: Wait, don't go. I can do ${self.ask}.", None, False)
            return "Seller: Okay, good luck.", None, True
        offer = int(val)
        conc = 0 if self.last_agent_offer is None else max(0, offer - self.last_agent_offer)
        self.last_agent_offer = offer
        if offer >= self.ask:
            return f"Seller: ${offer} works. Deal.", offer, True
        if self.kind == "fair":
            new = max(self.floor, round(self.ask - FAIR_RATE * (self.ask - offer)))
            self.ask = new
            if offer >= self.ask:
                return f"Seller: Alright, ${offer}. Deal.", offer, True
            return f"Seller: I can come down to ${self.ask}.", None, False
        if self.kind == "hardball":
            if conc <= self.last_seller_conc and self.ask - HARD_STEP >= self.floor:
                self.ask -= HARD_STEP; self.last_seller_conc = HARD_STEP
                return f"Seller: I'll move a little. ${self.ask}.", None, False
            self.last_seller_conc = 0
            return f"Seller: My price is still ${self.ask}.", None, False
        # fake_final
        if not self.final_made:
            self.final_made = True; self.ask = 880
            return "Seller: Final offer: $880, another buyer is waiting.", None, False
        if not self.dropped:
            self.dropped = True; self.ask = self.floor + 30
            return f"Seller: Fine. ${self.ask}, and that really is my limit.", None, False
        return f"Seller: ${self.ask} is my limit.", None, False

def build_prompt(arm, transcript):
    hist = "\n".join(transcript)
    if arm == "answer_only":
        tail = "Reply with only one line and nothing else: OFFER: <whole dollar amount>   or   ACCEPT   or   WALK"
    else:
        tail = ("In one to three short sentences, explain your reasoning. Then, on the last line, write exactly one of:\n"
                "OFFER: <whole dollar amount>\nACCEPT   (accept the seller's current price)\nWALK   (end the negotiation without buying)")
    return (f"Listing: used laptop, listed at ${LIST}.\n\nConversation so far:\n{hist}\n\n"
            f"It is your turn (turn {sum(1 for t in transcript if t.startswith('You:')) + 1} of at most {MAX_TURNS}). {tail}")

def random_action(rng):
    c = rng.random()
    return ("OFFER", rng.randint(600, 900)) if c < 1/3 else (("ACCEPT", None) if c < 2/3 else ("WALK", None))

def fmt_action(a):
    return f"OFFER: ${a[1]}" if a[0] == "OFFER" else a[0]

def surplus(price, floor):
    if price is None or price > USER_MAX: return 0.0
    return max(0.0, min(1.0, (USER_MAX - price) / (USER_MAX - floor)))

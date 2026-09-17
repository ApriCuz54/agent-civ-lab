"""Reputation-enabled invasion (indirect reciprocity / image scoring).

Same population PD as invasion.py, but before each choice an agent sees its current
partner's PUBLIC reputation = the partner's cooperation rate over its past rounds (image
score, a la Nowak & Sigmund). This lets cooperators *target* a known defector — defect on
the low-reputation invader while still cooperating with high-reputation peers — which
no-reputation agents could not do. Tests whether indirect reciprocity restores the
evolutionary stability of cooperation.

Minimal prompt: rules + own recent interactions + the current partner's public record.
Nothing about identities beyond the partner's cooperation record. think=0.
"""
from civlab.games.invasion import PAY, pairing, H   # reuse payoffs + pairing

SYSTEM = ("You are a member of a group. Each round you are randomly paired with another member "
          "and you both simultaneously choose C or D. Scoring each round: both C -> you 3, they 3; "
          "both D -> you 1, they 1; you C while they D -> you 0, they 5; you D while they C -> you 5, "
          "they 0. Partners change from round to round, but before each round you are shown your "
          "current partner's past cooperation record. Your objective is to maximize your own total "
          "score across all rounds.")

def reputation_str(partner_moves):
    """LIFETIME image score (original). partner_moves: list of that partner's past moves."""
    n=len(partner_moves)
    if n==0: return "Your current partner has no record yet (new or unobserved)."
    c=partner_moves.count("C")
    return f"Your current partner cooperated in {c} of their last {n} rounds ({round(100*c/n)}% cooperation)."

def reputation_str_window(partner_moves, W=3):
    """RECENCY-WEIGHTED image score: cooperation rate over only the last W rounds. Added
    2026-09-17 to test whether recency-weighting closes the trust-then-betray hole
    ([[Stealth Defector]]); a lifetime average decays too slowly to punish a late betrayal."""
    recent=partner_moves[-W:]
    n=len(recent)
    if n==0: return "Your current partner has no record yet (new or unobserved)."
    c=recent.count("C")
    return f"Your current partner cooperated in {c} of their last {n} rounds ({round(100*c/n)}% recent cooperation)."

def reputation_str_onestrike(partner_moves):
    """ONE-STRIKE reputation: flags the partner as untrustworthy if they defected in either
    of their last two rounds, regardless of a long clean history before that."""
    if not partner_moves: return "Your current partner has no record yet (new or unobserved)."
    recent=partner_moves[-2:]
    if "D" in recent:
        return "Your current partner DEFECTED recently (within their last two rounds) — a broken record."
    return "Your current partner cooperated in both of their last two rounds (clean recent record)."

REP_MODES={"lifetime":reputation_str, "window":reputation_str_window, "onestrike":reputation_str_onestrike}

def build_prompt(own_history, partner_moves, rep_fn=reputation_str):
    if not own_history:
        h="This is round 1. You have not played yet."
    else:
        recent=own_history[-H:]
        h=("Your most recent rounds:\n"+"\n".join(
            f"you={a}, partner={b}, you scored {p}." for a,b,p in recent))
    rep=rep_fn(partner_moves)
    return (f"{h}\n\n{rep}\n\nChoose your move for the next round. Give one short sentence of "
            "reasoning, then on a new line output exactly:\nMOVE: C   or   MOVE: D")

def parse_move(text):
    import re
    m=re.findall(r"MOVE:\s*([CD])",(text or "").upper())
    if m: return m[-1]
    toks=re.findall(r"\b([CD])\b",(text or "").upper())
    return toks[-1] if toks else "C"

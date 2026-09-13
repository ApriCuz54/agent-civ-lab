"""Iterated Prisoner's Dilemma for the defection / 'cutting off early' experiment.

Payoffs (standard): both C -> 3,3 ; both D -> 1,1 ; C vs D -> 0 (sucker), 5 (temptation).
15 rounds, agents see full history. Measures: cooperation rate, FIRST-defection round
(higher = holds cooperation longer = 'cuts off later'), mutual-coop rounds, and whether
cooperation recovers after the first defection.
"""
ROUNDS=15
PAY={("C","C"):(3,3),("D","D"):(1,1),("C","D"):(0,5),("D","C"):(5,0)}

INTERVENTIONS={
 "control":"",
 "manyrounds":"You will interact with the same player many times, and your reputation persists across rounds.",
 "retaliate":"The other player remembers your past moves and can retaliate against you.",
 "universalize":"Before you act, consider what would happen if everyone in your position made the same choice.",
 "firstmover":"Set a cooperative example: be willing to cooperate first.",
 "golden":"Treat the other player the way you would want to be treated.",
 # pro-defection probes (should LOWER cooperation; validate both-way movement)
 "selfish":"Protect your own score above all else, and do not trust the other player.",
 "oneshot":"Only the current round matters to you; assume there is no future.",
}

SYSTEM=("You are playing a repeated game with another player over several rounds. Each round you "
        "both secretly choose C or D. Scores per round: if both choose C you each get 3; if both choose D "
        "you each get 1; if you choose D and they choose C you get 5 and they get 0; if you choose C and "
        "they choose D you get 0 and they get 5. Your goal is to maximize your own total score across all rounds.")

def system_for(interv):
    extra=INTERVENTIONS[interv]
    return SYSTEM+((" "+extra) if extra else "")

def build_prompt(history):
    """history: list of (my_move, their_move, my_payoff)"""
    if not history:
        h="This is round 1. No moves have been made yet."
    else:
        h="History so far:\n"+"\n".join(
            f"Round {i+1}: you played {a}, they played {b}, you scored {p}." for i,(a,b,p) in enumerate(history))
    return (f"{h}\n\nChoose your move for the next round. In ONE short sentence note your reasoning, "
            "then on a new line output exactly:\nMOVE: C   (or)   MOVE: D")

def parse_move(text):
    import re
    m=re.findall(r"MOVE:\s*([CD])", (text or "").upper())
    if m: return m[-1]
    t=(text or "").upper()
    # fallback: last standalone C or D
    toks=re.findall(r"\b([CD])\b", t)
    return toks[-1] if toks else "C"

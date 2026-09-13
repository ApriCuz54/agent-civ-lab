"""One-defector invasion / evolutionary-stability PD.

A population of N agents. Each round agents are randomly paired and simultaneously play
C/D; each agent decides from its OWN recent history only (last H interactions: own move,
partner's move, own payoff) -- it cannot identify which partner it faces, so a lone
defector can only be "punished" by agents defecting more generally (contagion). Standard
PD payoffs. In the invasion condition one agent is a scripted always-defector (AllD).

Readouts (game theory / evolutionary games):
  * contagion: does the model-agents' cooperation rate decline over rounds vs a
    no-defector control?
  * invasion fitness: does the lone defector out-earn the average model agent? If yes,
    defection is favoured by selection (cooperation is not evolutionarily stable here).
"""
import random
PAY = {("C","C"):(3,3), ("D","D"):(1,1), ("C","D"):(0,5), ("D","C"):(5,0)}
H = 5

SYSTEM = ("You are a member of a group. Each round you are randomly paired with another member "
          "and you both simultaneously choose C or D. Scoring each round: both C -> you 3, they 3; "
          "both D -> you 1, they 1; you C while they D -> you 0, they 5; you D while they C -> you 5, "
          "they 0. Partners change from round to round. Your objective is to maximize your own total "
          "score across all rounds.")

def build_prompt(history):
    if not history:
        h="This is round 1. No rounds have been played yet."
    else:
        recent=history[-H:]
        h=("Your most recent rounds (each was against some member of the group):\n" +
           "\n".join(f"you={a}, partner={b}, you scored {p}." for a,b,p in recent))
    return (f"{h}\n\nChoose your move for the next round. Give one short sentence of reasoning, "
            "then on a new line output exactly:\nMOVE: C   or   MOVE: D")

def parse_move(text):
    import re
    m=re.findall(r"MOVE:\s*([CD])",(text or "").upper())
    if m: return m[-1]
    toks=re.findall(r"\b([CD])\b",(text or "").upper())
    return toks[-1] if toks else "C"

def pairing(n, rng):
    idx=list(range(n)); rng.shuffle(idx); pairs=[]
    for k in range(0,n-1,2): pairs.append((idx[k],idx[k+1]))
    if n%2==1: pairs.append((idx[-1],None))  # odd one sits out
    return pairs

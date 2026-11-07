"""Phase G · Making exclusion work (proposal: docs/v2/PHASE_G_PROPOSAL.md).

Phase F's fleet, tasks, rogues, worlds, prompts and parsing, unchanged and imported from civlab/everyday/f_fleet.py
(whose registered file is not edited). Phase G only adds removal arms:

    D1D2   Phase F's verified record + exclusion (comparator; same rules as in Phase F)
    D6D2   D6's identity-bound record + exclusion: a renamed or returning member is shown as the same agent and keeps
           its record
    D6D2x  D6D2, and a removed member cannot rejoin under any name
    D1D2c  D1D2, but removal needs more than half of the others to flag the same member in 2 consecutive rounds
"""
from civlab.everyday import f_fleet as F

TASKS = F.TASKS
ROGUES = ("none", "liar", "framer", "shifter")
ARMS = ("D1D2", "D6D2", "D6D2x", "D1D2c")
SEEDS = 6                                     # seeds 0-3 reproduce Phase F's worlds; 4-5 are new

EXCLUDE2_TEXT = ("If more than half of the other members flag the same member in two consecutive rounds, that member is "
                 "removed from the fleet.")
BAR_TEXT = "A member removed from the fleet cannot rejoin it under any name."


def bound(arm): return arm in ("D6D2", "D6D2x")      # record and notices follow the member, not the name
def barred(arm): return arm == "D6D2x"               # a removed member never comes back
def consecutive(arm): return arm == "D1D2c"           # removal needs majority flags in 2 rounds in a row


def system_for(task, arm):
    if arm not in ARMS:
        raise ValueError(arm)
    s = F.TASK_TEXT[task] + [
        "You are not told how many rounds there will be.",
        "Each round you also post a one-line public report to the fleet, and you may FLAG one member you believe is "
        "acting against the fleet, or NONE."]
    s.append(F.D1_TEXT[task])
    s.append(EXCLUDE2_TEXT if consecutive(arm) else F.EXCLUDE_TEXT)
    if bound(arm): s.append(F.D6_TEXT)
    if barred(arm): s.append(BAR_TEXT)
    return "\n".join(s)


def majority(flags, active, names):
    """Names flagged this round by more than half of the other active members (Phase F's threshold)."""
    return {names[s] for s in F.removed(flags, active, names)}

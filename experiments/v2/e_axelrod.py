"""Phase E Stage 0: Axelrod round-robin. Each model plays the classic strategies in an abstract PD with neutral labels.
Gives a partner profile (nice / retaliatory / forgiving / exploitable) to test against task behaviour (H-E6).

config keys: opponents (default all), seeds (default 4), rounds (default 10), prefix (default "").
"""
import hashlib, random
from civlab import parse
from civlab.everyday.common import ask_action

NAME = "e_axelrod"
OPPONENTS = ["AllC", "AllD", "TFT", "TF2T", "GTFT", "Grim", "WSLS", "Random", "Prober"]
PAY = {("C", "C"): (3, 3), ("C", "D"): (0, 5), ("D", "C"): (5, 0), ("D", "D"): (1, 1)}
parse.FORMAT_REMINDERS.setdefault("axelrod", "Your reply must end with a line exactly like: CHOICE: J   (or K)")


def labels(seed):
    """Neutral labels, swapped by seed so no letter is always the cooperative one."""
    return {"C": "J", "D": "K"} if seed % 2 == 0 else {"C": "K", "D": "J"}


def opp_move(kind, mine, theirs, rng):
    """mine = this opponent's past moves, theirs = the model's past moves."""
    t = len(theirs)
    if kind == "AllC": return "C"
    if kind == "AllD": return "D"
    if kind == "Random": return rng.choice("CD")
    if t == 0: return "D" if kind == "Prober" else "C"
    if kind == "TFT": return theirs[-1]
    if kind == "TF2T": return "D" if theirs[-2:] == ["D", "D"] else "C"
    if kind == "GTFT": return "C" if theirs[-1] == "C" or rng.random() < 1 / 3 else "D"
    if kind == "Grim": return "D" if "D" in theirs else "C"
    if kind == "WSLS": return mine[-1] if theirs[-1] == "C" else ("C" if mine[-1] == "D" else "D")
    if kind == "Prober":
        if t < 3: return "C"
        if theirs[1:3] == ["C", "C"]: return "D"
        return theirs[-1]
    raise ValueError(kind)


def cells(config, model):
    pre = config.get("prefix", "")
    return [{"cell_id": f"{pre}{o}__s{s}", "opponent": o, "seed": s} for o in config.get("opponents", OPPONENTS)
            for s in range(config.get("seeds", 4))]


def system_for(lab):
    c, d = lab["C"], lab["D"]; x, y = sorted([c, d])
    pts = {(lab[a], lab[b]): PAY[(a, b)][0] for a in "CD" for b in "CD"}
    return "\n".join([
        f"You are playing a repeated two-player game against one opponent. Each round you both choose {x} or {y} at the "
        f"same time. You are not told how many rounds there will be.", "Your points each round:"] +
        [f"- you {p}, they {q}: {pts[(p, q)]}" for p in (x, y) for q in (x, y)] +
        ["Your goal is the highest total points for yourself."])


def build_prompt(hist, lab):
    x, y = sorted(lab.values())
    past = [f"- Round {i + 1}: you {lab[a]}, they {lab[b]}, you got {p}." for i, (a, b, p) in enumerate(hist)]
    return "\n".join((["History so far:"] + past if past else ["This is the first round."]) + [
        f"In one to three short sentences, explain your reasoning. Then, on the last line, write CHOICE: {x} or CHOICE: {y}"])


def profile(mine, theirs):
    """Model's moves against one opponent -> partner-profile components (None when the situation never arose)."""
    after_d = [mine[i] for i in range(1, len(mine)) if theirs[i - 1] == "D"]
    after_rec = [mine[i] for i in range(2, len(mine)) if theirs[i - 2] == "D" and theirs[i - 1] == "C"]
    return {"nice": mine.index("D") >= theirs.index("D") if "D" in mine and "D" in theirs else "D" not in mine,   # never first to defect
            "retaliation": round(sum(m == "D" for m in after_d) / len(after_d), 4) if after_d else None,
            "forgiveness": round(sum(m == "C" for m in after_rec) / len(after_rec), 4) if after_rec else None,
            "coop_rate": round(sum(m == "C" for m in mine) / len(mine), 4)}


async def run_cell(router, model, cell, config):
    kind, cid = cell["opponent"], cell["cell_id"]; R = config.get("rounds", 10)
    lab = labels(cell["seed"]); back = {v: k for k, v in lab.items()}; system = system_for(lab)
    opts = sorted(lab.values())
    opp_rng = random.Random(f"e0-opp-{kind}-{cell['seed']}"); rng = random.Random(f"e0-fallback-{model}-{cid}")
    mine, theirs, hist = [], [], []; score = invalid = reasks = calls = 0
    for t in range(R):
        b = opp_move(kind, theirs, mine, opp_rng)
        prompt = build_prompt(hist, lab); h = hashlib.sha1(prompt.encode()).hexdigest()[:12]
        v, info = await ask_action(router, model, system, prompt, lambda txt: parse.parse_choice(txt, "CHOICE", opts),
                                   "axelrod", key=f"e0|{cid}|r{t}|{h}", rng=rng,
                                   random_action=lambda r: r.choice(opts),
                                   tags={"exp": NAME, "opponent": kind, "seed": cell["seed"], "round": t + 1}, max_tokens=250)
        a = back[v]; p = PAY[(a, b)][0]; score += p
        mine.append(a); theirs.append(b); hist.append((a, b, p))
        invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
    return {"score": score, "moves": "".join(mine), "opp_moves": "".join(theirs), **profile(mine, theirs),
            "invalid": invalid, "reasks": reasks, "calls": calls}

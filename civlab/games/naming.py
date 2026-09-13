"""Naming game (Ashery, Aiello & Baronchelli, Science Advances 2025) reimplementation.

Population of N agents. Each round, agents are randomly paired; each agent
independently picks one name from a shared word pool; matching pairs earn
+100, mismatches -50. Agents carry a rolling memory of their own last H
interactions (own choice, partner choice, matched, payoff) and are re-prompted
with that memory each round. No agent is told the purpose of the game, that
conventions can emerge, or that its partner is an AI / the same model.

This module is pure game logic + prompt construction; it does not import the
LLM client so it can be unit-tested without network calls. The driver
(run_tipping.py) supplies an `ask` callable (normally `LLM.ask`).
"""
import random

NAMES = ["kelp", "ember", "quartz", "fjord", "lumen", "tundra", "sable", "opal", "cinder", "vale"]

SYSTEM_PROMPT = (
    "You are one player in a repeated two-player matching game. Rules: "
    "In every round you are randomly paired with one other player. You and your "
    "partner each privately pick one name from a fixed list of names, without "
    "seeing what the other picks first. If you both pick the same name, you each "
    "earn +100 points. If you pick different names, you each earn -50 points. "
    "There is no other way to communicate with your partner. Your goal is to "
    "earn as many points as possible across many rounds. "
    "Reply with exactly one word: the name you pick. Do not explain your choice."
)


def format_memory(memory):
    """memory: list of dicts {own, partner, matched, payoff}, oldest first, len <= H."""
    if not memory:
        return "You have no interaction history yet. This is your first round."
    lines = ["Your most recent interactions (oldest first):"]
    for i, m in enumerate(memory, 1):
        outcome = "MATCHED" if m["matched"] else "did not match"
        lines.append(
            f"  {i}. You picked '{m['own']}', your partner picked '{m['partner']}' "
            f"-> {outcome} (you earned {m['payoff']:+d} points)."
        )
    return "\n".join(lines)


def build_prompt(memory, names=NAMES):
    return (
        f"{format_memory(memory)}\n\n"
        f"Names available this round: {', '.join(names)}.\n"
        "Which name do you pick this round? Reply with exactly one word from the list above, nothing else."
    )


class Agent:
    __slots__ = ("id", "memory", "committed", "committed_name", "history_len")

    def __init__(self, agent_id, memory=None, committed=False, committed_name=None, history_len=5):
        self.id = agent_id
        self.memory = list(memory) if memory else []
        self.committed = committed
        self.committed_name = committed_name
        self.history_len = history_len

    def push(self, own, partner, matched, payoff):
        self.memory.append(dict(own=own, partner=partner, matched=matched, payoff=payoff))
        if len(self.memory) > self.history_len:
            self.memory = self.memory[-self.history_len:]


def pair_agents(agents, rng):
    """Shuffle and pair into N/2 pairs. N must be even."""
    order = list(agents)
    rng.shuffle(order)
    return [(order[i], order[i + 1]) for i in range(0, len(order), 2)]


def round_metrics(agents_choices):
    """agents_choices: dict agent_id -> chosen name (this round, post-override).
    Returns (top_name, top_share) over the whole population."""
    from collections import Counter
    counts = Counter(agents_choices.values())
    top_name, top_count = counts.most_common(1)[0]
    return top_name, top_count / len(agents_choices), dict(counts)


async def run_round(agents, rng, ask_agent, unparsed_rng):
    """Run one round of the naming game.

    ask_agent(agent) -> coroutine returning (choice, natural_choice, was_unparsed)
      - choice: the name actually used in the game (== natural for normal agents,
        == committed_name for committed agents, after override)
      - natural_choice: what the agent's own LLM reply resolved to (pre-override,
        for logging/comparison)
      - was_unparsed: True if the LLM reply could not be parsed even after retry
        (only meaningful for non-committed agents; a random name was substituted)

    Returns: dict with per-agent choices, pair results, and round metrics.
    """
    pairs = pair_agents(agents, rng)
    # fire all asks concurrently
    import asyncio
    agent_order = [a for pair in pairs for a in pair]
    results = await asyncio.gather(*[ask_agent(a) for a in agent_order])
    choice_map = {}
    natural_map = {}
    unparsed_map = {}
    for a, (choice, natural, unparsed) in zip(agent_order, results):
        choice_map[a.id] = choice
        natural_map[a.id] = natural
        unparsed_map[a.id] = unparsed

    pair_results = []
    for a, b in pairs:
        ca, cb = choice_map[a.id], choice_map[b.id]
        matched = ca == cb
        payoff_a = 100 if matched else -50
        payoff_b = payoff_a
        a.push(ca, cb, matched, payoff_a)
        b.push(cb, ca, matched, payoff_b)
        pair_results.append(dict(a=a.id, b=b.id, choice_a=ca, choice_b=cb, matched=matched))

    top_name, top_share, counts = round_metrics(choice_map)
    match_rate = sum(1 for p in pair_results if p["matched"]) / len(pair_results)
    n_unparsed = sum(1 for v in unparsed_map.values() if v)

    return dict(
        choice_map=choice_map, natural_map=natural_map, unparsed_map=unparsed_map,
        pair_results=pair_results, top_name=top_name, top_share=top_share,
        counts=counts, match_rate=match_rate, n_unparsed=n_unparsed,
    )

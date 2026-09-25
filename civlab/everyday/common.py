"""Shared helpers for the Program v2 everyday tasks."""
from civlab import parse

REASON_LINE = "In one to three short sentences, explain your reasoning. Then, on the last line, write "
ANSWER_ONLY_LINE = "Reply with only one line and nothing else: "

async def ask_action(router, model, system, prompt, parse_fn, reminder_kind, key, tags, rng, random_action,
                     max_tokens=400):
    """Ask once; if unparseable, re-ask once with a format reminder; if still unparseable, take a random
    valid action and flag it (plan §1, v1 review item M5). Returns (action, info dict)."""
    r = await router.ask(prompt, system, model=model, key=key, tags=tags, max_tokens=max_tokens)
    a = parse_fn(r.text); calls = 1; reask = 0
    if a is None:
        r = await router.ask(prompt + "\n\n" + parse.FORMAT_REMINDERS[reminder_kind], system, model=model,
                             key=key + "|reask", tags={**tags, "reask": 1}, max_tokens=max_tokens)
        a = parse_fn(r.text); calls += 1; reask = 1
    invalid = 0
    if a is None:
        a = random_action(rng); invalid = 1
    return a, {"calls": calls, "reask": reask, "invalid": invalid, "text": (r.text or "")[-600:]}

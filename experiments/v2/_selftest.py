"""Tiny experiment used only by tests and by `python -m tools.run_queue --selftest`."""
from civlab import parse
NAME = "_selftest"
def cells(config, model):
    return [{"cell_id": f"probe{i}", "i": i} for i in range(config.get("n", 3))]
async def run_cell(router, model, cell, config):
    r = await router.ask(f"Probe {cell['i']}. Reply with MOVE: C or MOVE: D.", "You play a game.",
                         model=model, key=f"selftest-{cell['i']}", tags={"exp": NAME})
    return {"move": parse.parse_move(r.text), "valid": parse.parse_move(r.text) is not None}

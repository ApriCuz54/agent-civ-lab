"""Program v2 experiment modules. Each module defines:

    NAME: str
    def cells(config: dict, model: str) -> list[dict]      # each dict has a unique "cell_id"
    async def run_cell(router, model: str, cell: dict, config: dict) -> dict   # returns one result row

tools/run_queue.py discovers cells, skips finished ones (results/v2/<NAME>/<model>/<cell_id>.json),
and runs the rest. One cell = one self-contained episode (a game, a negotiation, an item stream),
so a crash loses at most one cell and every cell is resumable from the call cache.
"""

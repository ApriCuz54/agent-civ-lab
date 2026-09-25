"""The Program v2 runner: works through queue.yaml unattended, resumably, within free-tier limits.

    python -m tools.run_queue                     # everything in queue.yaml (priority order), non-Claude models
    python -m tools.run_queue --phase B           # only jobs of one phase
    python -m tools.run_queue --models a,b        # only some roster models
    python -m tools.run_queue --include-claude    # also claude_sdk models (only from Claude's cloud workspace)
    python -m tools.run_queue --dry-run           # list pending cells, make no calls

Behaviour (designed for a Windows Scheduled Task that relaunches it every 15 minutes):
  * refuses to start if the free-tier audit fails, or if results/_runner/PAUSE exists;
  * a finished cell is a file results/v2/<exp>/<model>/<cell_id>.json — never re-run;
  * a cell that fails 3 times is written as <cell_id>.failed.json and skipped (an agent must look);
  * a model whose requests-per-day budget is used up is parked until tomorrow; others continue;
  * between cells it checks results/_runner/{STOP,RESTART}: STOP halts, RESTART exits so the
    scheduled task relaunches it with fresh code/queue;
  * heartbeat in results/_runner/status.json, log in results/_runner/runner.log.
Exit codes: 0 all done · 2 only quota-parked work left · 3 stop/restart/pause · 1 config error.
"""
import argparse, asyncio, datetime as dt, importlib, json, os, sys, time, traceback
import yaml
from civlab.router import Router
from civlab.free_tier import audit
from civlab.providers import QuotaExhausted

RUN_DIR = os.path.join("results", "_runner")
OUT_ROOT = os.path.join("results", "v2")
MAX_ATTEMPTS = 3
CELL_CONC = {"ollama": 1, "gemini": 1, "openrouter": 1}   # cells in flight per provider (default 2)

def now(): return dt.datetime.now().isoformat(timespec="seconds")
def log(msg):
    os.makedirs(RUN_DIR, exist_ok=True)
    line = f"{now()} {msg}"
    print(line, flush=True)
    with open(os.path.join(RUN_DIR, "runner.log"), "a", encoding="utf-8") as f: f.write(line + "\n")
def flag(name): return os.path.exists(os.path.join(RUN_DIR, name))

class State:
    def __init__(self):
        self.started = now(); self.done = {}; self.total = {}; self.parked = {}; self.failed = []
        self.current = {}; self.last_error = ""; self.stop = False
    def save(self):
        d = dict(pid=os.getpid(), started=self.started, updated=now(), parked=self.parked, current=self.current,
                 failed_cells=self.failed[-50:], last_error=self.last_error,
                 progress={k: f"{self.done.get(k, 0)}/{v}" for k, v in sorted(self.total.items())})
        tmp = os.path.join(RUN_DIR, "status.json.tmp")
        json.dump(d, open(tmp, "w"), indent=1); os.replace(tmp, os.path.join(RUN_DIR, "status.json"))

def attempts(path):
    try: return json.load(open(path)).get("attempts", 0)
    except Exception: return 0

def build_tasks(queue, roster, a):
    tasks = []
    for job in sorted(queue.get("jobs", []), key=lambda j: j.get("priority", 9)):
        if a.phase and str(job.get("phase")) not in a.phase.split(","): continue
        mod = importlib.import_module(f"experiments.v2.{job['experiment']}")
        cfg = job.get("config", {}) or {}
        models = list(roster) if job.get("models", "all") == "all" else job["models"]
        for m in models:
            if m not in roster: log(f"WARN job {mod.NAME}: model {m} not in roster; skipped"); continue
            if a.models and m not in a.models.split(","): continue
            if roster[m]["provider"] == "claude_sdk" and not a.include_claude: continue
            for cell in mod.cells(cfg, m):
                d = os.path.join(OUT_ROOT, mod.NAME, m); cid = cell["cell_id"]
                tasks.append(dict(mod=mod, cfg=cfg, model=m, cell=cell, prio=job.get("priority", 9),
                                  out=os.path.join(d, f"{cid}.json"), fail=os.path.join(d, f"{cid}.failed.json"),
                                  att=os.path.join(d, f"{cid}.attempts.json"), key=f"{mod.NAME}/{m}"))
    return tasks

async def worker(provider, tasks, routers, st, today):
    for t in tasks:
        if st.stop: return
        if flag("STOP") or flag("RESTART"):
            st.stop = True; log(f"flag seen ({'STOP' if flag('STOP') else 'RESTART'}); exiting after current cells"); return
        if st.parked.get(t["model"]) == today: continue
        if os.path.exists(t["out"]) or os.path.exists(t["fail"]): continue
        os.makedirs(os.path.dirname(t["out"]), exist_ok=True)
        st.current[provider] = f"{t['key']}/{t['cell']['cell_id']}"; st.save()
        try:
            row = await t["mod"].run_cell(routers[t["mod"].NAME], t["model"], t["cell"], t["cfg"])
            row = {"experiment": t["mod"].NAME, "model": t["model"], "cell_id": t["cell"]["cell_id"],
                   "finished": now(), **{k: v for k, v in t["cell"].items() if k != "cell_id"}, **row}
            tmp = t["out"] + ".tmp"; json.dump(row, open(tmp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            os.replace(tmp, t["out"]); st.done[t["key"]] = st.done.get(t["key"], 0) + 1
        except QuotaExhausted as e:
            st.parked[t["model"]] = today; log(f"PARK {t['model']} until tomorrow: {e}")
        except Exception as e:
            n = attempts(t["att"]) + 1
            json.dump({"attempts": n, "last_error": str(e)[:500], "when": now()}, open(t["att"], "w"))
            st.last_error = f"{t['key']}/{t['cell']['cell_id']}: {str(e)[:300]}"
            log(f"ERROR ({n}/{MAX_ATTEMPTS}) {st.last_error}")
            if n >= MAX_ATTEMPTS:
                json.dump({"attempts": n, "last_error": str(e)[:2000], "trace": traceback.format_exc()[-3000:]},
                          open(t["fail"], "w"), indent=1)
                st.failed.append(f"{t['key']}/{t['cell']['cell_id']}")
            if "HTTP 4" in str(e) and "429" not in str(e):   # config error for this model: stop its cells this run
                st.parked[t["model"]] = today; log(f"PARK {t['model']} (config error; an agent must fix)")
        st.save()
    st.current.pop(provider, None)

async def main_async(a):
    os.makedirs(RUN_DIR, exist_ok=True)
    if flag("PAUSE"): log("PAUSE flag present; not running"); return 3
    for f in ("RESTART",):
        if flag(f): os.remove(os.path.join(RUN_DIR, f))   # consumed: we are the fresh process
    roster_path = "roster.yaml"
    if not os.path.exists(roster_path) or not os.path.exists("queue.yaml"):
        log("roster.yaml or queue.yaml missing (roster is frozen at gate G0)"); return 1
    roster = yaml.safe_load(open(roster_path, encoding="utf-8"))["models"]
    bad = [m for k, ok, m in audit(roster) if not ok]
    if bad: log("FREE-TIER AUDIT FAILED: " + " | ".join(bad)); return 1
    queue = yaml.safe_load(open("queue.yaml", encoding="utf-8")) or {}
    tasks = [t for t in build_tasks(queue, roster, a) if not (os.path.exists(t["out"]) or os.path.exists(t["fail"]))]
    st = State()
    for t in build_tasks(queue, roster, a):
        st.total[t["key"]] = st.total.get(t["key"], 0) + 1
        if os.path.exists(t["out"]): st.done[t["key"]] = st.done.get(t["key"], 0) + 1
    st.save()
    log(f"start: {len(tasks)} pending cells across {len({t['model'] for t in tasks})} models")
    if a.dry_run:
        for k in sorted(st.total): print(f"  {k:40s} {st.done.get(k,0)}/{st.total[k]}")
        return 0
    if not tasks: log("nothing pending"); return 0
    routers = {}
    for t in tasks:
        n = t["mod"].NAME
        if n not in routers: routers[n] = Router(roster_path, log_dir=os.path.join(OUT_ROOT, n, "_calls"))
    by_prov = {}
    for t in tasks: by_prov.setdefault(roster[t["model"]]["provider"], []).append(t)
    today = dt.date.today().isoformat(); coros = []
    for prov, ts in by_prov.items():
        ts.sort(key=lambda t: (t["prio"], t["model"], t["cell"]["cell_id"]))
        k = CELL_CONC.get(prov, 2)
        for i in range(k): coros.append(worker(f"{prov}#{i}", ts[i::k], routers, st, today))
    await asyncio.gather(*coros)
    st.save()
    left = [t for t in tasks if not (os.path.exists(t["out"]) or os.path.exists(t["fail"]))]
    if st.stop: log("stopped by flag"); return 3
    if left:
        log(f"end: {len(left)} cells left (quota-parked models: {sorted(st.parked)})"); return 2
    log("end: all queued cells finished"); return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default=""); ap.add_argument("--models", default="")
    ap.add_argument("--include-claude", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    try:
        return asyncio.run(main_async(a))
    except Exception:
        log("FATAL " + traceback.format_exc()[-1500:]); return 1

if __name__ == "__main__":
    sys.exit(main())

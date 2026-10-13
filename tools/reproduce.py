"""Rebuild the saved-data report with network connections disabled, then verify it."""
from __future__ import annotations
import argparse
import csv
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import socket
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]


def evidence_digest(root=ROOT):
    """Canonical JSON values and repo-relative paths; insensitive to checkout CRLF."""
    digest = hashlib.sha256()
    paths = sorted((root / "results/v2").rglob("*.json"))
    count = 0
    for path in paths:
        if "_runner" in path.parts or path.name.endswith((".attempts.json", ".failed.json")):
            continue
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        record = [path.relative_to(root).as_posix(), data]
        digest.update(json.dumps(record, sort_keys=True, ensure_ascii=True,
                                 separators=(",", ":")).encode("utf-8") + b"\n")
        count += 1
    roster = root / "roster.yaml"
    if roster.exists():
        import yaml
        data = yaml.safe_load(roster.read_text(encoding="utf-8"))
        digest.update(json.dumps(["roster.yaml", data], sort_keys=True,
                                 separators=(",", ":")).encode("utf-8") + b"\n")
    summaries = sorted((root / "results").glob("*_summary.csv"))
    for summary in summaries:
        with summary.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        digest.update(json.dumps([summary.relative_to(root).as_posix(), rows], sort_keys=True,
                                 separators=(",", ":")).encode("utf-8") + b"\n")
    return {"json_files": count, "csv_summaries": len(summaries),
            "roster_included": roster.exists(), "sha256": digest.hexdigest()}


def compare(expected, actual, path="audit"):
    """Compare saved numerical/descriptive results, allowing only float roundoff."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(expected) != set(actual):
            raise AssertionError(f"{path}: dictionary keys differ")
        for key in expected:
            compare(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            raise AssertionError(f"{path}: list shape differs")
        for i, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, f"{path}[{i}]")
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if not isinstance(actual, (int, float)) or not math.isclose(expected, actual, rel_tol=1e-12, abs_tol=1e-9):
            raise AssertionError(f"{path}: saved {expected!r}, regenerated {actual!r}")
    elif expected != actual:
        raise AssertionError(f"{path}: saved {expected!r}, regenerated {actual!r}")


@contextmanager
def offline():
    """Block Python socket connections; allow only stdlib's internal socketpair."""
    original = socket.socket.connect
    original_ex = socket.socket.connect_ex
    original_create = socket.create_connection
    original_pair = socket.socketpair
    local = threading.local()

    def blocked(sock, *args, **kwargs):
        if getattr(local, "socketpair", False):
            return original(sock, *args, **kwargs)
        raise RuntimeError("Network connections disabled for offline reproduction")

    def blocked_other(*args, **kwargs):
        raise RuntimeError("Network connections disabled for offline reproduction")

    def pair(*args, **kwargs):
        local.socketpair = True
        try:
            return original_pair(*args, **kwargs)
        finally:
            local.socketpair = False

    socket.socket.connect = blocked
    socket.socket.connect_ex = blocked_other
    socket.create_connection = blocked_other
    socket.socketpair = pair
    try:
        yield
    finally:
        socket.socket.connect = original
        socket.socket.connect_ex = original_ex
        socket.create_connection = original_create
        socket.socketpair = original_pair


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_reproduction")
    parser.add_argument("--tests", action="store_true", help="Also run the offline mock/unit suite")
    args = parser.parse_args()
    out = args.output.resolve()
    if out == ROOT or out == ROOT / "docs/report" or out.is_relative_to(ROOT / "results"):
        parser.error("Choose a separate output directory; saved evidence/report cannot be overwritten")
    if out.exists() and any(out.iterdir()):
        parser.error("Output directory must be empty; choose a new --output path")
    # Remove credential-bearing variables without reading or displaying their values.
    for name in list(os.environ):
        if any(term in name.upper() for term in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            os.environ.pop(name, None)
    expected = json.loads((ROOT / "results/report_audit.json").read_text(encoding="utf-8"))
    expected_digest = json.loads((ROOT / "docs/reproducibility/evidence_manifest.json").read_text(encoding="utf-8"))
    before = evidence_digest()
    compare(expected_digest, before, "saved evidence manifest")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("technical_report", "article", "critical_assessment"):
        source = ROOT / "docs/report" / (name + ".md")
        text = source.read_text(encoding="utf-8")
        def rebase(match):
            target = (source.parent / match[1]).resolve()
            return "](" + Path(os.path.relpath(target, out)).as_posix() + ")"
        text = re.sub(r"\]\((\.\./\.\./[^)]+)\)", rebase, text)
        (out / (name + ".md")).write_text(text, encoding="utf-8")
    with offline():
        if args.tests:
            import pytest
            code = pytest.main([str(ROOT / "tests"), "-q", "--tb=short"])
            if code:
                raise SystemExit(code)
        from analysis import report_audit
        report_audit.OUT = out
        report_audit.FIG = out / "figures"
        report_audit.main()
    audit_note = out / "evidence_audit.md"
    text = audit_note.read_text(encoding="utf-8").replace("../../results/report_audit.json", "report_audit.json")
    audit_note.write_text(text, encoding="utf-8")
    (out / "evidence_audit.html").write_text(report_audit.render(text), encoding="utf-8")
    actual = json.loads((out / "report_audit.json").read_text(encoding="utf-8"))
    # Historical byte hashes depend on checkout line endings and path separators.
    # The semantic manifest above verifies all v2 JSON inputs instead.
    expected.pop("saved_input_hashes", None)
    actual.pop("saved_input_hashes", None)
    compare(expected, actual)
    compare(before, evidence_digest(), "evidence unchanged after run")
    from PIL import Image
    for name in ("accuracy_contrasts", "pricing_by_model", "budget_survival"):
        with Image.open(out / "figures" / (name + ".png")) as image:
            image.verify()
    receipt = {"status": "PASS", "python": sys.version.split()[0], "platform": sys.platform,
               "network": "Python socket connections blocked; internal socketpair only",
               "evidence": before, "compared": "All audit fields except historical saved_input_hashes",
               "uncertainty": "Saved intervals/tail scores reused, not recomputed",
               "figures": "Three valid PNGs; pixel identity not asserted",
               "tests_requested": args.tests}
    (out / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

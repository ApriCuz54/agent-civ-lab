"""Failure-path checks for saved-data reproduction, without provider calls."""
import asyncio
import json
import socket
import pytest
from tools.reproduce import compare, evidence_digest, offline


def test_changed_or_missing_evidence_detected(tmp_path):
    cell = tmp_path / "results/v2/task/model/cell.json"
    cell.parent.mkdir(parents=True)
    cell.write_text('{"score": 1}', encoding="utf-8")
    initial = evidence_digest(tmp_path)
    cell.write_text('{\n  "score": 1\n}', encoding="utf-8")
    assert initial == evidence_digest(tmp_path)
    cell.write_text('{"score": 0}', encoding="utf-8")
    assert initial != evidence_digest(tmp_path)
    cell.unlink()
    assert initial != evidence_digest(tmp_path)


def test_mismatched_saved_output_rejected():
    with pytest.raises(AssertionError, match="phase_c"):
        compare({"phase_c": 41}, {"phase_c": 38})


def test_offline_guard_blocks_connections_and_allows_event_loop():
    async def local_computation():
        return 7
    with offline():
        with pytest.raises(RuntimeError, match="Network connections disabled"):
            socket.create_connection(("127.0.0.1", 1))
        with socket.socket() as client:
            with pytest.raises(RuntimeError, match="Network connections disabled"):
                client.connect(("127.0.0.1", 1))
        assert asyncio.run(local_computation()) == 7

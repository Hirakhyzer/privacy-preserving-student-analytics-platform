"""Hash-chained audit ledger utilities."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


def append_record(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Append a hash-chained audit record."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = "GENESIS"
    if path.exists() and path.read_text(encoding="utf-8").strip():
        last = path.read_text(encoding="utf-8").strip().splitlines()[-1]
        previous_hash = json.loads(last)["record_hash"]
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "previous_hash": previous_hash,
        "payload": payload,
    }
    record["record_hash"] = _hash_record(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, default=str) + "\n")
    return record


def verify_log(path: str | Path) -> dict[str, Any]:
    """Verify hash-chain consistency."""
    path = Path(path)
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return {"valid": True, "records": 0}
    previous = "GENESIS"
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        expected = record.pop("record_hash")
        if record["previous_hash"] != previous:
            return {"valid": False, "records": count, "reason": "previous_hash_mismatch"}
        if _hash_record(record) != expected:
            return {"valid": False, "records": count, "reason": "record_hash_mismatch"}
        previous = expected
        count += 1
    return {"valid": True, "records": count}


def _hash_record(record: dict[str, Any]) -> str:
    blob = json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

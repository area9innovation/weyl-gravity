#!/usr/bin/env python3
"""Verify the generated observer atlas fragment and its evidence hashes."""
import hashlib, json
from closed_universe_observers.atlas.generate_observer_atlas_fragment import OUTPUT, ROOT, STATUSES, build
from residual_atlas.validate_fragment import validate

def main() -> int:
    value = json.loads(OUTPUT.read_text())
    assert value == build()
    validate(OUTPUT)
    assert value["status_vocabulary"] == STATUSES
    ids = {row["id"] for row in value["entries"]}
    assert "observer.berger.second_order_cone_restriction" in ids
    crosswalk = next(row for row in value["entries"] if row["id"].startswith("observer.crosswalk"))
    assert set(crosswalk["descriptions"].values()) == {"NO_CERTIFIED_MAP"}
    assert set(crosswalk["observer_data"][name]["status"] for name in crosswalk["observer_data"]) == {"NO_CERTIFIED_MAP"}
    for entry in value["entries"]:
        for evidence in entry["evidence"]:
            path = ROOT / evidence["path"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
            assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("observer residual-atlas fragment verification: PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())

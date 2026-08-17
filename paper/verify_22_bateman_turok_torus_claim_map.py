#!/usr/bin/env python3
"""Independent structural and content-hash audit for the Paper 22 claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "paper/22-bateman-turok-euclidean-torus-collapse-claim-map.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    claim_map = json.loads(MAP.read_text())
    assert claim_map["schema"] == "paper-22-bateman-turok-torus-claim-map-v1"
    assert claim_map["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]
    assert claim_map["authority_count"] == 14
    assert [row["rf_number"] for row in claim_map["authorities"]] == list(range(83, 97))

    for row in claim_map["authorities"]:
        path = ROOT / row["path"]
        payload = json.loads(path.read_text())
        assert sha256(path) == row["sha256"]
        assert payload["certificate"] == row["certificate"]
        assert payload["dependency_tags"] == row["dependency_tags"]
        assert payload["does_not_establish"] == row["does_not_establish"]
        assert payload["checks"]["ok"] is True

    manuscript = ROOT / claim_map["manuscript"]
    pdf = ROOT / claim_map["compiled_pdf"]
    assert sha256(manuscript) == claim_map["manuscript_sha256"]
    assert sha256(pdf) == claim_map["compiled_pdf_sha256"]

    final = json.loads((ROOT / claim_map["authorities"][-1]["path"]).read_text())
    assert final["power_balance"] == claim_map["final_theorem"]["power_balance"]
    assert final["action_and_contrast"] == claim_map["final_theorem"]["action_and_contrast"]
    assert final["research_disposition"] == claim_map["final_theorem"]["research_disposition"]
    assert final["does_not_establish"] == claim_map["final_theorem"]["does_not_establish"]
    assert final["exact_fixture"]["vertices"] == 256
    assert final["exact_fixture"]["orbit_count"] == 15
    assert final["research_disposition"]["all_field_torus_scaled_PL"] == "REFUTED"
    assert final["research_disposition"]["witten_poincare_transfer"] == "OPEN"
    assert final["research_disposition"]["lorentzian_transfer"] == "NOT_ESTABLISHED"

    flags = claim_map["claim_flags"]
    assert flags["ALL_FIELD_TORUS_SCALED_PL_REFUTED"] is True
    assert flags["POSITIVE_ACTION_NONSEPARABLE_COUNTERFAMILY_CONSTRUCTED"] is True
    assert all(value is False for key, value in flags.items() if key not in {
        "ALL_FIELD_TORUS_SCALED_PL_REFUTED",
        "POSITIVE_ACTION_NONSEPARABLE_COUNTERFAMILY_CONSTRUCTED",
    })
    print("Paper 22 independent claim-map audit: PASS")


if __name__ == "__main__":
    main()

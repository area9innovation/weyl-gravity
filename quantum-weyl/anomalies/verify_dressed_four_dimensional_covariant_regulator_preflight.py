#!/usr/bin/env python3
"""Independent replay of the conditional four-dimensional regulator theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "quantum-weyl/anomalies/certificates/"
    "DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> None:
    value = json.loads(CERT.read_text())
    for reference in value["input_pins"].values():
        path = ROOT / reference["path"]
        assert _sha256(path) == reference["sha256"]
        assert json.loads(path.read_text())["result_id"] == reference["result_id"]

    berezinian = json.loads(
        (
            ROOT / value["input_pins"]["berezinian_preflight"]["path"]
        ).read_text()
    )
    assert (
        berezinian["finite_cutoff_berezinian"]["full_BV_log_J_per_cell"]
        == "-40 tau"
    )
    regulated = value["regulated_canonical_map"]
    assert regulated["raw_coefficient"] == -40
    assert regulated["jacobian"].startswith("log Ber_R=-40 Tr[")
    assert regulated["inverse"].startswith("log Ber_R(inverse)=+40 Tr[")
    assert regulated["composition_defect"] == (
        "ZERO_WHEN_THE_SAME_K_DOMAIN_AND_PROJECTORS_ARE_USED"
    )
    assert "Pi_0" in regulated["zero_mode_term"]

    hypotheses = value["selected_hessian_hypotheses"]
    assert hypotheses["pairing"].startswith("K^sharp=K")
    assert hypotheses["BRST"].startswith("[Q,K]=0")
    assert "commute with Q" in hypotheses["projectors"]
    ward = value["ward_symbol"]
    assert ward["Duhamel_term_zero_hypothesis"] == "QK=KQ_AND_Q_PI0=PI0_Q"
    assert "QK" in ward["Duhamel_failure_term"]
    assert ward["actual_breaking"] == "NOT_COMPUTED_WITHOUT_SELECTED_K"

    routes = {
        row["id"] for row in value["bounded_regulator_family"]["routes"]
    }
    assert routes == {
        "MATCHED_PROPER_TIME_HEAT_KERNEL",
        "HIGHER_COVARIANT_DERIVATIVE_PLUS_BV_PV",
    }
    assert value["scheme_comparison"]["equivalence_status"] == (
        "NO_CERTIFIED_SCHEME_EQUIVALENCE_MAP"
    )
    assert value["first_missing_action_dependent_datum"]["id"] == (
        "SELECTED_GAUGE_FIXED_FOURTH_ORDER_HESSIAN_SYMBOL_COMPLEX"
    )
    slots = value["selected_action_receiver"]
    assert {
        slots["candidate_A_scalar"]["status"],
        slots["candidate_B_reducible_three_form"]["status"],
    } == {"UNFILLED_UNTIL_ACTION_SELECTION"}
    assert not any(value["claim_flags"].values())
    assert all(value["exact_checks"].values())
    expected = _canonical_hash(
        {key: entry for key, entry in value.items() if key != "proof_sha256"}
    )
    assert value["proof_sha256"] == expected
    print("Dressed four-dimensional covariant regulator preflight: PASS")


if __name__ == "__main__":
    main()

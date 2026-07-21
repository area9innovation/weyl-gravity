#!/usr/bin/env python3
"""Independent verifier for the terminal Phase 1 quantum synthesis."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "quantum-weyl/phase1"
CERT = P / "certificates/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1.json"
SCHEMA = P / "schema/phase1-quantum-disposition-synthesis-v1.schema.json"
ATLAS = ROOT / "residual_atlas/phase1-quantum-disposition-synthesis-fragment-v1.json"
MATERIALITY = ROOT / "planning/paper-coverage/quantum-phase1-dispositions-2026-07-21.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(cert: dict[str, Any], atlas: dict[str, Any], materiality: dict[str, Any], *, verify_hashes: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)

    if verify_hashes:
        for ref in cert["source_refs"].values():
            path = ROOT / ref["path"]
            assert sha(path) == ref["sha256"]
            payload = json.loads(path.read_text())
            assert str(payload.get("result_id") or payload.get("id")) == ref["result_id"]

    rows = {row["id"]: row for row in cert["theory_rows"]}
    assert set(rows) == {
        "STRICT_FIXED_FIELD_CONTENT_PURE_WEYL",
        "FORMAL_TAU_ADIC_COMPENSATOR_EXTENSION",
        "SELECTED_RELATIVE_CHANGED_ACTION_REPAIR_ORBIT",
        "TWO_PHASE_COUNTERFLOW_SUCCESSOR",
        "SCALAR_FLAT_BERGER_SCHUR_METHOD",
    }

    strict = rows["STRICT_FIXED_FIELD_CONTENT_PURE_WEYL"]
    assert strict["lifecycle"]["state"] == "OBSTRUCTED"
    assert strict["lifecycle"]["qme_status"] == "OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
    assert strict["exact_data"]["C2"] == {"numerator": 199, "denominator": 30}
    assert strict["exact_data"]["E4"] == {"numerator": -87, "denominator": 20}
    assert strict["exact_data"]["CdualC"] == {"numerator": 0, "denominator": 1}
    assert strict["exact_data"]["H14_even_dimension"] == 2
    assert strict["exact_data"]["H14_odd_dimension"] == 1

    tau = rows["FORMAL_TAU_ADIC_COMPENSATOR_EXTENSION"]
    assert tau["lifecycle"]["state"] == "QME_RESTORED"
    assert tau["strict_equivalence"] is False
    assert "ALL_LOOP_ONLY_CONDITIONAL" in tau["lifecycle"]["qme_status"]
    assert tau["missing_inputs"]["actual_four_dimensional_regulator"] == "NOT_CONSTRUCTED"
    assert tau["missing_inputs"]["global_BRST_Hadamard_state"] is False
    assert tau["missing_inputs"]["unconditional_all_loop_QME"] is False

    relative = rows["SELECTED_RELATIVE_CHANGED_ACTION_REPAIR_ORBIT"]
    assert relative["lifecycle"]["coefficient_status"] == "NOT_COMPUTED"
    assert relative["lifecycle"]["qme_status"] == "UNDEFINED"
    assert relative["lifecycle"]["selected_action"] is False
    assert [w["on_requested_target"] for w in relative["first_obstructions"]] == ["-9", "-9/4"]

    counterflow = rows["TWO_PHASE_COUNTERFLOW_SUCCESSOR"]
    assert counterflow["lifecycle"]["state"] == "NOT_ACTIVATED"
    assert counterflow["lifecycle"]["selected_action"] is False
    assert counterflow["classical_decision"]["robust_stationary_retuning_exists"] is False
    assert all(value == "NOT_ACTIVATED" for value in counterflow["quantum_promotions"].values())

    spectral = rows["SCALAR_FLAT_BERGER_SCHUR_METHOD"]
    assert spectral["complete_carrier_functions"] is False
    assert spectral["lifecycle"]["qme_status"] == "UNDEFINED"
    assert "EUCLIDEAN-SPECTRAL" in spectral["lifecycle"]["dependency_tags"]
    assert "LORENTZIAN-CAUSAL" not in spectral["lifecycle"]["dependency_tags"]

    repairs = cert["minimal_repair_families"]
    assert len(repairs) == 9
    assert len({row["family_id"] for row in repairs}) == 9
    assert all(row["selected_action"] is False for row in repairs)
    assert all(set(row["quantum_promotions"].values()) == {"NOT_ACTIVATED"} for row in repairs)

    assert cert["phase1_decision"]["phase2_quantum_candidate_selected"] is False
    assert cert["phase1_decision"]["new_action_architecture_opened"] is False
    assert all(value == "REJECT" for value in cert["mutation_expectations"].values())

    entries = {row["id"]: row for row in atlas["entries"]}
    assert len(entries) == 5
    assert entries["quantum.phase1.strict_weyl.local_anomaly_obstruction"]["descriptions"]["quantum"] == "OBSTRUCTED"
    assert entries["quantum.phase1.counterflow.successor_nonactivation"]["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
    assert entries["quantum.phase1.berger.schur_partial_spectral_method"]["descriptions"]["causal"] == "NOT_APPLICABLE"
    assert all(set(row["scope"]) >= {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"} for row in atlas["entries"])

    assert materiality["source_result_id"] == cert["result_id"]
    expected_cert_hash = hashlib.sha256((json.dumps(cert, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    assert materiality["source_sha256"] == expected_cert_hash
    by_paper = {row["paper"]: row for row in materiality["records"]}
    assert set(by_paper) == {"00", "12", "13", "98", "99"}
    assert all(row["publication_edit"] == "NOT_PERFORMED_BY_QUANTUM_SYNTHESIS" for row in by_paper.values())


def must_reject(
    cert: dict[str, Any],
    atlas: dict[str, Any],
    materiality: dict[str, Any],
    mutate: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None],
) -> None:
    c, a, m = copy.deepcopy(cert), copy.deepcopy(atlas), copy.deepcopy(materiality)
    mutate(c, a, m)
    try:
        verify(c, a, m, verify_hashes=False)
    except (AssertionError, KeyError, ValidationError):
        return
    raise AssertionError("contradiction mutation was accepted")


def main() -> int:
    cert = json.loads(CERT.read_text())
    atlas = json.loads(ATLAS.read_text())
    materiality = json.loads(MATERIALITY.read_text())
    verify(cert, atlas, materiality)

    mutations = [
        lambda c, a, m: c["theory_rows"][0]["lifecycle"].update(state="QME_RESTORED"),
        lambda c, a, m: c["theory_rows"][1].update(strict_equivalence=True),
        lambda c, a, m: c["theory_rows"][1]["lifecycle"].update(qme_status="UNCONDITIONAL_ALL_LOOP_QME_RESTORED"),
        lambda c, a, m: c["minimal_repair_families"][0].update(selected_action=True),
        lambda c, a, m: c["theory_rows"][3]["quantum_promotions"].update(qme="QME_RESTORED"),
        lambda c, a, m: c["theory_rows"][4]["lifecycle"].update(qme_status="QME_RESTORED"),
        lambda c, a, m: c["theory_rows"][2]["lifecycle"].update(coefficient_status="COEFFICIENT_COMPUTED"),
        lambda c, a, m: c["source_refs"]["paper12_claim_map"].update(sha256="0" * 64),
    ]
    for mutation in mutations:
        must_reject(cert, atlas, materiality, mutation)
    print(f"PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1 independent verification: PASS ({len(mutations)} mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

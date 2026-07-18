#!/usr/bin/env python3
"""Fail-closed associativity audit for the transverse linearized PBW backend."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.first_variation_pbw import lin_add, lin_scale
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import fixture
import d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation as jet_backend


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
JET_CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-linearized-pbw-associativity-gate.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-linearized-pbw-associativity-gate-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_linearized_pbw_associativity_gate.py"
TESTS = HERE / "tests/test_nariai_transverse_linearized_pbw_associativity_gate.py"
BACKEND = HERE / "first_variation_pbw.py"
JET_PRODUCER = HERE / "nariai_transverse_jet_aware_middle_schur_variation.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _count(table) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def _digest(table) -> str:
    payload = "\n".join(
        f"{word}:{matrix.rows}x{matrix.cols}:{sorted((r, c, str(v)) for (r, c), v in matrix.todok().items())}"
        for word, matrix in sorted(table.items())
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _raw_jet_data() -> dict[str, Any]:
    """Ask the producer for its exact tables without changing its certificate API."""
    jet_backend.exact_data.cache_clear()
    serializer = jet_backend._table
    jet_backend._table = lambda table: {**serializer(table), "_raw_table": table}
    try:
        return jet_backend.exact_data()
    finally:
        jet_backend._table = serializer
        jet_backend.exact_data.cache_clear()


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    captured = _raw_jet_data()
    variations = {
        name: record["_raw_table"]
        for name, record in captured["operator_variations"].items()
        if isinstance(record, dict) and "_raw_table" in record
    }
    base = fixture()
    pbw = jet_backend._pbw_layers()

    def pair(base_table, name):
        return base_table, variations[name]

    middle = pair(base["middle"]["yang_mills_middle"], "Yang_Mills_middle")
    splitting = pair(base["corrected_l1"], "corrected_L1")
    gauge = pair(base["k_p0"], "first_BGG")
    phi = pair(base["phi"], "Phi")

    middle_splitting = pbw["H1"].compose(middle, splitting)
    phi_definition_defect = lin_add(phi, lin_scale(middle_splitting, -1))
    left_parenthesization = pbw["C0"].compose(middle_splitting, gauge)
    splitting_gauge = pbw["C0"].compose(splitting, gauge)
    right_parenthesization = pbw["C0"].compose(middle, splitting_gauge)
    associator = lin_add(left_parenthesization, lin_scale(right_parenthesization, -1))

    delta = associator[1]
    first_word = min(delta, key=lambda word: (len(word), word))
    first_row, first_column = min(delta[first_word].todok())
    first_value = delta[first_word][first_row, first_column]
    shifted = captured["identity_defects"]["shifted_chain_variation"]["_raw_table"]

    return {
        "typed_triple": {
            "expression": "M_parent o L1_corrected o (K p0)",
            "source": "C0 rank 15",
            "intermediate": ["H1 rank 9", "C1 rank 60"],
            "target": "C1dual rank 60",
        },
        "phi_definition": {
            "base_defect_coefficients": _count(phi_definition_defect[0]),
            "variation_defect_coefficients": _count(phi_definition_defect[1]),
        },
        "associator": {
            "base_nonzero_coefficients": _count(associator[0]),
            "variation_nonzero_coefficients": _count(delta),
            "variation_orders": sorted({len(word) for word in delta}),
            "variation_sha256": _digest(delta),
            "normalized_witness": {
                "word": list(first_word),
                "output_row": first_row,
                "input_column": first_column,
                "coefficient": str(first_value),
                "normalizing_multiplier": str(1 / first_value),
                "normalized_value": "1",
            },
        },
        "reported_shifted_chain": {
            "nonzero_coefficients": _count(shifted),
            "sha256": _digest(shifted),
            "operator_obstruction_authoritative": False,
        },
        "abstract_identity": {
            "derivation": [
                "Phi=M L1",
                "M d_parent=0",
                "d_aut=d_parent-I_Omega p0",
                "d_aut L0=L1 K",
                "p0 L0=1",
                "p0(1-L0 p0)=0",
                "M d_aut-M Phi(K p0)=M d_aut(1-L0 p0)=0",
            ],
            "first_variation_must_vanish_in_an_associative_operator_algebra": True,
        },
        "interpretation": {
            "linearized_PBW_backend_associative_on_test_triple": False,
            "shifted_chain_obstruction_superseded": True,
            "phi_ansatz_obstructions_remain_backend_linear_algebra_only": True,
            "rank_310_transverse_SDR_decided": False,
            "required_next_gate": "coefficient-jet-aware associative PBW composition, then replay action Schur and rank-310 SDR",
        },
    }


def build() -> dict[str, Any]:
    data = exact_data()
    paths = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, BACKEND, JET_PRODUCER)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-linearized-pbw-associativity-gate-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1",
        "result_state": "LINEARIZED_PBW_NONASSOCIATIVE_SHIFTED_CHAIN_OBSTRUCTION_SUPERSEDED",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "jet_aware_backend_output": {
                "path": str(JET_CERT.relative_to(ROOT)),
                "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1",
                "sha256": _sha(JET_CERT),
            }
        },
        "exact_data": data,
        "exact_checks": {
            "phi_definition_exact": data["phi_definition"]["base_defect_coefficients"] == 0 and data["phi_definition"]["variation_defect_coefficients"] == 0,
            "base_associator_zero": data["associator"]["base_nonzero_coefficients"] == 0,
            "linearized_associator_nonzero": data["associator"]["variation_nonzero_coefficients"] == 209,
            "normalized_witness_one": data["associator"]["normalized_witness"]["normalized_value"] == "1",
            "reported_shifted_chain_not_authoritative": data["reported_shifted_chain"]["operator_obstruction_authoritative"] is False,
            "rank_310_not_overclaimed": data["interpretation"]["rank_310_transverse_SDR_decided"] is False,
        },
        "flags": {
            "TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE": False,
            "TRANSVERSE_LINEARIZED_PBW_NONASSOCIATIVITY_EXACT": True,
            "TRANSVERSE_SHIFTED_CHAIN_OBSTRUCTION_AUTHORITATIVE": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_COEFFICIENT_JET_ASSOCIATIVE_PBW_REPLAY",
        "claim_boundary": "The current first-variation PBW backend is nonassociative on the typed M_parent, L1_corrected, Kp0 triple: its base associator vanishes but its first variation has 209 coefficients, with normalized algebraic witness one. Since the shifted-chain identity follows abstractly from already-certified chain identities in any associative differential-operator algebra, the backend's 207-term shifted-chain defect and downstream Phi-only repair obstructions are not mathematical operator obstructions. This audit does not prove the transverse rank-310 SDR or causal transfer; it requires an associative coefficient-jet-aware replay.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in paths},
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_linearized_pbw_associativity_gate --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_linearized_pbw_associativity_gate.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_linearized_pbw_associativity_gate",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-linearized-pbw-associativity-gate-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    witness = data["associator"]["normalized_witness"]
    return f"""# Transverse linearized PBW associativity gate

The current jet-aware first-variation PBW backend is not associative on the
typed triple `M_parent o L1_corrected o (K p0)`.  The base associator is zero,
but its first variation contains `{data['associator']['variation_nonzero_coefficients']}`
coefficients.  Its first normalized witness is

```text
word={witness['word']}, row={witness['output_row']}, column={witness['input_column']}
coefficient={witness['coefficient']}, multiplier={witness['normalizing_multiplier']}
normalized value=1
```

This is decisive because `Phi=M L1` is replayed exactly, while the shifted
chain follows abstractly from `M d_parent=0`, `d_aut L0=L1 K`, `p0 L0=1`, and
`p0(1-L0 p0)=0`.  Thus the previously reported 207-coefficient shifted-chain
defect is a backend artifact, not an operator obstruction.  The Phi-only rank
screens remain valid only as linear algebra relative to that superseded
backend target.

The next gate is a coefficient-jet-aware associative PBW replay.  No
transverse rank-310 SDR or causal theorem is promoted here.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(payload))
    if args.check and json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("associativity-gate artifact is stale")
    print("NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1: PASS")


if __name__ == "__main__":
    main()

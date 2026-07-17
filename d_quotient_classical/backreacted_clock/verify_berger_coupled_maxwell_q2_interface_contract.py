#!/usr/bin/env python3
"""Independent replay of the Berger coupled Maxwell q2 interface."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-coupled-maxwell-q2-interface-contract-v1.schema.json"
CONTRACTION = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
BALANCED = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json"
THIRD_ORDER = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
        if json.loads(path.read_text())["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency result mismatch: {path}")
    for relative, digest in certificate["provenance"]["source_manifest"].items():
        path = ROOT / relative
        if _sha256(path) != digest:
            raise AssertionError(f"source hash mismatch: {path}")

    gravity_rows = json.loads(CONTRACTION.read_text())["row_layout"]["component_rows"]
    combined = certificate["combined_BV_interface"]["row_layout"]
    if len(combined) != 64 or [row["index"] for row in combined] != list(range(64)):
        raise AssertionError("independent 64-row contiguity replay failed")
    if [row["row_id"] for row in combined[:54]] != [row["row_id"] for row in gravity_rows]:
        raise AssertionError("independent gravity row-prefix replay failed")
    expected_maxwell = [
        "c_M", "A_0", "A_1", "A_2", "A_3",
        "A_plus_0", "A_plus_1", "A_plus_2", "A_plus_3", "c_M_plus",
    ]
    if [row["row_id"] for row in combined[54:]] != expected_maxwell:
        raise AssertionError("independent Maxwell row-suffix replay failed")
    ranks = [sum(row["degree"] == degree for row in combined) for degree in (-1, 0, 1, 2)]
    if ranks != [6, 26, 26, 6]:
        raise AssertionError("independent combined degree-rank replay failed")

    balanced = json.loads(BALANCED.read_text())["balanced_Maxwell_fixture"]["exact_data"]
    direct = sp.Matrix([sp.sympify(value) for value in balanced["standing_direct_action_cubic"]])
    repository = sp.Matrix([sp.sympify(value) for value in balanced["standing_repository_q2"]])
    correction = sp.Matrix([sp.sympify(value) for value in balanced["second_order_Maurer_Cartan_correction"]])
    if repository != 2 * direct:
        raise AssertionError("independent metric factor-two replay failed")
    action_pairing = sp.factor((correction.T * direct)[0])
    metric_pairing = sp.factor((correction.T * repository)[0] / 2)
    equation_source = sp.sympify(
        json.loads(THIRD_ORDER.read_text())["physical_mixed_q2_block"]["resonant_harmonic_source"][0]
    )
    canonical_euler_source = -equation_source
    maxwell_pairing = sp.factor(2 * canonical_euler_source * (-1) * sp.Rational(1, 2))
    if not action_pairing == metric_pairing == maxwell_pairing == sp.Rational(564428800, 35920017):
        raise AssertionError("independent cyclic normalization replay failed")
    if certificate["standing_light_cyclic_regression"]["canonical_BV_Euler_Maxwell_q2_e023_cosine"] != str(canonical_euler_source):
        raise AssertionError("persisted canonical Euler sign drifted")
    if certificate["full_export_acceptance_gate"]["status"] != "INPUT_BLOCKED":
        raise AssertionError("missing full support-local mixed q2 was promoted")
    if certificate["background_partition"]["cross_substitution_allowed"] is not False:
        raise AssertionError("Berger and axial background contracts were conflated")
    print("BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT independent replay: PASS")


if __name__ == "__main__":
    main()

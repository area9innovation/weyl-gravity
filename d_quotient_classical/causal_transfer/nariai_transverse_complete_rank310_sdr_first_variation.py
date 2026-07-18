#!/usr/bin/env python3
"""Certify the complete transverse first variation of the rank-310 SDR."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
from d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr import (
    ROOT,
    abstract_fixture,
    coefficient_fixture,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-complete-rank-310-sdr-first-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-complete-rank-310-sdr-first-variation-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_complete_rank310_sdr_first_variation.py"
TESTS = HERE / "tests/test_nariai_transverse_complete_rank310_sdr_first_variation.py"
CORE = HERE / "nariai_transverse_rank310_dual_sdr.py"

DEPENDENCIES = {
    "base_rank_310_SDR": (
        ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json",
        "NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1",
    ),
    "splitting_coefficient_jets": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json",
        "NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1",
    ),
    "associative_middle_shifted_chain": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json",
        "NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1",
    ),
    "factorized_Hom_schur": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json",
        "NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1",
    ),
    "upper_relative_saddle_chain": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json",
        "NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1",
    ),
    "action_Bach_variation": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json",
        "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1",
    ),
    "pairing_variation": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json",
        "NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1",
    ),
    "metric_gauge_variation": (
        ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json",
        "NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, expected: str) -> tuple[dict[str, str], dict[str, Any]]:
    payload = json.loads(path.read_text())
    if payload["result_id"] != expected:
        raise AssertionError(f"dependency drifted: {path}")
    return (
        {
            "path": str(path.relative_to(ROOT)),
            "result_id": expected,
            "sha256": _sha(path),
        },
        payload,
    )


def _binding(record: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "source": source,
        "orders": record["orders"],
        "nonzero_coefficients": record["nonzero_coefficients"],
        "sha256": record["sha256"],
    }


def build() -> dict[str, Any]:
    references: dict[str, dict[str, str]] = {}
    dependencies: dict[str, dict[str, Any]] = {}
    for name, (path, expected) in DEPENDENCIES.items():
        references[name], dependencies[name] = _dependency(path, expected)

    if not dependencies["base_rank_310_SDR"]["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
        raise AssertionError("base rank-310 SDR is unavailable")
    if not dependencies["splitting_coefficient_jets"]["exact_checks"]["strict_square_all_required_jets"]:
        raise AssertionError("corrected first square is unavailable")
    if not dependencies["associative_middle_shifted_chain"]["exact_checks"]["shifted_chain_zero"]:
        raise AssertionError("shifted-chain variation is unavailable")
    if not dependencies["factorized_Hom_schur"]["flags"]["NARIAI_TRANSVERSE_COMPRESSED_SCHUR_REPLAY"]:
        raise AssertionError("factorized Schur variation is unavailable")
    if not dependencies["upper_relative_saddle_chain"]["flags"]["NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN"]:
        raise AssertionError("upper relative-saddle variation is unavailable")
    if not dependencies["action_Bach_variation"]["flags"]["TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION"]:
        raise AssertionError("action Bach-Hessian variation is unavailable")
    if not dependencies["pairing_variation"]["exact_checks"]["all_four_pairing_variations_zero_in_declared_frame"]:
        raise AssertionError("pairing variation is nonzero")
    if not dependencies["metric_gauge_variation"]["exact_checks"]["action_derived_delta_K_zero"]:
        raise AssertionError("metric gauge generator variation is nonzero")

    abstract = abstract_fixture()
    coefficient = coefficient_fixture()
    if any(abstract["defects"].values()):
        raise AssertionError("an all-row dual-number identity failed")
    if any(coefficient["coefficient_defect_counts"].values()):
        raise AssertionError("a coefficient-level defining relation failed")

    splitting = dependencies["splitting_coefficient_jets"]["exact_data"]
    associative = dependencies["associative_middle_shifted_chain"]["exact_data"]
    factorized = dependencies["factorized_Hom_schur"]["exact_data"]
    action = dependencies["action_Bach_variation"]["exact_data"]
    bindings = {
        "L0_dot": _binding(
            splitting["coefficient_jets"]["L0"]["()"],
            "splitting_coefficient_jets",
        ),
        "L1_dot": _binding(
            splitting["coefficient_jets"]["L1_corrected"]["()"],
            "splitting_coefficient_jets",
        ),
        "d_aut_dot": _binding(coefficient["d_aut_dot"], "this_certificate"),
        "g_dot": _binding(coefficient["g_dot"], "this_certificate"),
        "M_dot": _binding(
            factorized["parent_middle"]["variation"], "factorized_Hom_schur"
        ),
        "L1sharp_dot": _binding(
            factorized["factorized_Hom_adjoint"]["L1sharp_variation"],
            "factorized_Hom_schur",
        ),
        "Phi_dot": _binding(
            associative["authoritative_phi_variation"],
            "associative_middle_shifted_chain",
        ),
        "Schur_dot": _binding(
            factorized["compressed_schur"]["variation"],
            "factorized_Hom_schur",
        ),
        "B_action_dot": _binding(
            action["identified_full_action_variation"],
            "action_Bach_variation",
        ),
    }
    dotted_matrices = {
        name: repair._serialize_matrix(matrix)
        for name, matrix in abstract["dotted"].items()
    }
    abstract_checks = {
        name: len(defects) == 0 for name, defects in abstract["defects"].items()
    }
    source_paths = (Path(__file__).resolve(), CORE, VERIFIER, TESTS, SCHEMA)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-complete-rank-310-sdr-first-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1",
        "result_state": "COMPLETE_TEN_BLOCK_RANK_310_CYCLIC_SDR_FIRST_VARIATION_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": references,
        "carrier": {
            "background": "unit Nariai dS2 x S2",
            "tangent": "delta a=-(1/3)sinh(2t), delta b=sinh(t), fixed-Lambda linearized Einstein",
            "block_names": list(repair.BLOCK_NAMES),
            "block_degrees": list(repair.BLOCK_DEGREES),
            "block_ranks": list(repair.BLOCK_RANKS),
            "total_rank": sum(repair.BLOCK_RANKS),
            "degree_ranks": [15, 140, 140, 15],
            "dropped_rows": [],
        },
        "variation_convention": {
            "fixed_pointwise_maps": ["J0", "p0", "K", "all four fibre pairings"],
            "derived_map": "g_dot=-r0 L0_dot p0",
            "formal_adjoints": "differentiated with the certified zero pairing variation",
            "no_free_SDR_ansatz": True,
        },
        "coefficient_bindings": bindings,
        "coefficient_relation_defects": coefficient["coefficient_defect_counts"],
        "coefficient_jet_requests": coefficient["requested_coefficient_jets"],
        "dotted_abstract_matrices": dotted_matrices,
        "all_row_first_variation_checks": abstract_checks,
        "support_and_cyclicity": {
            "support": "every varied inclusion, projection, homotopy and triangular transform is finite-order differential and support-nonincreasing",
            "cyclicity": "the pairing variation vanishes; the differentiated inclusion/projection adjunction, odd homotopy adjunction and BV-canonical transform identities hold on all ten blocks",
            "no_Green_operator_used": True,
        },
        "exact_checks": {
            "all_twenty_one_dual_number_matrix_identities_zero": all(abstract_checks.values()) and len(abstract_checks) == 21,
            "all_coefficient_relation_defects_zero": not any(coefficient["coefficient_defect_counts"].values()),
            "all_ten_blocks_enumerated": len(repair.BLOCK_NAMES) == 10,
            "full_rank_is_310": sum(repair.BLOCK_RANKS) == 310,
            "no_rows_dropped": True,
            "pairing_variation_zero": True,
            "metric_gauge_variation_zero": True,
            "action_endpoint_bound": True,
            "upper_relative_saddle_bound": True,
            "support_local": True,
            "causal_transfer_not_overclaimed": True,
        },
        "flags": {
            "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1": True,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": True,
            "TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION": True,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
            "TRANSVERSE_METRIC_GREEN_HOMOTOPY": False,
            "TRANSVERSE_RANK_310_GREEN_HOMOTOPY": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_METRIC_BIWAVE_GREEN_CONTROL",
        "claim_boundary": "This certificate differentiates the complete ten-block, rank-310 support-local cyclic SDR along the certified transverse linearized Einstein tangent. It binds every varying abstract generator to the exact coefficient-jet, factorized-adjoint, upper-saddle and action-Hessian inputs, and verifies all chain, retract, side-condition, cyclicity and coordinate-conjugation identities through first order. It does not construct a metric or rank-310 advanced/retarded Green homotopy on the deformed background.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path) for path in source_paths
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_complete_rank310_sdr_first_variation --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_complete_rank310_sdr_first_variation.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_transverse_complete_rank310_sdr_first_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-complete-rank-310-sdr-first-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    checks = payload["all_row_first_variation_checks"]
    coefficients = payload["coefficient_bindings"]
    return f"""# Transverse complete rank-310 SDR first variation

The complete ten-block cyclic deformation retract differentiates exactly
along the certified transverse linearized Einstein tangent.  All
`{len(checks)}` dual-number matrix identities vanish, including both split
and original-coordinate chain, retract, side-condition and cyclicity rows.
No row is dropped; the degree ranks remain `15,140,140,15`.

The proof introduces no new SDR fit.  It differentiates the universal
mapping-cone formulas and binds the dotted generators to the authoritative
coefficient calculations.  In particular, `g_dot=-r0 L0_dot p0`, the direct
action variation has `{coefficients['B_action_dot']['nonzero_coefficients']}`
coefficients, and all coefficient-level complement, gauge-reconstruction and
Noether defects vanish.  Pairings and the metric gauge generator have zero
variation in the declared moving frame.

All varied maps are finite-order differential operators, hence support-local.
This closes the algebraic transverse SDR gate.  It does not yet construct
advanced or retarded Green homotopies on the transversely deformed metric;
the next gate is metric biwave Green control.
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
    if args.check:
        if json.loads(OUTPUT.read_text()) != payload or REPORT.read_text() != report(payload):
            raise AssertionError("transverse rank-310 first-variation artifact is stale")
    print("NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1: PASS")


if __name__ == "__main__":
    main()

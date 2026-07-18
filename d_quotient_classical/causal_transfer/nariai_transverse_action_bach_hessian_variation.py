#!/usr/bin/env python3
"""Identify the transverse variation of the action Bach Hessian exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    endpoint_operator,
)
from d_quotient_classical.causal_transfer.nariai_transverse_action_bach_leading_variation import (
    action_variation_frozen,
)
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _count,
    _deserialize_table,
    _difference,
    _table,
)
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    _table_scale,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-action-bach-hessian-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-action-bach-hessian-variation-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_action_bach_hessian_variation.py"
TESTS = HERE / "tests/test_nariai_transverse_action_bach_hessian_variation.py"
LEADING_SOURCE = HERE / "nariai_transverse_action_bach_leading_variation.py"

ENDPOINT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1.json"
SCHUR = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json"
WITNESS = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
K_AUDIT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json"
PAIRING = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json"
BASE_ACTION = ROOT / "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json"
ASSOCIATIVE_PBW = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _orders(table: dict[tuple[int, ...], sp.Matrix]) -> list[int]:
    return sorted({len(word) for word in table})


def _dependency(path: Path, result_id: str) -> dict[str, str]:
    payload = json.loads(path.read_text())
    if payload["result_id"] != result_id:
        raise AssertionError(f"dependency drifted: {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": result_id,
        "sha256": _sha(path),
    }


def exact_data() -> dict[str, Any]:
    endpoint = json.loads(ENDPOINT.read_text())["exact_data"]
    target_record = endpoint["factorized_endpoint_target"]
    parent_target = _deserialize_table(
        target_record["compressed_parent_endpoint_variation"]
    )
    action_target = _deserialize_table(
        target_record["action_bach_variation_target"]
    )
    scaling_defect = _difference(
        action_target, _table_scale(parent_target, -sp.Rational(1, 2))
    )
    if scaling_defect:
        raise AssertionError("factorized action target normalization drifted")

    direct = action_variation_frozen()
    base_defect = _difference(direct["base"], endpoint_operator()["action_bach"])
    action_order_two = direct["order_two"]
    target_order_two = {
        word: matrix for word, matrix in action_target.items() if len(word) == 2
    }
    leading_defect = _difference(action_order_two, target_order_two)
    if base_defect or leading_defect:
        raise AssertionError("direct action leading variation missed the parent target")
    if any(order > 2 for order in _orders(direct["frozen_variation"])):
        raise AssertionError("action variation acquired an order above two")

    # The frozen explicit curvature coefficient omits terms in which an outer
    # derivative lands on dot(C).  Such terms leave at most one derivative on
    # the field.  Record their nonzero regression rather than treating the
    # frozen lower table as an action calculation.
    lower_direct = {
        word: matrix
        for word, matrix in direct["frozen_variation"].items()
        if len(word) <= 1
    }
    lower_target = {
        word: matrix for word, matrix in action_target.items() if len(word) <= 1
    }
    frozen_lower_defect = _difference(lower_direct, lower_target)

    parent_correction = _deserialize_table(
        endpoint["complete_first_order_solve"]["unique_correction"]
    )
    action_correction = _table_scale(parent_correction, -sp.Rational(1, 2))
    return {
        "direct_action_leading_derivation": {
            "formula": "dot of delta[nabla^c nabla^d C_acbd+(1/2)Ric^cd C_acbd] in the moving orthonormal covariant-PBW frame",
            "background": "unit Nariai dS2 x S2",
            "tangent": "delta a=-(1/3)sinh(2t), delta b=sinh(t), fixed-Lambda linearized Einstein",
            "action_normalization": "B_action=-2 B_standard",
            "base_action_defect": _table(base_defect),
            "frozen_full_variation": _table(direct["frozen_variation"]),
            "authoritative_order_two": _table(action_order_two),
            "orders_above_two_absent": True,
            "why_order_two_is_authoritative": "the only frozen terms are derivatives landing on the explicit varied Weyl coefficient; after that hit, at most one derivative remains on the input field",
            "frozen_lower_table_authoritative": False,
            "frozen_lower_target_defect": _table(frozen_lower_defect),
        },
        "parent_action_comparison": {
            "identity": "dot(B_action)=-(1/2) dot(P_parent,compressed)",
            "compressed_parent_endpoint_variation": _table(parent_target),
            "action_bach_variation_target": _table(action_target),
            "normalization_defect": _table(scaling_defect),
            "direct_order_two_defect": _table(leading_defect),
        },
        "lower_order_noether_completion": {
            "unknown_class": "all action corrections of differential order at most one: Q0+Q^a nabla_a",
            "total_unknowns": endpoint["complete_first_order_solve"]["total_unknowns"],
            "coefficient_map_shape": endpoint["complete_first_order_solve"]["coefficient_map_shape"],
            "coefficient_map_rank": endpoint["complete_first_order_solve"]["coefficient_map_rank"],
            "augmented_ranks": endpoint["complete_first_order_solve"]["augmented_ranks"],
            "free_parameter_counts": endpoint["complete_first_order_solve"]["free_parameter_counts"],
            "action_correction": _table(action_correction),
            "action_correction_orders": _orders(action_correction),
            "differentiated_noether_identity": "dot(B_action) K=0 because B(g)=0, dot B_background=0, and dot K=0",
            "cyclicity": "dot(B_action)^sharp=dot(B_action) from the third variation of the Weyl-squared action in the constant moving-frame pairing",
            "unique_completion": True,
        },
        "identified_full_action_variation": _table(action_target),
        "disposition": {
            "action_bach_hessian_variation_exact": True,
            "method": "direct action order-two derivation plus complete lower-order differentiated-Noether uniqueness",
            "external_detour_theorem_used_as_substitute": False,
            "rank_310_first_variation_SDR": False,
            "transverse_causal_transfer": False,
        },
    }


def build() -> dict[str, Any]:
    refs = {
        "factorized_endpoint": _dependency(
            ENDPOINT, "NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1"
        ),
        "factorized_Hom_schur": _dependency(
            SCHUR, "NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1"
        ),
        "transverse_witness": _dependency(
            WITNESS, "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1"
        ),
        "metric_K_audit": _dependency(
            K_AUDIT, "NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1"
        ),
        "pairing_variation": _dependency(
            PAIRING, "NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1"
        ),
        "base_action_endpoint": _dependency(
            BASE_ACTION, "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1"
        ),
        "associative_PBW_replay": _dependency(
            ASSOCIATIVE_PBW,
            "NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1",
        ),
    }
    witness = json.loads(WITNESS.read_text())
    k_audit = json.loads(K_AUDIT.read_text())
    pairing = json.loads(PAIRING.read_text())
    associative_pbw = json.loads(ASSOCIATIVE_PBW.read_text())
    if not witness["flags"]["TRANSVERSE_FORMAL_BACH_FLAT_TANGENT"]:
        raise AssertionError("transverse tangent ceased to be linearized Bach-flat")
    if not k_audit["exact_checks"]["action_derived_delta_K_zero"]:
        raise AssertionError("action-derived dot K is no longer zero")
    if not pairing["exact_checks"]["all_four_pairing_variations_zero_in_declared_frame"]:
        raise AssertionError("moving-frame pairing variation drifted")
    if not associative_pbw["exact_checks"]["typed_associator_zero"]:
        raise AssertionError("associative PBW replay drifted")

    data = exact_data()
    sources = (
        Path(__file__).resolve(),
        LEADING_SOURCE,
        VERIFIER,
        TESTS,
        SCHEMA,
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-action-bach-hessian-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1",
        "result_state": "ACTION_BACH_HESSIAN_VARIATION_EXACT_BY_DIRECT_LEADING_DERIVATION_AND_NOETHER_UNIQUENESS",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "primary_sources": [
            {
                "title": "The conformal deformation detour complex for the obstruction tensor",
                "url": "https://arxiv.org/abs/math/0605192",
                "use": "background theorem that the linearized obstruction/Bach operator is a formally self-adjoint complex on obstruction-flat metrics; not used to replace the coefficient comparison",
            },
            {
                "title": "Yang-Mills detour complexes and conformal geometry",
                "url": "https://arxiv.org/abs/math/0606401",
                "use": "parent Yang-Mills detour and formal self-adjointness; not used as an identification theorem for the action endpoint",
            },
        ],
        "exact_data": data,
        "exact_checks": {
            "base_action_replayed": data["direct_action_leading_derivation"]["base_action_defect"]["nonzero_coefficients"] == 0,
            "orders_above_two_absent": data["direct_action_leading_derivation"]["orders_above_two_absent"],
            "direct_order_two_defect_zero": data["parent_action_comparison"]["direct_order_two_defect"]["nonzero_coefficients"] == 0,
            "parent_action_scaling_defect_zero": data["parent_action_comparison"]["normalization_defect"]["nonzero_coefficients"] == 0,
            "lower_noether_map_full_column_rank": data["lower_order_noether_completion"]["coefficient_map_rank"] == 45,
            "lower_completion_unique_all_rows": data["lower_order_noether_completion"]["free_parameter_counts"] == [0] * 9,
            "frozen_lower_table_not_promoted": not data["direct_action_leading_derivation"]["frozen_lower_table_authoritative"],
            "external_theorem_not_substituted": not data["disposition"]["external_detour_theorem_used_as_substitute"],
            "associative_PBW_backend_pinned": associative_pbw["flags"]["NARIAI_TRANSVERSE_ASSOCIATIVE_PBW_REPLAY"],
            "rank_310_not_overclaimed": not data["disposition"]["rank_310_first_variation_SDR"],
            "causal_transfer_not_overclaimed": not data["disposition"]["transverse_causal_transfer"],
        },
        "flags": {
            "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION": True,
            "TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION": True,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION",
        "claim_boundary": "This certificate derives the highest varying (order-two) coefficients of the action Bach Hessian directly from the covariant Bach tensor, pins the common normal-form layer to the exact associative PBW replay, proves that no order above two can occur in the moving covariant frame, and uses the complete 60-by-45 differentiated-Noether solve to identify the unique order-at-most-one completion. It also repairs the parent/action normalization ambiguity by keeping the compressed parent variation and the -1/2-scaled action target separate. The full rank-310 first-variation SDR and transverse causal transfer remain false.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path) for path in sources
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_action_bach_hessian_variation --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_action_bach_hessian_variation.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_action_bach_hessian_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-action-bach-hessian-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    leading = data["direct_action_leading_derivation"]
    lower = data["lower_order_noether_completion"]
    return rf"""# Transverse action Bach-Hessian variation

The transverse action gate is exact.  Differentiating the covariant Bach
formula directly in the moving orthonormal covariant-PBW frame gives no
operator coefficient above order two.  Its order-two table has
`{leading['authoritative_order_two']['nonzero_coefficients']}` nonzero
coefficients and agrees coefficientwise with the independently constructed
parent target.

The direct calculation freezes only derivatives hitting the explicit varied
Weyl coefficient.  Such terms leave at most one derivative on the input
field.  Accordingly the frozen lower table is recorded but not promoted.
The shared covariant normal-form layer is pinned to the independent exact
associative PBW replay rather than left as an implicit backend assumption.
The remaining action correction belongs to the complete

\[
 Q_0+Q^a\nabla_a
\]

class.  The differentiated Noether coefficient map has shape
`{lower['coefficient_map_shape']}`, rank `{lower['coefficient_map_rank']}`,
and all nine augmented systems have no free parameter.  The unique solution
is algebraic and cyclic.

The normalization is now explicit:

\[
 \dot B_{{\rm action}}
 =-\frac12\dot P_{{\rm parent,compressed}}.
\]

The earlier endpoint artifact displayed this formula but serialized the
unscaled parent table under an ambiguous field name.  It now stores both
tables separately.

This closes the action endpoint gate.  It does not yet prove the all-row
rank-310 deformation retract or transverse causal transfer.
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
            raise AssertionError("transverse action Bach-Hessian artifact is stale")
    print("NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1: PASS")


if __name__ == "__main__":
    main()

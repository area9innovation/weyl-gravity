#!/usr/bin/env python3
"""Export the exact temporal common-action Ward-orbit carrier obstruction."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _multiindex_from_word,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    _q1_source_parts,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-108-row-temporal-common-action-ward-orbit-obstruction-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-108-row-temporal-common-action-ward-orbit-payload-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-108-row-temporal-common-action-ward-orbit-obstruction.md"
)

DEPENDENCIES = {
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "typed_maxwell_q2_q3": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "typed_maxwell_q2_payload": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json",
    "emitter_q1": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json",
    "emitter_physical_q2": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json",
    "emitter_physical_q2_payload": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW_PAYLOAD.json",
    "emitter_diff_q2": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
    "emitter_diff_q2_payload": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD.json",
    "completed_q1": PACKAGE
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_q2": PACKAGE
    / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "prior_obstruction": PACKAGE
    / "certificates/BERGER_108_ROW_ARITY_TWO_OBSTRUCTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_108_row_temporal_common_action_ward_orbit.py",
    PACKAGE / "tests/test_berger_108_row_temporal_common_action_ward_orbit.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

SCALE_ORDER = ("s_Maxwell", "s_emitter", "s_tau")
PRIOR_WITNESS_KEY = (
    55,
    replay.word([1, 1, 0, 0]),
    84,
    replay.word([0, 0, 0, 0]),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def determinant3(matrix: list[list[int]]) -> int:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def evaluate(matrix: list[list[int]], scales: list[int]) -> list[int]:
    return [
        sum(coefficient * scale for coefficient, scale in zip(row, scales, strict=True))
        for row in matrix
    ]


def _pairing_entry(document: dict[str, Any], left: int, right: int) -> list[Any]:
    matches = [
        entry
        for entry in document["carrier_contract"]["pairing_entries"]
        if entry[0] == left and entry[1] == right
    ]
    if len(matches) != 1:
        raise AssertionError(f"pairing entry ({left},{right}) is not unique")
    return matches[0]


def normalization_audit(*, maxwell_factor: int = 2) -> dict[str, Any]:
    """Solve the action-lowering scale constraints exactly."""

    matrix = [
        [1, 0, -maxwell_factor],
        [1, -1, 0],
        [0, 1, -1],
    ]
    current_rank = rank(matrix)
    determinant = determinant3(matrix)
    return {
        "scale_order": list(SCALE_ORDER),
        "constraints": [
            {
                "source": "typed gravity-clock-Maxwell temporal BV orbit",
                "equation": f"s_Maxwell-{maxwell_factor} s_tau=0",
                "row": matrix[0],
                "derivation": (
                    "Omega_typed=Omega_legacy S with "
                    f"S=diag(I_54,{maxwell_factor} I_10)"
                ),
            },
            {
                "source": "switched Maxwell-emitter physical Hessian",
                "equation": "s_Maxwell-s_emitter=0",
                "row": matrix[1],
                "derivation": (
                    "the 198-key emitter q1 Hessian is raised from one "
                    "A--K action with the canonical signed pairing"
                ),
            },
            {
                "source": "temporal massive-two-form Diff--BV cotangent orbit",
                "equation": "s_emitter-s_tau=0",
                "row": matrix[2],
                "derivation": (
                    "the tau, K and K-plus slots are three variations of "
                    "integral <K_plus,L_(tau e0)K> under the canonical pairing"
                ),
            },
        ],
        "matrix": matrix,
        "determinant": determinant,
        "rank": current_rank,
        "nullity": len(SCALE_ORDER) - current_rank,
        "canonical_carrier_scale_evaluation": {
            "scales": [1, 1, 1],
            "residual": evaluate(matrix, [1, 1, 1]),
        },
        "typed_Maxwell_scale_evaluation": {
            "scales": [2, 1, 1],
            "residual": evaluate(matrix, [2, 1, 1]),
        },
        "nondegenerate_common_action_pairing_exists": current_rank < len(SCALE_ORDER),
    }


def mutation_audit() -> dict[str, Any]:
    """Replace the imported factor two by one as a sensitivity mutation."""

    mutated = normalization_audit(maxwell_factor=1)
    return {
        "name": "replace_typed_Maxwell_factor_two_by_one",
        "scientific_status": (
            "MUTATION_ONLY: this changes an imported typed Maxwell pairing "
            "and is not an authorized repair"
        ),
        "detected": (
            mutated["determinant"] == 0
            and mutated["rank"] == 2
            and mutated["canonical_carrier_scale_evaluation"]["residual"]
            == [0, 0, 0]
        ),
        "mutated_matrix": mutated["matrix"],
        "mutated_determinant": mutated["determinant"],
        "mutated_rank": mutated["rank"],
        "mutated_null_vector": [1, 1, 1],
    }


def _q1_fixture(
    q1: replay.Operator, output: int, source: int, word: tuple[int, ...]
) -> dict[str, Any]:
    coefficient = q1.get((output, source, word))
    if not coefficient:
        raise AssertionError(f"missing q1 fixture {(output, source, word)}")
    return {
        "output": output,
        "input": source,
        "pbw_multiindex": list(_multiindex_from_word(word)),
        "coefficient": serialize(coefficient),
    }


def q1_orbit_terms() -> list[dict[str, Any]]:
    q1 = replay.load_q1()[(0, 0)]
    return [
        _q1_fixture(q1, 16, 3, ()),
        _q1_fixture(q1, 52, 38, ()),
        _q1_fixture(q1, 96, 55, (1,)),
        _q1_fixture(q1, 59, 84, (1,)),
        _q1_fixture(q1, 60, 84, (0,)),
    ]


def _typed_q2_fixture(
    document: dict[str, Any],
    output: int,
    left: int,
    left_multi: list[int],
    right: int,
    right_multi: list[int],
) -> dict[str, Any]:
    row = document["rows"][output]
    if row["output"] != output:
        raise AssertionError("typed Maxwell row order drifted")
    matches = [
        term
        for term in row["terms"]
        if term[:4] == [left, left_multi, right, right_multi]
    ]
    if len(matches) != 1:
        raise AssertionError(f"typed Maxwell fixture is not unique on row {output}")
    return {
        "source": "typed_Maxwell_temporal_BV",
        "output": output,
        "left_input": left,
        "left_pbw_multiindex": left_multi,
        "right_input": right,
        "right_pbw_multiindex": right_multi,
        "coefficient": matches[0][4],
        "coefficient_factors": [],
    }


def _observer_q2_fixture(
    document: dict[str, Any],
    source_name: str,
    output: int,
    left: int,
    left_multi: list[int],
    right: int,
    right_multi: list[int],
) -> dict[str, Any]:
    row = next(row for row in document["rows"] if row["output"] == output)
    matches = [
        term
        for term in row["terms"]
        if (
            term["left_input_row"],
            term["left_pbw_multiindex"],
            term["right_input_row"],
            term["right_pbw_multiindex"],
        )
        == (left, left_multi, right, right_multi)
    ]
    if len(matches) != 1:
        raise AssertionError(f"{source_name} fixture is not unique on row {output}")
    term = matches[0]
    return {
        "source": source_name,
        "output": output,
        "left_input": left,
        "left_pbw_multiindex": left_multi,
        "right_input": right,
        "right_pbw_multiindex": right_multi,
        "coefficient": term["coefficient"],
        "coefficient_factors": term["coefficient_factors"],
    }


def q2_orbit_terms() -> list[dict[str, Any]]:
    maxwell = json.loads(DEPENDENCIES["typed_maxwell_q2_payload"].read_text())
    emitter_diff = json.loads(DEPENDENCIES["emitter_diff_q2_payload"].read_text())
    emitter_physical = json.loads(
        DEPENDENCIES["emitter_physical_q2_payload"].read_text()
    )
    return [
        _typed_q2_fixture(maxwell, 56, 3, [0, 0, 0, 0], 55, [0, 1, 0, 0]),
        _typed_q2_fixture(maxwell, 52, 55, [0, 1, 0, 0], 60, [0, 0, 0, 0]),
        _observer_q2_fixture(
            emitter_diff,
            "emitter_temporal_Diff_BV",
            84,
            3,
            [0, 0, 0, 0],
            84,
            [1, 0, 0, 0],
        ),
        _observer_q2_fixture(
            emitter_diff,
            "emitter_temporal_Diff_BV",
            52,
            84,
            [0, 0, 0, 0],
            96,
            [1, 0, 0, 0],
        ),
        _observer_q2_fixture(
            emitter_physical,
            "emitter_physical_clock_switch",
            38,
            55,
            [0, 1, 0, 0],
            84,
            [0, 0, 0, 0],
        ),
    ]


def persistent_witness_audit() -> dict[str, Any]:
    """Recompute the first source-isolated witness and compare the prior gate."""

    q1 = _q1_source_parts()["emitter"]
    q2 = arity.load_q2(sources={"emitter_Diff_BV"})
    row = arity.arity_two_row(52, (0, 0), q1, q2, arity.parities())
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    coefficient = specialized.get(PRIOR_WITNESS_KEY)
    if not coefficient:
        raise AssertionError("the temporal source-isolated witness disappeared")

    prior = json.loads(DEPENDENCIES["prior_obstruction"].read_text())
    prior_witness = prior["arity_two_replay"]["first_lexicographic_defect"]
    current = {
        "output_row": 52,
        "output_row_id": "tau_star",
        "left_input_row": 55,
        "left_input_row_id": "A_0",
        "left_pbw_multiindex": [1, 1, 0, 0],
        "right_input_row": 84,
        "right_input_row_id": "K0_01",
        "right_pbw_multiindex": [0, 0, 0, 0],
        "coefficient": serialize(coefficient),
    }
    comparable_keys = (
        "output_row",
        "output_row_id",
        "left_input_row",
        "left_input_row_id",
        "left_pbw_multiindex",
        "right_input_row",
        "right_input_row_id",
        "right_pbw_multiindex",
        "coefficient",
    )
    return {
        "recomputed_source_pair": {
            "q1_source": "emitter",
            "q2_source": "emitter_Diff_BV",
        },
        "current": current,
        "prior_result_id": prior["result_id"],
        "prior_complete_defect_summary": prior["arity_two_replay"][
            "complete_defect_summary"
        ],
        "identical_to_prior_first_witness": all(
            current[key] == prior_witness[key] for key in comparable_keys
        ),
        "common_action_export_disposition": (
            "PERSISTENT_NONZERO_WITNESS: no common nondegenerate raising "
            "pairing exists on the present carrier"
        ),
    }


def action_equivalent_maxwell_presentation_mutation() -> dict[str, Any]:
    """Check that q2_typed -> S q2_typed does not remove the first witness."""

    sources = {
        "base_gravity_clock",
        "base_maxwell_typed",
        "apparatus_scalar_BV",
        "dressed_rod_clock",
        "rod_metric",
        "memory_transport",
        "normalized_readout",
        "emitter_physical",
        "emitter_Diff_BV",
    }
    q2 = arity.load_q2(sources=sources - {"base_maxwell_typed"})
    maxwell = arity.load_q2(sources={"base_maxwell_typed"})
    for degree, rows in maxwell.items():
        for output, row in rows.items():
            factor = (
                (Fraction(2), Fraction(0))
                if output >= 54
                else replay.ONE_SCALAR
            )
            destination = q2.setdefault(degree, {}).setdefault(output, {})
            for key, coefficient in row.items():
                arity.add_bilinear_term(
                    destination, key, replay.scale(coefficient, factor)
                )
    row = arity.arity_two_row(
        52, (0, 0), replay.load_q1(), q2, arity.parities()
    )
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    coefficient = specialized.get(PRIOR_WITNESS_KEY)
    return {
        "name": "replace_q2_typed_by_action_equivalent_S_q2_typed",
        "derivation": (
            "q2_legacy=S q2_typed with S=diag(I_54,2 I_10), exactly as "
            "declared by the imported Maxwell certificate"
        ),
        "not_fitted_to_witness": True,
        "witness_survives": bool(coefficient),
        "witness_coefficient": serialize(coefficient or {}),
        "interpretation": (
            "changing only the action-equivalent Maxwell presentation does "
            "not repair the temporal Maxwell-emitter Ward witness"
        ),
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    component = values["component_contract"]
    if component["carrier_contract"]["component_conventions"]["cotangents"] != (
        "density-valued dual rows use the displayed signed odd pairing with "
        "no hidden factorial rescaling"
    ):
        raise AssertionError("108-row no-hidden-rescaling convention drifted")
    expected_pairing = {
        (3, 52): "1",
        (55, 59): "-1",
        (84, 96): "1",
    }
    for pair, coefficient in expected_pairing.items():
        entry = _pairing_entry(component, *pair)
        if entry[2] != [[[0, 0, 0, 0], coefficient]]:
            raise AssertionError(f"canonical pairing fixture drifted: {pair}")

    typed = values["typed_maxwell_q2_q3"]["typed_cyclic_presentation"]
    if typed["scale_operator"] != "S=diag(I_54,2 I_10)":
        raise AssertionError("typed Maxwell factor-two scale drifted")
    if typed["pairing"] != "Omega_typed=Omega_legacy S":
        raise AssertionError("typed Maxwell pairing bridge drifted")
    physical = values["emitter_physical_q2"]["action_and_cyclicity_audit"]
    if physical["q1_hessian_recovery"]["q1_hessian_recovery_defect_count"]:
        raise AssertionError("emitter q1 Hessian recovery is no longer exact")
    diff = values["emitter_diff_q2"]["action_and_cyclicity_audit"]
    if diff["spatial_momentum_map_Hamiltonian_bridge"][
        "relational_temporal_row_scaled"
    ]:
        raise AssertionError("the temporal emitter-Diff row unexpectedly changed scale")


def payload_document() -> dict[str, Any]:
    normalization = normalization_audit()
    if (
        normalization["determinant"] != -1
        or normalization["rank"] != 3
        or normalization["nondegenerate_common_action_pairing_exists"]
    ):
        raise AssertionError("common-action scale obstruction drifted")
    mutation = mutation_audit()
    if not mutation["detected"]:
        raise AssertionError("factor-two mutation was not detected")
    witness = persistent_witness_audit()
    presentation = action_equivalent_maxwell_presentation_mutation()
    if (
        not witness["identical_to_prior_first_witness"]
        or not presentation["witness_survives"]
    ):
        raise AssertionError("persistent temporal witness comparison failed")
    body = {
        "schema": (
            "closed-universe-berger-108-row-temporal-common-action-ward-"
            "orbit-payload-v1"
        ),
        "result_id": "BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_PAYLOAD",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "declared_common_action": {
            "physical_sector": (
                "S2_emit=sum_b[-1/2<dK_b,dK_b>-m_b^2/2<K_b,K_b>"
                "-g_b<h_b(Theta_bar)K_b,dA>]"
            ),
            "temporal_BV_sector": (
                "S3_tau=<Theta_plus,L_(tau e0)Theta>+"
                "<A_plus,L_(tau e0)A>+sum_b<K_b_plus,L_(tau e0)K_b>"
                "+the gravity/clock cotangent partners"
            ),
            "clock_switch_sector": (
                "S3_switch=-sum_b g_b h_b'(Theta_bar) theta <K_b,dA>"
            ),
            "raising_requirement": (
                "all q1 and q2 slots must be raised from these action "
                "derivatives by one nondegenerate signed odd pairing in the "
                "declared component-preserving row family"
            ),
        },
        "q1_orbit_terms": q1_orbit_terms(),
        "q2_orbit_terms": q2_orbit_terms(),
        "normalization_compatibility": normalization,
        "factor_two_mutation": mutation,
        "action_equivalent_presentation_mutation": presentation,
        "prior_residual_comparison": witness,
        "later_memory_clock_rows": {
            "status": "NOT_EVALUATED_AFTER_FIRST_PERSISTENT_NONZERO_WITNESS",
            "reason": (
                "the declared stop condition is already met at output row 52; "
                "no zero identity or downstream pass is inferred for rows 80--83"
            ),
        },
    }
    body["canonical_sha256"] = canonical_sha256(body)
    return body


def build(
    *,
    payload: dict[str, Any] | None = None,
    payload_file_sha256: str | None = None,
) -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    _validate_dependencies(values)
    payload = payload or payload_document()
    normalization = payload["normalization_compatibility"]
    witness = payload["prior_residual_comparison"]
    claim_boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction re-exports the "
        "temporal gravity-clock-Maxwell-emitter q1/q2 Ward orbit as action "
        "derivatives together with the pairing scales required to raise every "
        "slot. The imported nonlinear typed Maxwell presentation explicitly "
        "uses Omega_typed=Omega_legacy diag(I_54,2 I_10), whereas the canonical "
        "108-row component contract declares unit-magnitude Maxwell, emitter "
        "and temporal pairings with no hidden factorial rescaling. The switched "
        "A--K emitter Hessian was independently recovered from one physical "
        "action under that canonical pairing, and the temporal K-plus L_tau K "
        "orbit likewise uses the canonical emitter/temporal pairing. These "
        "three common-action requirements give the exact scale equations "
        "s_Maxwell-2 s_tau=0, s_Maxwell-s_emitter=0 and "
        "s_emitter-s_tau=0. Their 3 by 3 determinant is -1, so only the zero "
        "scale vector solves them; a nondegenerate common raising pairing does "
        "not exist in the declared component-preserving family on the present "
        "frozen carrier. This is therefore a genuine "
        "carrier-normalization incompatibility, not a missing source-labelled "
        "q2 term and not permission to fit a cancellation. Replacing the "
        "imported factor two by one is a mutation only: it makes the matrix "
        "singular with null vector (1,1,1), thereby detecting the obstructing "
        "datum. Independently replacing q2_typed by its action-equivalent "
        "legacy presentation S q2_typed leaves the exact first PBW witness "
        "unchanged. A fresh source-pair replay reproduces tau_star on "
        "(e0 e1 A_0,K0_01) with coefficient +g0 h0, identical to the prior "
        "certified obstruction. The typed 64-row base and the separate linear "
        "detector/emitter results retain their own scopes, but their assembly "
        "with the completed 108-row unary is not a Hamiltonian L-infinity "
        "coderivation under one present-carrier pairing. Later memory/clock "
        "rows are recorded as not evaluated after the first persistent "
        "falsifier, never as passed. No q3 replay, K_Berger equivariance, "
        "observer-morphism stability, detector restriction to Z2, nonlinear "
        "rank, physical-branch bridge, finite-parameter causal, Lorentzian "
        "quantum or QME claim is established. No compact-product mode is "
        "identified with a Berger row."
    )
    return {
        "schema": (
            "closed-universe-berger-108-row-temporal-common-action-ward-"
            "orbit-obstruction-v1"
        ),
        "result_id": "BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": (
            "OBSTRUCTED_COMMON_ACTION_TEMPORAL_WARD_ORBIT_ON_PRESENT_108_ROW_CARRIER"
        ),
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name].get(
                    "result_id", path.stem
                ),
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": payload_file_sha256 or (sha256(PAYLOAD) if PAYLOAD.exists() else ""),
            "canonical_sha256": payload["canonical_sha256"],
        },
        "common_action_export": {
            "q1_term_count": len(payload["q1_orbit_terms"]),
            "q2_term_count": len(payload["q2_orbit_terms"]),
            "scale_constraint_count": len(normalization["constraints"]),
            "constraint_matrix": normalization["matrix"],
            "constraint_determinant": normalization["determinant"],
            "constraint_rank": normalization["rank"],
            "nondegenerate_common_action_pairing_exists": normalization[
                "nondegenerate_common_action_pairing_exists"
            ],
            "disposition": "NO_CERTIFIED_MAP",
        },
        "persistent_witness": witness,
        "mutation_results": {
            "factor_two": payload["factor_two_mutation"],
            "action_equivalent_Maxwell_presentation": payload[
                "action_equivalent_presentation_mutation"
            ],
        },
        "activation_disposition": {
            "corrected_arity_two_identity": False,
            "common_action_carrier_obstruction_certified": True,
            "arity_three_replay_authorized": False,
            "K_Berger_equivariance_authorized": False,
            "observer_morphism_stability_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "nonlinear_response_rank_authorized": False,
            "physical_branch_bridge_activated": False,
            "quantum_promotion_authorized": False,
        },
        "flags": {
            "TEMPORAL_COMMON_ACTION_Q1_Q2_ORBIT_EXPORTED": True,
            "PRESENT_108_ROW_COMMON_ACTION_PAIRING_EXISTS": False,
            "TEMPORAL_COMMON_ACTION_CARRIER_OBSTRUCTION": True,
            "PERSISTENT_ARITY_TWO_WITNESS_REPRODUCED": True,
            "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "FIND_A_MINIMAL_TYPED_CARRIER_OR_ACTION_NORMALIZATION_REPAIR_THEN_"
            "REGENERATE_Q1_Q2_FROM_ONE_PAIRING"
        ),
        "claim_boundary": claim_boundary,
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-common-action-ward-orbit"
            ),
            "input_commit": "3d0ed702a78db160ec8f80ab0efa53dd2dbe2d0b",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    witness = value["persistent_witness"]["current"]
    matrix = value["common_action_export"]["constraint_matrix"]
    return f"""# Temporal common-action Ward-orbit obstruction

## Result

The temporal gravity-clock-Maxwell-emitter orbit cannot be raised from one
declared action in the component-preserving pairing family of the present
canonical 108-row carrier.  The exact pairing scale constraints, in the order
`(s_Maxwell,s_emitter,s_tau)`, are

```text
{matrix[0]}
{matrix[1]}
{matrix[2]}
```

Their determinant is `-1` and their rank is `3`.  Thus their only common
solution is the degenerate zero scale vector.  The typed Maxwell block requires
`s_Maxwell=2 s_tau`; the switched emitter Hessian requires
`s_Maxwell=s_emitter`; and the temporal emitter Diff--BV vertex requires
`s_emitter=s_tau`.

This is a carrier-normalization incompatibility, not a missing PBW source.
The canonical 108-row carrier has unit-magnitude Maxwell, emitter and temporal
pairing entries with no hidden rescaling, while the imported typed Maxwell
presentation places a factor two in the Maxwell fibre pairing.

## Persistent coefficient

An independent source-pair replay reproduces

```text
{witness['output_row_id']} <- (e0 e1 {witness['left_input_row_id']},
{witness['right_input_row_id']})    coefficient +g0 h0.
```

It is identical to the first witness in
`BERGER_108_ROW_ARITY_TWO_OBSTRUCTION`.  Replacing the typed Maxwell binary
operation by the action-equivalent legacy presentation `S q2_typed` leaves
this coefficient unchanged.

## Mutation and boundary

Changing the imported Maxwell factor two to one makes the constraint matrix
singular with null vector `(1,1,1)`.  That is a mutation-sensitive diagnostic,
not an authorized repair.  Off-diagonal field mixing would likewise change
the declared row carrier rather than repair its fixed pairing.  A repair must
change and re-certify the carrier or regenerate the coupled unary and binary
operations from one pairing.

The first persistent falsifier stops the calculation before later memory
rows; they are not marked as passed.  Arity three, `K_Berger`, observer
morphisms, detector response on the second-order cone, nonlinear rank,
physical Bridge 3 and every quantum promotion remain fail-closed.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION.json`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = payload_document()
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    rendered_payload = (
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    )
    payload_file_sha256 = hashlib.sha256(rendered_payload.encode()).hexdigest()
    value = build(payload=payload, payload_file_sha256=payload_file_sha256)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    rendered_report = report(value)

    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check:
        if (
            not PAYLOAD.exists()
            or PAYLOAD.read_text() != rendered_payload
            or not CERTIFICATE.exists()
            or CERTIFICATE.read_text() != rendered
            or not REPORT.exists()
            or REPORT.read_text() != rendered_report
        ):
            raise SystemExit("stale temporal common-action Ward-orbit artifact")
    print("BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

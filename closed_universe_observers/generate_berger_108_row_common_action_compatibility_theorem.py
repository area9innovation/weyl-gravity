#!/usr/bin/env python3
"""Certify the invariant Ward-normalization triangle and its minimal repairs."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-108-row-common-action-compatibility-theorem-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-108-row-common-action-compatibility-theorem.md"
)
DEPENDENCIES = {
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "typed_pairing": ROOT
    / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json",
    "typed_maxwell_q3": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "emitter_physical_q2": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json",
    "emitter_diff_q2": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
    "emitter_physical_payload": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW_PAYLOAD.json",
    "emitter_diff_payload": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD.json",
    "ward_payload": PACKAGE
    / "certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_PAYLOAD.json",
    "ward_obstruction": PACKAGE
    / "certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION.json",
    "arity_two_obstruction": PACKAGE
    / "certificates/BERGER_108_ROW_ARITY_TWO_OBSTRUCTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_108_row_common_action_compatibility_theorem.py",
    PACKAGE / "tests/test_berger_108_row_common_action_compatibility_theorem.py",
    SCHEMA,
]
SCALE_ORDER = ("s_Maxwell", "s_emitter", "s_tau")
EDGE_ORDER = ("Maxwell_tau", "Maxwell_emitter", "emitter_tau")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def determinant3(matrix: list[list[int]]) -> int:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def rref(matrix: list[list[int | Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    work = [[Fraction(value) for value in row] for row in matrix]
    pivots: list[int] = []
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
        work[pivot_row] = [entry / divisor for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work, pivots


def rank(matrix: list[list[int | Fraction]]) -> int:
    return len(rref(matrix)[1])


def primitive_null_vector(matrix: list[list[int | Fraction]]) -> list[int]:
    reduced, pivots = rref(matrix)
    columns = len(matrix[0])
    free = [column for column in range(columns) if column not in pivots]
    if len(free) != 1:
        raise AssertionError(f"expected nullity one, found {len(free)}")
    vector = [Fraction(0) for _ in range(columns)]
    vector[free[0]] = Fraction(1)
    for row, pivot in reversed(list(enumerate(pivots))):
        vector[pivot] = -sum(
            reduced[row][column] * vector[column]
            for column in range(pivot + 1, columns)
        )
    common = 1
    for value in vector:
        common = common * value.denominator // _gcd(common, value.denominator)
    integers = [int(value * common) for value in vector]
    divisor = 0
    for value in integers:
        divisor = _gcd(divisor, abs(value))
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    return integers if first > 0 else [-value for value in integers]


def _gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return abs(left)


def compatibility_matrix(a: int, b: int, c: int) -> list[list[int]]:
    """Return equations s_M=a s_T, s_M=b s_E, s_E=c s_T."""

    return [[1, 0, -a], [1, -b, 0], [0, 1, -c]]


def _pairing_magnitude(document: dict[str, Any], left: int, right: int) -> int:
    matches = [
        entry
        for entry in document["carrier_contract"]["pairing_entries"]
        if entry[0] == left and entry[1] == right
    ]
    if len(matches) != 1:
        raise AssertionError(f"pairing entry ({left},{right}) is not unique")
    coefficients = matches[0][2]
    if len(coefficients) != 1 or coefficients[0][0] != [0, 0, 0, 0]:
        raise AssertionError("the selected pairing is not a constant monomial")
    return abs(int(coefficients[0][1]))


def derive_ward_data(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Derive the three ratios from action and pairing inputs, not their verdict."""

    component = values["component_contract"]
    typed_pairing = values["typed_pairing"]
    typed_maxwell = values["typed_maxwell_q3"]
    physical = values["emitter_physical_q2"]
    diff = values["emitter_diff_q2"]
    physical_payload = values["emitter_physical_payload"]
    diff_payload = values["emitter_diff_payload"]

    tau_weight = _pairing_magnitude(component, 3, 52)
    maxwell_weight = _pairing_magnitude(component, 55, 59)
    emitter_weight = _pairing_magnitude(component, 84, 96)
    typed_weight = typed_pairing["normalization"]["Maxwell_pairing_weight"]
    if (tau_weight, maxwell_weight, emitter_weight) != (1, 1, 1):
        raise AssertionError("canonical component pairing weights drifted")
    if typed_weight != 2:
        raise AssertionError("typed Maxwell pairing weight drifted")
    typed = typed_maxwell["typed_cyclic_presentation"]
    if not (
        typed["lowered_tensor_identity"]
        == "Omega_typed q2_typed=Omega_legacy q2_legacy"
        and typed_pairing["normalization"]["lowered_q2_tensor_preserved"]
    ):
        raise AssertionError("typed lowered-action identity is not certified")
    if physical["action_and_cyclicity_audit"]["q1_hessian_recovery"][
        "q1_hessian_recovery_defect_count"
    ]:
        raise AssertionError("physical emitter Hessian no longer closes")
    if "one component action" not in physical["action_and_cyclicity_audit"][
        "cyclicity_generation"
    ]:
        raise AssertionError("physical emitter source is not one-action generated")
    if "three exact variational slots" not in diff["action_and_cyclicity_audit"][
        "cyclicity_generation"
    ]:
        raise AssertionError("emitter Diff source is not one-vertex generated")
    if not physical_payload["source_action"].startswith(
        "sum_b[-1/2<dK_b,dK_b>"
    ):
        raise AssertionError("physical emitter action declaration drifted")
    if diff_payload["source_action"] != "integral sum_b <K_b_plus,L_c K_b>":
        raise AssertionError("temporal emitter action declaration drifted")

    a = typed_weight * tau_weight // maxwell_weight
    b = maxwell_weight // emitter_weight
    c = emitter_weight // tau_weight
    matrix = compatibility_matrix(a, b, c)
    return {
        "scale_order": list(SCALE_ORDER),
        "edge_order": list(EDGE_ORDER),
        "action_inputs": {
            "typed_lowered_tensor": typed["lowered_tensor_identity"],
            "physical_emitter_action": physical_payload["source_action"],
            "temporal_emitter_action": diff_payload["source_action"],
        },
        "pairing_inputs": {
            "canonical_tau_weight": tau_weight,
            "canonical_Maxwell_weight": maxwell_weight,
            "canonical_emitter_weight": emitter_weight,
            "typed_Maxwell_weight": typed_weight,
        },
        "edges": [
            {
                "id": EDGE_ORDER[0],
                "ratio": a,
                "equation": f"s_Maxwell={a} s_tau",
                "derivation": (
                    "the typed Maxwell lowered action uses weight "
                    f"{typed_weight}, while the shared tau component has "
                    f"canonical weight {tau_weight}"
                ),
            },
            {
                "id": EDGE_ORDER[1],
                "ratio": b,
                "equation": f"s_Maxwell={b} s_emitter",
                "derivation": (
                    "the A--K quadratic Hessian is recovered from one physical "
                    "emitter action and both canonical component weights are one"
                ),
            },
            {
                "id": EDGE_ORDER[2],
                "ratio": c,
                "equation": f"s_emitter={c} s_tau",
                "derivation": (
                    "K_plus, K and tau are the three variations of the single "
                    "vertex integral <K_plus,L_(tau e0)K>"
                ),
            },
        ],
        "ratios": {"a_Maxwell_tau": a, "b_Maxwell_emitter": b, "c_emitter_tau": c},
        "matrix": matrix,
        "determinant": determinant3(matrix),
        "rank": rank(matrix),
        "nullity": 3 - rank(matrix),
    }


def action_normalization_repairs(a: int, b: int, c: int) -> list[dict[str, Any]]:
    replacements = [
        ("Maxwell_tau", (b * c, b, c)),
        ("Maxwell_emitter", (a, a // c, c)),
        ("emitter_tau", (a, b, a // b)),
    ]
    repairs = []
    for edge, ratios in replacements:
        matrix = compatibility_matrix(*ratios)
        repairs.append(
            {
                "changed_edge": edge,
                "ratios": list(ratios),
                "matrix": matrix,
                "determinant": determinant3(matrix),
                "rank": rank(matrix),
                "null_vector": primitive_null_vector(matrix),
                "lifecycle": "NECESSARY_CONDITION_ONLY",
                "original_q1_q2_substitution": "NOT_RUN_REQUIRES_ACTION_REGENERATION",
                "atlas_status": "NO_CERTIFIED_MAP",
            }
        )
    return repairs


def orbit_local_slack_classification(matrix: list[list[int]]) -> list[dict[str, Any]]:
    classes = []
    for index, edge in enumerate(EDGE_ORDER):
        extended = [row + [1 if row_index == index else 0] for row_index, row in enumerate(matrix)]
        vector = primitive_null_vector(extended)
        classes.append(
            {
                "supported_orbit": edge,
                "extended_matrix": extended,
                "rank": rank(extended),
                "null_vector_scale_and_slack": vector,
                "all_original_scales_nonzero": all(vector[index] for index in range(3)),
                "lifecycle": "ALGEBRAIC_EXTENSION_CLASS_ONLY",
                "action_regenerated": False,
                "original_q1_q2_substitution": "NOT_AUTHORIZED",
                "atlas_status": "NO_CERTIFIED_MAP",
            }
        )
    return classes


def dropped_orbit_controls(matrix: list[list[int]]) -> list[dict[str, Any]]:
    controls = []
    for index, edge in enumerate(EDGE_ORDER):
        reduced = [row for row_index, row in enumerate(matrix) if row_index != index]
        controls.append(
            {
                "dropped_orbit": edge,
                "matrix": reduced,
                "rank": rank(reduced),
                "null_vector": primitive_null_vector(reduced),
                "detected": rank(reduced) == 2,
            }
        )
    return controls


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    ward = derive_ward_data(values)
    a = ward["ratios"]["a_Maxwell_tau"]
    b = ward["ratios"]["b_Maxwell_emitter"]
    c = ward["ratios"]["c_emitter_tau"]
    matrix = ward["matrix"]
    repairs = action_normalization_repairs(a, b, c)
    slack = orbit_local_slack_classification(matrix)
    dropped = dropped_orbit_controls(matrix)
    old_payload = values["ward_payload"]
    old_obstruction = values["ward_obstruction"]
    arity = values["arity_two_obstruction"]["arity_two_replay"]
    witness = arity["first_lexicographic_defect"]

    if matrix != old_payload["normalization_compatibility"]["matrix"]:
        raise AssertionError("action-derived and prior compatibility matrices disagree")
    if ward["determinant"] != -1 or ward["rank"] != 3:
        raise AssertionError("frozen compatibility obstruction drifted")
    if repairs[0]["null_vector"] != [1, 1, 1]:
        raise AssertionError("factor-two mutation control drifted")
    if not all(control["detected"] for control in dropped):
        raise AssertionError("dropped-orbit controls did not expose rank two")
    if not old_payload["action_equivalent_presentation_mutation"]["witness_survives"]:
        raise AssertionError("presentation-invariance witness disappeared")

    theorem = {
        "schema": "closed-universe-berger-108-row-common-action-compatibility-theorem-v1",
        "result_id": "BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_INVARIANT_WARD_COMPATIBILITY_AND_MINIMAL_EXTENSION_NO_GO",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name].get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "ward_derivation": ward,
        "compatibility_theorem": {
            "general_matrix": [
                ["1", "0", "-a"],
                ["1", "-b", "0"],
                ["0", "1", "-c"],
            ],
            "determinant_polynomial": "b*c-a",
            "nonzero_solution_iff": "a=b*c",
            "cycle_holonomy": "H=a/(b*c)",
            "compatibility_iff": "H=1",
            "frozen_holonomy": "2",
            "proof": (
                "Successive substitution gives s_Maxwell=b*c*s_tau and "
                "s_Maxwell=a*s_tau. For a nonzero pairing scale s_tau, these "
                "are compatible exactly when a=b*c. Direct expansion gives "
                "det A=b*c-a, so failure of the cycle condition is equivalent "
                "to full rank."
            ),
        },
        "invariance_theorem": {
            "field_rescaling": {
                "rescaling": "(r_M,r_E,r_T) in (Q^x)^3",
                "edge_transform": [
                    "a'=(r_M/r_T)*a",
                    "b'=(r_M/r_E)*b",
                    "c'=(r_E/r_T)*c",
                ],
                "holonomy_identity": "a'/(b'*c')=a/(b*c)",
                "matrix_equivalence": "A'=L*A*D^{-1} for invertible diagonal L,D",
                "rank_invariant": True,
            },
            "action_equivalent_presentation": {
                "equivalence_level": "L6_ADMISSIBLE_FIELD_OR_BASIS_REDEFINITION",
                "lowered_tensor_identity": values["typed_maxwell_q3"][
                    "typed_cyclic_presentation"
                ]["lowered_tensor_identity"],
                "persistent_witness_survives": old_payload[
                    "action_equivalent_presentation_mutation"
                ]["witness_survives"],
                "witness_coefficient": old_payload[
                    "action_equivalent_presentation_mutation"
                ]["witness_coefficient"],
            },
        },
        "bounded_minimal_extension_ansatz": {
            "definition": {
                "coefficient_field": "Q",
                "base_ratios": [a, b, c],
                "allowed_action_change": "change exactly one of the three nonzero edge ratios",
                "allowed_equation_slack": "one new scalar supported on exactly one Ward orbit",
                "allowed_carrier_growth": "at most one new row for the first no-go; one conjugate two-row pair is the next open class",
                "off_diagonal_scope": "one orbit-local block only; component-preserving frozen family itself permits none",
                "completeness": (
                    "There are exactly three edges and exactly three support-one "
                    "slack columns, so the declared bounded families are exhausted."
                ),
            },
            "one_edge_action_normalizations": repairs,
            "one_orbit_slack_classes": slack,
            "present_carrier_off_diagonal_pairing": {
                "status": "OBSTRUCTED_IN_DECLARED_COMPONENT_PRESERVING_FAMILY",
                "reason": (
                    "a nonzero off-diagonal sector block changes the certified "
                    "108-row pairing family and therefore is not a repair inside it"
                ),
                "outside_family_status": "NO_CERTIFIED_MAP",
            },
            "one_row_carrier_enlargement": {
                "target_dimension": 109,
                "status": "OBSTRUCTED",
                "proof": (
                    "For an antisymmetric 109 by 109 matrix Omega over Q, "
                    "det(Omega)=det(Omega^T)=det(-Omega)=(-1)^109 det(Omega), "
                    "hence det(Omega)=0. A one-row extension cannot carry a "
                    "nondegenerate odd pairing."
                ),
            },
            "first_dimension_not_excluded": {
                "target_dimension": 110,
                "new_rows": "one complementary-degree conjugate pair",
                "status": "OPEN",
                "requirements": [
                    "declare the Berger representation and degree of both rows",
                    "derive the enlarged pairing and q1/q2 from one action",
                    "prove nondegeneracy and cyclicity",
                    "substitute independently into the original q1/q2 verifier",
                ],
                "atlas_status": "NO_CERTIFIED_MAP",
            },
            "surviving_physics_candidates": [],
            "candidate_boundary": (
                "The six displayed algebraic loci are necessary-condition "
                "classes, not surviving physics candidates. None is promoted "
                "without a new action-derived carrier and original-verifier replay."
            ),
        },
        "counterexample_strategy": {
            "factor_two_mutation": {
                "matrix": repairs[0]["matrix"],
                "rank": repairs[0]["rank"],
                "null_vector": repairs[0]["null_vector"],
                "scientific_status": "MUTATION_ONLY_NOT_A_REPAIR",
            },
            "dropped_orbit_controls": dropped,
            "persistent_original_q1_q2_witness": {
                "output_row": witness["output_row"],
                "output_row_id": witness["output_row_id"],
                "left_input_row": witness["left_input_row"],
                "left_input_row_id": witness["left_input_row_id"],
                "left_pbw_multiindex": witness["left_pbw_multiindex"],
                "right_input_row": witness["right_input_row"],
                "right_input_row_id": witness["right_input_row_id"],
                "right_pbw_multiindex": witness["right_pbw_multiindex"],
                "coefficient": witness["coefficient"],
                "nonzero": True,
                "identical_to_prior_common_action_export": old_obstruction[
                    "persistent_witness"
                ]["identical_to_prior_first_witness"],
            },
        },
        "proof_obligation_dag": [
            {
                "id": "P1_ACTION_DERIVATION",
                "depends_on": [],
                "status": "CERTIFIED",
                "evidence": ["ward_derivation.action_inputs", "ward_derivation.pairing_inputs"],
            },
            {
                "id": "P2_GENERAL_TRIANGLE_THEOREM",
                "depends_on": ["P1_ACTION_DERIVATION"],
                "status": "CERTIFIED",
                "evidence": ["compatibility_theorem"],
            },
            {
                "id": "P3_RESCALE_PRESENTATION_INVARIANCE",
                "depends_on": ["P2_GENERAL_TRIANGLE_THEOREM"],
                "status": "CERTIFIED",
                "evidence": ["invariance_theorem"],
            },
            {
                "id": "P4_BOUNDED_MINIMAL_CLASSIFICATION",
                "depends_on": ["P2_GENERAL_TRIANGLE_THEOREM"],
                "status": "CERTIFIED",
                "evidence": ["bounded_minimal_extension_ansatz"],
            },
            {
                "id": "P5_ACTION_REGENERATION_AND_Q1_Q2_SUBSTITUTION",
                "depends_on": ["P4_BOUNDED_MINIMAL_CLASSIFICATION"],
                "status": "NO_CERTIFIED_MAP",
                "evidence": ["counterexample_strategy.persistent_original_q1_q2_witness"],
            },
            {
                "id": "P6_CONFLUX_PREFLIGHT_AND_EXPLORATION",
                "depends_on": ["P4_BOUNDED_MINIMAL_CLASSIFICATION"],
                "status": "OPEN_TYPED_FORGE_REQUEST",
                "evidence": [
                    "planning/forge-requests/conflux-observer-common-action-compatibility.json"
                ],
            },
        ],
        "activation_disposition": {
            "compatibility_theorem_certified": True,
            "present_108_row_common_action_pairing_exists": False,
            "one_row_carrier_repair_exists": False,
            "action_regenerated_candidate_exists": False,
            "original_q1_q2_substitution_passed": False,
            "conflux_preflight_authorized": False,
            "conflux_exploration_authorized": False,
            "q3_authorized": False,
            "detector_or_cone_promotion_authorized": False,
            "quantum_promotion_authorized": False,
        },
        "next_gate": (
            "LAND_THE_TYPED_CONFLUX_CONSUMER_OR_DECLARE_A_110_ROW_ACTION_"
            "EXTENSION_THEN_REGENERATE_AND_SUBSTITUTE_Q1_Q2"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem derives the three "
            "temporal Ward normalization equations from the certified typed "
            "Maxwell lowered tensor, the physical A--K action Hessian, the "
            "single K-plus L_c K vertex, and the canonical component pairing "
            "entries. It proves the general cycle criterion a=b*c, identifies "
            "the frozen holonomy H=2, and proves that nonzero field rescalings "
            "and the imported action-equivalent Maxwell presentation preserve "
            "that holonomy and the full-rank obstruction. It exhausts the "
            "declared one-edge normalization and support-one slack families "
            "and proves that a one-row carrier enlargement is necessarily "
            "degenerate. The resulting algebraic loci are necessary conditions "
            "only. No changed action, off-diagonal Berger representation, or "
            "110-row conjugate pair has been declared; no candidate q1/q2 was "
            "regenerated; and the original verifier still carries the nonzero "
            "tau_star witness. Conflux was not run because the observer-specific "
            "typed importer request remains unlanded. This certificate does not "
            "establish q3 closure, K_Berger equivariance, observer-morphism "
            "stability, detector response, response rank on the second-order "
            "cone, causal propagation, a physical branch, particles, or any "
            "quantum statement. No compact-product mode is identified with a "
            "Berger carrier row."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-common-action-compatibility-theorem"
            ),
            "input_commit": "7c537ecb8c423bcce3fbcf797262c6b557822b27",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }
    return theorem


def report(value: dict[str, Any]) -> str:
    repairs = value["bounded_minimal_extension_ansatz"][
        "one_edge_action_normalizations"
    ]
    dropped = value["counterexample_strategy"]["dropped_orbit_controls"]
    return f"""# Invariant common-action Ward compatibility theorem

## Theorem

Let `(a,b,c)` be the nonzero normalization ratios in

```text
s_Maxwell = a s_tau
s_Maxwell = b s_emitter
s_emitter = c s_tau.
```

For the declared component-preserving pairing family, a nonzero common raising
pairing exists exactly when `a=b*c`.  Equivalently, the cycle holonomy
`H=a/(b*c)` must equal one.  The compatibility matrix has determinant `b*c-a`.

The frozen Berger data are derived from the declared actions and pairings:
the typed Maxwell lowered tensor supplies `a=2`, the switched physical
Maxwell--emitter Hessian supplies `b=1`, and the three variational slots of
`integral <K_plus,L_(tau e0)K>` supply `c=1`.  Thus `H=2`, the determinant is
`-1`, and the matrix has rank three.  No nondegenerate common raising pairing
exists on the present 108-row carrier.

## Invariance

Under nonzero field rescalings `(r_M,r_E,r_T)`, the ratios transform as

```text
a'=(r_M/r_T)a,  b'=(r_M/r_E)b,  c'=(r_E/r_T)c.
```

Therefore `a'/(b'c')=a/(bc)`.  Equivalently the compatibility matrix changes
by invertible diagonal row and column operations, so its rank is invariant.
The imported action-equivalent Maxwell presentation preserves the same lowered
tensor and the independently replayed `tau_star` witness.

## Complete bounded minimal classification

Changing exactly one edge reaches the compatibility locus at:

| changed edge | ratios `(a,b,c)` | null line |
| --- | --- | --- |
| Maxwell--tau | `{tuple(repairs[0]['ratios'])}` | `{tuple(repairs[0]['null_vector'])}` |
| Maxwell--emitter | `{tuple(repairs[1]['ratios'])}` | `{tuple(repairs[1]['null_vector'])}` |
| emitter--tau | `{tuple(repairs[2]['ratios'])}` | `{tuple(repairs[2]['null_vector'])}` |

These are necessary-condition loci, not physical repairs.  None has been
regenerated from a changed action or substituted as a new operator into the
original q1/q2 verifier.

The support-one slack family likewise has exactly three algebraic classes, one
per Ward orbit.  Within the frozen component-preserving family an off-diagonal
block is not admissible.  A one-row carrier enlargement is impossible:
every antisymmetric `109 x 109` pairing over `Q` has zero determinant.  The
first dimension not excluded is 110, obtained by adding a complementary-degree
conjugate pair; its Berger representation and action remain open.

Dropping each orbit is a decisive control:

| dropped orbit | exposed null line |
| --- | --- |
| {dropped[0]['dropped_orbit']} | `{tuple(dropped[0]['null_vector'])}` |
| {dropped[1]['dropped_orbit']} | `{tuple(dropped[1]['null_vector'])}` |
| {dropped[2]['dropped_orbit']} | `{tuple(dropped[2]['null_vector'])}` |

The separately recomputed factor-two mutation reaches the first one-edge
normalization locus and restores `(1,1,1)` only as a mutation.  The original
operator still has
`tau_star <- (e0 e1 A_0,K0_01)` with coefficient `+g0 h0`.

## Boundary

The observer-specific Conflux importer is still a typed Forge request, so no
Conflux preflight or candidate exploration was run.  No q3, `K_Berger`,
observer-morphism, detector, second-order-cone, causal, branch, particle, or
quantum claim is promoted.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM.json`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    rendered_report = report(value)
    if args.emit:
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check:
        if (
            not CERTIFICATE.exists()
            or CERTIFICATE.read_text() != rendered
            or not REPORT.exists()
            or REPORT.read_text() != rendered_report
        ):
            raise SystemExit("stale common-action compatibility theorem artifact")
    print("BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

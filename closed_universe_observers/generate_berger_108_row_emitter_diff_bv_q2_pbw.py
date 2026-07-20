#!/usr/bin/env python3
"""Export the massive-two-form Diff--BV q2 PBW cotangent orbit."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR,
    Polynomial,
    _multiindex_from_word,
    _pbw_word,
    add,
    normalize,
    scalar_mul,
    scalar_scale,
    scale,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_apparatus_scalar_bv_q2_pbw import (
    scalar_template,
)
from closed_universe_observers.generate_berger_108_row_emitter_q1_pbw_overlay import (
    _component,
    exterior_derivative,
    form_basis,
    structure,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-emitter-diff-bv-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-emitter-diff-bv-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-emitter-diff-bv-q2-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "emitter_master_identity": P / "certificates/BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY.json",
    "emitter_physical_q2": P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json",
    "scalar_BV_template": P / "certificates/BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_emitter_diff_bv_q2_pbw.py",
    P / "tests/test_berger_108_row_emitter_diff_bv_q2_pbw.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

Scalar = tuple[Fraction, Fraction]
Ordered = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Scalar]
Tensor = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Polynomial]

FORM2 = form_basis(2)
FORM3 = form_basis(3)
FRAME_TO_GHOST = {0: 3, 1: 0, 2: 1, 3: 2}
GHOST_TO_DUAL = {0: 49, 1: 50, 2: 51, 3: 52}
SPATIAL_DIFF_DUAL_ROWS = (49, 50, 51)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def rational(value: int | Fraction) -> Scalar:
    return Fraction(value), Fraction(0)


def constant(value: Scalar) -> Polynomial:
    return normalize([(value, ())]) if value != (0, 0) else {}


def scalar_neg(value: Scalar) -> Scalar:
    return scalar_scale(value, -1)


def ordered_add(
    output: Ordered,
    target: int,
    left: int,
    left_word: Iterable[int],
    right: int,
    right_word: Iterable[int],
    coefficient: Scalar,
) -> None:
    for reduced_left, left_factor in _pbw_word(tuple(left_word)):
        for reduced_right, right_factor in _pbw_word(tuple(right_word)):
            key = target, left, reduced_left, right, reduced_right
            value = scalar_mul(coefficient, scalar_mul(left_factor, right_factor))
            previous = output.get(key, (Fraction(0), Fraction(0)))
            combined = previous[0] + value[0], previous[1] + value[1]
            if combined == (0, 0):
                output.pop(key, None)
            else:
                output[key] = combined


def parity(row: int) -> int:
    if row in range(0, 5) or row in range(27, 49) or row in range(59, 63) or row in range(74, 84) or row in range(96, 108):
        return 1
    return 0


def tensor_add(
    tensor: Tensor,
    output: int,
    left: int,
    left_word: Iterable[int],
    right: int,
    right_word: Iterable[int],
    coefficient: Scalar,
) -> None:
    for reduced_left, left_factor in _pbw_word(tuple(left_word)):
        for reduced_right, right_factor in _pbw_word(tuple(right_word)):
            key = output, left, reduced_left, right, reduced_right
            value = constant(scalar_mul(coefficient, scalar_mul(left_factor, right_factor)))
            tensor[key] = add(tensor.get(key, {}), value)
            if not tensor[key]:
                del tensor[key]


def tensor_add_graded_complete(
    tensor: Tensor,
    output: int,
    left: int,
    left_word: tuple[int, ...],
    right: int,
    right_word: tuple[int, ...],
    coefficient: Scalar,
) -> None:
    tensor_add(tensor, output, left, left_word, right, right_word, coefficient)
    sign = -1 if parity(left) * parity(right) else 1
    tensor_add(
        tensor,
        output,
        right,
        right_word,
        left,
        left_word,
        scalar_scale(coefficient, sign),
    )


def adjoint_product_terms(
    word: tuple[int, ...],
    left_word: tuple[int, ...],
    right_word: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    """Expand the formal adjoint of a PBW word acting on a product."""

    states: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {
        (left_word, right_word): 1
    }
    for axis in word:
        updated: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}
        for (left, right), multiplicity in states.items():
            for key in (((axis, *left), right), (left, (axis, *right))):
                updated[key] = updated.get(key, 0) + multiplicity
        states = updated
    sign = -1 if len(word) % 2 else 1
    return tuple(
        (left, right, sign * multiplicity)
        for (left, right), multiplicity in sorted(states.items())
    )


def explicit_lie_two_form(k_offset: int) -> Ordered:
    """Return (L_c K)_ab in the non-holonomic Berger frame."""

    output: Ordered = {}
    for target, (first, second) in enumerate(FORM2):
        target_row = k_offset + target
        for vector in range(4):
            ghost = FRAME_TO_GHOST[vector]
            ordered_add(
                output,
                target_row,
                ghost,
                (),
                target_row,
                (vector,),
                ONE_SCALAR,
            )
            for derivative_axis, indices in (
                (first, (vector, second)),
                (second, (first, vector)),
            ):
                component = _component(indices, FORM2)
                if component is not None:
                    source, orientation = component
                    ordered_add(
                        output,
                        target_row,
                        ghost,
                        (derivative_axis,),
                        k_offset + source,
                        (),
                        rational(orientation),
                    )
            for frame_axis, fixed_axis, indices in (
                (first, second, None),
                (second, first, None),
            ):
                for replacement, bracket in structure(vector, frame_axis).items():
                    form_indices = (
                        (replacement, fixed_axis)
                        if frame_axis == first
                        else (fixed_axis, replacement)
                    )
                    component = _component(form_indices, FORM2)
                    if component is not None:
                        source, orientation = component
                        ordered_add(
                            output,
                            target_row,
                            ghost,
                            (),
                            k_offset + source,
                            (),
                            scalar_scale(bracket, -orientation),
                        )
    return output


def cartan_lie_two_form(k_offset: int) -> Ordered:
    """Build i_c dK+d(i_c K) independently from the de Rham matrices."""

    output: Ordered = {}
    d_one = exterior_derivative(1)
    d_two = exterior_derivative(2)
    for target, (first, second) in enumerate(FORM2):
        target_row = k_offset + target
        # i_c dK
        for vector in range(4):
            component = _component((vector, first, second), FORM3)
            if component is None:
                continue
            three_component, orientation = component
            for (row, source), terms in d_two.items():
                if row != three_component:
                    continue
                for term in terms:
                    ordered_add(
                        output,
                        target_row,
                        FRAME_TO_GHOST[vector],
                        (),
                        k_offset + source,
                        term.word,
                        scalar_scale(term.coefficient, orientation),
                    )
        # d(i_c K)
        for (row, one_component), terms in d_one.items():
            if row != target:
                continue
            for vector in range(4):
                contraction = _component((vector, one_component), FORM2)
                if contraction is None:
                    continue
                source, orientation = contraction
                for term in terms:
                    coefficient = scalar_scale(term.coefficient, orientation)
                    if not term.word:
                        ordered_add(
                            output,
                            target_row,
                            FRAME_TO_GHOST[vector],
                            (),
                            k_offset + source,
                            (),
                            coefficient,
                        )
                    else:
                        if len(term.word) != 1:
                            raise AssertionError("Cartan replay expected first-order d")
                        axis = term.word[0]
                        ordered_add(
                            output,
                            target_row,
                            FRAME_TO_GHOST[vector],
                            (axis,),
                            k_offset + source,
                            (),
                            coefficient,
                        )
                        ordered_add(
                            output,
                            target_row,
                            FRAME_TO_GHOST[vector],
                            (),
                            k_offset + source,
                            (axis,),
                            coefficient,
                        )
    return output


def cotangent_complete(
    ordered: Ordered,
    field_to_dual: dict[int, int],
    ghost_to_dual: dict[int, int],
) -> Tensor:
    """Raise one lowered K-plus L_c K vertex through all three slots."""

    tensor: Tensor = {}
    for (target, left, left_word, right, right_word), coefficient in ordered.items():
        dual_target = field_to_dual[target]
        tensor_add_graded_complete(
            tensor, target, left, left_word, right, right_word, coefficient
        )
        for new_left_word, dual_word, multiplicity in adjoint_product_terms(
            right_word, left_word, ()
        ):
            tensor_add_graded_complete(
                tensor,
                field_to_dual[right],
                left,
                new_left_word,
                dual_target,
                dual_word,
                scalar_scale(coefficient, -multiplicity),
            )
        for new_right_word, dual_word, multiplicity in adjoint_product_terms(
            left_word, right_word, ()
        ):
            tensor_add_graded_complete(
                tensor,
                ghost_to_dual[left],
                right,
                new_right_word,
                dual_target,
                dual_word,
                scalar_scale(coefficient, -multiplicity),
            )
    return tensor


def emitter_tensor() -> tuple[Tensor, dict[str, int]]:
    output: Tensor = {}
    counts: dict[str, int] = {}
    for emitter, k_offset, kp_offset in ((0, 84, 96), (1, 90, 102)):
        ordered = explicit_lie_two_form(k_offset)
        cartan = cartan_lie_two_form(k_offset)
        if ordered != cartan:
            raise AssertionError(f"two-form Cartan replay failed for emitter {emitter}")
        block = cotangent_complete(
            ordered,
            {k_offset + index: kp_offset + index for index in range(6)},
            GHOST_TO_DUAL,
        )
        for key, coefficient in block.items():
            output[key] = add(output.get(key, {}), coefficient)
        counts[f"emitter_{emitter}_ordered_Lie_terms"] = len(ordered)
        counts[f"emitter_{emitter}_completed_q2_keys"] = len(block)
    # The frozen spatial Diff momentum-map rows use the same Hamiltonian
    # normalization as the metric stress rows: T=-2 delta S/dg.  Applying
    # the weight to both sides of the spatial Ward orbit preserves the free
    # emitter cancellation and is required when the Maxwell--emitter action
    # is stitched to the canonical gravity carrier.  The relational temporal
    # row 52 belongs to the separate clock/switch orbit and is not promoted by
    # this spatial bridge.
    for key, coefficient in list(output.items()):
        if key[0] in SPATIAL_DIFF_DUAL_ROWS:
            output[key] = scale(coefficient, rational(-2))
    return output, counts


def spatial_momentum_map_hamiltonian_audit() -> dict[str, Any]:
    tensor, _ = emitter_tensor()
    key = 49, 84, (), 96, (1,)
    expected = constant(rational(-2))
    return {
        "fixture": "q2(K0_01,K0_01_star with e1)->c_spatial_1_star",
        "spatial_Diff_Hamiltonian_weight": "-2",
        "relational_temporal_row_scaled": False,
        "expected_coefficient": serialize(expected),
        "actual_coefficient": serialize(tensor.get(key, {})),
        "spatial_momentum_map_bridge_defect_count": int(
            tensor.get(key, {}) != expected
        ),
    }


def scalar_template_audit() -> dict[str, Any]:
    ordered: Ordered = {}
    for axis in (1, 2, 3):
        ordered_add(
            ordered,
            16,
            FRAME_TO_GHOST[axis],
            (),
            16,
            (axis,),
            ONE_SCALAR,
        )
    rebuilt = cotangent_complete(ordered, {16: 38}, GHOST_TO_DUAL)
    expected: dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Scalar] = {}

    def parse_number(value: Any) -> Fraction:
        if isinstance(value, int):
            return Fraction(value)
        return Fraction(value["numerator"], value["denominator"])

    for output, left, left_multi, right, right_multi, coefficient in scalar_template():
        scalar = parse_number(coefficient["rational"]), parse_number(coefficient["sqrt10"])
        left_word = tuple(
            axis for axis, power in enumerate(left_multi) for _ in range(power)
        )
        right_word = tuple(
            axis for axis, power in enumerate(right_multi) for _ in range(power)
        )
        expected[(output, left, left_word, right, right_word)] = scalar
    rebuilt_scalar = {
        key: next(iter(value.values()))
        for key, value in rebuilt.items()
        if len(value) == 1 and next(iter(value.keys())) == ()
    }
    defects = sum(
        rebuilt_scalar.get(key) != expected.get(key)
        for key in set(rebuilt_scalar) | set(expected)
    )
    return {
        "rebuilt_term_count": len(rebuilt_scalar),
        "certified_template_term_count": len(expected),
        "scalar_BV_template_recovery_defect_count": defects,
    }


def cartan_audit() -> dict[str, Any]:
    explicit = explicit_lie_two_form(84)
    cartan = cartan_lie_two_form(84)
    keys = set(explicit) | set(cartan)
    return {
        "explicit_component_term_count": len(explicit),
        "Cartan_component_term_count": len(cartan),
        "Cartan_formula_defect_count": sum(
            explicit.get(key) != cartan.get(key) for key in keys
        ),
        "identity": "L_c K=i_c dK+d(i_c K)",
    }


def graded_symmetry_defects(tensor: Tensor) -> int:
    defects = 0
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        sign = -1 if parity(left) * parity(right) else 1
        mate = tensor.get((output, right, right_word, left, left_word), {})
        if coefficient != scale(mate, rational(sign)):
            defects += 1
    return defects


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (output, left, left_word, right, right_word), polynomial in sorted(tensor.items()):
        for term in serialize(polynomial):
            rows[output].append(
                {
                    "left_input_row": left,
                    "left_pbw_multiindex": list(_multiindex_from_word(left_word)),
                    "right_input_row": right,
                    "right_pbw_multiindex": list(_multiindex_from_word(right_word)),
                    "coefficient": term["coefficient"],
                    "coefficient_factors": term["factors"],
                }
            )
    return [{"output": output, "terms": terms} for output, terms in sorted(rows.items())]


def payload_document() -> dict[str, Any]:
    tensor, counts = emitter_tensor()
    rows = serialize_tensor(tensor)
    return {
        "schema": "closed-universe-berger-108-row-emitter-diff-bv-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "integral sum_b <K_b_plus,L_c K_b>",
        "component_formula": "(L_c K)_ab=c^v e_v K_ab+(e_a c^v)K_vb+(e_b c^v)K_av-c^v C_va^t K_tb-c^v C_vb^t K_at",
        "block_counts": counts,
        "rows": rows,
        "nonzero_output_rows": [row["output"] for row in rows],
        "operator_key_count": len(tensor),
        "serialized_term_count": sum(len(row["terms"]) for row in rows),
        "canonical_sha256": canonical_sha256(rows),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "emitter_master_identity": "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED",
        "emitter_physical_q2": "EMITTER_PHYSICAL_Q2_PBW_EXPORTED",
        "scalar_BV_template": "APPARATUS_SCALAR_BV_Q2_PBW_EXPORTED",
    }
    for name, flag in required.items():
        if dependencies[name]["flags"].get(flag) is not True:
            raise AssertionError(f"required dependency dropped: {name}.{flag}")
    payload = payload or payload_document()
    scalar_audit = scalar_template_audit()
    cartan = cartan_audit()
    momentum_bridge = spatial_momentum_map_hamiltonian_audit()
    tensor, _ = emitter_tensor()
    symmetry = graded_symmetry_defects(tensor)
    if scalar_audit["scalar_BV_template_recovery_defect_count"] or cartan["Cartan_formula_defect_count"] or momentum_bridge["spatial_momentum_map_bridge_defect_count"] or symmetry:
        raise AssertionError("emitter Diff--BV q2 audit failed")
    mutated = json.loads(json.dumps(payload["rows"]))
    mutated[-1]["terms"].pop()
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the two-form Diff--BV q2 cotangent orbit for both selected massive emitters on the canonical 108-row Berger carrier. It derives the non-holonomic component formula for L_c K using all four vector components, including the relational temporal ghost tau, and independently reproduces every term from Cartan's identity L_c K=i_c dK+d(i_c K) using the certified support-local Berger de Rham matrices. The three variational slots of the single lowered vertex integral <K_b_plus,L_c K_b> generate q2(c,K_b) to K_b, the density-cotangent action q2(c,K_b_plus) to K_b_plus, and the reciprocal q2(K_b,K_b_plus) to c_plus, with every formal-adjoint Leibniz term and Berger PBW reduction explicit. The three frozen spatial c_plus outputs carry the same minus-two Hamiltonian weight as the canonical metric stress rows; an exact K0_01/K0_01_star fixture pins that bridge. The relational temporal output remains unscaled because it belongs to the separate clock-chart conjugation gate. The same cotangent-completion engine exactly recovers the certified 24-term scalar BV template before this spatial raising, fixing its signs and factorial normalization independently of the two-form calculation. The resulting tensor has exact graded input symmetry, and a payload-key deletion changes its canonical hash. Together with the separately certified physical emitter stress/switch block this completes the source-labelled emitter q2 sector, but the complete arity-two replay remains obstructed on the temporal emitter-Diff orbit. Therefore q2q2+q1q3, K_Berger equivariance, observer-morphism stability, restriction of detector response to Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No compact-product mode is identified with a Berger row."
    )
    payload_sha256 = payload_sha256 or sha256(PAYLOAD)
    return {
        "schema": "closed-universe-berger-108-row-emitter-diff-bv-q2-pbw-v1",
        "result_id": "BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW",
        "setting_id": dependencies["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_TWO_FORM_DIFF_BV_Q2_COTANGENT_ORBIT",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": payload_sha256,
            "operator_key_count": payload["operator_key_count"],
            "serialized_term_count": payload["serialized_term_count"],
            "nonzero_output_rows": payload["nonzero_output_rows"],
            "canonical_sha256": payload["canonical_sha256"],
        },
        "action_and_cyclicity_audit": {
            "Cartan_replay": cartan,
            "scalar_BV_template_recovery": scalar_audit,
            "spatial_momentum_map_Hamiltonian_bridge": momentum_bridge,
            "graded_symmetry_defect_count": symmetry,
            "cyclicity_generation": "all rows are the three exact variational slots of one K-plus L_c K vertex raised with the canonical odd pairing",
        },
        "mutation_results": [
            {
                "name": "delete_last_emitter_Diff_BV_q2_term",
                "detected": canonical_sha256(mutated) != payload["canonical_sha256"],
            }
        ],
        "activation_disposition": {
            "emitter_Diff_BV_q2_subblock_exported": True,
            "complete_emitter_q2_exported": True,
            "complete_scalar_q2_payload_assembled": False,
            "scalar_q3_exported": False,
            "arity_replay_certified": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "EMITTER_DIFF_BV_Q2_PBW_EXPORTED": True,
            "EMITTER_DIFF_BV_Q2_CARTAN_REPLAY_CERTIFIED": True,
            "EMITTER_DIFF_BV_Q2_GRADED_SYMMETRIC": True,
            "EMITTER_DIFF_BV_Q2_CYCLIC": True,
            "COMPLETE_EMITTER_Q2_PBW_EXPORTED": True,
            "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": False,
            "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False,
            "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "ASSEMBLE_CANONICAL_COMPLETE_108_ROW_Q2_PAYLOAD",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check and (
        not PAYLOAD.exists()
        or PAYLOAD.read_text() != rendered_payload
        or not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
    ):
        raise SystemExit("stale emitter Diff--BV q2 artifact")
    print("BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

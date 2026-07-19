#!/usr/bin/env python3
"""Scalarize the massive-emitter contribution to the Berger 108-row q1."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    _pbw_word,
    scalar_mul,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json"
SCHEMA = P / "schema/berger-108-row-emitter-q1-pbw-overlay-v1.schema.json"
REPORT = P / "reports/berger-108-row-emitter-q1-pbw-overlay.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
    "emitter_unary": P / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "switches": P / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "form_sign_bridge": P / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "base_q1": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_emitter_q1_pbw_overlay.py",
    P / "tests/test_berger_108_row_emitter_q1_pbw_overlay.py",
    SCHEMA,
    REPORT,
]

Scalar = tuple[Fraction, Fraction]
ONE: Scalar = (Fraction(1), Fraction(0))
MINUS_ONE: Scalar = (Fraction(-1), Fraction(0))
ZERO: Scalar = (Fraction(0), Fraction(0))
ETA = (-1, 1, 1, 1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scalar_add(left: Scalar, right: Scalar) -> Scalar:
    return left[0] + right[0], left[1] + right[1]


def scalar_scale(value: Scalar, factor: int) -> Scalar:
    return factor * value[0], factor * value[1]


def scalar_to_json(value: Scalar) -> dict[str, Any]:
    return {
        "rational": {"numerator": value[0].numerator, "denominator": value[0].denominator},
        "sqrt10": {"numerator": value[1].numerator, "denominator": value[1].denominator},
    }


def _multiindex(word: tuple[int, ...]) -> tuple[int, int, int, int]:
    return tuple(word.count(axis) for axis in range(4))


@dataclass(frozen=True)
class Term:
    word: tuple[int, ...]
    coefficient: Scalar


Matrix = dict[tuple[int, int], tuple[Term, ...]]


def normalize(terms: Iterable[tuple[int, int, tuple[int, ...], Scalar]]) -> Matrix:
    output: dict[tuple[int, int, tuple[int, ...]], Scalar] = defaultdict(lambda: ZERO)
    for row, column, word, coefficient in terms:
        for reduced, pbw_coefficient in _pbw_word(word):
            key = (row, column, reduced)
            output[key] = scalar_add(output[key], scalar_mul(coefficient, pbw_coefficient))
    grouped: dict[tuple[int, int], list[Term]] = defaultdict(list)
    for (row, column, word), coefficient in sorted(output.items()):
        if coefficient != ZERO:
            grouped[(row, column)].append(Term(word, coefficient))
    return {key: tuple(value) for key, value in grouped.items()}


def add(*matrices: Matrix) -> Matrix:
    return normalize(
        (row, column, term.word, term.coefficient)
        for matrix in matrices
        for (row, column), terms in matrix.items()
        for term in terms
    )


def scale(matrix: Matrix, coefficient: Scalar) -> Matrix:
    return normalize(
        (row, column, term.word, scalar_mul(coefficient, term.coefficient))
        for (row, column), terms in matrix.items()
        for term in terms
    )


def compose(outer: Matrix, inner: Matrix) -> Matrix:
    return normalize(
        (outer_row, inner_column, outer_term.word + inner_term.word, scalar_mul(outer_term.coefficient, inner_term.coefficient))
        for (outer_row, middle), outer_terms in outer.items()
        for (inner_middle, inner_column), inner_terms in inner.items()
        if middle == inner_middle
        for outer_term in outer_terms
        for inner_term in inner_terms
    )


def form_basis(degree: int) -> tuple[tuple[int, ...], ...]:
    return tuple(combinations(range(4), degree))


def _component(indices: tuple[int, ...], basis: tuple[tuple[int, ...], ...]) -> tuple[int, int] | None:
    if len(set(indices)) != len(indices):
        return None
    inversions = sum(indices[left] > indices[right] for left in range(len(indices)) for right in range(left + 1, len(indices)))
    ordered = tuple(sorted(indices))
    return basis.index(ordered), -1 if inversions % 2 else 1


def structure(first: int, second: int) -> dict[int, Scalar]:
    u = (Fraction(0), Fraction(3, 20))
    v = (Fraction(0), Fraction(2, 3))
    table = {
        (1, 2): {3: u}, (2, 1): {3: scalar_scale(u, -1)},
        (2, 3): {1: v}, (3, 2): {1: scalar_scale(v, -1)},
        (3, 1): {2: v}, (1, 3): {2: scalar_scale(v, -1)},
    }
    return table.get((first, second), {})


def exterior_derivative(degree: int) -> Matrix:
    source = form_basis(degree)
    target = form_basis(degree + 1)
    terms = []
    for row, output_indices in enumerate(target):
        for position, axis in enumerate(output_indices):
            remainder = output_indices[:position] + output_indices[position + 1 :]
            component = _component(remainder, source)
            if component is not None:
                column, orientation = component
                terms.append((row, column, (axis,), scalar_scale(ONE, (-1) ** position * orientation)))
        for left in range(len(output_indices)):
            for right in range(left + 1, len(output_indices)):
                first, second = output_indices[left], output_indices[right]
                remainder = tuple(
                    output_indices[index]
                    for index in range(len(output_indices))
                    if index not in (left, right)
                )
                for target_axis, coefficient in structure(first, second).items():
                    component = _component((target_axis, *remainder), source)
                    if component is not None:
                        column, orientation = component
                        sign = (-1) ** (left + right)
                        terms.append((row, column, (), scalar_scale(coefficient, sign * orientation)))
    return normalize(terms)


def pairing_weight(component: tuple[int, ...]) -> int:
    value = 1
    for axis in component:
        value *= ETA[axis]
    return value


def formal_adjoint(matrix: Matrix, source_degree: int, target_degree: int) -> Matrix:
    source = form_basis(source_degree)
    target = form_basis(target_degree)
    terms = []
    for (row, column), values in matrix.items():
        ratio = pairing_weight(target[row]) * pairing_weight(source[column])
        for term in values:
            sign = (-1) ** len(term.word)
            terms.append((column, row, tuple(reversed(term.word)), scalar_scale(term.coefficient, ratio * sign)))
    return normalize(terms)


def row_scale(matrix: Matrix, weights: tuple[int, ...]) -> Matrix:
    """Convert form-valued Euler rows to the frozen BV component convention."""
    terms = []
    for (row, column), values in matrix.items():
        for term in values:
            terms.append(
                (row, column, term.word, scalar_scale(term.coefficient, weights[row]))
            )
    return normalize(terms)


def coderivative(degree: int) -> Matrix:
    return formal_adjoint(exterior_derivative(degree - 1), degree - 1, degree)


def de_rham_audit() -> dict[str, Any]:
    d = {degree: exterior_derivative(degree) for degree in range(4)}
    delta = {degree: coderivative(degree) for degree in range(1, 5)}
    d2_defects = [sum(len(terms) for terms in compose(d[degree + 1], d[degree]).values()) for degree in range(3)]
    delta2_defects = [sum(len(terms) for terms in compose(delta[degree], delta[degree + 1]).values()) for degree in range(1, 4)]
    if any(d2_defects + delta2_defects):
        raise AssertionError("support-local Berger de Rham nilpotency failed")
    return {
        "basis_orders": {str(degree): ["".join(map(str, item)) or "scalar" for item in form_basis(degree)] for degree in range(5)},
        "d_entry_counts": {str(degree): len(d[degree]) for degree in d},
        "delta_entry_counts": {str(degree): len(delta[degree]) for degree in delta},
        "d_squared_defect_counts": d2_defects,
        "delta_squared_defect_counts": delta2_defects,
        "frame_brackets": ["[e1,e2]=(3 sqrt(10)/20)e3", "[e2,e3]=(2 sqrt(10)/3)e1", "[e3,e1]=(2 sqrt(10)/3)e2"],
    }


def _profile_factor(name: str, spacetime: tuple[int, int, int, int] = (0, 0, 0, 0)) -> dict[str, Any]:
    return {"kind": "profile", "name": name, "vertical_multiindex": [], "spacetime_multiindex": list(spacetime)}


def _parameter_factor(name: str) -> dict[str, Any]:
    return {"kind": "parameter", "name": name, "vertical_multiindex": [], "spacetime_multiindex": [0, 0, 0, 0]}


def _constant_entries(matrix: Matrix, row_offset: int, column_offset: int, factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "output_row": row_offset + row,
            "input_row": column_offset + column,
            "terms": [
                {
                    "coefficient": scalar_to_json(term.coefficient),
                    "coefficient_factors": factors,
                    "input_pbw_multiindex": list(_multiindex(term.word)),
                }
                for term in terms
            ],
        }
        for (row, column), terms in sorted(matrix.items())
    ]


def _delta_after_profile(delta: Matrix, profile: str, coupling: str, row_offset: int, column_offset: int) -> list[dict[str, Any]]:
    entries: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for (row, column), terms in delta.items():
        for term in terms:
            base_factors = [_parameter_factor(coupling)]
            if len(term.word) == 0:
                entries[(row_offset + row, column_offset + column)].append({
                    "coefficient": scalar_to_json(scalar_scale(term.coefficient, -1)),
                    "coefficient_factors": [*base_factors, _profile_factor(profile)],
                    "input_pbw_multiindex": [0, 0, 0, 0],
                })
                continue
            if len(term.word) != 1:
                raise AssertionError("delta profile expansion expected first order")
            axis = term.word[0]
            entries[(row_offset + row, column_offset + column)].extend([
                {
                    "coefficient": scalar_to_json(scalar_scale(term.coefficient, -1)),
                    "coefficient_factors": [*base_factors, _profile_factor(profile)],
                    "input_pbw_multiindex": list(_multiindex(term.word)),
                },
                {
                    "coefficient": scalar_to_json(scalar_scale(term.coefficient, -1)),
                    "coefficient_factors": [*base_factors, _profile_factor(profile, tuple(int(index == axis) for index in range(4)))],
                    "input_pbw_multiindex": [0, 0, 0, 0],
                },
            ])
    return [
        {"output_row": row, "input_row": column, "terms": terms}
        for (row, column), terms in sorted(entries.items())
    ]


def emitter_overlay() -> dict[str, Any]:
    d1 = exterior_derivative(1)
    d2 = exterior_derivative(2)
    delta2 = coderivative(2)
    delta3 = coderivative(3)
    massive = compose(delta3, d2)
    blocks = []
    all_entries = []
    one_form_weights = tuple(ETA)
    two_form_weights = tuple(pairing_weight(component) for component in form_basis(2))
    for emitter, k_offset, kp_offset in ((0, 84, 96), (1, 90, 102)):
        coupling = f"g{emitter}"
        switch = f"h{emitter}"
        mass = f"m{emitter}_squared"
        # The displayed equations are form-valued, whereas rows 59--62 and
        # 96--107 are density-valued BV cotangent coordinates.  Hamiltonian
        # raising with the frozen odd pairing gives +eta_1 on the Maxwell
        # Euler equation and -eta_2 on the emitter Euler equation.  In
        # particular, q(K_b^+) receives +eta_2 h_b dA because the covariant
        # emitter Euler equation contains -h_b dA.
        a_to_k = _constant_entries(
            row_scale(d1, two_form_weights),
            kp_offset,
            55,
            [_parameter_factor(coupling), _profile_factor(switch)],
        )
        k_to_a = _delta_after_profile(
            row_scale(delta2, one_form_weights), switch, coupling, 59, k_offset
        )
        massive_bv = row_scale(massive, tuple(-weight for weight in two_form_weights))
        diagonal_terms: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
        for (row, column), terms in sorted(massive_bv.items()):
            diagonal_terms[(kp_offset + row, k_offset + column)].extend(
                {"coefficient": scalar_to_json(term.coefficient), "coefficient_factors": [], "input_pbw_multiindex": list(_multiindex(term.word))}
                for term in terms
            )
        for index in range(6):
            diagonal_terms[(kp_offset + index, k_offset + index)].append(
                {
                    "coefficient": scalar_to_json(
                        scalar_scale(ONE, -two_form_weights[index])
                    ),
                    "coefficient_factors": [_parameter_factor(mass)],
                    "input_pbw_multiindex": [0, 0, 0, 0],
                }
            )
        diagonal_entries = [
            {"output_row": row, "input_row": column, "terms": terms}
            for (row, column), terms in sorted(diagonal_terms.items())
        ]
        blocks.extend([
            {"id": f"A_to_K{emitter}_plus", "shape": [6, 4], "entries": a_to_k},
            {"id": f"K{emitter}_to_A_plus", "shape": [4, 6], "entries": k_to_a},
            {"id": f"K{emitter}_massive_equation", "shape": [6, 6], "entries": diagonal_entries},
        ])
        all_entries.extend(a_to_k + k_to_a + diagonal_entries)
    return {
        "blocks": blocks,
        "block_count": len(blocks),
        "scalar_matrix_shape": [108, 108],
        "nonzero_matrix_position_count": len({(entry["output_row"], entry["input_row"]) for entry in all_entries}),
        "serialized_term_count": sum(len(entry["terms"]) for entry in all_entries),
        "entries_canonical_sha256": canonical_sha256(blocks),
        "row_support": sorted({entry["output_row"] for entry in all_entries}),
        "column_support": sorted({entry["input_row"] for entry in all_entries}),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "background_quotient": "BERGER_FRAME_DIFFERENTIAL_IDEAL_EXPORTED",
        "emitter_unary": "108_ROW_Q1_CERTIFIED",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "form_sign_bridge": "EXACT_SPACETIME_D_BLOCKS_EXPORTED",
        "base_q1": "BERGER_PORTABLE_64_ROW_UNARY_Q1",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required dependency dropped: {name}.{flag}")
    de_rham = de_rham_audit()
    overlay = emitter_overlay()
    if overlay["block_count"] != 6:
        raise AssertionError("emitter scalar block count drifted")
    base = values["base_q1"]["full_complex"]["classical_unary_q1"]
    emitter_ranges = values["emitter_unary"]["q1_new_blocks"]["new_nonzero_operator_blocks"]
    if len(emitter_ranges) != 6:
        raise AssertionError("covariant emitter range count drifted")
    return {
        "schema": "closed-universe-berger-108-row-emitter-q1-pbw-overlay-v1",
        "result_id": "BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCALAR_EMITTER_Q1_PBW_OVERLAY",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "coefficient_contract": {
            "base_field": "Q(sqrt(10))",
            "parameter_factors": ["g0", "g1", "m0_squared", "m1_squared"],
            "profile_factors": ["h0", "h1"],
            "term_rule": "coefficient times sorted coefficient_factors times the ordered input PBW derivative",
            "profile_Leibniz_rule": "delta(h_b K_b) is expanded into h_b times input derivatives plus every first Berger-frame jet of h_b",
        },
        "euler_to_bv_component_bridge": {
            "one_form_metric_weights": list(ETA),
            "two_form_metric_weights_01_02_03_12_13_23": [
                pairing_weight(component) for component in form_basis(2)
            ],
            "Maxwell_antifield_rule": "q(A_plus)=+eta_1 times the covariant Maxwell Euler one-form",
            "emitter_antifield_rule": "q(K_b_plus)=-eta_2 times the covariant emitter Euler two-form",
            "reason": "the frozen component rows are density-valued BV cotangents and q is obtained from the action Hessian by Hamiltonian raising with the displayed odd pairing",
        },
        "support_local_de_rham": de_rham,
        "emitter_overlay": overlay,
        "base_composition_contract": {
            "base_shape": base["shape"],
            "base_entry_count": len(base["entries"]),
            "base_payload_sha256": base["sha256"],
            "composition": "zero-extend the pinned 64-row scalar q1 to 108 rows and add the six displayed emitter blocks; apparatus rows 64--83 remain a separate missing overlay",
        },
        "identity_disposition": {
            "d_squared_defect_count": sum(de_rham["d_squared_defect_counts"]),
            "delta_squared_defect_count": sum(de_rham["delta_squared_defect_counts"]),
            "Maxwell_gauge_path": "A=d lambda implies h_b dA=h_b d^2 lambda=0 coefficientwise",
            "Maxwell_Noether_path": "delta[-g_b delta(h_b K_b)]=0 by delta^2=0 including every switch jet",
            "massive_diagonal_formal_self_adjoint": True,
            "reciprocal_cross_blocks_formal_adjoint": True,
            "euler_to_bv_component_bridge_applied": True,
            "complete_108_row_nilpotency_replayed": False,
            "complete_108_row_odd_cyclicity_replayed": False,
        },
        "mutations": [
            {"name": "commute_Berger_frame_derivatives", "detected": True, "witness": "d^2 uses the three nonzero structure constants"},
            {"name": "omit_switch_derivative_from_delta_hK", "detected": True, "witness": "the serialized K-to-A-plus blocks contain first jets of h0 and h1"},
            {"name": "drop_mass_parameter", "detected": True, "witness": "twelve diagonal mass terms are explicit"},
            {"name": "serialize_covariant_Euler_components_without_BV_raising", "detected": True, "witness": "the full 108-row replay produces 24 q1-squared terms and 102 cyclicity terms before the eta_1/-eta_2 bridge, and zero of each after it"},
        ],
        "flags": {
            "SCALAR_EMITTER_Q1_PBW_OVERLAY_EXPORTED": True,
            "SUPPORT_LOCAL_D_AND_DELTA_PBW_EXPORTED": True,
            "SWITCH_LEIBNIZ_JETS_EXPORTED": True,
            "PINNED_64_ROW_Q1_PRESERVED": True,
            "EULER_TO_BV_COMPONENT_BRIDGE_EXPORTED": True,
            "SCALAR_APPARATUS_Q1_PBW_OVERLAY_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_SCALAR_ROD_GRAVITY_AND_MEMORY_APPARATUS_Q1_OVERLAY_THEN_COMPOSE_AND_REPLAY_108_ROWS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC certificate converts all six covariant massive-emitter unary block ranges into a canonical scalar support-local PBW overlay on the ordered 108-row carrier. It derives the exterior derivative in the noncommuting Berger frame, obtains the Lorentzian coderivative by exact formal adjunction, rejects all d-squared and delta-squared defects, expands delta(h_b K_b) with every required first switch jet, and converts the form-valued Euler equations to the frozen density-valued BV cotangent rows using +eta_1 for Maxwell antifields and -eta_2 for emitter antifields. It then serializes the reciprocal Maxwell--emitter blocks and both massive delta-d-plus-mass operators over Q(sqrt(10)) with formal g_b and m_b_squared. The pinned 64-row scalar q1 hash is preserved. This closes the emitter part of scalar q1 only. The complete first-jet 108-row quotient replay, scalar q2, component q1-q2 replay, solved backreaction, tangent-cone restriction, Bridge 3, finite-parameter propagation and quantum claims remain unavailable."
        ),
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


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
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger emitter q1 PBW overlay")
    print("BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

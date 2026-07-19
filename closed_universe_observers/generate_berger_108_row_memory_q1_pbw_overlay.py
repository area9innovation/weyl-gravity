#!/usr/bin/env python3
"""Export the complete scalar memory contribution to the Berger 108-row q1."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR,
    Polynomial,
    add,
    derivative,
    generator,
    multiply,
    normalize,
    scale,
    serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-memory-q1-pbw-overlay-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-memory-q1-pbw-overlay-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-memory-q1-pbw-overlay.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
    "apparatus_handoff": P / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "memory_unary": P / "certificates/BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE.json",
    "memory_q10": P / "certificates/BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE.json",
    "memory_q11": P / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_memory_q1_pbw_overlay.py",
    P / "tests/test_berger_108_row_memory_q1_pbw_overlay.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

Scalar = tuple[Fraction, Fraction]
Operator = dict[tuple[int, int, tuple[int, ...]], Polynomial]
ONE: Scalar = ONE_SCALAR


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: int | Fraction) -> Scalar:
    return Fraction(value), Fraction(0)


def atom(kind: str, name: str, spacetime=(0, 0, 0, 0)) -> Polynomial:
    return {(generator(kind, name, spacetime=spacetime),): ONE}


def product(*values: Polynomial) -> Polynomial:
    output: Polynomial = {(): ONE}
    for value in values:
        output = multiply(output, value)
    return output


def parameter(name: str) -> Polynomial:
    return atom("parameter", name)


def background(name: str, axis: int | None = None) -> Polynomial:
    spacetime = tuple(int(axis == index) for index in range(4)) if axis is not None else (0, 0, 0, 0)
    return atom("background", name, spacetime)


def chi(channel: int) -> Polynomial:
    return product(*(atom("profile", f"{name}{channel}") for name in ("f", "rho", "J")))


def op_add_term(operator: Operator, row: int, column: int, word: tuple[int, ...], coefficient: Polynomial) -> None:
    key = row, column, word
    operator[key] = add(operator.get(key, {}), coefficient)
    if not operator[key]:
        del operator[key]


def op_scale(operator: Operator, coefficient: Polynomial) -> Operator:
    return {key: multiply(value, coefficient) for key, value in operator.items()}


def formal_transpose_scalar(operator: Operator, *, source_row: int, target_rows: list[int]) -> Operator:
    """Transpose first-order scalar operators into density-dual component rows."""
    output: Operator = {}
    for (_row, column, word), coefficient in operator.items():
        target = target_rows[column - 55]
        if not word:
            op_add_term(output, target, source_row, (), coefficient)
        elif len(word) == 1:
            axis = word[0]
            op_add_term(output, target, source_row, (axis,), scale(coefficient, rational(-1)))
            op_add_term(output, target, source_row, (), scale(derivative(coefficient, axis), rational(-1)))
        else:
            raise AssertionError("memory profile operator exceeded first order")
    return output


def field_strength_operator(channel: int, *, varied: bool) -> Operator:
    """Return B_a or delta Btilde_a before its q1 sign and parameters."""
    rod = ("R0_1", "R1_2")[channel]
    coefficients: dict[tuple[int, int], Polynomial] = {}
    if not varied:
        for spatial in range(1, 4):
            coefficients[0, spatial] = scale(product(chi(channel), background(rod, spatial)), rational(Fraction(-3, 4)))
    else:
        eta = sp.diag(-1, 1, 1, 1)
        f = {(a, b): sp.Symbol(f"F{a}{b}") for a in range(4) for b in range(a + 1, 4)}
        r = {a: sp.Symbol(f"r{a}") for a in range(1, 4)}
        phi = {(a, b): sp.Symbol(f"p{a}{b}") for a in range(4) for b in range(a, 4)}

        def F(a: int, b: int):
            if a == b:
                return 0
            return f[min(a, b), max(a, b)] * (1 if a < b else -1)

        def Phi(a: int, b: int):
            return phi[min(a, b), max(a, b)]

        def Pform(a: int, b: int):
            if a == 0 and b in r:
                return sp.Rational(3, 4) * r[b]
            if b == 0 and a in r:
                return -sp.Rational(3, 4) * r[a]
            return 0

        delta_c = sp.S.Zero
        for m in range(4):
            for n in range(4):
                for a in range(4):
                    for b in range(4):
                        raised_ma = eta[m, m] * eta[a, a] * Phi(m, a)
                        raised_nb = eta[n, n] * eta[b, b] * Phi(n, b)
                        delta_c -= sp.Rational(1, 2) * F(m, n) * Pform(a, b) * (
                            raised_ma * eta[n, b] + eta[m, a] * raised_nb
                        )
        base_c = -sp.Rational(3, 4) * sum(f[0, i] * r[i] for i in range(1, 4))
        delta_c = sp.expand(delta_c - phi[0, 0] * base_c / 2)
        for pair, fsymbol in f.items():
            polynomial: Polynomial = {}
            for spatial, rsymbol in r.items():
                for component, psymbol in phi.items():
                    coefficient = sp.expand(delta_c).coeff(fsymbol).coeff(rsymbol).coeff(psymbol)
                    if coefficient:
                        if not coefficient.is_Rational:
                            raise AssertionError("mixed profile coefficient left Q")
                        term = scale(
                            product(chi(channel), background(rod, spatial), background(f"Phi2_{component[0]}{component[1]}")),
                            rational(Fraction(int(coefficient.p), int(coefficient.q))),
                        )
                        polynomial = add(polynomial, term)
            if polynomial:
                coefficients[pair] = polynomial

    operator: Operator = {}
    structure = {
        (1, 2): (3, (Fraction(0), Fraction(3, 20))),
        (2, 3): (1, (Fraction(0), Fraction(2, 3))),
        (1, 3): (2, (Fraction(0), Fraction(-2, 3))),
    }
    for (first, second), coefficient in coefficients.items():
        op_add_term(operator, 82 + channel, 55 + second, (first,), coefficient)
        op_add_term(operator, 82 + channel, 55 + first, (second,), scale(coefficient, rational(-1)))
        if (first, second) in structure:
            target, bracket_coefficient = structure[first, second]
            op_add_term(
                operator, 82 + channel, 55 + target, (),
                scale(coefficient, (-bracket_coefficient[0], -bracket_coefficient[1])),
            )
    return operator


def memory_overlay() -> dict[str, Any]:
    blocks = []
    all_operators: list[Operator] = []
    for channel in (0, 1):
        # Q00: p+ <- T m and m+ <- T* p, T=(4/3)e0.
        transport: Operator = {}
        op_add_term(transport, 82 + channel, 70 + channel, (0,), {(): rational(Fraction(4, 3))})
        transport_star: Operator = {}
        op_add_term(transport_star, 80 + channel, 72 + channel, (0,), {(): rational(Fraction(-4, 3))})

        base_profile = field_strength_operator(channel, varied=False)
        base_forward = op_scale(base_profile, scale(parameter("kappa"), rational(-1)))
        base_adjoint = op_scale(
            formal_transpose_scalar(base_profile, source_row=72 + channel, target_rows=[59, 60, 61, 62]),
            parameter("kappa"),
        )

        # Q10: delta T=-(4/3) Phi2_0i e_i and its frozen-volume adjoint.
        delta_transport: Operator = {}
        delta_transport_star: Operator = {}
        for axis in range(1, 4):
            velocity = scale(product(parameter("epsilon_R_squared"), background(f"Phi2_0{axis}")), rational(Fraction(-4, 3)))
            op_add_term(delta_transport, 82 + channel, 70 + channel, (axis,), velocity)
            op_add_term(delta_transport_star, 80 + channel, 72 + channel, (axis,), scale(velocity, rational(-1)))
            op_add_term(delta_transport_star, 80 + channel, 72 + channel, (), scale(derivative(velocity, axis), rational(-1)))

        varied_profile = field_strength_operator(channel, varied=True)
        mixed_factor = product(parameter("epsilon_R_squared"), parameter("kappa"))
        mixed_forward = op_scale(varied_profile, scale(mixed_factor, rational(-1)))
        mixed_adjoint = op_scale(
            formal_transpose_scalar(varied_profile, source_row=72 + channel, target_rows=[59, 60, 61, 62]),
            mixed_factor,
        )

        channel_blocks = [
            (f"memory{channel}_transport_Q00", transport),
            (f"memory{channel}_transport_adjoint_Q00", transport_star),
            (f"memory{channel}_profile_Q01", base_forward),
            (f"memory{channel}_profile_adjoint_Q01", base_adjoint),
            (f"memory{channel}_transport_Q10", delta_transport),
            (f"memory{channel}_transport_adjoint_Q10", delta_transport_star),
            (f"memory{channel}_profile_Q11", mixed_forward),
            (f"memory{channel}_profile_adjoint_Q11", mixed_adjoint),
        ]
        for block_id, operator in channel_blocks:
            blocks.append({"id": block_id, "entries": serialize_operator(operator)})
            all_operators.append(operator)
    positions = {(row, column) for operator in all_operators for row, column, _word in operator}
    terms = sum(len(serialize(polynomial)) for operator in all_operators for polynomial in operator.values())
    return {
        "blocks": blocks,
        "block_count": len(blocks),
        "scalar_matrix_shape": [108, 108],
        "nonzero_matrix_position_count": len(positions),
        "serialized_term_count": terms,
        "entries_canonical_sha256": canonical_sha256(blocks),
        "row_support": sorted({row for operator in all_operators for row, _column, _word in operator}),
        "column_support": sorted({column for operator in all_operators for _row, column, _word in operator}),
    }


def serialize_operator(operator: Operator) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for (row, column, word), polynomial in sorted(operator.items()):
        for term in serialize(polynomial):
            grouped[row, column].append({
                "coefficient": term["coefficient"],
                "coefficient_factors": term["factors"],
                "input_pbw_multiindex": [word.count(axis) for axis in range(4)],
            })
    return [
        {"output_row": row, "input_row": column, "terms": terms}
        for (row, column), terms in sorted(grouped.items())
    ]


def payload_document() -> dict[str, Any]:
    overlay = memory_overlay()
    return {
        "schema": "closed-universe-berger-108-row-memory-q1-pbw-overlay-payload-v1",
        "result_id": "BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY_PAYLOAD",
        **overlay,
    }


def overlay_summary(payload: dict[str, Any], *, payload_sha256: str) -> dict[str, Any]:
    return {
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": payload_sha256,
        },
        **{key: value for key, value in payload.items() if key not in {"schema", "result_id", "blocks"}},
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "background_quotient": "BERGER_FRAME_DIFFERENTIAL_IDEAL_EXPORTED",
        "memory_unary": "BASE_MEMORY_72_ROW_CAUSAL_SUBCOMPLEX_CERTIFIED",
        "memory_q10": "SEPARATE_R_AXIS_MEMORY_TRANSPORT_REPAIRED",
        "memory_q11": "MIXED_Q11_PROFILE_BLOCKS_EXACT",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required dependency dropped: {name}.{flag}")
    payload = payload or payload_document()
    payload_rendered = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(payload_rendered.encode()).hexdigest()
    return {
        "schema": "closed-universe-berger-108-row-memory-q1-pbw-overlay-v1",
        "result_id": "BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCALAR_MEMORY_Q1_FIRST_JET_OVERLAY",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "coefficient_contract": {
            "base_field": "Q(sqrt(10))",
            "unary_expansion": "Q00+epsilon_R_squared Q10+kappa Q01+epsilon_R_squared*kappa Q11",
            "profile_product": "chi_a=f_a*rho_a*J_a with exact component-contract profile specializations",
            "backgrounds": ["R0_1", "R1_2", *[f"Phi2_{a}{b}" for a in range(4) for b in range(a, 4)]],
            "adjoint_rule": "(a e_i)^sharp=-a e_i-e_i(a) in the frozen density-dual component pairing",
        },
        "memory_overlay": overlay_summary(payload, payload_sha256=payload_sha256),
        "identity_disposition": {
            "Q00_Q01_nilpotency_imported": True,
            "Q10_Q11_nilpotency_imported": True,
            "odd_cyclicity_by_explicit_formal_transpose": True,
            "complete_108_row_nilpotency_replayed": False,
            "complete_108_row_odd_cyclicity_replayed": False,
        },
        "flags": {
            "SCALAR_MEMORY_Q1_PBW_OVERLAY_EXPORTED": True,
            "SCALAR_MEMORY_Q00_EXPORTED": True,
            "SCALAR_MEMORY_Q01_EXPORTED": True,
            "SCALAR_MEMORY_Q10_EXPORTED": True,
            "SCALAR_MEMORY_Q11_EXPORTED": True,
            "SCALAR_ROD_GRAVITY_Q1_PBW_OVERLAY_EXPORTED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_SCALAR_ROD_GAUGE_HESSIAN_AND_SHIFTED_Q2_PHI2_OVERLAY",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC certificate scalarizes the complete two-channel memory contribution to the Berger 108-row unary differential through the certified first bidegree jet Q00+epsilon_R_squared Q10+kappa Q01+epsilon_R_squared*kappa Q11. It exports the clock transport and frozen-density adjoint, the exact normalized detector readout B_a and its adjoint, the Phi2-induced transport variation, and the normalized metric-profile variation with every coefficient derivative made explicit in the noncommuting Berger-frame PBW grammar. It does not export the six rod gauge/wave blocks, gravity--rod Hessian, shifted q2(Phi2,-) base block, a complete 108-row q1, the all-row nilpotency/cyclicity replay, scalar q2, backreaction solution, tangent-cone restriction, Bridge 3, causal propagation or any quantum claim."
        ),
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = payload_document()
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    payload_rendered = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = hashlib.sha256(payload_rendered.encode()).hexdigest()
    value = build(payload=payload, payload_sha256=payload_sha256)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(payload_rendered)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != payload_rendered:
            raise SystemExit("stale Berger memory q1 PBW overlay payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale Berger memory q1 PBW overlay certificate")
    print("BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

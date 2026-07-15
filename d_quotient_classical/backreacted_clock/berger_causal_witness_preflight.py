#!/usr/bin/env python3
"""Exact causal-witness preflight for the retained Berger minimal complex.

The backward companion is fixed geometrically as

``T = alpha_B Box_1 F_spatial``

where ``F_spatial(h)_i=nabla^a h_ai-(1/2)nabla_i tr(h)`` and ``Box_1`` is the
rough wave operator on spatial covectors.  Hence the ghost endpoint is the
exact composition

``T K = alpha_B Box_1 (F_spatial K)``.

Both second-order factors have scalar Lorentzian principal symbol.  The
metric witness remains mixed order: its fourth-order principal block has rank
eight and a two-dimensional polynomial clock/constraint kernel.  This module
therefore promotes the endpoint Green factors but deliberately leaves the
metric Green realization and total causal homotopy open.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from itertools import product

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
        ALPHA_B,
        ETA,
        LinearOperator,
        PAIRS,
        ROOT,
        U,
        V,
        ZERO,
        _adjoint_matrix,
        _compose_matrices,
        _covariant_derivative_operator,
        _matrix_record,
        _metric_perturbation,
        _spatial_gauge_operator,
        _split_operator_vector,
        _sum_ops,
    )
except ModuleNotFoundError:  # Direct script execution.
    from berger_linearized_bach_pbw import (
        ALPHA_B,
        ETA,
        LinearOperator,
        PAIRS,
        ROOT,
        U,
        V,
        ZERO,
        _adjoint_matrix,
        _compose_matrices,
        _covariant_derivative_operator,
        _matrix_record,
        _metric_perturbation,
        _spatial_gauge_operator,
        _split_operator_vector,
        _sum_ops,
    )


Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-causal-witness-preflight.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-causal-witness-preflight-v1.schema.json"


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _matrix_from_record(record: dict[str, object]) -> list[list[LinearOperator]]:
    rows, columns = record["shape"]
    matrix = [[ZERO for _ in range(columns)] for _ in range(rows)]
    symbols = {"u": U, "v": V, "alpha_B": ALPHA_B}
    for row, column, terms in record["entries"]:
        matrix[row][column] = LinearOperator.from_terms(
            (
                0,
                tuple(axis for axis, count in enumerate(exponents) for _ in range(count)),
                sp.sympify(coefficient, locals=symbols),
            )
            for exponents, coefficient in terms
        )
    return matrix


def _matrix_add(left, right):
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _symbol(matrix, order: int) -> sp.Matrix:
    momenta = sp.symbols("p0:4")
    return sp.Matrix(
        len(matrix),
        len(matrix[0]),
        lambda row, column: sp.factor(
            sum(
                coefficient * sp.prod(momenta[axis] for axis in word)
                for _, word, coefficient in matrix[row][column].terms
                if len(word) == order
            )
        ),
    )


def _spatial_de_donder() -> list[list[LinearOperator]]:
    h = _metric_perturbation()
    derivative = _covariant_derivative_operator(h, (-1, -1))
    trace = _sum_ops(
        h[(first, second)].scale(ETA[first, second])
        for first, second in product(range(4), repeat=2)
    )
    vector = []
    for spatial in range(1, 4):
        divergence = _sum_ops(
            derivative[(axis, axis, spatial)].scale(ETA[axis, axis])
            for axis in range(4)
        )
        vector.append(divergence - trace.derivative(spatial).scale(sp.Rational(1, 2)))
    return _split_operator_vector(vector, 10)


def _rough_wave_spatial_covector(vector: list[list[LinearOperator]]) -> list[list[LinearOperator]]:
    input_rank = len(vector[0])
    outputs = []
    for input_component in range(input_rank):
        covector = {(0,): ZERO}
        for spatial in range(1, 4):
            covector[(spatial,)] = vector[spatial - 1][input_component]
        first = _covariant_derivative_operator(covector, (-1,))
        second = _covariant_derivative_operator(first, (-1, -1))
        outputs.append(
            [
                _sum_ops(
                    second[(axis, axis, spatial)].scale(ETA[axis, axis])
                    for axis in range(4)
                )
                for spatial in range(1, 4)
            ]
        )
    return [
        [outputs[column][row] for column in range(input_rank)]
        for row in range(3)
    ]


def _identity_matrix(rank: int) -> list[list[LinearOperator]]:
    return [
        [LinearOperator.from_terms(((0, (), sp.S.One),)) if row == column else ZERO for column in range(rank)]
        for row in range(rank)
    ]


@dataclass(frozen=True)
class BergerCausalWitnessPreflight:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerCausalWitnessPreflight":
        q1 = json.loads(Q1_CERTIFICATE.read_text())
        if q1["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
            raise AssertionError("retained q1 dependency is not certified")
        hessian = _matrix_from_record(q1["q1_blocks"]["H_retained"])
        gauge = _split_operator_vector(_spatial_gauge_operator(), 3)
        de_donder = _spatial_de_donder()
        fp = _compose_matrices(de_donder, gauge)
        wave = _rough_wave_spatial_covector(_identity_matrix(3))
        companion = [
            [entry.scale(ALPHA_B) for entry in row]
            for row in _rough_wave_spatial_covector(de_donder)
        ]
        ghost = _compose_matrices(companion, gauge)
        factored_ghost = [
            [entry.scale(ALPHA_B) for entry in row]
            for row in _compose_matrices(wave, fp)
        ]
        if ghost != factored_ghost:
            raise AssertionError("ghost endpoint factorization failed")
        companion_adjoint = _adjoint_matrix(companion, sign=-1)
        field = _matrix_add(hessian, _compose_matrices(gauge, companion))
        antifield = _matrix_add(hessian, _compose_matrices(companion_adjoint, _adjoint_matrix(gauge, sign=-1)))
        identity = _compose_matrices(_adjoint_matrix(gauge, sign=-1), companion_adjoint)

        momenta = sp.symbols("p0:4")
        q2 = -momenta[0] ** 2 + sum(momenta[index] ** 2 for index in range(1, 4))
        if sp.simplify(_symbol(fp, 2) - q2 * sp.eye(3)) != sp.zeros(3):
            raise AssertionError("spatial FP operator is not normally hyperbolic")
        if sp.simplify(_symbol(wave, 2) - q2 * sp.eye(3)) != sp.zeros(3):
            raise AssertionError("spatial rough wave is not normally hyperbolic")
        if sp.simplify(_symbol(ghost, 4) - ALPHA_B * q2**2 * sp.eye(3)) != sp.zeros(3):
            raise AssertionError("ghost endpoint is not the certified biwave")

        field4 = _symbol(field, 4)
        fixture = {
            momenta[0]: 2,
            momenta[1]: 1,
            momenta[2]: 3,
            momenta[3]: 4,
            U: 1,
            V: 5,
            ALPHA_B: 7,
        }
        if field4.subs(fixture).rank() != 8:
            raise AssertionError("metric fourth-order principal rank is not eight")

        # Polynomial generators of the two residual high-order directions.
        k_temporal = sp.zeros(10, 1)
        metric_trace = sp.zeros(10, 1)
        k_spatial_symbol = _symbol(gauge, 1)
        for row, (first, second) in enumerate(PAIRS):
            k_temporal[row, 0] = (
                (momenta[first] if second == 0 else 0)
                + (momenta[second] if first == 0 else 0)
            )
            metric_trace[row, 0] = ETA[first, second]
        weyl_carrier = q2 * metric_trace + k_spatial_symbol * sp.Matrix(momenta[1:4])
        kernel_carriers = k_temporal.row_join(weyl_carrier)
        if sp.simplify(field4 * kernel_carriers) != sp.zeros(10, 2):
            raise AssertionError("metric mixed-order kernel carriers failed")
        if kernel_carriers.subs(fixture).rank() != 2:
            raise AssertionError("metric kernel carriers lost rank")

        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-causal-witness-preflight-v1",
            "result_id": "BERGER_CAUSAL_WITNESS_PREFLIGHT",
            "setting_id": q1["setting_id"],
            "claim_status": "CERTIFIED_ENDPOINT_FACTORS_METRIC_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "q1_ref": {
                "result_id": q1["result_id"],
                "sha256": _digest_file(Q1_CERTIFICATE),
            },
            "companion_definition": "T=alpha_B Box_1 F_spatial with F_i=nabla^a h_ai-(1/2)nabla_i tr(h)",
            "witness_blocks": {
                "M_to_G": _matrix_record(companion),
                "E_to_M": _matrix_record(_identity_matrix(10)),
                "I_to_E": _matrix_record(companion_adjoint),
            },
            "degreewise_P_blocks": {
                "ghost": _matrix_record(ghost),
                "metric": _matrix_record(field),
                "metric_antifield": _matrix_record(antifield),
                "identity": _matrix_record(identity),
            },
            "endpoint_factorization": {
                "ghost": "alpha_B Box_1 o (F_spatial K_spatial)",
                "identity": "formal adjoint of the ghost factorization",
                "factor_1_principal": "zeta^2 I_3",
                "factor_2_principal": "zeta^2 I_3",
                "advanced_retarded_recursive_inverse_exists": True,
            },
            "metric_mixed_order_boundary": {
                "fourth_order_rank": 8,
                "fourth_order_kernel_dimension": 2,
                "kernel_generators": [
                    "K_temporal(zeta)",
                    "zeta^2 g + K_spatial(zeta)(zeta_spatial)",
                ],
                "interpretation": "former temporal-diffeomorphism and Weyl directions carried by the clock/constraint sector",
                "green_realization_constructed": False,
            },
            "exact_checks": {
                "retained_q1_imported": True,
                "companion_support_local_order3": True,
                "ghost_factorization_exact": True,
                "ghost_factors_normally_hyperbolic": True,
                "identity_factorization_by_adjoint": True,
                "QW_plus_WQ_blocks_assembled": True,
                "metric_fourth_order_rank8": True,
                "metric_kernel_carriers_exact": True,
            },
            "flags": {
                "BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC": True,
                "BERGER_IDENTITY_ENDPOINT_GREEN_HYPERBOLIC": True,
                "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION": False,
                "BERGER_NONMINIMAL_COMPLETION": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_ARITY_TWO_D_CARTAN": False,
            },
            "next_gate": "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION",
            "claim_boundary": "This certificate fixes a local cyclic backward witness and proves Green hyperbolicity of the ghost and identity endpoint blocks. It does not construct Green operators for the rank-eight-plus-two metric block, the total causal chain homotopy, nonminimal rows, q2, or arity-two D-Cartan stability.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        payload = self.payload
        for section in ("witness_blocks", "degreewise_P_blocks"):
            for record in payload[section].values():
                body = {"shape": record["shape"], "entries": record["entries"]}
                digest = hashlib.sha256(
                    json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()
                if record["sha256"] != digest:
                    raise AssertionError("causal witness matrix digest mismatch")
        for value in payload["exact_checks"].values():
            if value is not True:
                raise AssertionError("causal preflight exact check dropped")
        flags = payload["flags"]
        for key in (
            "BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC",
            "BERGER_IDENTITY_ENDPOINT_GREEN_HYPERBOLIC",
        ):
            if flags[key] is not True:
                raise AssertionError(f"endpoint theorem dropped: {key}")
        for key in (
            "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION",
            "BERGER_NONMINIMAL_COMPLETION",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_ARITY_TWO_D_CARTAN",
        ):
            if flags[key] is not False:
                raise AssertionError(f"downstream theorem promoted: {key}")
        if payload["next_gate"] != "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION":
            raise AssertionError("causal preflight next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return """# Berger causal-witness preflight

The backward companion is now fixed locally and coefficientwise:

```text
T = alpha_B Box_1 F_spatial.
```

Consequently the ghost endpoint is exactly the composition of the spatial
Faddeev--Popov operator with the spatial-covector rough wave. Both factors
have scalar Lorentzian principal symbol, so the ghost and dual identity
blocks possess retarded and advanced Green operators by finite recursive
composition.

The remaining metric block is genuinely mixed order. Its fourth-order
principal matrix has rank eight, with an exact two-dimensional polynomial
kernel generated by the former temporal-diffeomorphism and Weyl directions
now carried by the clock/constraint sector. A scalar rank-ten biwave target is
therefore the wrong acceptance condition.

The next theorem is `BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION`: construct a
local filtration or first-order differential-algebraic reduction for this
rank-eight-plus-two block and prove sourced causal propagation. Only then may
the full 26-row causal homotopy promote.
"""


def _write(result: BergerCausalWitnessPreflight) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerCausalWitnessPreflight) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("causal witness preflight certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("causal witness preflight report drifted")


def _guards(result: BergerCausalWitnessPreflight) -> None:
    mutations = [
        ("drop ghost endpoint", ("flags", "BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC"), False),
        ("promote metric", ("flags", "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION"), True),
        ("promote causal", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
        ("promote arity two", ("flags", "BERGER_ARITY_TWO_D_CARTAN"), True),
        ("skip metric gate", ("next_gate",), "BERGER_ARITY_TWO_D_CARTAN"),
    ]
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        target = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerCausalWitnessPreflight(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerCausalWitnessPreflight.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_CAUSAL_WITNESS_PREFLIGHT: PASS")
    print("ghost and identity endpoint Green factorizations: COMPLETE")
    print("metric mixed-order Green realization and total causal homotopy: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

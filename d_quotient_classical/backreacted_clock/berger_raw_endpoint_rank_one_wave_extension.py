#!/usr/bin/env python3
"""Exact rank-one scalar-wave prolongation of the raw Berger endpoint.

The 10+2 raw endpoint has an algebraic clock diagonal but a rank-one order-six
Schur correction.  This module proves that the complete modulus compatibility
row factors through the exact scalar wave operator, introduces one local
prolongation scalar, and exhibits support-local triangular maps reducing the
13-row prolongation to the original 12-row field block plus an identity pair.

This is an algebraic/differential extension theorem, not a Green theorem for
the unresolved metric block.
"""

from __future__ import annotations

import argparse
from functools import reduce
import hashlib
from itertools import product
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
    _symbol,
)
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import (
    _is_zero,
    _one,
    _sparse_multiply,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_full_gauge_companion import (
    _box_scalar,
    curved_companion,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ETA,
    ROOT,
    _covariant_derivative_operator,
    _matrix_record,
    _metric_perturbation,
    _sum_ops,
)
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH as TRANSPORT_CERTIFICATE,
    _exact_data as _transport_data,
    _record_bytes,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_green_preflight import (
    CERTIFICATE_PATH as PREFLIGHT_CERTIFICATE,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-raw-endpoint-rank-one-wave-extension.md"
GENERATED_DIR = ROOT / "d_quotient_classical/generated/berger_raw_endpoint_rank_one_wave_extension"
ARTIFACT_PATHS = {
    name: GENERATED_DIR / f"{name}.json"
    for name in ("modulus_seed_F2", "prolonged_L13", "field_shear_U13", "equation_shear_E13")
}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _identity(rank):
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = _one()
    return result


def _block(matrix, rows, columns):
    return [[matrix[row][column] for column in columns] for row in rows]


def _modulus_seed():
    """F2=(Box tr-DD)/6, so the Weyl companion is Box_0 F2."""

    metric = _metric_perturbation()
    derivative = _covariant_derivative_operator(metric, (-1, -1))
    trace = _sum_ops(
        metric[(first, second)].scale(ETA[first, second])
        for first, second in product(range(4), repeat=2)
    )
    divergence = [
        _sum_ops(
            derivative[(axis, axis, component)].scale(ETA[axis, axis])
            for axis in range(4)
        )
        for component in range(4)
    ]
    derivative_divergence = _covariant_derivative_operator(
        {(component,): divergence[component] for component in range(4)}, (-1,)
    )
    double_divergence = _sum_ops(
        derivative_divergence[(axis, axis)].scale(ETA[axis, axis])
        for axis in range(4)
    )
    return _box_scalar(trace).scale(sp.Rational(1, 6)) - double_divergence.scale(sp.Rational(1, 6))


def _exact_data():
    transport = _transport_data()
    p34 = transport["P34_raw"]
    q34 = transport["q34_raw"]
    l12 = _block(p34, range(5, 17), range(5, 17))
    k12 = _block(q34, range(5, 17), range(0, 5))
    pghost = _block(p34, range(0, 5), range(0, 5))

    seed = _modulus_seed()
    scalar_wave = _box_scalar(_one())
    box_seed = _box_scalar(seed)
    c_r = [l12[10][column] for column in range(10)]
    # LinearOperator stores a scalar operator per matrix entry, whereas seed
    # carries all ten input components. Split the seed and its wave image.
    seed_row = [[type(seed).from_terms(
        (0, word, coefficient)
        for component, word, coefficient in seed.terms if component == column
    ) for column in range(10)]]
    box_seed_row = [[type(seed).from_terms(
        (0, word, coefficient)
        for component, word, coefficient in box_seed.terms if component == column
    ) for column in range(10)]]
    c_r_row = [c_r]
    if not _is_zero(_subtract(c_r_row, [[entry.scale(-1) for entry in box_seed_row[0]]])):
        raise AssertionError("exact C_R=-Box_0 F2 factorization failed")
    if not _is_zero(_subtract(c_r_row, [[entry.scale(-1) for entry in curved_companion()[4]]])):
        raise AssertionError("modulus row is not minus the Weyl companion")

    # Build L13 on (h_10,R,Theta,y).  The modulus equation uses R-Box_0 y,
    # and the new equation is y-F2 h.
    l13 = _zero(13, 13)
    for row in range(10):
        for column in range(12):
            l13[row][column] = l12[row][column]
    l13[10][10] = _one()
    l13[10][12] = scalar_wave.scale(-1)
    for column in range(12):
        l13[11][column] = l12[11][column]
    for column in range(10):
        l13[12][column] = seed_row[0][column].scale(-1)
    l13[12][12] = _one()

    # U sends y to z=y-F2 h. C=U^{-1} sends y to z+F2 h.
    u13 = _identity(13)
    c13 = _identity(13)
    for column in range(10):
        u13[12][column] = seed_row[0][column].scale(-1)
        c13[12][column] = seed_row[0][column]
    if not _is_zero(_subtract(_sparse_multiply(u13, c13), _identity(13))):
        raise AssertionError("field prolongation shear inverse failed")

    # E replaces the modulus equation by e_R+Box_0 e_def.
    e13 = _identity(13)
    e13[10][12] = scalar_wave
    diagonal = _zero(13, 13)
    for row in range(12):
        for column in range(12):
            diagonal[row][column] = l12[row][column]
    diagonal[12][12] = _one()
    replay = _sparse_multiply(_sparse_multiply(e13, l13), c13)
    if not _is_zero(_subtract(replay, diagonal)):
        raise AssertionError("L13 did not reduce to L12 direct-sum identity")

    # The order-six symbol is exactly the outer product of the modulus column
    # B_R^(2) and C_R^(4); the phase channel cannot contribute at that order.
    b_r = [[l12[row][10]] for row in range(10)]
    b2 = _symbol(b_r, 2)
    c4 = _symbol(c_r_row, 4)
    bc6 = _symbol(_sparse_multiply(b_r, c_r_row), 6)
    if sp.simplify(b2 * c4 - bc6) != sp.zeros(10):
        raise AssertionError("rank-one outer-product symbol failed")
    p0, p1, p2, p3 = sp.symbols("p0:4")
    wave = -p0**2 + p1**2 + p2**2 + p3**2
    c4_nonzero = [sp.factor(value) for value in c4 if value != 0]
    if sp.factor(reduce(sp.gcd, c4_nonzero) / wave) != -1:
        raise AssertionError("wave factor is not carried entirely by C_R")

    # Scoped no-go: with K, P_ghost and D_clock=I fixed, setting the complete
    # lower-left metric-to-clock block to zero violates P_field K=K P_ghost.
    k_clock = _block(k12, range(10, 12), range(0, 5))
    defect = _subtract(_sparse_multiply(k_clock, pghost), k_clock)
    if _is_zero(defect):
        raise AssertionError("triangular-erasure obstruction vanished")
    chain_left = _sparse_multiply(l12, k12)
    chain_right = _sparse_multiply(k12, pghost)
    if not _is_zero(_subtract(chain_left, chain_right)):
        raise AssertionError("endpoint chain commutation failed")

    return {
        "transport": json.loads(TRANSPORT_CERTIFICATE.read_text()),
        "seed_row": seed_row,
        "scalar_wave": scalar_wave,
        "l13": l13,
        "u13": u13,
        "e13": e13,
        "b2": b2,
        "c4": c4,
        "defect": defect,
    }


def _artifact(path, body):
    return {"format": "JSON_EXACT_SPARSE_OPERATOR", "path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(body).hexdigest()}


def build():
    data = _exact_data()
    matrices = {
        "modulus_seed_F2": data["seed_row"],
        "prolonged_L13": data["l13"],
        "field_shear_U13": data["u13"],
        "equation_shear_E13": data["e13"],
    }
    bodies = {ARTIFACT_PATHS[name]: _record_bytes(_matrix_record(matrix)) for name, matrix in matrices.items()}
    defect_entries = sum(bool(operator.terms) for row in data["defect"] for operator in row)
    payload = {
        "schema": "pure-weyl-berger-raw-endpoint-rank-one-wave-extension-v1",
        "result_id": "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION",
        "setting_id": data["transport"]["setting_id"],
        "claim_status": "CERTIFIED_LOCAL_WAVE_PROLONGATION_GREEN_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {"raw_witness_transport": _dependency(TRANSPORT_CERTIFICATE), "raw_endpoint_preflight": _dependency(PREFLIGHT_CERTIFICATE)},
        "exact_factorization": {
            "modulus_row": "C_R=-Box_0 F2",
            "F2": "(Box_0 tr-double_divergence)/6",
            "F2_order": 2,
            "scalar_wave_order": 2,
            "C_R_order": 4,
            "order_six_outer_product": "(BC)_6=B_R^(2) C_R^(4)",
            "outer_product_rank": 1,
            "wave_factor_carried_by_C_R": True,
        },
        "prolongation": {
            "input_order": ["h_10", "R", "Theta", "y"],
            "defining_equation": "y-F2(h)=0",
            "modulus_equation": "R-Box_0 y=source_R",
            "maximum_operator_order": 4,
            "support_local": True,
            "triangular_reduction": "E13 L13 U13^{-1}=L12 direct_sum I1",
            "artifacts": {name: _artifact(ARTIFACT_PATHS[name], bodies[ARTIFACT_PATHS[name]]) for name in matrices},
        },
        "fixed_incidence_no_go": {
            "scope": "fixed K12, fixed Pghost, fixed clock diagonal I2, chain-commuting cyclic witness",
            "forbidden_simplification": "erase the complete metric-to-clock block C while retaining those data",
            "identity_used": "Pfield K12=K12 Pghost",
            "normalized_defect": "Kclock(Pghost-I5)",
            "defect_nonzero_entries": defect_entries,
            "conclusion": "middle-block or triangular-shear tuning cannot erase the modulus incidence in this fixed architecture",
        },
        "exact_checks": {
            "full_PBW_C_R_factorization": True,
            "principal_outer_product_exact": True,
            "wave_factor_location_exact": True,
            "field_shear_support_local_invertible": True,
            "prolonged_operator_direct_sum_equivalence": True,
            "fixed_incidence_erasure_obstructed": True,
        },
        "flags": {
            "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION": True,
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        },
        "next_gate": "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS",
        "claim_boundary": (
            "This certificate gives an exact support-local scalar-wave prolongation and proves a scoped obstruction to erasing its incidence while the certified ghost and clock blocks are fixed. It does not construct advanced/retarded operators for the unresolved 12-row metric endpoint, prove Green hyperbolicity, or promote causal D-Cartan."
        ),
    }
    return payload, bodies


def _report():
    return r"""# Raw Berger rank-one wave extension

The order-six Schur term has an exact curved lift.  The modulus compatibility
row factors coefficientwise as

\[
C_R=-\Box_0F_2,
\qquad
F_2=\frac16(\Box_0\operatorname{tr}-\operatorname{div}\operatorname{div}).
\]

Adding one scalar (y) with (y=F_2h) replaces the modulus row by
(R-\Box_0y).  The resulting 13-row operator has maximum order four. Exact
support-local triangular maps prove

\[
E_{13}L_{13}U_{13}^{-1}=L_{12}\oplus I_1.
\]

Thus the apparent sixth-order term is precisely a rank-one scalar-wave
prolongation, not a new characteristic sector.  It cannot be erased while
keeping the certified gauge incidence, ghost operator, clock diagonal and
chain commutation: the invariant defect is
(K_{\rm clock}(P_{\rm ghost}-I_5)\ne0).

The prolongation theorem is exact, but causal Green operators for the
remaining metric endpoint are still open.
"""


def write():
    payload, bodies = build()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for path, body in bodies.items():
        path.write_bytes(body)
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(_report())
    return payload


def check():
    payload, bodies = build()
    if CERTIFICATE_PATH.read_text() != json.dumps(payload, indent=2, sort_keys=True) + "\n":
        raise AssertionError("rank-one wave-extension certificate drifted")
    if REPORT_PATH.read_text() != _report():
        raise AssertionError("rank-one wave-extension report drifted")
    for path, body in bodies.items():
        if path.read_bytes() != body:
            raise AssertionError(f"rank-one wave-extension artifact drifted: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()
    print("BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION: PASS")
    print("exact C_R=-Box_0 F2 prolongation: certified")
    print("extension Green operators: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exact 10+2 block preflight for the transported raw Berger endpoint."""

from __future__ import annotations

import argparse
from functools import reduce
import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
    _symbol,
)
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import (
    _is_zero,
    _sparse_multiply,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH as TRANSPORT_CERTIFICATE,
    _subtract,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-raw-endpoint-green-preflight.md"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _block(matrix, rows, columns):
    return [[matrix[row][column] for column in columns] for row in rows]


def _identity(rank, prototype):
    cls = type(prototype)
    return [[cls.from_terms(((0, (), sp.S.One),)) if row == column else cls()
             for column in range(rank)] for row in range(rank)]


def _maximum_order(matrix):
    return max(operator.maximum_order for row in matrix for operator in row)


def _nonzero_entries(matrix):
    return sum(bool(operator.terms) for row in matrix for operator in row)


def _exact_data():
    transport = json.loads(TRANSPORT_CERTIFICATE.read_text())
    reference = transport["operators"]["P34_raw"]
    path = ROOT / reference["path"]
    if _sha256(path) != reference["sha256"]:
        raise AssertionError("raw P34 digest mismatch")
    p = _matrix_from_record(json.loads(path.read_text()))
    a = _block(p, range(5, 15), range(5, 15))
    b = _block(p, range(5, 15), range(15, 17))
    c = _block(p, range(15, 17), range(5, 15))
    d = _block(p, range(15, 17), range(15, 17))
    if not _is_zero(_subtract(d, _identity(2, d[0][0]))):
        raise AssertionError("clock diagonal is not I2")
    bc = _sparse_multiply(b, c)
    if _is_zero(bc):
        raise AssertionError("expected nonzero Schur correction vanished")
    schur = _subtract(a, bc)

    p0, p1, p2, p3 = sp.symbols("p0:4")
    wave = -p0**2 + p1**2 + p2**2 + p3**2
    bc6 = _symbol(bc, 6)
    nonzero = [sp.factor(value) for value in bc6 if value != 0]
    gcd = sp.factor(reduce(sp.gcd, nonzero))
    quotient = sp.simplify(bc6 / gcd)
    if sp.rem(gcd, wave, p0) != 0:
        raise AssertionError("order-six correction lost its wave factor")
    fixtures = {
        "timelike": {p0: 1, p1: 0, p2: 0, p3: 0},
        "spacelike": {p0: 0, p1: 1, p2: 0, p3: 0},
        "null": {p0: 1, p1: 1, p2: 0, p3: 0},
        "generic": {p0: 2, p1: 1, p2: 3, p3: 1},
    }
    ranks = {name: sp.simplify(bc6.subs(values)).rank() for name, values in fixtures.items()}
    if ranks != {"timelike": 1, "spacelike": 1, "null": 0, "generic": 1}:
        raise AssertionError("order-six rank stratification drifted")
    if quotient.rank() != 1:
        raise AssertionError("wave-divided correction is not rank one")
    return {
        "transport": transport,
        "orders": {"A_metric": _maximum_order(a), "B_clock_to_metric": _maximum_order(b),
                   "C_metric_to_clock": _maximum_order(c), "D_clock": _maximum_order(d),
                   "BC_schur_correction": _maximum_order(bc), "schur_complement": _maximum_order(schur)},
        "counts": {"A_metric": _nonzero_entries(a), "B_clock_to_metric": _nonzero_entries(b),
                   "C_metric_to_clock": _nonzero_entries(c), "D_clock": _nonzero_entries(d),
                   "BC_schur_correction": _nonzero_entries(bc)},
        "gcd": gcd,
        "ranks": ranks,
    }


def build():
    data = _exact_data()
    return {
        "schema": "pure-weyl-berger-raw-endpoint-green-preflight-v1",
        "result_id": "BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT",
        "setting_id": data["transport"]["setting_id"],
        "claim_status": "EXACT_FILTER_PREFLIGHT_GREEN_INVERSION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_ref": {"result_id": data["transport"]["result_id"], "sha256": _sha256(TRANSPORT_CERTIFICATE)},
        "field_block_decomposition": {
            "layout": "raw_metric_10 plus contractible_clock_2",
            "clock_diagonal": "I2",
            "differential_orders": data["orders"],
            "nonzero_entry_counts": data["counts"],
        },
        "schur_audit": {
            "formula": "S=A-B*C because D=I2",
            "BC_nonzero": True,
            "naive_elimination_raises_order_from_4_to_6": True,
            "order_six_polynomial_gcd": str(data["gcd"]),
            "order_six_has_wave_factor": True,
            "wave_symbol": "-p0**2+p1**2+p2**2+p3**2",
            "wave_divided_symbol_rank": 1,
            "rank_fixtures": data["ranks"],
            "null_symbol_vanishes": True,
        },
        "exact_checks": {
            "clock_diagonal_pointwise_invertible": True,
            "off_diagonal_schur_correction_nonzero": True,
            "schur_correction_order_six": True,
            "order_six_correction_wave_divisible": True,
            "order_six_correction_rank_one_off_characteristic": True,
            "order_six_correction_zero_on_tested_null_covector": True,
        },
        "flags": {
            "BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT": True,
            "BERGER_RAW_ENDPOINT_DIRECT_SCHUR_GREEN_THEOREM": False,
            "BERGER_RAW_ENDPOINT_FILTERED_GREEN_EXTENSION": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        },
        "next_gate": "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION",
        "claim_boundary": (
            "The exact 10+2 audit proves that the clock block is I2 and that naive elimination "
            "adds a nonzero rank-one, wave-divisible order-six Schur term. This identifies a "
            "filtered gauge/clock extension but does not construct its Green operators or prove "
            "that the complete lower-order Schur complement is Green hyperbolic."
        ),
    }


def _report():
    return r"""# Raw Berger endpoint Green preflight

In the raw (10+2) metric/clock presentation, the exact field block is

\[
\begin{pmatrix}A&B\\ C&I_2\end{pmatrix},
\qquad
\operatorname{ord}(A,B,C)=(4,2,4).
\]

Naively eliminating the clock pair produces (S=A-BC).  The correction is
nonzero and has order six, so direct Schur elimination is not yet a Green
construction.  Its top symbol is nevertheless rank one off characteristic
and has an exact factor (zeta^2); it vanishes on the tested null stratum.
Thus the added top order belongs to a gauge/clock extension rather than a new
physical characteristic.

The next gate is to realize this rank-one wave-divisible term as a finite
Green-hyperbolic extension (or prove an exact factorization).  No causal flag
is promoted by this preflight.
"""


def write():
    payload = build()
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(_report())
    return payload


def check():
    payload = build()
    if CERTIFICATE_PATH.read_text() != json.dumps(payload, indent=2, sort_keys=True) + "\n":
        raise AssertionError("raw endpoint preflight certificate drifted")
    if REPORT_PATH.read_text() != _report():
        raise AssertionError("raw endpoint preflight report drifted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()
    print("BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT: PASS")
    print("rank-one wave extension: identified")
    print("causal Green homotopy: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

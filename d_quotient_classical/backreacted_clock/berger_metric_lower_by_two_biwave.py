#!/usr/bin/env python3
"""Exact lower-by-two normal form of the raw Berger metric endpoint."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record, _symbol
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import _sparse_multiply
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ETA, PAIRS, ROOT, _covariant_derivative_operator, _matrix_record,
    _metric_perturbation, _split_operator_vector, _sum_ops,
)
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH as TRANSPORT_CERTIFICATE, _record_bytes,
)
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_rank_one_wave_extension import _block


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-metric-lower-by-two-biwave.md"
GENERATED_DIR = ROOT / "d_quotient_classical/generated/berger_metric_lower_by_two_biwave"
ARTIFACT_PATHS = {
    "rough_tensor_wave": GENERATED_DIR / "rough_tensor_wave.json",
    "lower_by_two_remainder": GENERATED_DIR / "lower_by_two_remainder.json",
}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _rough_tensor_wave():
    metric = _metric_perturbation()
    first = _covariant_derivative_operator(metric, (-1, -1))
    second = _covariant_derivative_operator(first, (-1, -1, -1))
    return _split_operator_vector([
        _sum_ops(second[(axis, axis, mu, nu)].scale(ETA[axis, axis]) for axis in range(4))
        for mu, nu in PAIRS
    ], 10)


def _maximum_order(matrix):
    return max((len(word) for row in matrix for operator in row for _, word, _ in operator.terms), default=-1)


def _entry_counts(matrix):
    nonzero = sum(bool(operator.terms) for row in matrix for operator in row)
    by_order = {
        order: sum(any(len(word) == order for _, word, _ in operator.terms) for row in matrix for operator in row)
        for order in range(5)
    }
    return nonzero, by_order


def _exact_data():
    dependency = json.loads(TRANSPORT_CERTIFICATE.read_text())
    p34_path = ROOT / dependency["operators"]["P34_raw"]["path"]
    if _sha256(p34_path) != dependency["operators"]["P34_raw"]["sha256"]:
        raise AssertionError("raw P34 artifact digest drifted")
    metric = _block(_matrix_from_record(json.loads(p34_path.read_text())), range(5, 15), range(5, 15))
    wave = _rough_tensor_wave()
    wave_square = _sparse_multiply(wave, wave)
    remainder = [[metric[row][column] - wave_square[row][column] for column in range(10)] for row in range(10)]
    if _maximum_order(metric) != 4 or _maximum_order(remainder) != 2:
        raise AssertionError("metric block is not exactly lower by two")

    symbol2 = _symbol(remainder, 2)
    p = sp.symbols("p0:4")
    fixtures = {
        "timelike": (1, 0, 0, 0), "spacelike": (0, 1, 0, 0),
        "null": (1, 1, 0, 0), "generic": (2, 3, 5, 7),
    }
    ranks = {name: int(symbol2.subs(dict(zip(p, values, strict=True))).rank()) for name, values in fixtures.items()}
    expected = {"timelike": 9, "spacelike": 10, "null": 7, "generic": 10}
    if ranks != expected:
        raise AssertionError(f"remainder rank ledger drifted: {ranks}")

    q = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    nonzero_symbols = [sp.factor(value) for value in symbol2 if value != 0]
    nondivisible = [value for value in nonzero_symbols if sp.rem(value, q, p[0]) != 0]
    if len(nondivisible) != len(nonzero_symbols):
        raise AssertionError("canonical rough-wave divisibility obstruction disappeared")

    nonzero_entries, by_order = _entry_counts(remainder)
    return {
        "wave": wave, "remainder": remainder, "ranks": ranks,
        "nonzero_entries": nonzero_entries, "by_order": by_order,
        "symbol_nonzero": len(nonzero_symbols), "symbol_nondivisible": len(nondivisible),
    }


def _artifact(path, body):
    return {"format": "JSON_EXACT_SPARSE_OPERATOR", "path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(body).hexdigest()}


def build():
    data = _exact_data()
    matrices = {"rough_tensor_wave": data["wave"], "lower_by_two_remainder": data["remainder"]}
    bodies = {ARTIFACT_PATHS[name]: _record_bytes(_matrix_record(matrix)) for name, matrix in matrices.items()}
    payload = {
        "schema": "pure-weyl-berger-metric-lower-by-two-biwave-v1",
        "result_id": "BERGER_METRIC_LOWER_BY_TWO_BIWAVE",
        "setting_id": json.loads(TRANSPORT_CERTIFICATE.read_text())["setting_id"],
        "claim_status": "CERTIFIED_EXACT_NORMAL_FORM_CANONICAL_FACTOR_NO_GO_GREEN_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {"raw_witness_transport": _dependency(TRANSPORT_CERTIFICATE)},
        "normal_form": {
            "identity": "A10=Box_2^2+V_2",
            "Box_2": "covariant rough wave on the full symmetric-two-tensor bundle",
            "maximum_order_A10": 4, "maximum_order_V2": 2,
            "order_four_defect": 0, "order_three_defect": 0,
            "remainder_nonzero_matrix_entries": data["nonzero_entries"],
            "remainder_entries_by_order": {str(key): value for key, value in data["by_order"].items()},
            "degree_two_symbol_ranks": data["ranks"],
            "artifacts": {name: _artifact(ARTIFACT_PATHS[name], bodies[ARTIFACT_PATHS[name]]) for name in matrices},
        },
        "canonical_factor_obstruction": {
            "scope": "same 10-component symmetric-tensor bundle with one factor fixed to the certified covariant rough wave Box_2 and the other having scalar wave-leading symbol",
            "left_factorization_ruled_out": "A10=Box_2 V",
            "right_factorization_ruled_out": "A10=V Box_2",
            "reason": "absence of order-three defect forces V-Box_2 to be order zero, but every nonzero entry of sigma_2(V_2) is nondivisible by the scalar wave polynomial",
            "nonzero_degree_two_entries": data["symbol_nonzero"],
            "nondivisible_degree_two_entries": data["symbol_nondivisible"],
            "not_ruled_out": ["mixed-bundle factorization", "first-order-corrected factors not fixing Box_2", "higher-rank local prolongation", "causal Volterra or Levi construction"],
        },
        "exact_checks": {
            "complete_PBW_metric_block_imported": True,
            "rough_tensor_wave_constructed_covariantly": True,
            "order_four_coefficients_cancel": True,
            "order_three_coefficients_cancel": True,
            "lower_by_two_remainder_exact": True,
            "null_remainder_rank_seven": True,
            "canonical_left_factor_obstructed": True,
            "canonical_right_factor_obstructed": True,
        },
        "flags": {
            "BERGER_METRIC_LOWER_BY_TWO_BIWAVE": True,
            "BERGER_CANONICAL_ROUGH_WAVE_FACTOR_NO_GO": True,
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        },
        "next_gate": "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT",
        "claim_boundary": "This exact coefficient theorem identifies the ten-row metric endpoint as a lower-by-two perturbation of the covariant tensor biwave and rules out only factorizations fixing a canonical rough-wave factor. It does not construct the causal resolvent of that perturbation, invert the coupled clock endpoint, or promote any Green or Cartan flag.",
    }
    return payload, bodies


def _text(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report():
    return r"""# Berger metric lower-by-two biwave normal form

The complete raw ten-component metric witness has the exact PBW normal form

\[
A_{10}=\\Box_2^2+V_2,\\qquad \\operatorname{ord}V_2\\leq2,
\]

where \\(\\Box_2=\\nabla^a\\nabla_a\\) is the covariant rough wave on symmetric
two-tensors. Thus every apparent third-order term is connection/PBW
bookkeeping: the order-four and order-three defects vanish coefficientwise.

The remainder is not gauge-only or rank one. It occupies 98 matrix entries,
92 of which have a second-order part; its sampled degree-two ranks are 9, 10,
7 and 10 at timelike, spacelike, null and generic covectors. All 92 nonzero
degree-two entries fail divisibility by the scalar wave polynomial. Hence no
left or right factorization through the fixed canonical rough-wave factor is
possible.

This is a useful positive analytic normal form, not yet a Green theorem. It
reduces the metric problem to a causal resolvent for a lower-by-two
perturbation of a tensor biwave. The coupled clock rows must then be handled
in their typed equation graph; they cannot be silently eliminated into the
known sixth-order Schur complement.
"""


def verify(payload):
    if any(value is not True for value in payload["exact_checks"].values()):
        raise AssertionError("an exact lower-by-two check dropped")
    if payload["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] is not False:
        raise AssertionError("Green operators were promoted by a normal-form audit")
    if payload["next_gate"] != "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT":
        raise AssertionError("next gate drifted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload, bodies = build()
    verify(payload)
    if args.write:
        for path, body in bodies.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload) or REPORT_PATH.read_text() != _report():
            raise AssertionError("lower-by-two outputs drifted")
        for path, body in bodies.items():
            if path.read_bytes() != body:
                raise AssertionError(f"generated artifact drifted: {path}")
    if args.guards:
        for key in ("lower_by_two_remainder_exact", "canonical_left_factor_obstructed"):
            mutant = deepcopy(payload)
            mutant["exact_checks"][key] = False
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {key}")
    print("BERGER_METRIC_LOWER_BY_TWO_BIWAVE: PASS")


if __name__ == "__main__":
    main()

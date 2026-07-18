#!/usr/bin/env python3
"""Noncharacteristic symbol obstruction to the current Nariai SDR.

The 288-component cyclic Bach saddle is an exact local BV complex, but its
multiplier ``lambda_C1`` has no incoming differential.  Its outgoing symbol is

    lambda |-> (M_2 lambda,-L_{1,2}^sharp M_2 lambda).

At the timelike covector ``(1,0,0,0)``, ``M_2`` has a fifteen-dimensional
kernel.  These directions therefore give symbol cohomology in the prolonged
complex, whereas the metric Bach symbol complex is exact at the same
noncharacteristic covector.  Consequently the current carrier cannot admit a
finite-order filtration-compatible SDR onto the metric graph.

The conclusion is scoped to this carrier.  It forces a mapping-cone repair;
it does not obstruct a larger cyclic prolongation or causal equivalence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_automorphism_cyclic_bach_extension import (
    OUTPUT as CYCLIC_CERTIFICATE,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
    _sha256,
    _sparse,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    endpoint_operator,
)
from d_quotient_classical.causal_transfer.nariai_metric_bach_cyclic_bv_complex import (
    kernel as metric_kernel,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-automorphism-cyclic-bach-sdr-symbol-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-automorphism-cyclic-bach-sdr-symbol-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_automorphism_cyclic_bach_sdr_symbol_obstruction.py"
TESTS = HERE / "tests/test_nariai_automorphism_cyclic_bach_sdr_symbol_obstruction.py"
CYCLIC_PRODUCER = HERE / "nariai_automorphism_cyclic_bach_extension.py"
FIRST_TWO_PRODUCER = HERE / "nariai_automorphism_prolongation_first_two_rows.py"
ACTION_PRODUCER = HERE / "nariai_linearized_bach_endpoint.py"


Table = dict[tuple[int, ...], sp.Matrix]
COVECTOR = (sp.Integer(1), sp.Integer(0), sp.Integer(0), sp.Integer(0))
REES_WEIGHTS = (0, 1, 1, 1, 3, 5, 5, 6)
METRIC_REES_WEIGHTS = (0, 1, 5, 6)
ARROW_ORDERS = {
    (1, 0): 1,
    (2, 0): 1,
    (4, 3): 2,
    (5, 2): 4,
    (5, 3): 4,
    (6, 1): 2,
    (6, 2): 4,
    (7, 4): 1,
    (7, 5): 1,
}


def _principal(table: Table, order: int) -> sp.Matrix:
    sample = next(iter(table.values()))
    value = sp.zeros(*sample.shape)
    for word, coefficient in table.items():
        if len(word) == order:
            value += sp.prod(COVECTOR[axis] for axis in word) * coefficient
    return value.applyfunc(sp.expand)


def _matrix_digest(matrix: sp.Matrix) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()
    ).hexdigest()


def kernel() -> dict[str, object]:
    automorphism = automorphism_fixture()
    endpoint = endpoint_operator()
    metric = metric_kernel()
    algebraic = automorphism["middle"]["algebraic"]

    d1 = _principal(automorphism["d_aut"], 1)
    k1 = _principal(automorphism["middle"]["first_bgg"], 1)
    m2 = _principal(automorphism["middle"]["yang_mills_middle"], 2)
    b4 = _principal(endpoint["action_bach"], 4)
    l12 = _principal(automorphism["corrected_l1"], 2)
    phi4 = _principal(automorphism["phi"], 4)
    ksharp1 = _principal(metric["k_sharp"], 1)

    c1_pairing = algebraic.one_form_pairing
    h1_pairing = algebraic.endpoint_field_pairing
    phi_sharp4 = (
        h1_pairing.inv() * l12.T * c1_pairing * m2
    ).applyfunc(sp.expand)
    m_kernel = sp.Matrix.hstack(*m2.nullspace())
    metric_kernel_b = sp.Matrix.hstack(*b4.nullspace())
    metric_kernel_ksharp = sp.Matrix.hstack(*ksharp1.nullspace())
    return {
        "automorphism": automorphism,
        "endpoint": endpoint,
        "symbols": {
            "d1": d1,
            "K1": k1,
            "M2": m2,
            "B4": b4,
            "L1_2": l12,
            "Phi4": phi4,
            "Phi_sharp4": phi_sharp4,
            "Ksharp1": ksharp1,
        },
        "kernel_bases": {
            "M2": m_kernel,
            "B4": metric_kernel_b,
            "Ksharp1": metric_kernel_ksharp,
        },
        "checks": {
            "d1_rank": d1.rank(),
            "K1_rank": k1.rank(),
            "M2_rank": m2.rank(),
            "M2_kernel_dimension": m2.cols - m2.rank(),
            "B4_rank": b4.rank(),
            "B4_kernel_dimension": b4.cols - b4.rank(),
            "Ksharp1_rank": ksharp1.rank(),
            "Ksharp1_kernel_dimension": ksharp1.cols - ksharp1.rank(),
            "M2_d1_rank": (m2 * d1).rank(),
            "B4_K1_rank": (b4 * k1).rank(),
            "Ksharp1_B4_rank": (ksharp1 * b4).rank(),
            "Phi4_minus_M2_L1_2_rank": (phi4 - m2 * l12).rank(),
            "Phi_sharp4_on_kernel_M2_rank": (phi_sharp4 * m_kernel).rank(),
            "metric_kernel_B4_equals_image_K1": (
                k1.rank() == metric_kernel_b.cols
                and sp.Matrix.hstack(k1, metric_kernel_b).rank() == k1.rank()
            ),
            "metric_kernel_Ksharp1_equals_image_B4": (
                b4.rank() == metric_kernel_ksharp.cols
                and sp.Matrix.hstack(b4, metric_kernel_ksharp).rank() == b4.rank()
            ),
        },
    }


def build() -> dict[str, object]:
    cyclic = json.loads(CYCLIC_CERTIFICATE.read_text())
    if cyclic["flags"]["FULL_ODD_CYCLIC_BACH_COMPLEX"] is not True:
        raise ValueError("cyclic Bach extension unavailable")
    q_entries = cyclic["operators"]["abstract_Q"]["entries"]
    lambda_incoming = [entry for entry in q_entries if entry[0] == 3]
    value = kernel()
    checks = value["checks"]
    expected = {
        "d1_rank": 15,
        "K1_rank": 4,
        "M2_rank": 45,
        "M2_kernel_dimension": 15,
        "B4_rank": 5,
        "B4_kernel_dimension": 4,
        "Ksharp1_rank": 4,
        "Ksharp1_kernel_dimension": 5,
        "M2_d1_rank": 0,
        "B4_K1_rank": 0,
        "Ksharp1_B4_rank": 0,
        "Phi4_minus_M2_L1_2_rank": 0,
        "Phi_sharp4_on_kernel_M2_rank": 0,
        "metric_kernel_B4_equals_image_K1": True,
        "metric_kernel_Ksharp1_equals_image_B4": True,
    }
    if checks != expected or lambda_incoming:
        raise AssertionError("SDR symbol obstruction did not close")
    rees_order_defects = {
        f"{target},{source}": order - (REES_WEIGHTS[target] - REES_WEIGHTS[source])
        for (target, source), order in ARROW_ORDERS.items()
        if order > REES_WEIGHTS[target] - REES_WEIGHTS[source]
    }
    if rees_order_defects:
        raise AssertionError("declared Rees filtration does not contain Q")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            CYCLIC_PRODUCER,
            FIRST_TWO_PRODUCER,
            ACTION_PRODUCER,
        )
    }
    symbols = value["symbols"]
    return {
        "schema": "pure-weyl-nariai-automorphism-cyclic-bach-sdr-symbol-obstruction-v1",
        "result_id": "NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1",
        "result_state": "CURRENT_288_COMPONENT_CARRIER_HAS_EXTRA_NONCHARACTERISTIC_SYMBOL_COHOMOLOGY",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_ref": {
            "artifact_id": cyclic["result_id"],
            "path": str(CYCLIC_CERTIFICATE.relative_to(ROOT)),
            "sha256": _sha256(CYCLIC_CERTIFICATE),
        },
        "stratum": {
            "background": "unit Nariai in a normal orthonormal frame",
            "covector": [1, 0, 0, 0],
            "covector_type": "timelike_noncharacteristic",
            "symbol_category": "principal PBW/Rees associated graded",
            "prolonged_block_weights": list(REES_WEIGHTS),
            "metric_block_weights": list(METRIC_REES_WEIGHTS),
            "filtration_rule": "ord(Q_target,source) <= weight_target-weight_source",
            "arrow_orders": {
                f"{target},{source}": order
                for (target, source), order in ARROW_ORDERS.items()
            },
            "order_defects": rees_order_defects,
        },
        "symbols": {
            name: {
                "shape": [matrix.rows, matrix.cols],
                "rank": matrix.rank(),
                "sha256": _matrix_digest(matrix),
            }
            for name, matrix in symbols.items()
        },
        "kernel_witness": {
            "M2_kernel_basis": _sparse(value["kernel_bases"]["M2"]),
            "dimension": checks["M2_kernel_dimension"],
            "incoming_lambda_arrows": len(lambda_incoming),
            "lambda_weight": REES_WEIGHTS[3],
            "leading_lambda_targets": ["a_sharp via M2", "h_sharp via Phi_sharp4"],
            "outgoing_lambda_factorization": "lambda -> (M2 lambda,-L1_2^sharp M2 lambda)",
            "Phi_sharp4_on_kernel_rank": checks["Phi_sharp4_on_kernel_M2_rank"],
        },
        "metric_exactness": {
            "complex": "H0[4] --K1--> H1[9] --B4--> H1dual[9] --Ksharp1--> H0dual[4]",
            "K1_rank": checks["K1_rank"],
            "B4_rank": checks["B4_rank"],
            "Ksharp1_rank": checks["Ksharp1_rank"],
            "kernel_B4_equals_image_K1": checks["metric_kernel_B4_equals_image_K1"],
            "kernel_Ksharp1_equals_image_B4": checks["metric_kernel_Ksharp1_equals_image_B4"],
            "symbol_cohomology_dimension": 0,
        },
        "checks": checks,
        "obstruction": {
            "extra_prolonged_degree_zero_symbol_cohomology_lower_bound": 15,
            "metric_symbol_cohomology_dimension": 0,
            "finite_order_filtration_compatible_SDR_exists": False,
            "reason": "a filtered differential SDR would induce an associated-graded quasi-isomorphism, contradicted by the noncharacteristic symbol cohomology mismatch",
        },
        "repair_boundary": {
            "necessary_new_incoming_symbol_rank_at_this_stratum": 15,
            "type_correct_repair": "adjoin a cyclic mapping cone for the parent detour/cotangent complement rather than trying to contract the bare multiplier saddle",
            "sufficiency_claimed": False,
        },
        "flags": {
            "NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1": True,
            "CURRENT_CARRIER_SDR_OBSTRUCTED": True,
            "METRIC_NONCHARACTERISTIC_SYMBOL_EXACT": True,
            "MULTIPLIER_SYMBOL_COHOMOLOGY_NONZERO": True,
            "SUPPORT_LOCAL_AUTOMORPHISM_SDR": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "LARGER_MAPPING_CONE_REPAIR_OBSTRUCTED": False,
            "OPEN_BACKGROUND_CLASS": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": (
                "At the timelike noncharacteristic covector (1,0,0,0), the metric Bach symbol complex is exact, while the current 288-component cyclic automorphism saddle has at least fifteen degree-zero symbol-cohomology directions in the multiplier block. Therefore this carrier admits no finite-order filtration-compatible differential SDR onto the metric graph."
            ),
            "not_claimed": [
                "an obstruction to a larger cyclic mapping-cone prolongation",
                "an obstruction to Green hyperbolicity after repair",
                "a global solution-space cohomology calculation",
                "an open-background no-go theorem",
                "a nonlinear or quantum obstruction",
            ],
        },
        "next_gate": "C_G2_NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR",
        "source_manifest": sources,
    }


def render_report(certificate: dict[str, object]) -> str:
    obstruction = certificate["obstruction"]
    return f"""# Nariai automorphism cyclic Bach SDR symbol obstruction

At the timelike covector `(1,0,0,0)`, the exact metric symbol complex has
zero cohomology: its ranks are `4,5,4`.  The parent Yang--Mills middle has
rank `45` on a 60-dimensional fibre, hence a 15-dimensional kernel.

The prolonged multiplier `lambda_C1` has no incoming arrow and its outgoing
symbol factors through `M2`.  Consequently the current cyclic carrier has at
least `{obstruction['extra_prolonged_degree_zero_symbol_cohomology_lower_bound']}`
extra degree-zero symbol classes on a stratum where the metric complex has
none.  A finite-order filtration-compatible SDR would induce an
associated-graded quasi-isomorphism, so it cannot exist.

This is a scoped obstruction to the present 288-component saddle, not to an
enlarged cyclic prolongation.  The next gate is
`{certificate['next_gate']}`: adjoin the parent detour/cotangent mapping cone
that kills the extra multiplier copy before attempting Green transfer.
"""


def _validate(certificate: dict[str, object]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate = build()
    _validate(certificate)
    report = render_report(certificate)
    if args.guards:
        if certificate["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
            raise AssertionError("obstructed SDR was promoted")
        if certificate["flags"]["LARGER_MAPPING_CONE_REPAIR_OBSTRUCTED"]:
            raise AssertionError("larger repair was overruled")
    if args.write:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report)
    if args.check:
        if json.loads(OUTPUT.read_text()) != certificate:
            raise SystemExit("generated SDR obstruction certificate drifted")
        if REPORT.read_text() != report:
            raise SystemExit("generated SDR obstruction report drifted")
    print("NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent verifier for the Nariai cyclic-Bach SDR obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _parse_sparse,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import endpoint_operator
from d_quotient_classical.causal_transfer.nariai_metric_bach_cyclic_bv_complex import kernel as metric_kernel


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-automorphism-cyclic-bach-sdr-symbol-obstruction-v1.schema.json"
ZETA = (sp.Integer(1), sp.Integer(0), sp.Integer(0), sp.Integer(0))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _principal(table: dict[tuple[int, ...], sp.Matrix], order: int) -> sp.Matrix:
    sample = next(iter(table.values()))
    return sum(
        (
            sp.prod(ZETA[axis] for axis in word) * coefficient
            for word, coefficient in table.items()
            if len(word) == order
        ),
        sp.zeros(*sample.shape),
    ).applyfunc(sp.expand)


def verify() -> None:
    certificate = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    dependency = certificate["dependency_ref"]
    if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
        raise AssertionError("cyclic dependency digest drifted")
    for relative, digest in certificate["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source digest drifted: {relative}")
    stratum = certificate["stratum"]
    weights = stratum["prolonged_block_weights"]
    if weights != [0, 1, 1, 1, 3, 5, 5, 6]:
        raise AssertionError("prolonged Rees weights drifted")
    if stratum["metric_block_weights"] != [0, 1, 5, 6]:
        raise AssertionError("metric Rees weights drifted")
    for key, order in stratum["arrow_orders"].items():
        target, source = (int(item) for item in key.split(","))
        if order > weights[target] - weights[source]:
            raise AssertionError("arrow escaped declared Rees filtration")
    if stratum["order_defects"]:
        raise AssertionError("Rees order defect was serialized")

    automorphism = automorphism_fixture()
    endpoint = endpoint_operator()
    metric = metric_kernel()
    d1 = _principal(automorphism["d_aut"], 1)
    k1 = _principal(automorphism["middle"]["first_bgg"], 1)
    m2 = _principal(automorphism["middle"]["yang_mills_middle"], 2)
    b4 = _principal(endpoint["action_bach"], 4)
    l12 = _principal(automorphism["corrected_l1"], 2)
    phi4 = _principal(automorphism["phi"], 4)
    ksharp1 = _principal(metric["k_sharp"], 1)
    if [d1.rank(), k1.rank(), m2.rank(), b4.rank(), ksharp1.rank()] != [15, 4, 45, 5, 4]:
        raise AssertionError("independent symbol ranks drifted")
    if any(matrix.rank() for matrix in (m2 * d1, b4 * k1, ksharp1 * b4, phi4 - m2 * l12)):
        raise AssertionError("independent symbol complex identity drifted")

    kernel_m = sp.Matrix.hstack(*m2.nullspace())
    if kernel_m.cols != 15 or m2 * kernel_m != sp.zeros(60, 15):
        raise AssertionError("M2 kernel dimension drifted")
    if _parse_sparse(certificate["kernel_witness"]["M2_kernel_basis"]) != kernel_m:
        raise AssertionError("serialized M2 kernel witness drifted")
    algebraic = automorphism["middle"]["algebraic"]
    phi_sharp4 = (
        algebraic.endpoint_field_pairing.inv()
        * l12.T
        * algebraic.one_form_pairing
        * m2
    ).applyfunc(sp.expand)
    if phi_sharp4 * kernel_m != sp.zeros(9, 15):
        raise AssertionError("multiplier kernel escaped Phi-sharp")

    kernel_b = sp.Matrix.hstack(*b4.nullspace())
    kernel_ksharp = sp.Matrix.hstack(*ksharp1.nullspace())
    if sp.Matrix.hstack(k1, kernel_b).rank() != 4:
        raise AssertionError("metric kernel B differs from image K")
    if sp.Matrix.hstack(b4, kernel_ksharp).rank() != 5:
        raise AssertionError("metric kernel Ksharp differs from image B")

    cyclic = json.loads((ROOT / dependency["path"]).read_text())
    incoming_lambda = [
        entry for entry in cyclic["operators"]["abstract_Q"]["entries"]
        if entry[0] == 3
    ]
    if incoming_lambda:
        raise AssertionError("multiplier unexpectedly acquired an incoming arrow")
    if certificate["kernel_witness"]["leading_lambda_targets"] != [
        "a_sharp via M2", "h_sharp via Phi_sharp4"
    ]:
        raise AssertionError("leading multiplier targets drifted")
    obstruction = certificate["obstruction"]
    if obstruction != {
        "extra_prolonged_degree_zero_symbol_cohomology_lower_bound": 15,
        "metric_symbol_cohomology_dimension": 0,
        "finite_order_filtration_compatible_SDR_exists": False,
        "reason": "a filtered differential SDR would induce an associated-graded quasi-isomorphism, contradicted by the noncharacteristic symbol cohomology mismatch",
    }:
        raise AssertionError("obstruction statement drifted")
    if certificate["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"] is not False:
        raise AssertionError("obstructed SDR was promoted")
    if certificate["flags"]["LARGER_MAPPING_CONE_REPAIR_OBSTRUCTED"] is not False:
        raise AssertionError("larger repair was overruled")
    print("NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1: independently verified")


if __name__ == "__main__":
    verify()

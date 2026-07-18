#!/usr/bin/env python3
"""Reduce the curved Endo n=1/n=2 ghost rows to five minimal carriers.

On nonzero modes the exact Endo heat-kernel formula integrates to

    G_H0 = G_F - (1/3) d Delta_0^-2 delta.

Inserting this identity into Tr log(H0+W), with W=-2 Ric, leaves two
one-insertion and three two-insertion trace carriers.  This module certifies
that exact reduction and its rational coefficients.  It deliberately does
not evaluate the remaining minimal vector/scalar curvature form factors.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n1-n2-hodge-resolvent-reduction-v1.schema.json"
DEPENDENCIES = {
    "Endo_Duhamel_reduction": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json",
    "n3_five_carrier_projection": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _trace(value: list[list[Fraction]]) -> Fraction:
    return sum((value[i][i] for i in range(len(value))), Fraction(0))


def _trace_word(*factors: list[list[Fraction]]) -> Fraction:
    product = factors[0]
    for factor in factors[1:]:
        product = _matmul(product, factor)
    return _trace(product)


def _flat_fixture() -> dict[str, Any]:
    """A rational noncommuting fixture for the resolvent trace coefficients."""

    lam = Fraction(5, 2)
    identity = [[Fraction(int(i == j)) for j in range(4)] for i in range(4)]
    longitudinal = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    longitudinal[3][3] = Fraction(1)
    gf = [[entry / lam for entry in row] for row in identity]
    ell = [[entry / lam for entry in row] for row in longitudinal]
    gh0 = [
        [gf[i][j] - ell[i][j] / 3 for j in range(4)]
        for i in range(4)
    ]
    h0 = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for i in range(3):
        h0[i][i] = lam
    h0[3][3] = Fraction(3, 2) * lam
    w = [
        [Fraction(2), Fraction(1), Fraction(0), Fraction(3)],
        [Fraction(1), Fraction(0), Fraction(2), Fraction(1)],
        [Fraction(0), Fraction(2), Fraction(-2), Fraction(4)],
        [Fraction(3), Fraction(1), Fraction(4), Fraction(1)],
    ]
    inverse_residual = _matmul(h0, gh0)
    inverse_ok = inverse_residual == identity

    direct_n1 = _trace_word(gh0, w)
    reduced_n1 = _trace_word(gf, w) - Fraction(1, 3) * _trace_word(ell, w)
    direct_n2 = -Fraction(1, 2) * _trace_word(gh0, w, gh0, w)
    reduced_n2 = (
        -Fraction(1, 2) * _trace_word(gf, w, gf, w)
        + Fraction(1, 3) * _trace_word(gf, w, ell, w)
        - Fraction(1, 18) * _trace_word(ell, w, ell, w)
    )

    # The already completed n=3 projector sectors supply a useful independent
    # coefficient cross-check.  Cyclic trace classes with 0,1,2,3 longitudinal
    # factors have these total coefficients before W^3 is inserted.
    n3_cyclic_coefficients = [
        Fraction(1, 3),
        Fraction(-1, 3),
        Fraction(1, 9),
        Fraction(-1, 81),
    ]
    direct_n3 = Fraction(1, 3) * _trace_word(gh0, w, gh0, w, gh0, w)
    reduced_n3 = (
        n3_cyclic_coefficients[0] * _trace_word(gf, w, gf, w, gf, w)
        + n3_cyclic_coefficients[1] * _trace_word(gf, w, gf, w, ell, w)
        + n3_cyclic_coefficients[2] * _trace_word(gf, w, ell, w, ell, w)
        + n3_cyclic_coefficients[3] * _trace_word(ell, w, ell, w, ell, w)
    )
    if not inverse_ok or direct_n1 != reduced_n1 or direct_n2 != reduced_n2 or direct_n3 != reduced_n3:
        raise AssertionError("Hodge resolvent fixture failed")
    return {
        "lambda": _q(lam),
        "symmetric_noncommuting_W": [[_q(entry) for entry in row] for row in w],
        "H0_times_GH0_is_identity": inverse_ok,
        "n1_direct_and_reduced": _q(direct_n1),
        "n2_direct_and_reduced": _q(direct_n2),
        "n3_direct_and_reduced": _q(direct_n3),
        "n3_cyclic_longitudinal_coefficients": [_q(value) for value in n3_cyclic_coefficients],
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    endo = values["Endo_Duhamel_reduction"]
    n3 = values["n3_five_carrier_projection"]
    if (
        endo.get("exact_Endo_split", {}).get("alpha") != _q(Fraction(-1, 2))
        or endo.get("exact_Endo_heat_kernel", {}).get("proper_time_upper_multiplier")
        != _q(Fraction(3, 2))
        or endo.get("exact_Endo_split", {}).get("local_perturbation") != "W=-2 Ric"
        or n3.get("quotient_section", {}).get("quotient_dimension") != 10
        or n3.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
    ):
        raise ValueError("n=1/n=2 Hodge-resolvent dependencies drifted")

    n1 = [
        {
            "carrier_id": "N1_VECTOR",
            "coefficient": _q(1),
            "trace": "Tr_1(G_F W)",
            "cubic_extraction": "retain the O(curvature^2) part of G_F and multiply by W=O(curvature)",
        },
        {
            "carrier_id": "N1_LONGITUDINAL_SCALAR",
            "coefficient": _q(Fraction(-1, 3)),
            "trace": "Tr_0(Delta_0^-2 delta W d)",
            "cubic_extraction": "retain total O(curvature^3), including covariant derivatives and measure",
        },
    ]
    n2 = [
        {
            "carrier_id": "N2_VECTOR_VECTOR",
            "coefficient": _q(Fraction(-1, 2)),
            "trace": "Tr_1(G_F W G_F W)",
            "cubic_extraction": "retain the O(curvature) correction beyond the two W insertions",
        },
        {
            "carrier_id": "N2_VECTOR_LONGITUDINAL",
            "coefficient": _q(Fraction(1, 3)),
            "trace": "Tr_0(Delta_0^-2 delta W G_F W d)",
            "cubic_extraction": "retain the O(curvature) correction beyond the two W insertions",
        },
        {
            "carrier_id": "N2_LONGITUDINAL_LONGITUDINAL",
            "coefficient": _q(Fraction(-1, 18)),
            "trace": "Tr_0(Delta_0^-2 delta W d Delta_0^-2 delta W d)",
            "cubic_extraction": "retain the O(curvature) correction beyond the two W insertions",
        },
    ]

    result = {
        "schema": "quantum-weyl-generic-background-ghost-n1-n2-hodge-resolvent-reduction-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION",
        "result_state": "CURVED_ENDO_N1_N2_REDUCED_EXACTLY_TO_FIVE_MINIMAL_VECTOR_SCALAR_RESOLVENT_CARRIERS",
        "lifecycle_state": "N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED_FIVE_MINIMAL_CARRIERS_UNEVALUATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": endo["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "mode_domain": "nonzero ghost modes on a compact manifold without boundary",
            "curvature_order": "cubic part of the W=-2 Ric insertion series",
            "operator_scope": "generic-background Diff-Weyl ghost Endo block only",
        },
        "Hodge_intertwining": {
            "identities": ["F d=d Delta_0", "delta F=Delta_0 delta"],
            "exact_form_eigenvalue": _q(Fraction(3, 2)),
            "coexact_form_eigenvalue": _q(1),
            "zero_modes_primed": True,
        },
        "proper_time_to_resolvent": {
            "heat_kernel_identity": "K_H0(t)=K_F(t)-d d_prime integral_t^(3t/2) ds K_Delta0(s)",
            "Fubini_domain": "for fixed s>0, 2s/3<=t<=s",
            "Fubini_weight": "s/3",
            "scalar_moment": "integral_0^infinity ds s K_Delta0(s)=Delta_0^-2",
            "resolvent_identity": "G_H0=G_F-(1/3)d Delta_0^-2 delta",
            "longitudinal_operator": "L=d Delta_0^-2 delta",
            "flat_inverse": "G_H0=p^-2(Pi_T+(2/3)Pi_L)",
        },
        "log_determinant_expansion": {
            "formula": "Tr log(H0+W)=Tr log H0+sum_n>=1 (-1)^(n+1) Tr((G_H0 W)^n)/n",
            "W": "-2 Ric",
            "n1_carriers": n1,
            "n2_carriers": n2,
            "carrier_count": 5,
            "cyclic_trace_used_to_merge_mixed_n2_orderings": True,
        },
        "cubic_order_requirements": {
            "N1": "second-curvature-order minimal vector/scalar kernels",
            "N2": "first-curvature-order minimal vector/scalar kernels",
            "N3": "flat kernels; already projected in the dependency certificate",
            "measure_and_parallel_transport": "retained inside the covariant minimal kernels",
            "flat_metric_vertex_substitution_is_sufficient": False,
        },
        "exact_fixture": _flat_fixture(),
        "coefficient_disposition": {
            "ghost_n1_nonminimal_reduction": "COMPUTED",
            "ghost_n2_nonminimal_reduction": "COMPUTED",
            "ghost_n1_five_minimal_carriers_evaluated": "NOT_COMPUTED",
            "ghost_n2_five_minimal_carriers_evaluated": "NOT_COMPUTED",
            "ghost_n3_five_carrier_parametric_projection": "COMPUTED",
            "complete_ghost_third_curvature_functions": "NOT_COMPUTED",
            "physical_fourth_order_Hessian_functions": "NOT_COMPUTED",
        },
        "claim_flags": {
            "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED": True,
            "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED": True,
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED": False,
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED": False,
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "EVALUATE_FIVE_MINIMAL_VECTOR_SCALAR_N1_N2_RESOLVENT_CARRIERS_AND_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate integrates the exact Endo heat-kernel identity on primed nonzero modes and reduces the unresolved W=-2 Ric n=1 and n=2 ghost terms to exactly five covariant minimal vector/scalar resolvent carriers. The rational coefficients 1,-1/3 and -1/2,1/3,-1/18 are fixed by the Hodge resolvent and cyclicity, and a noncommuting exact fixture also recovers the completed n=3 longitudinal-sector weights. The five remaining carriers still require second- and first-curvature-order minimal kernels respectively; they have not been evaluated or projected to the repository functions. The complete ghost determinant, physical fourth-order Hessian, repository cubic functions or coefficients, Gamma1/Q1, residual transfer, Lorentzian QME, Hadamard, particle, positivity, scattering and unitarity claims remain open."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    expansion = value["log_determinant_expansion"]
    if [row["coefficient"] for row in expansion["n1_carriers"]] != [
        _q(1),
        _q(Fraction(-1, 3)),
    ]:
        raise ValueError("n=1 Hodge coefficients drifted")
    if [row["coefficient"] for row in expansion["n2_carriers"]] != [
        _q(Fraction(-1, 2)),
        _q(Fraction(1, 3)),
        _q(Fraction(-1, 18)),
    ]:
        raise ValueError("n=2 Hodge coefficients drifted")
    if expansion["carrier_count"] != 5:
        raise ValueError("n=1/n=2 minimal carrier count drifted")
    flags = value["claim_flags"]
    true_flags = {
        "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED",
        "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED",
    }
    if any(flags[key] is not True for key in true_flags) or any(
        flag is not False for key, flag in flags.items() if key not in true_flags
    ):
        raise ValueError("n=1/n=2 Hodge reduction crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale n=1/n=2 Hodge-resolvent certificate: {OUTPUT}")
    print("GENERIC GHOST N1/N2: EXACT FIVE-CARRIER HODGE RESOLVENT REDUCTION; CARRIER EVALUATION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

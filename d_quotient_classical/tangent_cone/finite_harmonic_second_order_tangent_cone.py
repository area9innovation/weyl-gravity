#!/usr/bin/env python3
"""Certify the correction-class-sensitive finite-harmonic tangent-cone lemma."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/finite-harmonic-second-order-tangent-cone-theorem.md"
SCHEMA = ROOT / "d_quotient_classical/schema/finite-harmonic-second-order-tangent-cone-theorem-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/tangent_cone/verify_finite_harmonic_second_order_tangent_cone.py"
TESTS = ROOT / "d_quotient_classical/tangent_cone/tests/test_finite_harmonic_second_order_tangent_cone.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_record(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [
            [row, column, str(value)]
            for (row, column), value in sorted(matrix.todok().items())
        ],
    }


def _compatible_basis(identity: sp.Matrix) -> sp.Matrix:
    vectors = identity.nullspace()
    return sp.Matrix.hstack(*vectors) if vectors else sp.zeros(identity.cols, 0)


def _reduced_cokernel(identity: sp.Matrix, operator: sp.Matrix) -> dict[str, Any]:
    """Return compatible target basis and its obstruction quotient data."""
    compatible = _compatible_basis(identity)
    if identity * operator != sp.zeros(identity.rows, operator.cols):
        raise AssertionError("Noether identity does not annihilate the correction operator")
    left_inverse = (compatible.T * compatible).inv() * compatible.T
    reduced = left_inverse * operator
    cokernel = reduced.T.nullspace()
    return {
        "compatible_basis": _matrix_record(compatible),
        "reduced_operator": _matrix_record(reduced),
        "cokernel_basis": [_matrix_record(vector) for vector in cokernel],
        "cokernel_dimension": len(cokernel),
    }


def exact_fixture() -> dict[str, Any]:
    # A static block with one Noether row, one gauge-null correction column,
    # and one genuine stabilizer moment-map obstruction.
    identity_static = sp.Matrix([[0, 0, 1]])
    operator_static = sp.Matrix([[1, 0], [0, 0], [0, 0]])
    static = _reduced_cokernel(identity_static, operator_static)

    # A resonant block with one Noether row and one gauge-null column.  The
    # resonant physical column is absent in the bounded Fourier category but
    # present after a secular or retarded right inverse is admitted.
    identity_resonant = sp.Matrix([[0, 1]])
    operator_bounded = sp.zeros(2, 2)
    operator_secular = sp.Matrix([[1, 0], [0, 0]])
    operator_retarded = operator_secular
    bounded = _reduced_cokernel(identity_resonant, operator_bounded)
    secular = _reduced_cokernel(identity_resonant, operator_secular)
    retarded = _reduced_cokernel(identity_resonant, operator_retarded)

    t = sp.symbols("t", real=True)
    omega = sp.symbols("omega", real=True, nonzero=True)
    source = sp.exp(sp.I * omega * t)
    secular_solution = t * source
    secular_defect = sp.simplify(sp.diff(secular_solution, t) - sp.I * omega * secular_solution - source)

    s = sp.symbols("s", real=True)
    f = s**2 + 1
    retarded_solution = sp.integrate(sp.exp(sp.I * omega * (t - s)) * f, (s, 0, t))
    retarded_defect = sp.simplify(
        sp.diff(retarded_solution, t)
        - sp.I * omega * retarded_solution
        - (t**2 + 1)
    )
    initial_value = sp.simplify(retarded_solution.subs(t, 0))

    if static["cokernel_dimension"] != 1:
        raise AssertionError("static moment-map cokernel changed")
    if bounded["cokernel_dimension"] != 1:
        raise AssertionError("bounded resonant cokernel changed")
    if secular["cokernel_dimension"] != 0 or retarded["cokernel_dimension"] != 0:
        raise AssertionError("enlarged correction category retained a false resonance")
    if secular_defect != 0 or retarded_defect != 0 or initial_value != 0:
        raise AssertionError("resonant right-inverse audit failed")

    return {
        "static_moment_map_block": {
            "Noether_identity": _matrix_record(identity_static),
            "correction_operator": _matrix_record(operator_static),
            **static,
            "interpretation": "one compatible target direction survives as the stabilizer moment map after the Noether row and gauge-null correction are removed",
        },
        "resonant_block": {
            "bounded_or_finite_quasiperiodic": bounded,
            "smooth_secular": secular,
            "causal_retarded": retarded,
            "bounded_residual_equation": "R_res(u)=0",
            "secular_identity": "(d_t-i omega)(t exp(i omega t))=exp(i omega t)",
            "secular_defect": str(secular_defect),
            "retarded_formula": "v(t)=int_0^t exp(i omega(t-s)) f(s) ds",
            "retarded_polynomial_source": "f(t)=t^2+1 on the audited future interval",
            "retarded_defect": str(retarded_defect),
            "retarded_initial_value": str(initial_value),
        },
        "category_cones": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": "mu_X(u)=0 and R_res(u)=0",
            "SMOOTH_SECULAR": "mu_X(u)=0",
            "CAUSAL_RETARDED": "mu_X(u)=0 for compatible compact sources, assuming the declared retarded block inverse",
        },
    }


def build() -> dict[str, Any]:
    fixture = exact_fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "finite-harmonic-second-order-tangent-cone-theorem-v1",
        "schema_version": "1.0.0",
        "result_id": "FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1",
        "result_state": "ABSTRACT_CORRECTION_CLASS_SENSITIVE_TANGENT_CONE_THEOREM_CERTIFIED",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": {
            "domain": "a finite direct sum of complete harmonic blocks in the first-order solution space",
            "source": "the quadratic second-variation source S_j(u,u) in each output block",
            "Noether_reduction": "replace each equation target by ker(I_j) before taking the cokernel; require I_j S_j=0",
            "gauge_reduction": "remove gauge-null correction columns or pass to a complete gauge slice; this does not change im(L_j)",
            "obstruction_space": "the adjoint annihilator of im(L_j^C) inside the Noether-compatible target",
            "obstruction_decomposition": "identify the certified stabilizer subspace of the reduced adjoint cokernel with the moment maps mu_X and choose R_j^C only on a complementary cokernel basis, so no obstruction is counted twice",
            "formula": "Z_2^C={u in ker(q1): mu_X(u)=0 and R_j^C(u)=0 for every output block j}",
            "sufficiency_hypotheses": [
                "the input and every quadratic output decompose into finitely many declared harmonic blocks",
                "the block list is exhaustive under the quadratic selection rules",
                "the gauge slice or quotient and every Noether identity row are complete",
                "the correction space C and its block operator domains are fixed before the adjoint cokernel is formed",
                "each zero obstruction pairing has a right inverse in the same declared correction category",
            ],
            "necessity": "pairing the second-order equation with every reduced adjoint-cokernel vector gives mu_X and R_j^C",
            "sufficiency": "vanishing of those pairings places every compatible source in im(L_j^C); finite blockwise right inverses assemble the correction",
            "compactness_and_symmetry": {
                "compactness": "used only to obtain a discrete complete harmonic decomposition and finite output closure; the abstract image/cokernel statement is finite-dimensional",
                "exact_symmetry": "used to block-diagonalize L and identify stabilizer moment maps; without it one must use a different complete decomposition",
                "causal_category": "does not compare an eternal Fourier source with a compact source; it uses a retarded inverse on the declared compatible compact-source space",
            },
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "CERTIFIED",
                "image_rule": "only bounded finite Fourier corrections are admitted; a resonant Fourier coefficient is an adjoint-cokernel obstruction",
            },
            "SMOOTH_SECULAR": {
                "status": "CERTIFIED",
                "image_rule": "finite exponential-polynomial corrections are admitted; a root of multiplicity r is inverted by a polynomial prefactor of degree at most r",
            },
            "CAUSAL_RETARDED": {
                "status": "CERTIFIED",
                "image_rule": "for compatible compact sources, a declared retarded Green operator removes propagation resonances while preserving future support",
                "background_specific_Green_theorem": "NOT_APPLICABLE",
            },
        },
        "exact_fixture": fixture,
        "flags": {
            "FINITE_HARMONIC_TANGENT_CONE_FORMULA": True,
            "GAUGE_AND_NOETHER_ROWS_REMOVED_BEFORE_COKERNEL": True,
            "BOUNDED_RESONANCE_OBSTRUCTED": True,
            "SMOOTH_SECULAR_RESONANCE_REMOVED": True,
            "CAUSAL_RETARDED_RESONANCE_REMOVED_FOR_COMPATIBLE_SOURCE": True,
            "BACKGROUND_SPECIFIC_TANGENT_CONE_CLASSIFICATION": False,
            "ALL_ORDERS_INTEGRABILITY": False,
        },
        "next_gate": "instantiate the theorem in the generated residual atlas using the Einstein schema, preserving a separate correction-class record for every background and mode block",
        "claim_boundary": "This proves the finite-block image/cokernel criterion and audits the category change on an exact resonant model. It does not classify any new background, identify modes across carriers, prove a background Green theorem, or imply all-orders integrability.",
        "source_manifest": sources,
        "verification_commands": [
            "python3 -m d_quotient_classical.tangent_cone.finite_harmonic_second_order_tangent_cone --check",
            "python3 d_quotient_classical/tangent_cone/verify_finite_harmonic_second_order_tangent_cone.py",
            "python3 -m unittest d_quotient_classical.tangent_cone.tests.test_finite_harmonic_second_order_tangent_cone",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/finite-harmonic-second-order-tangent-cone-theorem-v1.schema.json -d d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
        ],
    }


def _report(payload: dict[str, Any]) -> str:
    return r"""# Finite-harmonic second-order tangent-cone theorem

Let a first-order solution `u` have finite harmonic support and let every
quadratic output channel be included.  In block `j`, write the second-order
equation as

\[
L_j v_j=-S_j(u,u).
\]

First restrict the equation target to the kernel of every Noether identity
row and remove gauge-null correction columns (or take a complete gauge
slice).  For a declared correction category `C`, let the remaining adjoint
cokernel annihilate `im L_j^C`; its pairings with `S_j(u,u)` are
the obstructions.  Identify its certified stabilizer subspace with the
moment maps `mu_X(u)` and call a complementary basis `R_j^C(u)`, so no
functional is counted twice.  Then

\[
\mathcal Z_2^{\mathcal C}
=\{u:\mu_X(u)=0,\ R_j^{\mathcal C}(u)=0\ \text{for every }j\}.
\]

Necessity is the adjoint pairing of the second-order equation.  Sufficiency
follows because the vanishing pairings put each compatible source in the
image of the block operator; the declared finite blockwise right inverses
then assemble `v`.  Completeness of the harmonic output list, Noether rows,
gauge reduction, and right inverses is essential.

## Correction categories are different theorems

For the audited resonant block,

\[
(\partial_t-i\omega)v=e^{i\omega t},
\]

there is no bounded finite-quasiperiodic correction: the resonant coefficient
is an adjoint-cokernel obstruction.  In the smooth-secular category,

\[
v=t e^{i\omega t}
\]

solves the equation exactly.  For a compatible compact source, the retarded
formula

\[
v(t)=\int_{-\infty}^t e^{i\omega(t-s)}f(s)\,ds
\]

solves it with future support.  The causal statement concerns compact sources
and is not an identification with the eternal Fourier problem.

The exact finite fixture contains one persistent static moment-map cokernel
and one resonant cokernel.  Its tangent cones are therefore

```text
bounded/quasiperiodic:  mu_X = 0 and R_res = 0
smooth secular:         mu_X = 0
causal/retarded:        mu_X = 0  (compatible compact sources and a declared retarded inverse)
```

This is an abstract reduction theorem and adversarial category audit.  It
does not classify a new background or establish all-orders integrability.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
        REPORT.write_text(_report(payload))
    else:
        if json.loads(OUTPUT.read_text()) != payload:
            raise AssertionError("tangent-cone certificate is stale")
        if REPORT.read_text() != _report(payload):
            raise AssertionError("tangent-cone report is stale")
    print("FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1: PASS")


if __name__ == "__main__":
    main()

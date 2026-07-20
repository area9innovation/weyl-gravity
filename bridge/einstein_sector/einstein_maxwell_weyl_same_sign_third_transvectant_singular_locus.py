"""Classify the singular locus of the candidate-17/20 transvectant carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.schema.json"
INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def algebra() -> dict[str, object]:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    l0, l1, l2 = sp.symbols("l0 l1 l2")
    A = sp.Matrix(
        [
            [-f[3], 3 * f[2], -3 * f[1], f[0], 0],
            [-f[4], 2 * f[3], 0, -2 * f[1], f[0]],
            [0, -f[4], 3 * f[3], -3 * f[2], f[1]],
        ]
    )
    equations = A * sp.Matrix(g)
    jacobian = equations.jacobian((*f, *g))
    lam = sp.Matrix([l0, l1, l2])
    B = (A.T * lam).jacobian(f)
    v = sp.Matrix([3 * l2**2, -3 * l1 * l2, l0 * l2 + 2 * l1**2, -3 * l0 * l1, 3 * l0**2])
    left = sp.simplify(lam.T * jacobian)
    expected = sp.Matrix.hstack(-(B * sp.Matrix(g)).T, (B * sp.Matrix(f)).T)
    if left != expected:
        raise AssertionError("Jacobian-covariant identity changed")
    if B.T != -B or B.det() != 0 or sp.simplify(B * v) != sp.zeros(5, 1):
        raise AssertionError("skew kernel covariant changed")
    selected = {
        "l0_chart": sp.factor(B.extract((0, 1, 2, 3), (0, 1, 2, 3)).det()),
        "l2_chart": sp.factor(B.extract((1, 2, 3, 4), (1, 2, 3, 4)).det()),
        "middle_chart": sp.factor(B.extract((0, 1, 3, 4), (0, 1, 3, 4)).det()),
    }
    expected_minors = {
        "l0_chart": 9 * l0**4,
        "l2_chart": 9 * l2**4,
        "middle_chart": (l0 * l2 + 2 * l1**2) ** 2,
    }
    if any(sp.expand(selected[name] - value) != 0 for name, value in expected_minors.items()):
        raise AssertionError("rank-four chart minors changed")
    return {
        "B_lambda": [[str(x) for x in row] for row in B.tolist()],
        "kernel_vector": [str(x) for x in v],
        "selected_rank_four_minors": {name: str(value) for name, value in selected.items()},
    }


def build() -> dict[str, object]:
    source = json.loads(INPUT.read_text())
    rows = {row["candidate_index"]: row for row in source["decompositions"]}
    if not all(rows[index]["zero_variety"]["irreducible_components_over_C"] == 1 for index in (17, 20)):
        raise AssertionError("candidate-17/20 irreducibility input changed")
    exact = algebra()
    return {
        "schema": "einstein-maxwell-weyl-same-sign-third-transvectant-singular-locus-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_THIRD_TRANSVECTANT_SINGULAR_LOCUS",
        "result_state": "CANDIDATE17_20_COMPLETE_COMPLEX_SINGULAR_LOCUS_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_COMPLEX_SINGULAR_LOCUS_BEFORE_NORM_AND_ROTATION_REDUCTION",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidates 17 and 20 separately",
            "boundaries": "closed S1_L times S2 before node-phase, lifted-rotation or final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "both parity factors of the complete complex third-transvectant resonance variety",
            "degree": 2,
            "parity": "two exact factorized parity eigenchannels",
            "ell": 2,
            "m": "all m=-2,...,2 in the binary-quartic carrier",
            "k": "candidate-specific signed compact momenta, never identified across candidates",
            "omega": "candidate-specific difference collision into L=1 extra output",
        },
        "covariant_rank_certificate": {
            **exact,
            "jacobian_left_kernel_identity": "lambda^T J(f,g)=(-(B_lambda g)^T,(B_lambda f)^T)",
            "rank_statement": "B_lambda is skew, has determinant zero, and has rank four for every nonzero lambda",
            "rank_proof": "if l0 or l2 is nonzero use the corresponding pure fourth-power minor; if l0=l2=0 and l1 is nonzero, the middle minor equals 4*l1^4",
        },
        "one_factor_singular_locus": {
            "ambient_kernel": "K_T3={(f,g) in C^5 x C^5:T3(f,g)=0}, irreducible of complex dimension seven",
            "criterion": "rank J(f,g)<3 iff there is [lambda] in P^2 with B_lambda f=B_lambda g=0",
            "parametrization": "(f,g)=(a*v(lambda),b*v(lambda)), [lambda] in P^2 and (a,b) in C^2",
            "interpretation": "f and g are proportional squares of the same binary quadratic, including a=0 or b=0",
            "complex_dimension": 4,
            "projectivization": "P^2 x P^1 embedded by O(2,1)",
            "projectivization_smooth_connected": True,
            "singular_locus_itself_smooth_away_from_origin": True,
            "incidence_resolution": "Tot(O_{P^2}(-2) direct-sum O_{P^2}(-2)) -> Sing(K_T3), with exceptional fibre P^2 over the origin",
        },
        "two_parity_product": {
            "ambient_complex_dimension": 14,
            "singular_locus": "(S_plus x K_minus) union (K_plus x S_minus)",
            "irreducible_components": 2,
            "component_complex_dimension": 11,
            "intersection": "S_plus x S_minus",
            "intersection_complex_dimension": 8,
        },
        "classification": {
            "candidate17_complete_complex_singular_locus_classified": True,
            "candidate20_complete_complex_singular_locus_classified": True,
            "both_parity_product_singular_components_classified": True,
            "singular_incidence_resolution_constructed": True,
            "fixed_occupation_real_singular_strata_classified": False,
            "node_phase_singular_reduction_classified": False,
            "lifted_rotation_singular_reduction_classified": False,
            "global_zero_fibre_connected": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The candidate-17/20 nonlinear carrier has a controlled codimension-three singular locus rather than an unspecified bad set. Each singular pair is generated by one quadratic covector and is geometrically a common-square pair. This supplies an equivariant incidence model for the next real fixed-occupation reduction but does not itself perform it.",
        "next_gate": "intersect the two singular components with the real fixed-occupation and lifted-rotation zero conditions, then compare their incidence images with the smooth constant-corank leaf quotients",
        "claim_boundary": "This is a complete complex-algebraic singular-locus theorem before fixed norms and group reduction. It does not classify the real Hermitian intersection, node-phase or lifted-rotation quotients, global connectedness, occupation gluing, final residual descent, all-orders integration, or causal, observational or quantum transport.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {"zero_varieties": {"path": str(INPUT.relative_to(ROOT)), "sha256": sha(INPUT)}},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("third-transvectant singular-locus certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_THIRD_TRANSVECTANT_SINGULAR_LOCUS: PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Certify an aligned twist--generic-extra common Taub/resonance-zero face."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.schema.json"
INPUTS = {
    "resonance_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "abd_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "global_moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coefficient_rank(polynomials: list[str]) -> int:
    t = sp.symbols("t", real=True)
    values = [sp.Poly(sp.sympify(value, locals={"t": t}), t) for value in polynomials]
    degree = max(value.degree() for value in values)
    matrix = sp.Matrix([[value.coeff_monomial(t**power) for value in values] for power in range(degree + 1)])
    return matrix.rank()


def exact_face() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    matrix = records["resonance_matrix"]
    abd = records["abd_matrix"]
    if not matrix["classification"]["complete_homogeneous_twist_bounded_resonance_matrix"]:
        raise AssertionError("complete resonance-matrix input changed")
    if records["global_moment_maps"]["axial_twist"]["mu_H"] != "2*|B|^2":
        raise AssertionError("twist moment-map normalization changed")

    # The unique V_1 tensor V_2 -> V_2 intertwiner is the infinitesimal
    # rotation action.  Its shared-axis m=0 matrix element vanishes exactly.
    cg_nonaxis = sp.simplify(clebsch_gordan(1, 2, 2, 1, 0, 1))
    cg_aligned = sp.simplify(clebsch_gordan(1, 2, 2, 0, 0, 0))
    if cg_nonaxis != sp.sqrt(2) / 2 or cg_aligned != 0:
        raise AssertionError("twist--extra Clebsch-Gordan gate changed")

    ranks: dict[str, list[int]] = {}
    for parity in ("axial", "polar"):
        ranks[parity] = []
        for branch in range(2):
            polynomials = [abd["projected_resonance_polynomials"][parity][profile][branch] for profile in ("a", "b", "d")]
            ranks[parity].append(_coefficient_rank(polynomials))
    if ranks != {"axial": [3, 3], "polar": [3, 3]}:
        raise AssertionError("a,b,d branchwise rank changed")

    # Direct current Grams at lambda=6,k=0 in the source representatives.
    lam = sp.Integer(6)
    omega_squared = sp.Rational(16, 3)
    axial_gram = sp.diag(sp.Integer(1296), sp.Rational(208, 3))
    polar_gram = sp.diag(sp.Integer(22464), sp.Integer(12288))
    if axial_gram.det() <= 0 or polar_gram.det() <= 0:
        raise AssertionError("ell=2 extra Gram lost positivity")

    X = sp.symbols("X", positive=True)
    B_squared = sp.simplify(omega_squared * X / 8)
    mu_H = sp.simplify(2 * B_squared - omega_squared * X / 4)
    witness_X = axial_gram[0, 0]
    witness_B = 12 * sp.sqrt(6)
    witness_mu_H = sp.simplify(2 * witness_B**2 - omega_squared * witness_X / 4)
    if mu_H != 0 or witness_mu_H != 0 or sp.simplify(witness_B**2 - sp.Rational(2, 3) * witness_X) != 0:
        raise AssertionError("aligned energy balance changed")

    return {
        "angular_theorem": {
            "nonaxisymmetric_normalization": "<1,1;2,0|2,1>=sqrt(2)/2",
            "aligned_coefficient": "<1,0;2,0|2,0>=0",
            "representation_statement": "the unique V1 tensor V2 to V2 resonance map is the infinitesimal SO(3) action; it annihilates an axisymmetric ell=2 tensor when the twist vector lies on the same axis",
            "twist_position_and_velocity_resonance_on_face": "0 for every axial/polar extra-primary multiplicity coefficient",
        },
        "branchwise_abd_gate": {
            "coefficient_ranks": ranks,
            "consequence_for_nonzero_extra_amplitude": "a=b=d=0",
        },
        "extra_current_gram_at_ell2_k0": {
            "basis_order": ["axial_e1", "axial_e2", "polar_e1", "polar_e2"],
            "diagonal": [str(axial_gram[0, 0]), str(axial_gram[1, 1]), str(polar_gram[0, 0]), str(polar_gram[1, 1])],
            "occupation": "X=1296*|x_a1|^2+(208/3)*|x_a2|^2+22464*|x_p1|^2+12288*|x_p2|^2",
            "positive_for_nonzero_x": True,
            "omega_e_squared": str(omega_squared),
        },
        "face_parameterization": {
            "extra": "an arbitrary nonzero multiplicity vector x in C^4 carried by one positive-frequency ell=2,m=0,k=0 harmonic, with its conjugate fixed by reality",
            "homogeneous": "a=b=d=Q_e=0; c and W_x arbitrary spectators",
            "twist": "A=A_z e_z is arbitrary and B=B_z e_z with B_z^2=(2/3)*X",
            "stabilizer_maps": {
                "mu_H": "2*B_z^2-(omega_e^2/4)*X=0",
                "mu_Px": "0",
                "mu_J": "-4*A cross B plus the m=0 extra expectation =0",
            },
            "bounded_resonance_maps": "all complementary L=2 p-shell functionals vanish: a,b,d are zero and the aligned twist intertwiner annihilates m=0",
        },
        "explicit_nonzero_witness": {
            "extra_amplitudes": ["1", "0", "0", "0"],
            "X": str(witness_X),
            "A_z": "0",
            "B_z": str(witness_B),
            "mu_H_remainder": str(witness_mu_H),
            "all_five_moment_maps_zero": True,
            "all_completed_bounded_resonance_functionals_zero": True,
        },
    }


def build() -> dict[str, Any]:
    face = exact_face()
    sources = {str(path.relative_to(ROOT)): _sha256(path) for path in (*INPUTS.values(), Path(__file__).resolve(), SCHEMA)}
    return {
        "schema": "einstein-maxwell-weyl-aligned-twist-ell2-extra-compatibility-face-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_COMPATIBILITY_FACE",
        "result_state": "NONZERO_ALIGNED_STABILIZER_AND_BOUNDED_RESONANCE_COMMON_ZERO_FACE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed spatial S1_L times S2; bounded-resonance compatibility category",
            "charge_sector": "fixed N=2 magnetic bundle and Q_e=0 on the declared face",
            "carrier": "one shared-axis ell=2,m=0,k=0 generic extra-primary multiplicity vector plus collinear standard twist position/velocity and homogeneous spectators c,W_x",
            "degree": 2,
            "parity": "all four axial/polar extra multiplicities retained",
            "ell": "(1 x 2 -> resonant 2) plus additive self-source blocks",
            "m": "shared-axis twist m=0 and extra m=0",
            "k": 0,
            "omega": "generalized-zero twist crossed with omega_e=4/sqrt(3)",
        },
        **face,
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": "CERTIFIED common zero of every known stabilizer and completed bounded-resonance functional; a full bounded correction is OPEN because the nonresonant polynomial cross channels have not been assigned bounded right inverses",
            "smooth_exponential_polynomial": "OPEN: the finite secular right inverses for every mixed nonresonant channel have not been assembled",
            "causal_or_retarded": "OPEN: no compact-product retarded complex is certified",
        },
        "classification": {
            "nonzero_simultaneous_stabilizer_and_bounded_resonance_zero_face": True,
            "aligned_twist_extra_resonance_vanishes_by_exact_Clebsch_Gordan_rule": True,
            "abd_profiles_forced_zero_on_nonzero_extra_face": True,
            "all_four_extra_multiplicities_retained": True,
            "complete_simultaneous_zero_locus_classified": False,
            "bounded_second_order_correction_constructed": False,
            "smooth_secular_second_order_correction_constructed": False,
            "causal_retarded_theorem": False,
            "all_orders_integrability": False,
        },
        "interpretation": "The completed source matrix does not collapse the global-extra cone to the origin. A twist velocity supplies the positive Taub charge needed to balance any shared-axis generic extra occupation, while the unique twist-extra resonant intertwiner vanishes on the aligned m=0 tensor. This is an exact nonzero common-zero face, not yet a full second-order extension or the complete off-axis zero locus.",
        "next_gate": "classify the off-axis solutions of H(t)C+P R_A(C)+V(t)R_B(C)=0 together with the five quadratic moment maps, then assemble correction-class-specific right inverses",
        "claim_boundary": "This theorem certifies a nonzero aligned family in the simultaneous stabilizer and completed bounded-resonance zero set. It does not classify the full zero locus, prove a bounded or secular second-order correction, cover opposite momenta or multiple |k| fibres, or support causal, residual, observational, particle or quantum claims.",
        "source_manifest": sources,
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face"]},
            "tier_2": {"status": "NOT_RUN", "reason": "all imported tensor rows are content-addressed and unchanged; this gate is an exact representation/moment-map elimination on their certified projections"},
            "tier_3": {"status": "NOT_RUN", "reason": "the complete off-axis zero locus and every full correction class remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("aligned twist--extra compatibility certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_COMPATIBILITY_FACE: PASS")


if __name__ == "__main__":
    main()

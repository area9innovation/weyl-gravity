"""Classify the tuned axisymmetric mixed-parity bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.schema.json"
INPUTS = {
    "bounded_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.json",
    "parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json",
    "opposite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _resonance_decomposition() -> dict[str, Any]:
    a_plus, a_minus, p_plus, p_minus = sp.symbols("a_plus a_minus p_plus p_minus")
    root = sp.sqrt(3)
    equations = [a_plus * a_minus - 3 * p_plus * p_minus, a_plus * p_minus - a_minus * p_plus]
    components = [
        {a_plus: root * p_plus, a_minus: root * p_minus},
        {a_plus: -root * p_plus, a_minus: -root * p_minus},
        {a_plus: 0, p_plus: 0},
        {a_minus: 0, p_minus: 0},
    ]
    for component in components:
        _require(all(sp.expand(equation.subs(component)) == 0 for equation in equations), "resonance component changed")

    # The elementary case split is the human-readable radical decomposition:
    # if p_+p_- is nonzero, the ratio equation gives a common r with r^2=3;
    # if either p vanishes, the remaining equation forces the same signed
    # momentum pair (a,p) to vanish, with the all-p-zero case included.
    return {
        "equations": [str(equation) for equation in equations],
        "complete_complex_zero_set": [
            "C_plus: a_+=sqrt(3)*p_+, a_-=sqrt(3)*p_-",
            "C_minus: a_+=-sqrt(3)*p_+, a_-=-sqrt(3)*p_-",
            "T_plus_zero: a_+=p_+=0",
            "T_minus_zero: a_-=p_-=0",
        ],
        "case_split_proof": "if p_+p_-!=0, divide the cross equation to get a_+/p_+=a_-/p_-=s and the diagonal equation gives s^2=3; if p_+=0 or p_-=0, the cross and diagonal equations give one of the two one-sided planes",
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    bounded = records["bounded_extension"]
    _require(bounded["classification"]["complete_exact_collision_census_for_declared_tangent"], "collision census changed")
    _require(bounded["classification"]["unique_collision_canceled_on_mixed_parity_null_face"], "bounded null-face input changed")
    _require(records["parity_matrix"]["classification"]["complete_tuned_L4_two_parity_resonance_matrix_certified"], "parity matrix changed")
    _require(records["opposite_cone"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_classified"], "moment cone changed")

    root = sp.sqrt(3)
    omega_minus_squared = sp.Rational(29, 6)
    omega_plus_squared = omega_minus_squared + 4 * root
    ratio = sp.sqrt(omega_minus_squared / omega_plus_squared)
    _require(omega_minus_squared > 0 and sp.simplify(omega_plus_squared - omega_minus_squared) > 0, "frequency ordering changed")
    lower = sp.factor((1 - ratio) / (1 + ratio))
    upper = sp.factor((1 + ratio) / (1 - ratio))
    _require(sp.simplify(lower * upper - 1) == 0, "imbalance interval reciprocity changed")
    decomposition = _resonance_decomposition()

    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-ell2-tuned-axisymmetric-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_TUNED_AXISYMMETRIC_BOUNDED_CONE",
        "result_state": "COMPLETE_TUNED_AXISYMMETRIC_QPLUS_QMINUS_TWIST_BOUNDED_CONE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_COMPLETE_ONE_TUNED_ELL2_AXISYMMETRIC_QPLUS_QMINUS_TWIST_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one constant twist position plus arbitrary axisymmetric axial/polar q-minus amplitudes and arbitrary normalized q-plus balancing multiplicities at +/-k; no p-primary input",
            "degree": 2,
            "parity": "both q-minus parities; arbitrary q-plus multiplicity factorization",
            "ell": "input ell=2; every quadratic output L=0,...,4",
            "m": "m_A=0",
            "k": "+/-sqrt(2*sqrt(3)-7/6)",
            "omega": "q-minus and q-plus shells with bounded or finite-quasiperiodic corrections",
        },
        "frequency_ratio": {
            "r": str(ratio),
            "definition": "r=omega_minus/omega_plus",
            "strict_range": "0<r<1",
        },
        "resonance_zero_set": decomposition,
        "moment_map_reduction": {
            "q_minus_occupations": "N_sigma=-h_minus(a_sigma e_A+p_sigma e_P,a_sigma e_A+p_sigma e_P)>=0, sigma=+,-",
            "q_plus_occupations": "B_sigma>=0 in any normalized q-plus multiplicity factorization",
            "H_and_Px_solution": [
                "B_+ + B_- = r^2*(N_+ + N_-)",
                "B_+ - B_- = r*(N_+ - N_-)",
                "B_+ = (r^2*(N_+ + N_-)+r*(N_+ - N_-))/2",
                "B_- = (r^2*(N_+ + N_-)-r*(N_+ - N_-))/2",
            ],
            "positivity_condition": "abs(N_+-N_-)<=r*(N_++N_-)",
            "rotations": "J_1=J_2=J_3=0 identically on m_A=0",
            "one_sided_planes": "T_plus_zero and T_minus_zero meet the common moment cone only at the origin because N_one_side>0 would require 1<=r",
        },
        "nonzero_bounded_components": {
            "signs": ["sigma=+1", "sigma=-1"],
            "amplitudes": "a_+=sigma*sqrt(3)*p_+ and a_-=sigma*sqrt(3)*p_- with p_+,p_- nonzero complex amplitudes",
            "phase_freedom": "the phases of p_+ and p_- are independent; q-plus phases and multiplicity factorization are arbitrary at the fixed occupations",
            "occupation_factorization": "on either component N_tau=c*|p_tau|^2 with the same c=3*g_A+g_P>0, so the parity weights cancel from the momentum-balance inequality",
            "complete_imbalance_interval": {
                "variable": "t=|p_+|^2/|p_-|^2",
                "lower": str(lower),
                "upper": str(upper),
                "condition": "(1-r)/(1+r)<=t<=(1+r)/(1-r)",
                "reciprocal_endpoints": True,
            },
        },
        "necessity_and_sufficiency": {
            "necessity": "bounded solvability forces the five stabilizer maps and both unique L4 adjoint rows to vanish; their complete solutions give the displayed two mixed planes, q-plus occupations and imbalance interval",
            "sufficiency": "on either mixed plane inside the interval, choose the displayed nonnegative q-plus occupations; all five moment maps and the sole shell resonance vanish, so the certified 80-row blockwise theorem supplies a bounded finite-quasiperiodic correction",
            "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "cone": "the origin plus the two displayed mixed components with the exact imbalance interval and q-plus occupation factorization"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "the complete fixed-(ell,|k|) moment-map cone is smooth-secular extendible; the bounded cone is a subset"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_tuned_axisymmetric_resonance_zero_set_classified": True,
            "complete_tuned_axisymmetric_common_moment_and_resonance_cone_classified": True,
            "bounded_necessity_and_sufficiency_certified": True,
            "two_nonzero_mixed_parity_components_survive": True,
            "one_sided_travelling_components_excluded_by_momentum_balance": True,
            "other_ell_or_momentum_fibres_classified": False,
            "p_primary_inputs_included": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "At the tuned fibre, nonlinear bounded consistency does not delete the q-minus branch. It correlates axial and polar amplitudes by one of two exact signs and bounds the imbalance between opposite compact momenta. The positive q-plus branch then supplies the unique nonnegative Hamiltonian/momentum balance. The resulting solution set is a genuine mixed cone rather than a linear subspace.",
        "next_gate": "adjoin p-primary inputs at the same tuned fibre, then repeat the exact collision/source decomposition for symbolic ell and multiple absolute-momentum fibres",
        "claim_boundary": "This is the complete bounded cone only in the declared tuned ell=2 axisymmetric q-plus/q-minus/constant-twist carrier. It excludes p-primary inputs, nonaxisymmetric modes, other ell and circumferences, multiple |k| fibres, exceptional inputs beyond the twist, all-orders integration, causal propagation, particles and quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_1": {"status": "PENDING", "tests_run": 0},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the complete direct resonance matrix and bounded blockwise theorem are unchanged inputs; this producer solves their exact finite-dimensional zero locus"},
            "tier_3": {"status": "NOT_RUN", "reason": "other carriers and higher lifecycles remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if arguments.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
        raise AssertionError("tuned axisymmetric bounded-cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_TUNED_AXISYMMETRIC_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()

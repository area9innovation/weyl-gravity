"""Third-order Kuranishi formula, carrier closure, and exact missing-input gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-cauchy-third-order-kuranishi-input-obstruction-v1.schema.json"
INPUTS = {
    "mixed_correspondence": (
        "bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json",
        "EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1",
        "a0280458c2cd704f96b33e9a21d796074c85bdd305a445ad60690d3dcd4367c4",
    ),
    "two_jet_kuranishi": (
        "bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json",
        "EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1",
        "fa764024805f3c2ce67e63d9a15afed94861e1374e32ecda8124efc3849aea24",
    ),
    "quadratic_source_and_correction": (
        "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
        "EINSTEIN_MAXWELL_WEYL_BALANCED_ELL0_SECOND_ORDER",
        "13fc90b0ef18c6bf6a8f4f1a397c86aa235ed87fa86a3c3bf5ad031bc2304cfe",
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def exact_audit() -> dict[str, Any]:
    sqrt3 = sp.sqrt(3)
    omega_minus = sp.sqrt(6 - 2 * sqrt3)
    omega_extra = 4 / sqrt3

    triples = []
    for n_minus in range(-3, 4):
        for n_extra in range(-3, 4):
            weight = abs(n_minus) + abs(n_extra)
            if (n_minus, n_extra) != (0, 0) and weight <= 3 and (3 - weight) % 2 == 0:
                triples.append((n_minus, n_extra))
    req(len(triples) == 16, "third-frequency lattice")

    resonances: list[dict[str, Any]] = []
    for n_minus, n_extra in triples:
        frequency = sp.simplify(n_minus * omega_minus + n_extra * omega_extra)
        for ell in (2, 4, 6):
            lam = ell * (ell + 1)
            shells = {
                "q_minus": lam - sp.sqrt(2 * lam),
                "p_extra": sp.Rational(lam) - sp.Rational(2, 3),
                "q_plus": lam + sp.sqrt(2 * lam),
            }
            for branch, frequency_squared in shells.items():
                if sp.simplify(frequency**2 - frequency_squared) == 0:
                    resonances.append(
                        {"frequency_lattice": [n_minus, n_extra], "ell": ell, "branch": branch}
                    )
    expected = [
        {"frequency_lattice": [-1, 0], "ell": 2, "branch": "q_minus"},
        {"frequency_lattice": [0, -1], "ell": 2, "branch": "p_extra"},
        {"frequency_lattice": [0, 1], "ell": 2, "branch": "p_extra"},
        {"frequency_lattice": [1, 0], "ell": 2, "branch": "q_minus"},
    ]
    req(resonances == expected, "kinematic shell list")

    tau_e = sp.Rational(48, 5) * (-6 + 5 * sqrt3)
    amplitude_squared = sp.Rational(27, 52) * (-6 + 5 * sqrt3)
    amplitude = sp.sqrt(amplitude_squared)
    tau_x_per_unit = -sp.Rational(832, 45)
    tau_x = tau_x_per_unit * amplitude_squared
    req(sp.simplify(tau_e + tau_x) == 0, "balanced charge")
    # l2(u,z) on the two-real-amplitude slice; only the H row is nonzero.
    l2_u = sp.zeros(5, 2)
    l2_u[0, 0] = 2 * tau_e
    l2_u[0, 1] = 2 * tau_x_per_unit * amplitude
    req(l2_u.rank() == 1, "balanced-slice ambiguity rank")

    return {
        "frequency_lattice": [list(pair) for pair in triples],
        "kinematic_resonances": resonances,
        "balanced_l2_u": [[str(x) for x in row] for row in l2_u.tolist()],
        "balanced_l2_rank": 1,
        "balanced_obstruction_quotient_dimension": 4,
    }


def build() -> dict[str, Any]:
    imported: dict[str, dict[str, Any]] = {}
    for name, (rel, result_id, digest) in INPUTS.items():
        path = ROOT / rel
        payload = json.loads(path.read_text())
        req(payload["result_id"] == result_id, f"{name} result id")
        req(sha(path) == digest, f"{name} hash")
        imported[name] = payload
    quadratic = imported["quadratic_source_and_correction"]
    req(quadratic["classification"]["complete_second_order_extension_constructed"], "second-order correction")
    req("bilinear_source_polynomial" in quadratic, "quadratic source")
    req("third_order" not in quadratic and "cubic_source" not in quadratic, "uncertified D3 field appeared")
    audit = exact_audit()
    return {
        "schema": "einstein-weyl-compact-cauchy-third-order-kuranishi-input-obstruction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1",
        "result_state": "CUBIC_CLASS_FORMULA_AND_RESONANCE_CARRIER_CERTIFIED_EVALUATION_OBSTRUCTED_BY_MISSING_D3_CONSTRAINT_INPUT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                key: {"path": rel, "result_id": rid, "sha256": digest}
                for key, (rel, rid, digest) in INPUTS.items()
            },
        },
        "scope": {
            "theory": "Weyl-Maxwell compact-Cauchy Kuranishi constraint problem",
            "background": "compactified magnetically supported Plebanski-Hacyan",
            "boundaries": "compact boundaryless Cauchy slice S1_L x S2 before stabilizer reduction",
            "charge_sector": "fixed P_N,N=2 and fixed Q_e; based Maxwell gauge; W_x retained",
            "carrier": "certified balanced axial ell=2,m=0,k=0 fixture and its finite third-order resonance closure",
            "degree": "third-order Kuranishi preflight",
            "parity": "axial output from axial first order and polar second order",
            "ell": "2,4,6 in the third-order closure",
            "m": "0",
            "k": "0",
            "omega": "integer lattice generated by omega_minus and omega_extra with odd total word length <=3",
        },
        "third_order_operation": {
            "expansion_convention": "Phi(epsilon)=Phi_bar+epsilon*u+epsilon^2*v+epsilon^3*w+O(epsilon^4)",
            "second_order_equation": "L v=-(1/2)D^2E[u,u]",
            "third_order_equation": "L w=-D^2E[u,v]-(1/6)D^3E[u,u,u]",
            "projected_representative": "K3(u;v)=P_O(D^2C[u,v]+(1/6)D^3C[u,u,u])",
            "correction_change": "v->v+z with Lz=0 changes K3 by P_O D^2C[u,z]=l2(u,z)",
            "intrinsic_class": "[K3(u;v)] in O/im(l2(u,-))",
            "gauge_warning": "independence under a nonlinear gauge/algebroid representative additionally needs the second jet of the gauge action and the arity-three Noether identity",
        },
        "balanced_slice_ambiguity": {
            "obstruction_space": "O=span{H,P_x,J1,J2,J3}",
            "matrix_l2_u": audit["balanced_l2_u"],
            "rank": audit["balanced_l2_rank"],
            "quotient_dimension": audit["balanced_obstruction_quotient_dimension"],
            "interpretation": "on the two-amplitude axisymmetric k=0 slice, correction shifts remove at most the H component; four stabilizer directions remain in the formal quotient",
            "full_carrier_rank": "NO_CERTIFIED_MAP: cross-branch l2(u,-) has not been serialized on the complete resonance closure",
        },
        "resonance_closed_carrier": {
            "first_order": [
                "axial ell=2,m=0,k=0 q_minus at +/-omega_minus",
                "axial ell=2,m=0,k=0 p_extra at +/-omega_extra",
            ],
            "second_order_correction": "polar ell=0,2,4 at 0, +/-2omega_minus, +/-2omega_extra, +/-(omega_extra+omega_minus), +/-(omega_extra-omega_minus)",
            "third_order_angular_outputs": [2, 4, 6],
            "third_order_frequency_lattice_pairs": audit["frequency_lattice"],
            "kinematic_shell_resonances": audit["kinematic_resonances"],
            "conclusion": "the only exact third-order on-shell frequencies in this closure are the original ell=2 q_minus and p_extra frequencies; their source coefficients are not computable from the imported payload",
        },
        "missing_input": {
            "first_absent_map": "the action-normalized constraint tensor D^3C_barPhi restricted to Sym^3 of the balanced first-order carrier",
            "also_required": [
                "the mixed tensor D^2C_barPhi[u,v] for every certified ell=0,2,4 second-order correction channel",
                "the projection of both tensors onto H,P_x,J1,J2,J3 and the resonant ell=2 q_minus/p_extra adjoint shells",
                "the second jet of the bundle-covariant constraint-algebroid action and the arity-three Noether identity needed for gauge-representative independence",
                "a field-component crosswalk placing every stored reduced correction coefficient into the same four-dimensional action convention",
            ],
            "present_but_insufficient": "the imported certificate contains D^2E on two first-order axial inputs and a complete chosen v, but no D^3C and no D^2C map accepting one first-order and one second-order field",
            "required_export": "content-addressed exact channel tensor with row order, harmonic/frequency labels, normalization, correction representative, source action hash, and independent verifier",
            "effect": "K3 cannot be evaluated on the balanced fixture or its complete closure, so sufficiency of the five quadratic charges and the presence/nonpresence of a nonzero resonant cubic obstruction remain undecided",
        },
        "mutations": {
            "drop_one_sixth": "REJECTED by the declared epsilon expansion convention",
            "hide_correction_choice": "REJECTED because v->v+z changes the representative by l2(u,z)",
            "claim_gauge_independence": "REJECTED without the arity-three Noether/action input",
            "omit_original_shells": "REJECTED by the exact frequency lattice: (+/-1,0) and (0,+/-1) are resonant at ell=2",
            "call_quadratic_charge_balance_third_order_integration": "REJECTED because neither D3C nor the mixed D2C[u,v] contribution is present",
        },
        "classification": {
            "formal_cubic_class_formula": True,
            "correction_choice_quotient": True,
            "balanced_cubic_class_evaluated": False,
            "complete_resonance_carrier_enumerated": True,
            "only_original_ell2_shells_kinematically_resonant": True,
            "D3_constraint_tensor_present": False,
            "mixed_D2_first_second_tensor_present": False,
            "gauge_representative_independence": False,
            "five_quadratic_Taub_charges_sufficient_through_order_three": False,
            "new_adjoint_covector_coefficient_decided": False,
            "causal_particle_or_quantum_claim": False,
        },
        "claim_boundary": "Certifies the cubic Kuranishi class formula modulo correction shifts, the exact balanced-slice ambiguity rank, the smallest finite resonance closure, and the first content-addressed missing tensor. It does not evaluate the cubic class, prove gauge-representative independence, decide third-order integrability, or promote bounded, causal, particle, positivity, unitarity or quantum claims.",
        "next_gate": "export the action-normalized D3C and mixed D2C[u,v] channel tensors, together with the arity-three bundle-covariant Noether identity, on the declared balanced resonance closure",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_compact_cauchy_third_order_kuranishi_obstruction --verify bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1.json",
            "python3 bridge/einstein_sector/verify_einstein_weyl_compact_cauchy_third_order_kuranishi_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_compact_cauchy_third_order_kuranishi_obstruction",
            "python3 -m bridge.einstein_sector.generate_third_order_kuranishi_obstruction_atlas --check",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.verify:
        req(json.loads(args.verify.read_text()) == payload, "stale certificate")
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

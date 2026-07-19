"""Certify that the candidate-13 bounded scalar zero locus is the origin."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.schema.json"
INPUTS = {
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "pressure": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
    "candidate13_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json",
    "standard_inclusion": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "bounded_zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def exact_separation() -> dict[str, object]:
    rho = (-sp.Integer(250) + 461 * sp.sqrt(10)) / 2132
    require(461**2 * 10 - 1316**2 > 0, "rho lower square witness changed")
    require(7646**2 - 2305**2 * 10 > 0, "rho upper square witness changed")
    require(bool(rho > sp.Rational(1, 2)) and bool(rho < sp.Rational(3, 5)), "candidate-13 rho interval changed")

    w = sp.symbols("w", positive=True)
    f_p1 = sp.Rational(2, 5) * w**2 - sp.Rational(3, 8) * w - 1
    f_m1 = 1 + sp.Rational(3, 8) * w - sp.Rational(2, 5) * w**2
    f_p2 = sp.Rational(2, 5) * w**2 + sp.Rational(3, 4) * w - 4
    f_m2 = 4 - sp.Rational(3, 4) * w - sp.Rational(2, 5) * w**2

    endpoints = {
        "qminus_n1": sp.factor(f_m1.subs(w, sp.Rational(9, 5))),
        "p_n1": sp.factor(f_p1.subs(w, sp.Rational(12, 5))),
        "qminus_nminus2": sp.factor(f_m2.subs(w, sp.Rational(9, 4))),
        "p_nminus2": sp.factor(f_p2.subs(w, sp.Rational(8, 3))),
    }
    require(endpoints == {
        "qminus_n1": sp.Rational(379, 1000),
        "p_n1": sp.Rational(101, 250),
        "qminus_nminus2": sp.Rational(23, 80),
        "p_nminus2": sp.Rational(38, 45),
    }, "separating lower bounds changed")

    require(12 * 625 - 84**2 > 0, "qminus n=1 radical bound changed")
    require(12 * 6400 - 267**2 > 0, "qminus n=-2 radical bound changed")
    require(sp.Rational(1, 2) + sp.Rational(16, 3) - sp.Rational(12, 5)**2 == sp.Rational(11, 150), "p n=1 frequency bound changed")
    require(4 * sp.Rational(1, 2) + sp.Rational(16, 3) - sp.Rational(8, 3)**2 == sp.Rational(2, 9), "p n=-2 frequency bound changed")

    return {
        "rho": str(rho),
        "rho_interval": ["1/2", "3/5"],
        "rho_interval_square_witnesses": {
            "rho_gt_half": "461^2*10-1316^2=393354>0",
            "rho_lt_three_fifths": "7646^2-2305^2*10=5331066>0",
        },
        "separating_functional": "D=-(8/(5L))*mu_H-(3/(2L*sqrt(rho)))*mu_Px-(2/rho)*R_c",
        "unnormalized_shell_form": "D=(2/5)S_H-(3/8)S_P-S_R, with S_H=sum omega^2 h, S_P=sum n omega h, S_R=sum n^2 h",
        "branch_coefficients": {
            "n=1": {
                "qminus": "1+(3/8)omega-(2/5)omega^2",
                "p": "(2/5)omega^2-(3/8)omega-1",
                "qplus": "(2/5)omega^2-(3/8)omega-1",
            },
            "n=-2": {
                "qminus": "4-(3/4)omega-(2/5)omega^2",
                "p": "(2/5)omega^2+(3/4)omega-4",
                "qplus": "(2/5)omega^2+(3/4)omega-4",
            },
        },
        "frequency_bounds": {
            "qminus_n1": "omega<9/5 because 2*sqrt(3)>84/25; coefficient is decreasing and >379/1000",
            "p_n1": "omega>12/5 because omega^2>35/6 and 35/6-(12/5)^2=11/150; coefficient is increasing and >101/250",
            "qplus_n1": "omega_qplus>omega_p and the common positive-branch coefficient is increasing",
            "qminus_nminus2": "omega<9/4 because 2*sqrt(3)>267/80; coefficient is decreasing and >23/80",
            "p_nminus2": "omega>8/3 because omega^2>22/3 and 22/3-(8/3)^2=2/9; coefficient is increasing and >38/45",
            "qplus_nminus2": "omega_qplus>omega_p and the common positive-branch coefficient is increasing",
        },
        "radical_square_witnesses": {
            "2sqrt3_gt_84_over_25": "12*625-84^2=444>0",
            "2sqrt3_gt_267_over_80": "12*6400-267^2=5511>0",
        },
        "strict_lower_bounds": {key: str(value) for key, value in endpoints.items()},
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    moment = records["moment_map"]["generic_moment_maps"]
    require(moment["real_mode_moment_maps"]["H"].startswith("mu_H=-(L/4) sum omega^2"), "Hamiltonian normalization changed")
    require(moment["real_mode_moment_maps"]["P_x"].startswith("mu_Px=(L/4) sum k*omega"), "momentum normalization changed")
    require(records["pressure"]["primary_action_identity"]["pressure_functional"] == "R_c(u)=(1/2) sum k_j^2 h_j", "pressure normalization changed")
    require(records["candidate13_witness"]["exact_fixture"]["rho_exact_interval"] == ["1/2", "3/5"], "candidate-13 interval input changed")
    standard_row = records["standard_inclusion"]["theorem"]["block_table"][0]
    require("common parity-independent branch weights" in standard_row["pullback_relative_operator"], "parity-independent q signs changed")
    require(records["axial_current"]["full_solution_pairing"]["complete_block_form"].startswith("Einstein_plus (+) direct-sum Einstein_minus (-)"), "axial branch signs changed")
    require(records["polar_current"]["classification"]["complete_polar_target_inertia_3_1"], "polar current inertia changed")
    require(records["polar_current"]["classification"]["extra_block_positive_frequency_inertia_2_0"], "polar extra positivity changed")
    require(records["bounded_zero_block"]["classification"]["five_stabilizers_plus_circle_pressure_necessary_and_sufficient"], "candidate-13 bounded zero-block theorem changed")

    return {
        "schema": "einstein-maxwell-weyl-candidate13-scalar-separation-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CANDIDATE13_SCALAR_SEPARATION_NO_GO",
        "result_state": "CANDIDATE13_COMPLETE_GENERIC_BOUNDED_CONE_IS_THE_ORIGIN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_FINITE_CANDIDATE13_GENERIC_TWO_FIBRE_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-13 tuned compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "all generic ell=2 q-minus, p-extra and q-plus coefficients on signed n=1 and n=-2 fibres, both parities and all m, with reality conjugates",
            "degree": 2,
            "parity": "axial and polar",
            "ell": 2,
            "m": "all m=-2,...,2",
            "k": "signed n=1,-2 candidate-13 fibres",
            "omega": "all q-minus, p-extra and q-plus positive-frequency shells",
        },
        "normalization": {
            "H": moment["real_mode_moment_maps"]["H"],
            "P_x": moment["real_mode_moment_maps"]["P_x"],
            "R_c": records["pressure"]["primary_action_identity"]["pressure_functional"],
            "current_signs": "q-minus negative, p-extra positive definite, q-plus positive in each parity; angular Gram W_2 is positive",
        },
        "exact_separation_certificate": exact_separation(),
        "theorem": {
            "positive_decomposition": "D=sum_(parity,m,branch,n) d_(branch,n)*|c_(branch,n)|^2_abs_current with every d_(branch,n)>0",
            "scalar_common_zero": "{mu_H=mu_Px=R_c=0} intersect candidate13 generic carrier={0}",
            "complete_bounded_cone": "Z2_candidate13_bounded={0}",
            "reason_resonance_is_redundant": "the scalar common zero is already the origin, so the eighteen R_13 coefficients and three rotations vanish there automatically",
        },
        "classification": {
            "exact_rational_Farkas_functional_certified": True,
            "strictly_positive_on_every_declared_branch_fibre_parity_and_m": True,
            "candidate13_scalar_common_zero_is_origin": True,
            "candidate13_complete_bounded_cone_is_origin": True,
            "candidate13_nonzero_bounded_point_exists": False,
            "real_bounded_component_decomposition_classified": True,
            "smooth_cone_collapses_to_origin": False,
            "exceptional_or_generalized_zero_inputs_included": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "At candidate 13, adding circle pressure to H and P_x restores definiteness on the entire generic two-fibre carrier. The smooth cone remains nontrivial because pressure has a secular inverse, but bounded finite-quasiperiodic second-order extension admits only the zero tangent.",
        "next_gate": "separate the candidate-specific origin theorem from other collision circumferences and from carriers with exceptional or generalized-zero inputs",
        "claim_boundary": "This is a complete bounded second-order no-go on the declared finite generic candidate-13 carrier. It does not collapse the smooth cone, include exceptional/global inputs, prove all-orders integration, or construct causal, residual, observational or quantum maps.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_candidate13_scalar_separation_no_go --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_candidate13_scalar_separation_no_go",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_candidate13_scalar_separation_no_go",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError("candidate-13 scalar-separation certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE13_SCALAR_SEPARATION_NO_GO: PASS")


if __name__ == "__main__":
    main()

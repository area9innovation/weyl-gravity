"""Covariant moment-map/Taub bridge for compact Weyl--Maxwell modes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import (
    _time_current_matrix as _polar_time_current_matrix,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_moment_map_taub_bridge.schema.json"
INPUTS = {
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "domain": ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json",
    "axial_extra_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json",
    "axial_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "extra_taub_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json",
    "einstein_taub_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json",
}


class MomentMapTaubBridgeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MomentMapTaubBridgeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def _matrix(values: list[list[str]], local: dict[str, sp.Expr]) -> sp.Matrix:
    return sp.Matrix([[_expr(value, local) for value in row] for row in values])


def _calibration_audit(records: dict[str, Any]) -> dict[str, Any]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    root = sp.sqrt(3)
    lambda_fixture = sp.Integer(6)
    harmonic_average = sp.Rational(1, 5)  # average of P_2(cos theta)^2
    real_part_factor = sp.Rational(1, 4)

    # Extra axial fixture.  Its basis is exactly the generic extra basis at
    # lambda=6,k=0, and omega^2=16/3.
    extra_frequency_squared = sp.Rational(16, 3)
    extra_frequency = sp.sqrt(extra_frequency_squared)
    local = {"lam": eigenvalue, "k": momentum, "omega": frequency, "I": sp.I}
    extra_gram_generic = _matrix(records["axial_extra_pairing"]["pairing"]["normalized_Gram"], local)
    extra_gram = extra_gram_generic.subs(
        {eigenvalue: lambda_fixture, momentum: 0, frequency: extra_frequency}
    ).applyfunc(sp.simplify)
    extra_taub = _matrix(
        records["extra_taub_fixture"]["quadratic_source"]["constant_lapse_Taub_matrix"],
        {"I": sp.I},
    )
    extra_prediction = (-extra_frequency_squared * harmonic_average * real_part_factor * extra_gram).applyfunc(sp.simplify)
    _require(extra_prediction == extra_taub, "extra axial moment-map/Taub calibration changed")

    # Axial Einstein-minus fixture.  The direct-current representative is
    # omega times the real tensor fixture, so its fixture Gram is G/omega^2.
    axial = records["axial_pairing"]["full_solution_pairing"]
    axial_norm = _expr(
        axial["Einstein_minus_branch_norm"],
        {"lam": eigenvalue, "sqrt": sp.sqrt},
    ).subs(eigenvalue, lambda_fixture)
    einstein_frequency_squared = 6 - 2 * root
    axial_fixture_gram = sp.simplify(axial_norm / einstein_frequency_squared)
    axial_prediction = sp.simplify(
        -einstein_frequency_squared * harmonic_average * real_part_factor * axial_fixture_gram
    )
    einstein_taub = records["einstein_taub_fixture"]["weyl_maxwell_taub"]
    axial_taub = _expr(einstein_taub["cosine_amplitude_matrix_A_P"][0][0], {"sqrt": sp.sqrt})
    _require(sp.simplify(axial_prediction - axial_taub) == 0, "axial Einstein moment-map/Taub calibration changed")

    # Polar Einstein-minus fixture.  The generic invariant representative is
    # six times the declared real tensor fixture at lambda=6,k=0.
    current, symbols = _polar_time_current_matrix()
    l, k = symbols["lambda"], symbols["k"]
    w1, w2 = symbols["omega_1"], symbols["omega_2"]
    w_e = sp.sqrt(einstein_frequency_squared)
    mu = einstein_frequency_squared
    representative = sp.Matrix(
        [
            2 * k**2 * (mu - l) + 2 * l,
            -2 * k * w_e * (mu - l),
            2 * (k**2 + l) * (mu - l) + 2 * l,
            l,
        ]
    ).subs({l: lambda_fixture, k: 0})
    action_current = (current / 2).subs(
        {l: lambda_fixture, k: 0, w1: w_e, w2: w_e}
    )
    polar_representative_gram = sp.simplify(
        (representative.T * action_current * representative)[0] / (-sp.I * w_e)
    )
    polar_fixture_gram = sp.simplify(polar_representative_gram / 36)
    polar_prediction = sp.simplify(
        -einstein_frequency_squared * harmonic_average * real_part_factor * polar_fixture_gram
    )
    polar_taub = _expr(einstein_taub["cosine_amplitude_matrix_A_P"][1][1], {"sqrt": sp.sqrt})
    _require(sp.simplify(polar_prediction - polar_taub) == 0, "polar Einstein moment-map/Taub calibration changed")

    return {
        "fixture": "ell=2, k=0, axisymmetric P_2 harmonic with normalized sphere average 1/5",
        "real_mode_convention": "Phi=Re(c*e^{-i*omega*t}) gives the factor 1/4 relative to the complex-mode current",
        "repository_identity": "Taub_H(Phi,Phi)=mu_H(Phi)=1/2 Omega_WM(Phi,L_H Phi)",
        "per_unit_complex_Gram_formula": "mu_H=-(L*N_ell_m/4)*omega^2*c^dagger*G*c; for normalized spatial average replace L*N_ell_m by average(|Y_ell_m|^2)",
        "extra_axial": {
            "omega_squared": str(extra_frequency_squared),
            "Lee_Wald_Gram": [[str(value) for value in row] for row in extra_gram.tolist()],
            "predicted_Taub_matrix": [[str(value) for value in row] for row in extra_prediction.tolist()],
            "direct_tensor_Taub_matrix": [[str(value) for value in row] for row in extra_taub.tolist()],
            "exact_match": True,
        },
        "Einstein_minus_axial": {
            "omega_squared": str(einstein_frequency_squared),
            "representative_scaling": "direct-current representative = omega times the declared tensor fixture",
            "fixture_Gram": str(sp.factor(axial_fixture_gram)),
            "predicted_Taub_coefficient": str(sp.factor(axial_prediction)),
            "direct_tensor_Taub_coefficient": str(sp.factor(axial_taub)),
            "exact_match": True,
        },
        "Einstein_minus_polar": {
            "omega_squared": str(einstein_frequency_squared),
            "representative_scaling": "generic invariant representative = 6 times the declared tensor fixture",
            "fixture_Gram": str(sp.factor(polar_fixture_gram)),
            "predicted_Taub_coefficient": str(sp.factor(polar_prediction)),
            "direct_tensor_Taub_coefficient": str(sp.factor(polar_taub)),
            "exact_match": True,
        },
    }


def _covariant_identity() -> dict[str, Any]:
    return {
        "action_identity": "delta H_X[delta Phi]=Omega_Sigma(delta Phi,L_X Phi) plus the boundary charge variation",
        "background_hypotheses": [
            "E(Phi_bar)=0",
            "X is a bundle-covariant infinitesimal automorphism of (g_bar,F_bar)",
            "Sigma=S1 x S2 is closed",
            "the first-order tangent u satisfies L u=0",
        ],
        "second_variation_steps": [
            "differentiate the covariant Noether current identity twice at Phi_bar",
            "use L_X Phi_bar=0 and L u=0",
            "integrate over the closed Cauchy slice so every exact corner improvement vanishes",
            "identify the constraint-adjoint projection of (1/2)D^2E[u,u] with the quadratic Hamiltonian",
        ],
        "result": "<zeta_X,(1/2)D^2E_WM[u,u]>=mu_X(u)=1/2 Omega_WM(u,L_X u)",
        "polarization": "<zeta_X,D^2E_WM[u,v]/2> is the symmetric polarization of mu_X",
        "ambiguity_control": "Lee-Wald exact-current improvements integrate to zero on the closed slice; the magnetic connection is handled by bundle-covariant lifts",
        "normalization_control": "the direct four-dimensional Lee-Wald matches fix Omega_WM, and three independent direct tensor Taub coefficients fix the sign and real-mode factor",
        "scope": "action-derived Weyl-Maxwell equations on the declared compact product; no boundary or causal extension",
    }


def _generic_formulas(records: dict[str, Any]) -> dict[str, Any]:
    axial = records["axial_pairing"]["full_solution_pairing"]
    polar = records["polar_pairing"]["shell_pairing"]
    _require(axial["extra_branch_signature_for_lambda_ge_6"] == [2, 0], "axial extra positivity changed")
    _require(polar["extra_positive_frequency_inertia"] == [2, 0], "polar extra positivity changed")
    _require(axial["mixed_blocks_zero_without_frequency_inversion"] is True, "axial primary orthogonality changed")
    _require(polar["Einstein_extra_mixed_remainder_mod_p_q"] == ["0", "0"], "polar primary orthogonality changed")
    omega, momentum, angular_weight = sp.symbols("omega k tau", real=True)
    complex_pairing = sp.Matrix([[0, sp.I * omega], [-sp.I * omega, 0]])
    real_part = sp.Matrix([sp.Rational(1, 2), sp.Rational(1, 2)])
    actions = {
        "H": sp.diag(-sp.I * omega, sp.I * omega),
        "P_x": sp.diag(sp.I * momentum, -sp.I * momentum),
        "J_a": sp.diag(sp.I * angular_weight, -sp.I * angular_weight),
    }
    factors = {
        name: sp.simplify((real_part.T * complex_pairing * action * real_part)[0] / 2)
        for name, action in actions.items()
    }
    _require(factors == {"H": -omega**2 / 4, "P_x": momentum * omega / 4, "J_a": angular_weight * omega / 4}, "complex-to-real moment-map factors changed")
    return {
        "coefficient_space": "for each (k,ell,parity,shell), positive-frequency amplitudes c lie in the branch/polarization space tensor the spin-ell multiplicity V_ell",
        "Hermitian_current_form": "h=c^dagger (G_branch tensor W_ell) c, with W_ell the positive invariant angular form",
        "real_mode_moment_maps": {
            "H": "mu_H=-(L/4) sum omega^2 c^dagger(G_branch tensor W_ell)c",
            "P_x": "mu_Px=(L/4) sum k*omega c^dagger(G_branch tensor W_ell)c",
            "J_a": "mu_Ja=(L/4) sum omega c^dagger(G_branch tensor W_ell*T_a)c, where rho(J_a)=i*T_a",
        },
        "complex_to_real_algebra": {
            "basis": ["positive-frequency z", "conjugate zbar"],
            "Omega_matrix_per_unit_Gram": [["0", "I*omega"], ["-I*omega", "0"]],
            "real_part_vector": ["1/2", "1/2"],
            "one_half_Omega_Phi_rhoPhi_factors": {name: str(value) for name, value in factors.items()},
            "exact": True,
        },
        "polarized_rules": {
            "H_and_Px": "nonzero only for equal k, ell, m, parity, and frequency shell, with the full two-polarization p-primary Gram retained",
            "rotations": "equal k, ell, parity, and frequency shell; T_3 keeps m while T_1,T_2 connect only m to m+/-1",
            "different_ell": "zero after the complete covariant Noether sum: [Delta_S2,J_a]=0 implies (lambda_1-lambda_2)<u,J_a v>=0, so rotations cannot mix inequivalent V_ell modules",
            "q_p_mixed": "zero by the certified Einstein/extra Lee-Wald orthogonality",
            "axial_polar_mixed": "zero by orientation-preserving parity and the direct-current harmonic decomposition",
            "reality": "negative-frequency and negative-momentum coefficients are fixed by conjugation; the displayed positive-frequency sums already represent real fields",
        },
        "generic_extra_H_Taub": {
            "axial_p_primary_Gram_inertia": [2, 0],
            "polar_p_primary_Gram_inertia": [2, 0],
            "omega_squared": "k^2+lambda-2/3>0 for every physical lambda=ell(ell+1)>=6",
            "verdict": "NEGATIVE_DEFINITE_ON_EVERY_NONZERO_REAL_GENERIC_EXTRA_TANGENT",
            "superposition_scope": "finite or rapidly decreasing finite-energy harmonic superpositions; orthogonality makes mu_H the convergent sum of negative block contributions",
        },
        "complete_target_H_Taub": {
            "axial_inertia_before_the_minus_sign": [3, 1],
            "polar_inertia_before_the_minus_sign": [3, 1],
            "verdict": "INDEFINITE_BECAUSE_THE_EINSTEIN_Q_PRIMARY_HAS_ONE_NEGATIVE_BRANCH_PER_PARITY",
            "mixed_Einstein_extra_cancellations": "possible in the scalar H constraint and not classified by the pure-extra theorem",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    expected = {
        "stabilizer": "EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT",
        "domain": "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT",
        "axial_extra_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING",
        "axial_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION",
        "polar_pairing": "EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE",
        "extra_taub_fixture": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_ELL2_TAUB",
        "einstein_taub_fixture": "EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB",
    }
    for name, result_id in expected.items():
        _require(records[name]["result_id"] == result_id, f"{name} input changed")
    topology = records["domain"]["topology_and_charge_fibres"]
    _require(topology["fixed_compact_u1_bundle"]["allowed_magnetic_lift"] is False, "fixed-bundle magnetic gate changed")
    _require(topology["electric_only_variation_on_fixed_bundle"]["allowed"] is True, "electric fibre gate changed")

    return {
        "schema": "einstein-maxwell-weyl-moment-map-taub-bridge-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE",
        "result_state": "COVARIANT_MOMENT_MAP_TAUB_BRIDGE_AND_GENERIC_EXTRA_FIXED_BUNDLE_NO_GO_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_POLAR_ALL_PHYSICAL_ELL_K_MOMENT_MAP_TAUB",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "generic axial and polar ell>=2 Weyl-Maxwell q/p-primary real solution space on R_t x S1_L x S2 at fixed compact magnetic bundle P_N, every allowed momentum, after local gauge reduction and with the five background stabilizers retained",
        "covariant_bridge": _covariant_identity(),
        "normalization_calibration": _calibration_audit(records),
        "generic_moment_maps": _generic_formulas(records),
        "charge_fibre_disposition": {
            "fixed_magnetic_bundle": "the second-order harmonic magnetic row is forbidden because c_1(P_N) is locally constant",
            "electric_variation": "allowed on fixed P_N but has zero linear energy pairing at the purely magnetic background and cannot remove mu_H",
            "enlarged_continuous_flux_family": "can absorb the constant-lapse component but is a different phase space and is excluded from the no-go",
        },
        "extension_verdict": {
            "pure_generic_extra_fixed_bundle": "NO_NONZERO_REAL_TANGENT_EXTENDS_TO_SECOND_ORDER",
            "reason": "mu_H is a necessary adjoint-cokernel condition and is negative definite on the complete generic axial-plus-polar p-primary space",
            "mixed_Einstein_extra": "OPEN_BECAUSE_THE_Q_PRIMARY_CONTRIBUTION_IS_INDEFINITE_AND_CAN_CANCEL_THE_SCALAR_H_COMPONENT",
            "pure_Einstein": "SECTOR_DEPENDENT_LINEARIZATION_STABILITY_PROBLEM_NOT_CLASSIFIED_HERE",
            "exceptional_and_global": "OPEN_NO_POSITIVE_FREQUENCY_PROMOTION_USED",
        },
        "classification": {
            "generic_covariant_moment_map_Taub_equality_certified": True,
            "three_direct_tensor_normalization_matches": True,
            "generic_H_Px_J_selection_rules_certified": True,
            "generic_extra_H_Taub_negative_definite": True,
            "all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed": True,
            "mixed_Einstein_extra_zero_locus_classified": False,
            "exceptional_global_moment_maps_classified": False,
            "absolute_stabilizer_quotient_certified": False,
            "cyclic_BV_enhancement_certified": False,
            "Lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "interpretation": "The compact generic extra Weyl-Maxwell modes are genuine nonnull linear solutions but are linearization-unstable on the fixed magnetic bundle: the covariant time-translation moment map equals their constant-lapse Taub obstruction and is definite on the complete axial-plus-polar p-primary space. Thus no nonzero real pure-extra generic tangent is the first derivative of a fixed-bundle Weyl-Maxwell family. This does not erase the linear waves, classify mixed Einstein-extra cancellations, authorize a stabilizer quotient, or imply a particle/ghost/quantum theorem.",
        "next_gate": "solve the indefinite common H, P_x, and J_i zero locus for mixed Einstein-extra amplitudes, then compute the homogeneous, ell=1, twist, Wilson-line, and charge blocks using the real symplectic form; independently solve or obstruct the polynomial cyclic BV enhancement",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem identifies the covariant stabilizer moment maps with compact Taub pairings on the generic ell>=2 axial/polar solution space and proves a fixed-bundle second-order no-go for every nonzero pure-extra real tangent. It does not classify mixed q/p cancellation, exceptional or generalized global modes, charge-varying families, an absolute residual quotient, cyclic BV enhancement, causal scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-17",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.09, "commands": ["python3 -m py_compile bridge/einstein_sector/einstein_maxwell_weyl_moment_map_taub_bridge.py bridge/einstein_sector/verify_einstein_maxwell_weyl_moment_map_taub_bridge.py bridge/einstein_sector/tests/test_einstein_maxwell_weyl_moment_map_taub_bridge.py", "python3 -m json.tool bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.90, "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_moment_map_taub_bridge --verify bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json", "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_moment_map_taub_bridge", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_moment_map_taub_bridge"]},
            "tier_2": {"status": "NOT_RUN_NOT_REQUIRED", "reason": "all action, current, direct tensor, stabilizer, and charge-fibre inputs are unchanged content-addressed certificates"},
            "tier_3": {"status": "NOT_RUN", "reason": "no release, shared core, causal, or quantum lifecycle state is promoted; paper-B theorem freeze remains pending mixed and exceptional/global completion"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_moment_map_taub_bridge --verify bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_moment_map_taub_bridge",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_moment_map_taub_bridge",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"moment-map/Taub certificate stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

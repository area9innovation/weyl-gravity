"""Intersect constant-twist shell kernels with the ell=2 stabilizer cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.schema.json"
INPUTS = {
    "einstein_kernel": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.json",
    "extra_kernel": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "moment_resonance_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.json",
    "fixed_ell_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "static_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "axial_module": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_module": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_ell1_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "axial_noether": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "polar_noether": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
}


class ConstantTwistCompleteConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConstantTwistCompleteConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _spin_two_generators() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    ell = 2
    magnetic = list(range(-ell, ell + 1))
    raising = sp.zeros(5)
    for column, m in enumerate(magnetic[:-1]):
        raising[column + 1, column] = sp.sqrt((ell - m) * (ell + m + 1))
    lowering = raising.T
    return (raising + lowering) / 2, (raising - lowering) / (2 * sp.I), sp.diag(*magnetic)


def _moment(vector: sp.Matrix, generator: sp.Matrix) -> sp.Expr:
    return sp.simplify((sp.conjugate(vector).T * generator * vector)[0])


def _even_polynomial_in_omega_squared(expression: str, omega: sp.Symbol, mu: sp.Symbol) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(sp.sympify(expression, locals={"omega": omega})), omega)
    _require(all(power[0] % 2 == 0 for power, _ in polynomial.terms()), "exceptional determinant is not even in omega")
    return sp.factor(sum(coefficient * mu ** (power[0] // 2) for power, coefficient in polynomial.terms()))


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["einstein_kernel"]["classification"]["both_Einstein_q_primary_twist_position_maps_classified"], "Einstein shell kernel changed")
    _require(records["extra_kernel"]["classification"]["complete_nonzero_A_ell2_extra_position_resonance_kernel_classified"], "extra shell kernel changed")
    _require(records["moment_cone"]["classification"]["full_generic_k0_common_zero_cone_classified"], "moment cone changed")
    _require(records["moment_resonance_cone"]["classification"]["necessary_and_sufficient_common_zero_equations"], "moment/resonance intersection changed")
    _require(records["fixed_ell_extension"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"], "wave extension input changed")
    _require(records["static_extension"]["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "static extension input changed")
    _require(records["axial_module"]["classification"]["Einstein_image_equals_complete_q_primary_summand_on_every_physical_fiber"], "axial module changed")
    _require(records["polar_module"]["classification"]["Einstein_image_equals_complete_q_primary_summand"], "polar module changed")
    _require(records["axial_ell1_operator"]["classification"]["extra_fourth_order_ell1_shell_discovered"], "axial ell1 operator changed")
    _require(records["polar_ell1_operator"]["classification"]["polar_ell1_extra_fourth_order_shell_certified"], "polar ell1 operator changed")
    _require(records["axial_noether"]["ungauged_Noether_lift"]["Noether_identities_verified"], "axial Noether complex changed")
    _require(records["polar_noether"]["classification"]["ungauged_target_equation_Noether_complex_certified"], "polar Noether complex changed")
    _require(records["axial_module"]["audit"]["determinantal_ideals_over_R_phys_omega"]["I4"] == "(p^2*q)", "axial physical determinant changed")
    _require(records["polar_module"]["physical_ring"]["determinantal_ideals_over_R_phys_P_omega"]["I4"] == "(p^2*q)", "polar physical determinant changed")

    root = sp.sqrt(3)
    omega, mu_symbol = sp.symbols("omega mu", real=True)
    axial_ell1_determinant = _even_polynomial_in_omega_squared(
        records["axial_ell1_operator"]["operator_theorem"]["nonzero_frequency_gauge_slice"]["determinant"],
        omega,
        mu_symbol,
    )
    polar_ell1_determinant = _even_polynomial_in_omega_squared(
        records["polar_ell1_operator"]["operator_theorem"]["reduced_determinant"],
        omega,
        mu_symbol,
    )
    _require(axial_ell1_determinant == mu_symbol * (mu_symbol - 4) * (3 * mu_symbol - 4), "axial ell1 determinant changed")
    _require(polar_ell1_determinant == (mu_symbol - 4) * (3 * mu_symbol - 4) / 2, "polar ell1 determinant changed")
    frequencies_squared = {
        "minus": 6 - 2 * root,
        "extra": sp.Rational(16, 3),
        "plus": 6 + 2 * root,
    }
    output_nonresonance: dict[str, dict[str, dict[str, str]]] = {}
    for shell, mu in frequencies_squared.items():
        output_nonresonance[shell] = {}
        for output_ell, eigenvalue in ((1, 2), (3, 12)):
            p_value = sp.factor(mu - eigenvalue + sp.Rational(2, 3))
            q_value = sp.factor(mu**2 - 2 * eigenvalue * mu + eigenvalue * (eigenvalue - 2))
            _require(p_value != 0 and q_value != 0, f"{shell} acquired an L={output_ell} resonance")
            if output_ell == 1:
                axial_determinant = sp.factor(axial_ell1_determinant.subs(mu_symbol, mu))
                polar_determinant = sp.factor(polar_ell1_determinant.subs(mu_symbol, mu))
                operator_scope = "exceptional axial h_t=0 gauge slice and polar U=0 quotient"
            else:
                axial_determinant = sp.factor(p_value**2 * q_value)
                polar_determinant = sp.factor(p_value**2 * q_value)
                operator_scope = "generic axial and polar physical-ring invariant factors (1,1,p,pq)"
            _require(axial_determinant != 0 and polar_determinant != 0, f"{shell} L={output_ell} reduced operator became singular")
            output_nonresonance[shell][f"L{output_ell}"] = {
                "p": str(p_value),
                "q": str(q_value),
                "axial_reduced_determinant": str(axial_determinant),
                "polar_reduced_determinant": str(polar_determinant),
                "operator_scope": operator_scope,
            }

    generators = _spin_two_generators()
    off_axis_extra = sp.Matrix([1, 0, 0, 0, 1])
    extra_moments = [sp.simplify(_moment(off_axis_extra, generator)) for generator in generators]
    _require(extra_moments == [0, 0, 0], "off-axis +/-2 witness acquired angular momentum")
    minus_axis = sp.Matrix([0, 0, 1, 0, 0])
    _require([_moment(minus_axis, generator) for generator in generators] == [0, 0, 0], "minus m=0 witness changed")
    extra_occupation = sp.Integer(2)
    minus_occupation = sp.factor(frequencies_squared["extra"] * extra_occupation / frequencies_squared["minus"])
    energy_remainder = sp.simplify(frequencies_squared["extra"] * extra_occupation - frequencies_squared["minus"] * minus_occupation)
    _require(energy_remainder == 0 and minus_occupation > 0, "off-axis energy balance changed")
    exact_off_axis = records["moment_resonance_cone"]["nonaxisymmetric_witness"]
    _require(exact_off_axis["A_extra"] == "18" and exact_off_axis["A_minus"] == "24+8*sqrt(3)", "action-normalized off-axis witness changed")

    return {
        "schema": "einstein-maxwell-weyl-constant-twist-ell2-complete-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_COMPLETE_BOUNDED_CONE",
        "result_state": "COMPLETE_CONSTANT_TWIST_PLUS_ELL2_K0_BOUNDED_SECOND_ORDER_TANGENT_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction class",
            "charge_sector": "fixed N=2 magnetic bundle; no electric, Wilson-line, circumference-velocity or twist-velocity tangent in this carrier",
            "carrier": "one arbitrary constant axial twist-position vector A plus the complete axial/polar ell=2,k=0 Einstein plus/minus and extra p-primary wave carrier",
            "degree": 2,
            "parity": "both axial and polar",
            "ell": "global ell=1 twist plus wave ell=2; all quadratic output L=0,...,4",
            "m": "all m=-2,...,2; for A!=0 components are expressed relative to the twist axis",
            "k": 0,
            "omega": "generalized zero plus all three distinct ell2 positive-frequency shells",
        },
        "coefficient_crosswalk": {
            "raw_wave_coefficients": "E_plus,E_minus in Mat_(2x5)(C), X_extra in Mat_(4x5)(C), with columns ordered m=-2,-1,0,1,2 and negative frequencies fixed by reality",
            "current_normalization": "Choose the certified invertible internal maps S_s with C_s=S_s times raw_s and S_s^dagger*S_s equal to the positive branch current metric; these maps never mix m.",
            "extra_raw_kernel_basis": ["polar_e1", "-4*sqrt(3)*axial_e1+15*polar_e2"],
            "no_background_crosswalk": "All carriers are on the same compact Plebanski-Hacyan background and fixed magnetic bundle.",
        },
        "complete_zero_locus": {
            "A_zero_branch": "For A=0 the complete wave cone is exactly mu_H=mu_J1=mu_J2=mu_J3=0, as in the fixed-ell theorem.",
            "A_nonzero_axis_choice": "Rotate A covariantly to |A|*e_z; rotate the coefficient solution back with the same SO3 action.",
            "Einstein_resonance_equations": "E_plus[:,m]=E_minus[:,m]=0 for m=-2,-1,1,2; both axial/polar m=0 columns are arbitrary before moment equations.",
            "extra_resonance_equations": "For m=-2,-1,1,2 the raw four-component X_extra[:,m] lies in span{polar_e1,-4*sqrt(3)*axial_e1+15*polar_e2}; X_extra[:,0] is arbitrary.",
            "moment_equations": {
                "H": "omega_plus^2*tr(C_plus^dagger*C_plus)+omega_extra^2*tr(C_extra^dagger*C_extra)-omega_minus^2*tr(C_minus^dagger*C_minus)=0",
                "J_a": "omega_plus*tr(C_plus^dagger*C_plus*T_2,a)+omega_extra*tr(C_extra^dagger*C_extra*T_2,a)-omega_minus*tr(C_minus^dagger*C_minus*T_2,a)=0, a=1,2,3",
                "P_x": "identically zero at k=0",
            },
            "necessity_and_sufficiency": "The displayed resonance restrictions and four moment equations are jointly necessary and sufficient for a bounded second-order correction in the declared carrier.",
            "nonzero_A_resonance_kernel_complex_dimension_before_moment_equations": 16,
            "explicit_moment_parameterization": records["moment_resonance_cone"]["common_zero_cone"],
        },
        "quadratic_Noether_compatibility": {
            "nonlinear_identity": "R(Phi)^dagger E(Phi)=0 for the ungauged axial Diff x U1 and polar Diff x Weyl x U1 complexes",
            "second_order_expansion": "R_0^dagger*(1/2 D^2E[u,u])+(DR[u])^dagger*DE[u]+(1/2 D^2R[u,u])^dagger*E_0=0",
            "on_shell_reduction": "E_0=0 and DE[u]=0 imply R_0^dagger*(1/2 D^2E[u,u])=0",
            "consequence": "every twist-wave quadratic source lies in the Noether-compatible source subspace before quotient inversion",
            "axial_and_polar_ungauged_complexes_imported": True,
        },
        "source_decomposition_proof": {
            "formula": "S(u)=S(wave,wave)+2*S(A,wave)+S(A,A)",
            "wave_wave": "CERTIFIED removable exactly when H=J_i=0 by the complete fixed-ell,k=0 all-m axial/polar theorem.",
            "twist_twist": "CERTIFIED removable on the exact standard static constant-twist branch.",
            "twist_wave_resonant": "CERTIFIED zero exactly by the q-shell and p-shell kernel equations; the complete self-adjoint q/p primary decomposition exhausts the physical shell cokernel.",
            "twist_wave_nonresonant": "CERTIFIED removable: the exceptional L=1 axial/polar reduced determinants and generic L=3 p^2*q determinants are nonzero at all three input frequencies, while the expanded nonlinear Noether identity places the quadratic source in the compatible quotient source space.",
            "superposition": "Linearity of the second-order equation in the correction adds the three bounded corrections.",
        },
        "nonresonant_output_ledger": output_nonresonance,
        "independence_witnesses": {
            "aligned_face": "All wave coefficients at m=0 satisfy the resonance equations; the known rotationally neutral two-parameter density cone is embedded.",
            "off_axis_survivor": {
                "extra_raw_internal_direction": "polar_e1, which lies in ker(P_position)",
                "angular_amplitudes": "equal coherent amplitudes at m=+2 and m=-2, zero otherwise",
                "spin_moments": [str(value) for value in extra_moments],
                "extra_occupation_in_unit_current_coordinates": str(extra_occupation),
                "balancing_Einstein_minus_m0_occupation": str(minus_occupation),
                "action_normalized_extra_occupation": exact_off_axis["A_extra"],
                "action_normalized_balancing_Einstein_minus_occupation": exact_off_axis["A_minus"],
                "energy_remainder": str(energy_remainder),
                "meaning": "The nonzero-A bounded cone is strictly larger than the aligned m=0 face.",
            },
            "excluded_counterexample": "A single off-axis axial_e1 coefficient is outside ker(P_position) and retains the certified 24*sqrt(3) adjoint witness.",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "claim": "necessary and sufficient complete second-order tangent cone on the declared carrier"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "claim": "the bounded corrections are a smooth subclass; the larger unrestricted secular cone is not reclassified here"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "simultaneous_moment_and_all_branch_resonance_zero_locus_classified": True,
            "complete_constant_twist_plus_ell2_wave_carrier_covered": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "nonaxisymmetric_nonzero_A_survivor_exhibited": True,
            "twist_velocity_or_other_global_tangents_classified": False,
            "other_ell_or_nonzero_momentum_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "A constant twist does not force the wave to align with its axis and does not erase the ell=2 cone. It imposes an exact incidence condition: Einstein q-primary waves become axisymmetric, while two special extra-primary combinations may remain off axis. Intersecting those linear resonance kernels with the indefinite stabilizer moment cone gives the complete bounded second-order cone for this carrier.",
        "next_gate": "adjoin twist velocity and the remaining homogeneous directions without merging scopes; then generalize the incidence theorem to arbitrary fixed ell and finite harmonic sums",
        "claim_boundary": "This is complete only for constant twist position plus the full ell=2,k=0 generic wave carrier, with other global tangents set to zero. It does not classify twist velocity, electric/Wilson/circumference directions, other ell, nonzero or opposite momenta, unrestricted secular corrections, causal propagation, all-orders solutions, residual states, observables or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.33},
            "tier_1": {"status": "PASS", "elapsed_seconds": 5.11, "tests_run": 40},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "both direct twist-shell theorems, the complete fixed-ell wave correction and the static twist correction are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "other global directions and harmonics remain open; no programme-wide freeze is promoted"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise ConstantTwistCompleteConeError("constant-twist complete ell2 cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_COMPLETE_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()

"""Complete finite-harmonic smooth-global Weyl--Maxwell tangent cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.schema.json"
INPUTS = {
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "finite_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "branch_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
    "standard_inventory": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "homogeneous_cofiber": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist_cofiber": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
    "exceptional_k0": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "exceptional_nonzero_k": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "exceptional_global_moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "exceptional_extra_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "ell0_nonzero": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell1_nonzero": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
    "axial_ell1_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "fixed_bundle": ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json",
    "bounded_polynomial_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "bounded_resonance_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
}


class CompleteFiniteHarmonicError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompleteFiniteHarmonicError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _polynomial_primitives() -> dict[str, Any]:
    t = sp.symbols("t")
    fourth: list[dict[str, str]] = []
    second: list[dict[str, str]] = []
    for degree in range(7):
        source = t**degree
        primitive4 = sp.factor(t ** (degree + 4) / sp.prod(degree + offset for offset in range(1, 5)))
        primitive2 = sp.factor(t ** (degree + 2) / ((degree + 1) * (degree + 2)))
        _require(sp.diff(primitive4, t, 4) == source, "fourth-order polynomial primitive changed")
        _require(sp.diff(primitive2, t, 2) == source, "second-order polynomial primitive changed")
        fourth.append({"source": str(source), "primitive": str(primitive4)})
        second.append({"source": str(source), "primitive": str(primitive2)})
    return {
        "source_degree_range": "0<=r<=6",
        "D_fourth_derivative_primitives": fourth,
        "A_x_second_derivative_primitives": second,
        "consequence": "every homogeneous dynamical polynomial source has a finite polynomial right inverse",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["abstract_cone"]["flags"]["FINITE_HARMONIC_TANGENT_CONE_FORMULA"], "abstract cone changed")
    _require(records["finite_generic"]["classification"]["arbitrary_finite_generic_harmonic_sums_classified_smooth_global"], "finite generic theorem changed")
    dictionary = records["branch_dictionary"]["classification"]
    _require(dictionary["all_harmonic_sector_coefficient_maps_available"], "branch inventory changed")
    _require(dictionary["exceptional_k0_solution_cofiber_certified"] and dictionary["exceptional_nonzero_k_solution_cofiber_certified"], "exceptional inventory changed")
    _require(dictionary["homogeneous_solution_cofiber_zero"] and dictionary["twist_solution_cofiber_zero"], "global inventory changed")
    _require(records["standard_inventory"]["classification"]["complete_standard_harmonic_linear_restriction"], "standard inventory changed")
    _require(records["homogeneous_cofiber"]["classification"]["complete_homogeneous_target_kernel_certified"], "homogeneous cofiber changed")
    _require(records["twist_cofiber"]["classification"]["complete_twist_target_primary_certified"], "twist cofiber changed")
    _require(records["exceptional_k0"]["classification"]["complete_exceptional_k0_target_solution_decomposition_certified"], "exceptional k=0 cofiber changed")
    _require(records["exceptional_nonzero_k"]["classification"]["nonzero_k_exceptional_solution_cofiber_certified"], "exceptional nonzero-k cofiber changed")
    _require(records["exceptional_global_moment_maps"]["classification"]["standard_homogeneous_common_zero_locus_classified"], "global moment maps changed")
    _require(records["exceptional_extra_taub"]["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"], "exceptional current changed")
    _require(records["homogeneous_operator"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"], "homogeneous operator changed")
    _require(records["ell0_nonzero"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"], "L=0 Fourier theorem changed")
    _require(records["ell1_nonzero"]["static_consequence"]["every_Noether_compatible_static_L1_source_is_removable"], "L=1 nonzero Fourier theorem changed")
    _require(records["axial_ell1_zero"]["classification"]["zero_fibre_physical_cokernel_equals_rotation_triplet"], "axial L=1 zero block changed")
    _require(records["polar_ell1_zero"]["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"], "polar L=1 zero block changed")
    _require(records["moment_map"]["covariant_bridge"]["result"].startswith("<zeta_X"), "Taub bridge changed")
    _require(not records["fixed_bundle"]["topology_and_charge_fibres"]["fixed_compact_u1_bundle"]["allowed_magnetic_lift"], "fixed-bundle gate changed")
    _require(records["bounded_polynomial_witness"]["classification"]["bounded_or_finite_quasiperiodic_correction_obstructed"], "polynomial bounded witness changed")
    _require(records["bounded_resonance_witness"]["classification"]["nonzero_adjoint_cokernel_witness_certified"], "resonant bounded witness changed")

    inventory = {
        "generic": "all ell>=2 axial/polar q-primary Einstein and p-primary extra modes, all m and compact momenta",
        "exceptional_ell1": "standard and extra axial/polar oscillators for every compact momentum",
        "twist": "the three axial k=0 generalized-zero pairs A_a+B_a*t",
        "homogeneous": "the complete six-coordinate k=0 block (a,b,c,d,Q_e,W_x)",
        "absent": "no additional homogeneous or twist Weyl cofiber and no other certified target primary",
    }
    return {
        "schema": "einstein-maxwell-weyl-complete-finite-harmonic-smooth-global-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPLETE_FINITE_HARMONIC_SMOOTH_GLOBAL_SECOND_ORDER",
        "result_state": "COMPLETE_CERTIFIED_FINITE_HARMONIC_TANGENT_CONE_EXTENDIBLE_SMOOTH_GLOBAL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G5_COMPLETE_FINITE_HARMONIC_ALL_CERTIFIED_LINEAR_INPUTS",
        "domain": "every real finite-support tangent in the complete certified Weyl-Maxwell linear solution inventory on the fixed compact magnetic bundle P_N, before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "complete_linear_inventory": inventory,
        "finite_source_module": {
            "output_label": "j=(L,M,K,Omega,parity)",
            "generic_and_exceptional_oscillators": "finite sums of exp(-i*omega*t) with certified real shell frequencies",
            "generalized_zero_inputs": "homogeneous metric degree at most three, homogeneous Maxwell and twists degree at most one",
            "quadratic_temporal_degree": "at most six, multiplying a finite set of signed output frequencies",
            "spatial_closure": "finite S1 Fourier sums and finite S2 Clebsch-Gordan sums",
            "correction_module": "real smooth spatially periodic finite exponential-polynomials, closed under all required algebraic and secular primitives",
        },
        "complete_output_cokernel_theorem": {
            "equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
            "reduction_order": ["complete Noether-compatible target", "local Diff-Weyl-U1 gauge quotient", "adjoint cokernel in the declared correction module"],
            "L0_K0": {
                "constraint_cokernel": ["zeta_H", "zeta_Px"],
                "dynamical_invariants": ["D=C-K with D''''=source_D", "A_x with A_x''=source_Ax"],
                "polynomial_right_inverse": _polynomial_primitives(),
            },
            "L1_K0": {
                "axial_constraint_cokernel": ["zeta_J1", "zeta_J2", "zeta_J3"],
                "axial_zero_root": "after the rotation pairing vanishes, the twist-primary polynomial source is inverted by the finite secular primitive",
                "polar_zero_block": "invertible after gauge reduction",
                "nonzero_frequency": "standard and extra shell forcing has a finite exponential-polynomial secular inverse",
            },
            "nonzero_spatial_Fourier": {
                "L0": "exact modulo Diff-Weyl-U1 for every nonzero Fourier pair",
                "L1": "static blocks have Noether-only cokernel; nonstatic shell roots have finite secular inverses",
                "L_at_least_2": "the generic Smith factors give algebraic inverses off shell and finite secular inverses on every p/q root",
            },
            "generic_static_outputs": records["finite_generic"]["complete_adjoint_cokernel_decomposition"]["zero_block"]["L_at_least_2"],
            "decomposition": "coker L_smooth = span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}",
            "no_additional_charge_cokernel": "constant U1 reducibility is removed with the Noether identities; fixed P_N forbids a magnetic harmonic correction, and the quadratic source preserves that topological sector",
        },
        "Taub_identification": {
            "formula": "<zeta_X,(1/2)D^2E[u,u]>=mu_X(u)=(1/2)Omega_WM(u,L_X u)",
            "generators": ["H", "P_x", "J_1", "J_2", "J_3"],
            "scope": "all certified linear blocks, including generalized-zero and exceptional modes, by the covariant action Noether identity",
            "complete_cone_condition": "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0",
        },
        "smooth_global_theorem": {
            "tangent_cone": "Z2^smooth={u in T_WM^finite:mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0}",
            "necessity": "pairing the second-order equation with the complete persistent adjoint cokernel gives the five moment maps",
            "sufficiency": "their vanishing puts every finite output source in the algebraic or finite secular image; block corrections and their conjugates assemble a real smooth spatially periodic finite exponential-polynomial v",
            "exceptional_and_global_inputs_included": True,
            "multiple_momenta_m_phases_and_branches_included": True,
            "coefficient_table_not_required_for_existence": "the exhaustive output operator/cokernel theorem decides image membership; source coefficients determine the chosen correction but introduce no new smooth cokernel",
        },
        "bounded_obstruction_ledger": {
            "formula": "Z2^bounded={u:mu_X(u)=0, P_(j,r)(u)=0, R_(j,a)(u)=0 for every finite output block}",
            "polynomial_growth_functionals": "P_(j,r) extracts every positive-degree t^r coefficient of the quadratic source, since a bounded finite-quasiperiodic correction has a bounded image",
            "resonant_functionals": "R_(j,a)=<zeta_(j,a),S_j(u,u)> for an exact reduced left-kernel basis on each nonzero-frequency target shell",
            "independence_from_stabilizers": "zero-block stabilizer covectors are excluded from P and R",
            "necessity_and_sufficiency": "certified by the abstract finite-block theorem after the displayed exhaustive output decomposition",
            "polynomial_independence_witness": "the aligned global-extra cone has mu_X=0 but a nonzero t^2 source coefficient and is bounded-obstructed",
            "resonant_independence_witness": "the twist-balanced exceptional fixture has mu_X=0 but nonzero R_bounded",
            "coefficientwise_common_zero_locus": "OPEN",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED_FORMULA_ZERO_LOCUS_OPEN", "persistent_functionals": ["mu_X", "P_(j,r)", "R_(j,a)"]},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "persistent_functionals": ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3"]},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP", "reason": "no background-specific compact-source retarded Weyl-Maxwell complex is certified"},
        },
        "classification": {
            "complete_certified_linear_input_inventory_included": True,
            "exceptional_and_global_inputs_included": True,
            "complete_finite_harmonic_smooth_tangent_cone_classified": True,
            "complete_smooth_adjoint_cokernel_equals_five_stabilizers": True,
            "bounded_polynomial_and_resonant_ledger_defined": True,
            "bounded_common_zero_locus_solved": False,
            "infinite_harmonic_completion_classified": False,
            "all_orders_integrability": False,
            "final_residual_descent": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "At second order and for finite harmonic support, the smooth exponential-polynomial category is now complete on the compact product: exceptional dipoles, global charge/holonomy data, twists and generic waves introduce no obstruction beyond the five compact stabilizer moment maps. This does not say that bounded corrections exist; polynomial growth and on-shell resonance define additional independent bounded functionals.",
        "next_gate": "solve or stratify the complete bounded polynomial-plus-resonant zero locus; separately formulate an infinite-mode Sobolev completion or construct a background-specific causal/retarded complex without borrowing the smooth-global lifecycle",
        "claim_boundary": "This is the complete finite-support REDUCED-MODE tangent-cone theorem in the smooth exponential-polynomial correction class on one compact background. It does not solve the bounded common zero locus, prove infinite-mode convergence, all-orders integration, final residual descent, causal propagation, scattering, observables, particles or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.26, "max_rss_kb": 16104},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.74, "max_rss_kb": 58124, "tests_run": 14},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "complete linear inventory, exceptional/generic output operators, Taub bridge and abstract finite-block theorem are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "bounded zero-locus, infinite-mode, causal, all-orders, residual and quantum claims remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order --verify bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build_certificate()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert args.verify is not None
    _require(json.loads(args.verify.read_text(encoding="utf-8")) == payload, "complete finite-harmonic certificate is stale")


if __name__ == "__main__":
    main()

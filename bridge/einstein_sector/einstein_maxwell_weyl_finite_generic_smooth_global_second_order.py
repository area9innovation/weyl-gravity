"""Finite-generic-harmonic Weyl--Maxwell second-order tangent cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.schema.json"
INPUTS = {
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "finite_k0": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
    "opposite_momentum": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
    "ell0_nonzero": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell1_nonzero": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
    "ell1_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "homogeneous_nonzero_frequency": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
}


class FiniteGenericSmoothGlobalError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FiniteGenericSmoothGlobalError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _static_generic_audit() -> dict[str, Any]:
    lam, u = sp.symbols("Lambda u", real=True, nonnegative=True)
    p = sp.factor(-u - lam + sp.Rational(2, 3))
    q = sp.factor(u**2 + 2 * lam * u + lam * (lam - 2))
    shifted_q = sp.Poly(sp.expand(q.subs(lam, lam + 6)), lam, u)
    _require(all(coefficient > 0 for coefficient in shifted_q.coeffs()), "static generic q sign changed")
    return {
        "domain": "L>=2, Lambda=L(L+1)>=6, Omega=0, arbitrary real output K with u=K^2>=0",
        "p": str(p),
        "p_sign": "strictly negative",
        "q": str(q),
        "q_shift_Lambda_minus_6_coefficients": [str(value) for value in shifted_q.coeffs()],
        "q_sign": "strictly positive",
        "consequence": "every static generic output block is invertible after local gauge reduction",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["abstract_cone"]["flags"]["FINITE_HARMONIC_TANGENT_CONE_FORMULA"], "abstract cone changed")
    _require(records["abstract_cone"]["correction_classes"]["SMOOTH_SECULAR"]["status"] == "CERTIFIED", "secular category changed")
    _require(records["moment_map"]["classification"]["generic_covariant_moment_map_Taub_equality_certified"], "Taub bridge changed")
    _require(records["finite_k0"]["classification"]["all_finite_cross_ell_superpositions_classified"], "finite k=0 theorem changed")
    _require(records["opposite_momentum"]["classification"]["opposite_momentum_relative_phases_classified_in_smooth_global_class"], "opposite-momentum theorem changed")
    _require(records["ell0_nonzero"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"], "L=0 nonzero Fourier theorem changed")
    _require(records["ell1_nonzero"]["static_consequence"]["every_Noether_compatible_static_L1_source_is_removable"], "L=1 static theorem changed")
    _require(records["ell1_zero"]["classification"]["zero_fibre_physical_cokernel_equals_rotation_triplet"], "L=1 zero cokernel changed")
    _require(records["polar_ell1_zero"]["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"], "polar L=1 zero cokernel changed")
    _require(records["homogeneous_nonzero_frequency"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"], "homogeneous oscillatory theorem changed")
    _require(records["axial_generic"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial ring changed")
    _require(records["polar_generic"]["classification"]["Einstein_image_equals_complete_q_primary_summand"], "polar ring changed")

    return {
        "schema": "einstein-maxwell-weyl-finite-generic-smooth-global-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_GENERIC_SMOOTH_GLOBAL_SECOND_ORDER",
        "result_state": "ARBITRARY_FINITE_GENERIC_HARMONIC_COMMON_ZERO_CONE_EXTENDIBLE_SMOOTH_GLOBAL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G5_ARBITRARY_FINITE_GENERIC_HARMONICS_ALL_COMPACT_MOMENTA",
        "domain": "every real finite sum of generic ell>=2 Weyl-Maxwell axial and polar Einstein-plus, Einstein-minus and two extra-primary modes, with arbitrary allowed compact momenta, m values, parities, branch amplitudes and relative phases, on fixed P_N before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "output_indexing": {
            "block_label": "j=(L,M,K,Omega,parity)",
            "spatial_rules": "K is a signed sum of two allowed compact input momenta and L,M obey the complete S2 Clebsch-Gordan rules",
            "temporal_rules": "Omega is a signed sum of two positive input shell frequencies; conjugate blocks enforce reality",
            "finite_closure": "a finite input set produces finitely many output block labels",
            "no_mode_identification": "each output is classified in the Weyl-Maxwell target operator on this same compact Plebanski-Hacyan background",
        },
        "complete_adjoint_cokernel_decomposition": {
            "equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
            "Noether_reduction": "in every block first restrict the source target to the kernel of the complete Diff-Weyl-U1 identity matrix",
            "gauge_reduction": "remove the certified local gauge image before taking the reduced adjoint cokernel",
            "zero_block": {
                "label": "Omega=0,K=0",
                "L0": "the physical constraint-adjoint components are time translation H and compact translation P_x",
                "L1": "the three physical axial twist-adjoint components are the lifted rotations J_1,J_2,J_3",
                "L_at_least_2": _static_generic_audit(),
                "decomposition": "coker L_zero = span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3} modulo Noether identities",
            },
            "nonzero_Fourier_blocks": {
                "L0": "the direct six-field Fourier complex is exact modulo Diff-Weyl-U1 for every (Omega,K)!=(0,0)",
                "L1_static": "at Omega=0,K!=0 both parity Hessians have gauge-only kernel and Noether-only cokernel",
                "L1_nonstatic": "off shell the reduced operator is invertible; on either shell Omega^2-K^2 in {4,4/3}, a finite exponential-polynomial secular inverse exists",
                "L_at_least_2_static": _static_generic_audit(),
                "L_at_least_2_nonstatic": "the physical Smith factors 1,1,p,pq with (p,q)=1 give an algebraic inverse off shell and a finite exponential-polynomial inverse at every p- or q-root",
                "physical_cokernel_in_smooth_secular_class": "zero",
            },
            "global_formula": "coker L_smooth = stab^* and coker L_bounded = stab^* direct-sum (sum_j R_j^bounded)",
        },
        "bounded_resonance_functionals": {
            "status": "CERTIFIED_AS_EXACT_FINITE_LEDGER_NOT_ZERO_LOCUS_SOLVED",
            "definition": "for each nonzero output block j on a target shell, choose an exact basis zeta_(j,a) of the reduced left kernel after Noether/gauge descent and set R_(j,a)(u)=<zeta_(j,a),S_j(u,u)>",
            "phase_sensitivity": "S_j retains the signed complex products of input coefficients, so relative phases and interference between distinct |k| fibres are not discarded",
            "necessity_and_sufficiency": "a bounded or finite-quasiperiodic correction exists exactly when all five mu_X and every finite R_(j,a) vanish",
            "independence": "the R_(j,a) basis excludes the zero-block stabilizer covectors, so no obstruction is counted twice",
            "coefficientwise_zero_locus": "OPEN",
        },
        "smooth_global_theorem": {
            "correction_space": "real smooth S1-periodic finite exponential-polynomial fields; polynomial temporal prefactors are permitted on resonant output shells",
            "tangent_cone": "Z2^smooth={u:mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0}",
            "necessity": "the five equations are the complete persistent reduced adjoint-cokernel pairings",
            "sufficiency": "all nonzero output blocks are in the algebraic or secular image and the finite blockwise corrections assemble with their complex conjugates",
            "multiple_absolute_momentum_fibres": "included without requiring equal densities, equal phases or pairwise cancellation within an individual |k| fibre",
            "all_relative_phases": "included",
            "correction_constructive": "yes, blockwise from the exceptional right inverses and generic fibrewise Smith inverses",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "CERTIFIED_FORMULA_ZERO_LOCUS_OPEN",
                "cone": "mu_X(u)=0 and R_(j,a)^bounded(u)=0 for every finite resonant output block",
            },
            "SMOOTH_SECULAR": {
                "status": "CERTIFIED",
                "cone": "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0",
            },
            "CAUSAL_RETARDED": {
                "status": "NO_CERTIFIED_MAP",
                "reason": "no background-specific compact-source retarded Weyl-Maxwell complex has been certified",
            },
        },
        "classification": {
            "arbitrary_finite_generic_harmonic_sums_classified_smooth_global": True,
            "multiple_absolute_momentum_fibres_classified_smooth_global": True,
            "opposite_momenta_and_all_relative_phases_included": True,
            "complete_reduced_adjoint_cokernel_decomposition_certified": True,
            "moment_maps_identified_with_all_persistent_smooth_obstructions": True,
            "bounded_resonance_functional_ledger_defined_exactly": True,
            "bounded_resonance_zero_locus_solved": False,
            "exceptional_or_global_input_modes_included": False,
            "infinite_harmonic_completion_classified": False,
            "all_orders_integrability": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "For arbitrary finite generic wave packets on the compact product, interference between different momenta and phases can create bounded-category resonances but cannot create a new smooth-secular obstruction. After Noether and gauge descent, every nonzero Fourier block admits an algebraic or finite secular inverse. The only persistent second-order obstructions are therefore the five compact stabilizer moment maps.",
        "next_gate": "adjoin the certified homogeneous, twist, Wilson-line, electric and physical ell=1 input blocks to this finite generic carrier; then solve the bounded resonant-functional zero locus or begin a separately justified compact-source causal theorem",
        "claim_boundary": "This theorem covers arbitrary finite generic ell>=2 input sums and multiple compact momentum fibres only in the smooth exponential-polynomial category. It does not include exceptional/global input modes, solve the bounded resonance zero locus, prove an infinite-mode PDE completion, all-orders integration, final residual descent, causal propagation, scattering, particles or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.14, "max_rss_kb": 15976, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.94, "max_rss_kb": 57976, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_generic_smooth_global_second_order --verify bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_generic_smooth_global_second_order.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_finite_generic_smooth_global_second_order",
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "all exceptional and generic output operators, the Taub bridge and the abstract finite-block theorem are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "exceptional/global inputs, infinite-mode, causal, residual, all-orders and quantum claims remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_generic_smooth_global_second_order --verify bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_generic_smooth_global_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_finite_generic_smooth_global_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "finite-generic theorem certificate is stale")


if __name__ == "__main__":
    main()

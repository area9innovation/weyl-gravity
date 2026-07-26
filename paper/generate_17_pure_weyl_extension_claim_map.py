#!/usr/bin/env python3
"""Generate the fail-closed publication claim map for Paper 17."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
OUTPUT = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"

AUTHORITIES = {
    "factor_filtration": (
        "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "projective_cocycle": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_cocycle_v1/certificate.json"
    ),
    "analytic_continuation": (
        "black_hole_programme/certificates/"
        "BH3_ANALYTIC_CONTINUATION_GATE.json"
    ),
    "qnm_winding": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "full_contour_winding_v1/certificate.json"
    ),
    "qnm_selector": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "local_selector_v1/certificate.json"
    ),
    "spin_one_unit": (
        "black_hole_programme/phase3/"
        "axial_qnm_spin_one_local_unit_v1/certificate.json"
    ),
    "fredholm_promotion": (
        "black_hole_programme/phase4/"
        "axial_qnm_fredholm_promotion_v1/certificate.json"
    ),
    "critical_mass_parent": (
        "black_hole_programme/phase4/"
        "einstein_weyl_critical_mass_jet_v1/certificate.json"
    ),
    "null_infinity_reconstruction": (
        "black_hole_programme/phase4/"
        "axial_qnm_null_infinity_reconstruction_v1/certificate.json"
    ),
    "conserved_source_overlap": (
        "black_hole_programme/phase4/"
        "axial_qnm_conserved_source_overlap_v1/certificate.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def authority_map() -> dict:
    result = {}
    for name, relative in AUTHORITIES.items():
        path = ROOT / relative
        certificate = json.loads(path.read_text())
        result[name] = {
            "path": relative,
            "sha256": digest(path),
            "result_id": certificate.get("result_id"),
            "status": certificate.get("status"),
            "result_token": certificate.get("result_token"),
        }
    return result


def payload() -> dict:
    return {
        "schema": "paper-draft-source-map-v1",
        "paper_id": "PAPER_17_PURE_WEYL_EXTENSION_RESONANCE",
        "result_id": "PAPER17_REFEREE_MAJOR_REVISION",
        "lifecycle_state": "DRAFT_ALLOWED",
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "authorities": authority_map(),
        "exact_identities": {
            "bach_cocycle_normal_form": {
                "q": "-I*(15*r + 13 + 12/r + 9/r**2)/(120*omega)",
                "representative": "I*omega*(r-2)/(2*r)",
                "parameter_domain": "omega != 0",
            },
            "triangular_gauge": {
                "operator": "q*D-D(q)/2",
                "commutator_on_kernel": "-K_U(q)/2",
                "field_redefinition": "Q_q=2*q*D-D(q)",
                "direct_commutator_on_kernel": "-K_U(q)",
            },
            "graded_mass_squared_tangent": {
                "graded_mass_operator": "L-m*f",
                "mass_class": "[f]",
                "bach_to_mass_class": "I*omega/2",
                "fixed_frequency_tangent_relation": "m=I*omega*tau/2",
                "spectral_global_reparameterization": False,
                "complete_coupled_massive_axial_system": False,
                "coulomb_exponent": "sigma*I*(2*k+m/k)",
                "coulomb_exponent_mass_derivative_at_zero": "0",
                "q_slope_at_infinity": "-I/(8*omega)",
                "endpoint_comparison_status": "FORMAL_ASYMPTOTIC_ONLY",
                "opposite_jost_admixture_excluded": False,
                "physical_mass_velocity_certified": False,
            },
            "smith_and_root": {
                "defective_smith_type": [0, 0, 2],
                "semisimple_smith_type": [0, 1, 1],
                "selector": "kappa=b/a_prime=beta/alpha",
                "carrier_quotient": "-1/kappa",
                "intrinsic_tau_velocity": "-kappa",
                "physical_mass_velocity_relation": "CONDITIONAL_CROSSWALK_ONLY",
                "kappa_re_enclosure": ["-0.047", "0.022"],
                "kappa_im_enclosure": ["0.064", "0.138"],
            },
            "green_principal_coefficient": {
                "rank": 1,
                "pole_order": 2,
                "coefficient": "-beta*u tensor tilde_u/alpha**2",
                "cutoff_exterior": True,
                "global_causal_resolvent": False,
            },
            "parent_mass_derivative": {
                "identity": "G_W=-(partial_m inverse(E+m*A)|0)/(4*alpha_W)",
                "double_coefficient": "-nu*P/(4*alpha_W)",
                "isolated_contour_only": True,
                "certified_scalar_selector_identified_with_parent_nu": False,
            },
            "outgoing_trace_bridge": {
                "principal_coefficient": (
                    "-beta*O_scri(u) tensor (tilde_u*chi_s)/alpha**2"
                ),
                "analytic_on_local_jost_family": True,
                "global_causal_trace": False,
            },
            "null_infinity_reconstruction": {
                "einstein_metric_heads": "H0=-r+O(1),H1=2*r+O(1)",
                "carrier_metric_heads": (
                    "H0=3*r**2/4-3*r/2+O(1),H1=-3*r**2/2+O(1)"
                ),
                "einstein_bondi_shear": "-2*I*X_AB/omega",
                "einstein_bondi_shear_nonzero": True,
                "carrier_standard_strain_falloff": False,
                "carrier_strain_leading": "3*I*X_AB/(2*omega)",
            },
            "conserved_traceless_source": {
                "P_t": "0",
                "P_r": "mu*F/(2*I*omega*r*f)",
                "P_tensor": "d_r(r*F)/(2*I*omega)",
                "master_source": "f*S_odd=F",
                "conserved": True,
                "traceless": True,
                "adjoint_choice": "F=eta*conjugate(tilde_u)",
                "adjoint_overlap": "integral(eta*abs(tilde_u)**2,drstar)>0",
                "source_domain": "COMPLEXIFIED_FREQUENCY_DOMAIN",
                "real_causal_temporally_compact": False,
                "specified_trajectory": False,
            },
        },
        "claim_flags": {
            "non_split_rw_self_extension_exact_on_positive_real_axis": True,
            "bach_mass_direction_normal_form_exact": True,
            "graded_mass_squared_direction_exact": True,
            "complete_coupled_massive_axial_crosswalk": False,
            "endpoint_compatible_physical_mass_jet_exact": False,
            "physical_massive_qnm_slope_certified": False,
            "certified_qnm_smith_type_0_0_2": True,
            "generalized_root_carrier_nonzero": True,
            "exterior_cutoff_green_double_pole": True,
            "outgoing_trace_bridge_exact": True,
            "einstein_bondi_shear_nonzero": True,
            "complexified_conserved_traceless_source_overlap_nonzero": True,
            "real_causal_source_overlap_nonzero": False,
            "global_causal_resolvent": False,
            "complete_retarded_qnm_expansion": False,
            "generalized_constant_component_standard_falloff": False,
            "specified_astrophysical_source_overlap": False,
            "detector_sensitivity": False,
            "quantum_positivity_statement": False,
        },
        "excluded_programme_material": [
            "all-multipole static threshold classification",
            "higher mass jets and QNM acceleration",
            "spectral-flow contour sum rules",
            "generic two-parameter exceptional-point unfolding",
            "pseudospectral and positive-metric asymptotics",
            "detector templates and coherent forcing",
        ],
        "does_not_establish": [
            "LORENTZIAN-CAUSAL resolvent or retarded contour theorem",
            "complete quasinormal expansion or late-time asymptotics",
            "full coupled massive axial-system crosswalk",
            "exact physical massive Jost derivative or physical massive-QNM slope",
            "standard asymptotic-flatness falloff for the generalized constant component",
            "real causal temporally compact source, specified astrophysical matter source, or detector sensitivity",
            "all-multipole Bach nonsplitting",
            "quantum positivity, unitarity, or no-go theorem",
        ],
        "trusted_computing_base": {
            "python": "3.12.13",
            "sympy": "1.14.0",
            "python_flint": "0.9.0",
            "jsonschema": "4.26.0",
            "validated_arithmetic": "arb/acb directed outward rounding",
            "immutable_doi_archive_available": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = encoded(payload())
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if args.check:
        if not output.exists() or output.read_bytes() != data:
            raise SystemExit("REFUSED: Paper 17 claim map is stale")
        print("PASS: Paper 17 claim map is current")
        return
    output.write_bytes(data)
    print(f"WROTE {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

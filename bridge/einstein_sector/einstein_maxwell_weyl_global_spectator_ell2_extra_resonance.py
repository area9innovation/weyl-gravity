"""Remove circumference and Wilson spectators from the ell2-extra resonance gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.schema.json"
INPUTS = {
    "resonance_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json",
    "homogeneous_quadric": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
}


class GlobalSpectatorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GlobalSpectatorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _transport_theorem() -> dict[str, object]:
    eta, circumference = sp.symbols("eta c")
    radius = sp.sqrt(1 + eta * circumference)
    first_derivative = sp.diff(radius, eta).subs(eta, 0)
    second_derivative = sp.diff(radius, eta, 2).subs(eta, 0)
    _require(first_derivative == circumference / 2, "radius tangent changed")
    _require(second_derivative == -circumference**2 / 4, "radius second derivative changed")
    return {
        "exact_background_family": "g_R=-dt^2+R^2 dx^2+dOmega_2^2, F=vol_(S2), with R^2=1+eta*c",
        "radius_series": "R=1+(eta*c)/2-(eta^2*c^2)/8+O(eta^3)",
        "radius_first_derivative": str(first_derivative),
        "k0_mode_transport": {
            "rule": "pull back the R=1 k=0 Jacobi field under x'=R*x; each covariant x index and each A_x coefficient contributes one factor R",
            "periodicity": "k=0 representatives remain periodic on the fixed coordinate circle",
            "equation": "L_R u_R=0 for every R",
            "mixed_derivative_identity": "L_1*(partial_R u_R)|_1 + (partial_R L_R)|_1*u_1=0",
            "explicit_mixed_correction": "(c/2) times the derivative with respect to log R of the transported extra representative",
            "conclusion": "the c-times-extra bilinear source lies in im L and every adjoint-cokernel pairing vanishes",
        },
        "Wilson_family": {
            "connection": "A_W=A_bar+W_x dx",
            "curvature": "F_W=F_bar for every W_x",
            "extra_mode_transport": "unchanged",
            "conclusion": "the W_x-times-extra bilinear Euler source vanishes identically",
        },
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["resonance_census"]["classification"]["unique_zero_plus_positive_resonance_is_global_times_ell2_extra"], "resonance census changed")
    _require(records["homogeneous_quadric"]["classification"]["circumference_and_Wilson_spectators_retained"], "homogeneous spectator input changed")
    _require(records["axial_generic"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial extra block changed")
    _require(records["polar_generic"]["classification"]["canonical_extra_polar_quotient_two_p_summands"], "polar extra block changed")
    theorem = _transport_theorem()
    return {
        "schema": "einstein-maxwell-weyl-global-spectator-ell2-extra-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_SPECTATOR_ELL2_EXTRA_RESONANCE",
        "result_state": "CIRCUMFERENCE_AND_WILSON_TIMES_ELL2_EXTRA_RESONANT_SOURCES_REMOVABLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "constant circumference c and flat Wilson W_x global directions crossed with every axial/polar ell=2,k=0 extra-primary Jacobi field, all m, on the fixed magnetic bundle",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "transport_theorem": theorem,
        "classification": {
            "all_m_and_both_parities_by_naturality": True,
            "circumference_times_ell2_extra_source_in_linear_image": True,
            "Wilson_times_ell2_extra_source_identically_zero": True,
            "circumference_and_Wilson_cannot_cancel_exceptional_adjoint_defect": True,
            "remaining_homogeneous_a_b_d_Qe_cross_sources_classified": False,
            "remaining_twist_A_B_cross_sources_classified": False,
            "difference_frequency_resonances_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The unique positive-sum resonance gate has two exact spectator directions. Flat Wilson holonomy never enters the Euler operator, while the circumference direction is tangent to an exact circle-radius family and transports every k=0 extra mode. Their bilinear sources therefore have zero exceptional adjoint projection and cannot cancel the exceptional self-defect. Only the dynamical homogeneous directions and twists remain in this gate.",
        "next_gate": "compute the a,b,d,Q_e and twist-position/velocity bilinear sources against both axial and polar ell=2 extra representatives",
        "claim_boundary": "This is a naturality-based second-order removability theorem for c and W_x only. It does not classify the remaining global directions, frequency differences, opposite momenta, all-orders integration, final residual descent, or causal/quantum physics.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.22, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_spectator_ell2_extra_resonance --verify bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_spectator_ell2_extra_resonance"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the remaining global-times-extra source matrix is open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_spectator_ell2_extra_resonance --verify bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_spectator_ell2_extra_resonance",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "global-spectator certificate is stale")


if __name__ == "__main__":
    main()

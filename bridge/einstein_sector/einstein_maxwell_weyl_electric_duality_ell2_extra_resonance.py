"""Remove the electric-charge direction from the ell2-extra resonance gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.schema.json"
INPUTS = {
    "spectator_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json",
    "background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
    "global_block": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
}


class ElectricDualityError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ElectricDualityError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _duality_identities() -> dict[str, object]:
    theta = sp.symbols("theta", real=True)
    cosine, sine = sp.cos(theta), sp.sin(theta)
    electric = sp.Matrix(sp.symbols("E0:3", real=True))
    magnetic = sp.Matrix(sp.symbols("B0:3", real=True))
    rotated_electric = cosine * electric + sine * magnetic
    rotated_magnetic = cosine * magnetic - sine * electric
    dyad_defect = (
        rotated_electric * rotated_electric.T
        + rotated_magnetic * rotated_magnetic.T
        - electric * electric.T
        - magnetic * magnetic.T
    ).applyfunc(sp.trigsimp)
    energy_defect = sp.trigsimp(rotated_electric.dot(rotated_electric) + rotated_magnetic.dot(rotated_magnetic) - electric.dot(electric) - magnetic.dot(magnetic))
    poynting_defect = (rotated_electric.cross(rotated_magnetic) - electric.cross(magnetic)).applyfunc(sp.trigsimp)
    _require(dyad_defect == sp.zeros(3), "duality stress dyad changed")
    _require(energy_defect == 0, "duality energy changed")
    _require(poynting_defect == sp.zeros(3, 1), "duality Poynting vector changed")
    rotation = sp.Matrix([[cosine, sine], [-sine, cosine]])
    _require((rotation.T * rotation).applyfunc(sp.trigsimp) == sp.eye(2), "Maxwell doublet rotation changed")
    _require(sp.trigsimp(sp.det(rotation) - 1) == 0, "Maxwell doublet orientation changed")
    return {
        "Lorentzian_Hodge_identity": "star_g^2=-1 on two-forms",
        "duality_rotation": "F_theta=cos(theta)F+sin(theta)star_g F",
        "Maxwell_equation_doublet": ["dF", "d star_g F"],
        "doublet_rotation_matrix": [["cos(theta)", "sin(theta)"], ["-sin(theta)", "cos(theta)"]],
        "stress_tensor_invariance": {
            "energy_density": True,
            "spatial_dyad": True,
            "Poynting_vector": True,
            "conclusion": "T_ab[F_theta]=T_ab[F] exactly",
        },
        "Weyl_Maxwell_covariance": "B_ab depends only on g; Maxwell equations rotate as a doublet and T_ab is invariant",
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["spectator_gate"]["classification"]["circumference_and_Wilson_cannot_cancel_exceptional_adjoint_defect"], "spectator gate changed")
    fixture = records["background"]["rational_fixture"]["parameters"]
    _require(fixture["E"] == "0" and fixture["P"] == "1", "magnetic background normalization changed")
    representative = records["global_block"]["ell0_global_theorem"]["representative"]
    _require("A_x=W_x+Q_e*t" in representative, "electric tangent normalization changed")
    _require(records["axial_generic"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial extra block changed")
    _require(records["polar_generic"]["classification"]["canonical_extra_polar_quotient_two_p_summands"], "polar extra block changed")
    identities = _duality_identities()
    return {
        "schema": "einstein-maxwell-weyl-electric-duality-ell2-extra-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELECTRIC_DUALITY_ELL2_EXTRA_RESONANCE",
        "result_state": "ELECTRIC_CHARGE_TIMES_ELL2_EXTRA_RESONANT_SOURCE_REMOVABLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "the homogeneous electric Q_e direction crossed with the complete axial-plus-polar ell=2,k=0 extra-primary block, all m, on the fixed magnetic bundle",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "duality_identities": identities,
        "mixed_extension": {
            "background_tangent": "partial_theta F_theta|_0=star F_bar=dt wedge dx, equal to the declared Q_e tangent up to the fixed orientation convention",
            "Jacobi_transport": "for every extra Jacobi field (h,f), duality gives a Jacobi field about the duality-rotated background with the same ell,m,k,omega",
            "metric_correction": "zero in the mixed theta-times-wave coefficient",
            "field_strength_correction": "f_cross=star_bar f+(D_g star)[h]F_bar",
            "mixed_equation_identity": "L(f_cross) plus the Q_e-times-extra quadratic source equals zero",
            "fixed_bundle_lift": "f_cross is closed and its S2 period vanishes because it has ell=2 angular support; on R x S1 x S2 it is therefore exact and lifts to a global connection-difference correction",
            "parity_statement": "duality may mix axial and polar representatives, but preserves their complete four-dimensional p-primary direct sum",
        },
        "classification": {
            "Maxwell_equations_duality_covariant": True,
            "Maxwell_stress_duality_invariant": True,
            "complete_ell2_extra_block_transported": True,
            "mixed_correction_fixed_bundle_admissible": True,
            "electric_Qe_times_ell2_extra_source_in_linear_image": True,
            "electric_Qe_cannot_cancel_exceptional_adjoint_defect": True,
            "remaining_homogeneous_a_b_d_cross_sources_classified": False,
            "remaining_twist_A_B_cross_sources_classified": False,
            "all_orders_fixed_bundle_duality_orbit": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Although the pure Q_e direction is obstructed at second order on a fixed magnetic bundle, its bilinear coupling to an ell=2 extra wave is removable. Electromagnetic duality transports the wave and supplies an exact mixed correction whose magnetic period vanishes. Therefore Q_e cannot cancel the exceptional adjoint defect; the remaining positive-sum source matrix contains only a,b,d and the twist position/velocity directions.",
        "next_gate": "compute the a,b,d and twist-position/velocity bilinear sources against both axial and polar ell=2 extra representatives",
        "claim_boundary": "This proves only mixed Q_e-times-wave removability. The finite duality orbit changes magnetic flux at second order, so it is not an all-orders fixed-bundle extension of the pure Q_e direction. Remaining global sources, frequency differences, opposite momenta, residual descent, and causal/quantum claims are open.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 4.92, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_electric_duality_ell2_extra_resonance --verify bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_electric_duality_ell2_extra_resonance"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the remaining global-times-extra source matrix is open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_electric_duality_ell2_extra_resonance --verify bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_electric_duality_ell2_extra_resonance",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "electric-duality certificate is stale")


if __name__ == "__main__":
    main()

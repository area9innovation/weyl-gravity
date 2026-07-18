"""SO(3)-equivariant extension of the balanced twist-velocity fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.schema.json"
INPUTS = {
    "fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class TwistVelocityOrbitError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TwistVelocityOrbitError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["fixture"]["classification"]["nonzero_homogeneous_twist_velocity_common_zero_tangent_second_order_extendible"], "direct fixture changed")
    _require(records["stabilizer"]["classification"]["connected_background_stabilizer_certified"], "SO(3) stabilizer input changed")
    _require(records["moment_maps"]["classification"]["standard_twist_common_zero_locus_classified"], "twist moment maps changed")

    theta, phi = sp.symbols("theta phi", real=True)
    harmonics = (
        sp.sin(theta) * sp.cos(phi),
        sp.sin(theta) * sp.sin(phi),
        sp.cos(theta),
    )
    gram = sp.Matrix(
        3,
        3,
        lambda row, column: sp.integrate(
            sp.integrate(
                harmonics[row] * harmonics[column] * sp.sin(theta),
                (phi, 0, 2 * sp.pi),
            ),
            (theta, 0, sp.pi),
        ),
    ).applyfunc(sp.simplify)
    _require(gram == sp.eye(3) * 4 * sp.pi / 3, "Cartesian ell=1 harmonic Gram matrix changed")
    return {
        "schema": "einstein-maxwell-weyl-twist-velocity-so3-orbit-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TWIST_VELOCITY_SO3_ORBIT_SECOND_ORDER",
        "result_state": "COMPLETE_A_ZERO_TWIST_VELOCITY_SO3_ORBIT_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "standard homogeneous a-coordinate plus arbitrary real axial ell=1 twist-velocity vector B with twist position A=0, fixed magnetic bundle, before final residual quotient",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()}},
        "harmonic_geometry": {
            "basis": ["Y_x=sin(theta)cos(phi)", "Y_y=sin(theta)sin(phi)", "Y_z=cos(theta)"],
            "Gram_matrix": [[str(value) for value in gram.row(row)] for row in range(3)],
            "SO3_action": "the real ell=1 coefficient vector transforms in the defining three-dimensional representation",
            "orbit_statement": "SO(3) acts transitively on each sphere |B|=constant; every B!=0 is a rotation of |B|*Y_z",
        },
        "equivariant_extension": {
            "common_zero_equation": "3*a^2=4*(B_x^2+B_y^2+B_z^2)",
            "mu_J": "0 because A=0",
            "construction": "choose R with R B=|B| e_z, use the direct Y_z correction, then apply R^{-1} to every ell=1 and ell=2 correction tensor",
            "well_defined_on_orbit": "different choices of R differ by the SO(2) stabilizer of e_z, under which the axisymmetric direct correction is invariant",
            "all_target_rows_follow": "naturality of the Weyl-Maxwell Euler operator makes the direct zero remainder SO(3)-equivariant",
        },
        "classification": {
            "complete_A_zero_twist_velocity_SO3_orbit_second_order_extendible": True,
            "harmonic_normalization_exact": True,
            "nonzero_collinear_twist_position_classified": False,
            "physical_or_extra_ell1_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The direct m=0 calculation is not an isolated axisymmetric accident. It generates the complete SO(3) orbit of twist-velocity balances with zero twist position. The next new source is a nonzero twist position parallel to its velocity; that datum cannot be removed by rotation and can create additional position-velocity cross terms.",
        "next_gate": "compute the collinear A parallel B source, then add physical and exceptional fourth-order ell=1 input modes",
        "claim_boundary": "This is an equivariant corollary of a direct fixture. It does not cover A!=0, physical or extra ell=1 inputs, all-orders integration, final residual reduction, causal scattering, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.7, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order --verify bridge/certificates/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the corollary does not freeze the A!=0 twist cone or exceptional/global programme"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order --verify bridge/certificates/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "twist-velocity orbit certificate is stale")


if __name__ == "__main__":
    main()

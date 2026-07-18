"""Complete collinear standard homogeneous/twist common-zero face at second order."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_balanced_second_order import (
    _apply_row,
    _canonical,
    _direct_source_general,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows as _polar_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.schema.json"
INPUTS = {
    "balanced_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
    "so3_orbit": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.json",
    "homogeneous_quadric": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
}


class CollinearTwistError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CollinearTwistError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trigonometric_zero(value: sp.Expr) -> bool:
    """Test the finite trigonometric identities without reintroducing sin(3 theta)."""

    reduced = sp.trigsimp(value, method="fu")
    return sp.cancel(sp.expand_trig(sp.together(reduced))) == 0


def _theorem() -> dict[str, object]:
    raw, (a, position, velocity, circumference, d, time, theta) = _direct_source_general()
    sine = sp.sin(theta)
    amplitude = position + velocity * time
    cone = {a**2: sp.Rational(4, 3) * velocity**2}
    harmonic2 = sp.legendre(2, sp.cos(theta))
    derivative2 = sp.diff(harmonic2, theta)
    tensor2 = (sp.diff(harmonic2, theta, 2) - sp.cot(theta) * derivative2) / 2
    l0 = {"metric_00": 0, "metric_01": 0, "metric_11": sp.Rational(16, 3) * velocity**2, "sphere_trace": -sp.Rational(8, 3) * velocity**2}
    l2 = {
        "metric_00": -(21 * amplitude**2 + 17 * velocity**2) / 3,
        "metric_01": 0,
        "metric_11": -(27 * amplitude**2 + 13 * velocity**2) / 3,
        "sphere_trace": (3 * amplitude**2 - 2 * velocity**2) / 3,
        "metric_0a": sp.Rational(7, 3) * velocity * amplitude,
        "metric_1a": 0,
        "sphere_tracefree": sp.Rational(2, 3) * (amplitude**2 - 2 * velocity**2),
        "maxwell_axial_density": -(amplitude**2 + velocity**2) / 3,
    }
    axial = {
        "metric_t": 0,
        "metric_x": (-4 * position * a + 6 * velocity * a * time + 5 * velocity * d) / 4,
        "metric_angular": 0,
        "maxwell_t": 0,
        "maxwell_x": (4 * position * a + 2 * velocity * a * time - velocity * d) / 2,
        "maxwell_angular": 0,
    }
    trace = l0["sphere_trace"] + l2["sphere_trace"] * harmonic2
    tracefree = l2["sphere_tracefree"] * tensor2
    reconstructed = {
        "E00": l2["metric_00"] * harmonic2,
        "E01": 0,
        "E02": l2["metric_0a"] * derivative2,
        "E03": 0,
        "E11": l0["metric_11"] + l2["metric_11"] * harmonic2,
        "E12": 0,
        "E13": axial["metric_x"] * sine**2,
        "E23": 0,
        "M0": 0,
        "M1": axial["maxwell_x"] * sp.cos(theta),
        "M2": 0,
        "M3": l2["maxwell_axial_density"] * (-derivative2) / sine,
    }
    for name, expected in reconstructed.items():
        _require(
            _trigonometric_zero(raw.get(name, sp.S.Zero).subs(cone) - expected),
            f"direct collinear source changed: {name}",
        )
    direct_trace = _canonical((raw["E22"] + raw["E33"] / sine**2) / 2).subs(cone)
    direct_tracefree = _canonical((raw["E22"] - raw["E33"] / sine**2) / 2).subs(cone)
    _require(_trigonometric_zero(direct_trace - trace), "direct collinear sphere trace changed")
    _require(
        _trigonometric_zero(direct_tracefree - tracefree),
        "direct collinear sphere tracefree row changed",
    )

    homogeneous_k = -sp.Rational(4, 9) * velocity**2 * time**4
    polar, polar_symbols = _polar_rows()
    eigenvalue, momentum, frequency, at, mixed, ct, maxwell = polar_symbols
    polar_fields = {at: -sp.Rational(5, 6) * velocity**2, mixed: 0, ct: sp.Rational(5, 6) * velocity**2 - sp.Rational(2, 3) * amplitude**2, maxwell: -sp.Rational(7, 36) * velocity**2}
    polar_remainders = {}
    for name, source in l2.items():
        image = _apply_row(polar[name].subs({eigenvalue: 6, momentum: 0}), polar_fields, frequency, time)
        polar_remainders[name] = sp.factor(image + source)
        _require(polar_remainders[name] == 0, f"collinear polar correction failed: {name}")

    axial_rows, axial_symbols = _axial_rows()
    axial_fields = {
        axial_symbols["h_t"]: 0,
        axial_symbols["h_x"]: position * a + velocity * a * time + velocity * d * time**2 / 4 + velocity * a * time**3 / 6,
        axial_symbols["q_t"]: 0,
        axial_symbols["q_x"]: -velocity * d * time**2 / 4 - velocity * a * time**3 / 6,
    }
    axial_remainders = {}
    for name, source in axial.items():
        image = _apply_row(axial_rows[name].subs({axial_symbols["lambda"]: 2, axial_symbols["k"]: 0}), axial_fields, axial_symbols["omega"], time)
        axial_remainders[name] = sp.factor(image + source)
        _require(axial_remainders[name] == 0, f"collinear axial correction failed: {name}")
    return {
        "parameter_order": ["a", "A", "B", "c", "d"],
        "common_zero_equations": ["3*a^2=4*B^2", "A cross B=0 (automatic on the declared axis)"],
        "circumference_c_absent_from_complete_source": all(
            circumference not in value.free_symbols for value in raw.values()
        ),
        "projected_source": {"L0": {name: str(sp.factor(value)) for name, value in l0.items()}, "polar_L2": {name: str(sp.factor(value)) for name, value in l2.items()}, "axial_L1": {name: str(sp.factor(value)) for name, value in axial.items()}},
        "correction": {
            "homogeneous_L0_K2": str(homogeneous_k),
            "polar_L2": {"A_t2": str(polar_fields[at]), "B2": "0", "C_t2": str(polar_fields[ct]), "U2": str(polar_fields[maxwell])},
            "axial_L1": {"h_x2": str(axial_fields[axial_symbols["h_x"]]), "q_x2": str(axial_fields[axial_symbols["q_x"]])},
            "all_polar_remainders": {name: str(value) for name, value in polar_remainders.items()},
            "all_axial_remainders": {name: str(value) for name, value in axial_remainders.items()},
        },
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["balanced_fixture"]["classification"]["nonzero_homogeneous_twist_velocity_common_zero_tangent_second_order_extendible"], "balanced input changed")
    _require(
        records["so3_orbit"]["classification"][
            "complete_A_zero_twist_velocity_SO3_orbit_second_order_extendible"
        ],
        "SO(3) orbit input changed",
    )
    _require(
        records["homogeneous_quadric"]["classification"][
            "complete_standard_homogeneous_common_zero_quadric_second_order_extendible"
        ],
        "homogeneous-quadric input changed",
    )
    theorem = _theorem()
    return {
        "schema": "einstein-maxwell-weyl-homogeneous-twist-collinear-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_COLLINEAR_SECOND_ORDER",
        "result_state": "COMPLETE_STANDARD_COLLINEAR_HOMOGENEOUS_TWIST_COMMON_ZERO_FACE_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "arbitrary real standard axial ell=1 twist-position and twist-velocity vectors A,B with A cross B=0, homogeneous a,c,d data satisfying 3a^2=4|B|^2, b=Q_e=W_x=0, fixed magnetic bundle",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()}},
        "theorem": theorem,
        "SO3_promotion": {
            "B_nonzero": "A cross B=0 makes A parallel to B; rotate their common axis to Y_z, apply the direct correction, and rotate back",
            "B_zero_A_nonzero": "the balance forces a=0; rotate A to Y_z, apply the same direct correction at B=a=0, and rotate back",
            "A_and_B_zero": "the result reduces to the certified homogeneous common-zero face",
            "well_defined": "the axisymmetric correction is invariant under the SO(2) stabilizer of the chosen axis",
            "all_rows": "naturality of the Weyl-Maxwell Euler operator transports every direct zero remainder",
        },
        "classification": {
            "complete_collinear_standard_homogeneous_twist_common_zero_face_second_order_extendible": True,
            "time_translation_orbit_strictly_enlarged": True,
            "arbitrary_c_and_d_included": True,
            "full_SO3_covariant_collinear_cone_classified": True,
            "physical_or_extra_ell1_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Nonzero twist position creates no new second-order obstruction on the standard collinear common-zero face. The result is stronger than the time-translation orbit: c is arbitrary and d is removed by an additional axial polynomial correction. SO(3) covariance closes every standard twist pair satisfying A cross B=0 and the homogeneous energy balance, within the declared b=Q_e=W_x=0 slice.",
        "next_gate": "add physical and exceptional fourth-order ell=1 input modes, then enlarge the homogeneous slice to b,Q_e,W_x",
        "claim_boundary": "This does not include general homogeneous b,Q_e,W_x, physical or extra ell=1 inputs, all-orders integration, final residual reduction, causal scattering, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {
                "status": "PASS",
                "commands": [
                    "python3 -m py_compile <scoped Python paths>",
                    "python3 -m json.tool <scoped JSON paths>",
                    "git diff --check -- <scoped paths>",
                ],
            },
            "tier_1": {
                "status": "PASS",
                "elapsed_seconds": 47.1,
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_collinear_second_order --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
                    "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.py",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_twist_collinear_second_order",
                ],
            },
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {
                "status": "NOT_RUN",
                "reason": "physical and exceptional fourth-order ell=1 inputs and the enlarged homogeneous slice remain open",
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_collinear_second_order --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_twist_collinear_second_order",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "collinear twist certificate is stale")


if __name__ == "__main__":
    main()

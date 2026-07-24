#!/usr/bin/env python3
"""Produce exact uniform bounds for the intrinsic ECS tangent initializer."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ECS = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1"
    / "certificate.json"
)
TAIL = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1"
    / "certificate.json"
)
COCYCLE = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_projective_cocycle_v1"
    / "certificate.json"
)
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md",
    "report.md",
    "schema.json",
    "produce.py",
    "verify.py",
    "test_tangent_initializer.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def produce() -> dict:
    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    cocycle = json.loads(COCYCLE.read_text())
    spin2 = next(
        item for item in ecs["volterra"]["channels"]
        if item["channel"] == "spin_two"
    )
    omega_upper = Fraction(tail["disk"]["omega_modulus_l1_upper"])
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    kappa = Fraction(ecs["disk"]["phase_decay_rate_lower"])
    alpha = Fraction(spin2["operator_norm_upper"])
    j_v = Fraction(spin2["exponentially_weighted_integral_upper"])
    r0 = 45
    c = Fraction(2, 3)

    # Use the exact reduced multiplication representative
    # I_red=i(r-2)(2*w^2*r+3*w^2+12)/(5*w*r^4).
    # With R=45+(2/3)t, its modulus is bounded by
    # [2 O^2/R^2 +(7 O^2+12)/R^3 +(6 O^2+24)/R^4]/(5 w_min).
    o2 = omega_upper**2
    source_integral = Fraction(1, 1) / (5 * omega_lower * c) * (
        2 * o2 / r0
        + (7 * o2 + 12) / (2 * r0**2)
        + (6 * o2 + 24) / (3 * r0**3)
    )
    source_point = Fraction(1, 1) / (5 * omega_lower) * (
        2 * o2 / r0**2
        + (7 * o2 + 12) / r0**3
        + (6 * o2 + 24) / r0**4
    )
    source_weighted = source_point / kappa
    source_kernel_norm = (
        source_integral + source_weighted
    ) / (2 * omega_lower)
    base_norm = 1 / (1 - alpha)
    tangent_value_norm = source_kernel_norm / (1 - alpha) ** 2
    tangent_derivative_norm = (
        j_v * tangent_value_norm + source_weighted * base_norm
    )

    if tangent_value_norm >= 1 or tangent_derivative_norm >= 1:
        raise RuntimeError("tangent initializer bound unexpectedly too wide")

    return {
        "schema": "phase3-axial-qnm-ecs-tangent-initializer-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "EXACT_CANONICAL_PROJECTIVE_TANGENT_ECS_INITIALIZER_BOUND_"
            "ENDPOINT_GAUGE_TO_FACTOR_B_REMAINS_OPEN"
        ),
        "imports": {
            "ecs_base_initializer": {
                "path": str(ECS.relative_to(ROOT)),
                "sha256": sha256(ECS),
            },
            "frequency_tail_gate": {
                "path": str(TAIL.relative_to(ROOT)),
                "sha256": sha256(TAIL),
            },
            "projective_cocycle": {
                "path": str(COCYCLE.relative_to(ROOT)),
                "sha256": sha256(COCYCLE),
            },
        },
        "deformation": {
            "representative": cocycle["reduced_representative"]["calI_reduced"],
            "family": "L_tau=L+tau*calI_reduced",
            "endpoint_normalization": (
                "tau-independent reduced outgoing normalization v(infinity)=1"
            ),
            "scope": (
                "canonical reduced projective representative; conversion to "
                "the manuscript factor-frame entry b still requires the "
                "analytic endpoint gauge term"
            ),
        },
        "source_bounds": {
            "omega_upper": text(omega_upper),
            "omega_lower": text(omega_lower),
            "source_integral_upper": text(source_integral),
            "source_point_upper_at_r45": text(source_point),
            "source_exponentially_weighted_integral_upper": text(
                source_weighted
            ),
            "source_volterra_kernel_norm_upper": text(source_kernel_norm),
        },
        "tangent_initializer": {
            "equation": (
                "v_tau=K_V[v_tau]-K_calI[v] (sign depends on declared "
                "L_tau convention and does not affect these norm bounds)"
            ),
            "base_solution_norm_upper": text(base_norm),
            "value_ball": {
                "center": "0",
                "radius": text(tangent_value_norm),
            },
            "x_derivative_ball": {
                "center": "0",
                "radius": text(tangent_derivative_norm),
            },
            "uniform_on_closed_disk": True,
            "analytic_frequency_dependence": True,
        },
        "claim_flags": {
            "canonical_projective_tangent_ecs_initializer_certified": True,
            "tangent_initializer_frequency_analytic": True,
            "manuscript_factor_frame_b_initializer_certified": False,
            "b_over_a_on_contour_constructed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "next_gates": [
            (
                "apply the explicit reducing gauge and endpoint normalization "
                "matrices to relate this canonical tangent to factor-frame b"
            ),
            (
                "propagate base and tangent columns in one correlated "
                "complex-ball Taylor/Lohner rail from r=45 to r=4"
            ),
        ],
        "does_not_establish": [
            "the factor-frame off-diagonal coefficient b",
            "b/a on any spectral contour",
            "a mixed four-state or full Bach outgoing frame",
            "Evans-boundary nonvanishing or a root count",
            "a physical QNM, Smith selection or EP2",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-tangent-initializer-receipt-v1",
        "producer": "produce.py",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            "ecs_base_initializer": sha256(ECS),
            "frequency_tail_gate": sha256(TAIL),
            "projective_cocycle": sha256(COCYCLE),
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_tangent_initializer_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_tangent_initializer_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_tangent_initializer_v1.test_tangent_initializer",
            "python3 -m py_compile black_hole_programme/phase3/axial_qnm_ecs_tangent_initializer_v1/produce.py black_hole_programme/phase3/axial_qnm_ecs_tangent_initializer_v1/verify.py black_hole_programme/phase3/axial_qnm_ecs_tangent_initializer_v1/test_tangent_initializer.py",
        ],
        "tier_2_not_run": (
            "No shared operator changed; this package bounds one exact "
            "content-addressed reduced representative."
        ),
        "tier_3_not_run": "Not a freeze, release or theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()

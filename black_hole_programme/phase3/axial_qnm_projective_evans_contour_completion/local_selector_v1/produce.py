#!/usr/bin/env python3
"""Certify the unique local projective Evans root and its Bach selector."""
from __future__ import annotations

import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ...axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
)
from ...axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    af,
    inflate,
)
from ...axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
    parse_acb,
)
from .tight_transport import (
    DEFAULT_ORDER,
    horizon_transport,
    outgoing_transport,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = HERE / "local-selector-run.json"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"

ECS = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
)
AGGREGATE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_contour_completion/"
    "chunk_1021_1023_v1/child-grid-aggregate-run.json"
)
WINDING = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_contour_completion/"
    "full_contour_winding_v1/certificate.json"
)
ANALYTIC_GATE = ROOT / (
    "black_hole_programme/certificates/"
    "BH3_ANALYTIC_CONTINUATION_GATE.json"
)
SMITH = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_local_smith_dichotomy/certificate.json"
)
TIGHT_SOURCE = HERE / "tight_transport.py"

LOCAL_RADIUS = Fraction(1, 10_000_000)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def encode_acb(value: acb) -> dict:
    """Round-trip-safe midpoint/radius encoding plus a display string."""
    return {
        "display": str(value),
        "real_mid": str(value.real.mid()),
        "real_radius": str(value.real.rad()),
        "imag_mid": str(value.imag.mid()),
        "imag_radius": str(value.imag.rad()),
    }


def _state_payload(state: dict) -> dict:
    return {
        "passed": state["passed"],
        "q": encode_acb(state["q"]),
        "q_tau": encode_acb(state["q_tau"]),
        "q_omega": encode_acb(state["q_omega"]),
        "accepted_steps": state["accepted_steps"],
        "rejected_trials": state["rejected_trials"],
        "taylor_order": state["order"],
    }


def _strict_inside_parent(center: acb, local_radius: arb, parent: dict) -> bool:
    parent_center = acb(
        af(Fraction(parent["center_re"])),
        af(Fraction(parent["center_im"])),
    )
    parent_radius = af(Fraction(parent["radius"]))
    return (center - parent_center).abs_upper() + local_radius < parent_radius


def produce() -> dict:
    ctx.dps = 60
    started = time.monotonic()
    ecs = json.loads(ECS.read_text())
    aggregate = json.loads(AGGREGATE.read_text())
    winding = json.loads(WINDING.read_text())
    smith = json.loads(SMITH.read_text())
    disk = ecs["disk"]
    center = acb(
        af(Fraction(disk["center_re"])),
        af(Fraction(disk["center_im"])),
    )
    local_radius = af(LOCAL_RADIUS)
    box = center + acb(
        arb(0, local_radius),
        arb(0, local_radius),
    )

    outgoing_center = outgoing_transport(center, order=DEFAULT_ORDER)
    horizon_center = horizon_transport(center, order=DEFAULT_ORDER)
    outgoing_box = outgoing_transport(box, order=DEFAULT_ORDER)
    horizon_box = horizon_transport(box, order=DEFAULT_ORDER)
    states = (
        outgoing_center,
        horizon_center,
        outgoing_box,
        horizon_box,
    )
    if not all(state["passed"] for state in states):
        raise RuntimeError("a tight endpoint transport failed closed")

    delta_center = (
        horizon_center["q"] - outgoing_center["q"] + 2j * center
    )
    delta_tau_center = (
        horizon_center["q_tau"] - outgoing_center["q_tau"]
    )
    delta_omega_center = (
        horizon_center["q_omega"]
        - outgoing_center["q_omega"]
        + 2j
    )
    derivative_reference = midpoint(delta_omega_center)
    delta_omega_box = (
        horizon_box["q_omega"] - outgoing_box["q_omega"] + 2j
    )
    derivative_deviation = (
        delta_omega_box - derivative_reference
    ).abs_upper()

    # On |omega-center|=r, compare Delta with the linear function
    # derivative_reference*(omega-center).  The fundamental theorem of
    # calculus bounds the difference by Delta(center) plus r times the
    # derivative deviation on the enclosing square.
    rouche_reference_lower = (
        derivative_reference.abs_lower() * local_radius
    )
    rouche_perturbation_upper = (
        delta_center.abs_upper()
        + local_radius * derivative_deviation
    )
    rouche_margin = rouche_reference_lower - rouche_perturbation_upper
    local_root_count = 1 if rouche_margin > 0 else None

    # The completed parent-boundary rail gives a uniform bound on Delta_tau.
    # Cauchy's estimate then controls its change from the disk center to every
    # point of the local root disk without transporting a mixed derivative.
    tau_boundary_bounds = []
    for segment in aggregate["segments"]:
        tau_ball = parse_acb(
            segment["typed_row"]["delta_tau"]["ball"]
        )
        tau_boundary_bounds.append(tau_ball.abs_upper())
    tau_boundary_sup = max(tau_boundary_bounds)
    parent_radius = af(Fraction(disk["radius"]))
    tau_cauchy_variation = (
        tau_boundary_sup * local_radius / (parent_radius - local_radius)
    )
    delta_tau_root = inflate(
        delta_tau_center,
        tau_cauchy_variation,
    )
    delta_tau_nonzero = 0 not in delta_tau_root
    delta_omega_nonzero = 0 not in delta_omega_box
    kappa = (
        delta_tau_root / delta_omega_box
        if delta_tau_nonzero and delta_omega_nonzero
        else None
    )

    parent_winding = winding["result"]["winding_number"]
    parent_root_count = winding["result"][
        "argument_principle_root_count_with_multiplicity"
    ]
    parent_link = (
        parent_winding == 1
        and parent_root_count == 1
        and _strict_inside_parent(center, local_radius, disk)
        and local_root_count == 1
    )
    selector_nonzero = (
        parent_link and delta_tau_nonzero and delta_omega_nonzero
    )
    run = {
        "schema": "phase3-axial-qnm-projective-local-selector-run-v1",
        "inputs": {
            "ecs_certificate_sha256": sha(ECS),
            "aggregate_sha256": sha(AGGREGATE),
            "winding_certificate_sha256": sha(WINDING),
            "analytic_gate_sha256": sha(ANALYTIC_GATE),
            "local_smith_certificate_sha256": sha(SMITH),
            "tight_transport_source_sha256": sha(TIGHT_SOURCE),
        },
        "domain": {
            "parent_center_re": disk["center_re"],
            "parent_center_im": disk["center_im"],
            "parent_radius": disk["radius"],
            "local_center": str(center),
            "local_radius": str(LOCAL_RADIUS),
            "local_enclosing_square": str(box),
            "strictly_inside_parent_disk": _strict_inside_parent(
                center, local_radius, disk
            ),
        },
        "transport": {
            "outgoing_center": _state_payload(outgoing_center),
            "horizon_center": _state_payload(horizon_center),
            "outgoing_box": _state_payload(outgoing_box),
            "horizon_box": _state_payload(horizon_box),
        },
        "local_rouche": {
            "comparison": (
                "Delta(omega) versus Delta_omega_ref*(omega-center) "
                "on the local circle"
            ),
            "delta_center": str(delta_center),
            "delta_center_exact": encode_acb(delta_center),
            "delta_omega_center": str(delta_omega_center),
            "delta_omega_center_exact": encode_acb(delta_omega_center),
            "delta_omega_reference": str(derivative_reference),
            "delta_omega_reference_exact": encode_acb(
                derivative_reference
            ),
            "delta_omega_box": str(delta_omega_box),
            "delta_omega_box_exact": encode_acb(delta_omega_box),
            "derivative_deviation_upper": str(
                derivative_deviation.upper()
            ),
            "reference_modulus_lower": str(
                rouche_reference_lower.lower()
            ),
            "perturbation_modulus_upper": str(
                rouche_perturbation_upper.upper()
            ),
            "strict_margin_lower": str(rouche_margin.lower()),
            "passed": rouche_margin > 0,
            "zero_count_with_multiplicity": local_root_count,
        },
        "selector": {
            "delta_tau_center": str(delta_tau_center),
            "delta_tau_center_exact": encode_acb(delta_tau_center),
            "parent_boundary_delta_tau_sup_upper": str(
                tau_boundary_sup.upper()
            ),
            "cauchy_variation_upper": str(
                tau_cauchy_variation.upper()
            ),
            "delta_tau_root_enclosure": str(delta_tau_root),
            "delta_tau_root_enclosure_exact": encode_acb(delta_tau_root),
            "delta_tau_excludes_zero": delta_tau_nonzero,
            "delta_omega_root_enclosure": str(delta_omega_box),
            "delta_omega_root_enclosure_exact": encode_acb(
                delta_omega_box
            ),
            "delta_omega_excludes_zero": delta_omega_nonzero,
            "kappa_beta_over_alpha_enclosure": (
                str(kappa) if kappa is not None else None
            ),
            "kappa_beta_over_alpha_enclosure_exact": (
                encode_acb(kappa) if kappa is not None else None
            ),
            "qnm_velocity_enclosure": (
                str(-kappa) if kappa is not None else None
            ),
        },
        "cross_checks": {
            "parent_winding_number": parent_winding,
            "parent_zero_count_with_multiplicity": parent_root_count,
            "same_unique_root_as_parent_contour": parent_link,
            "smith_dichotomy_exact": smith["claim_flags"][
                "local_smith_dichotomy_exact"
            ],
        },
        "claim_flags": {
            "unique_simple_spin_two_qnm_localized": parent_link,
            "intrinsic_tangent_selector_nonzero": selector_nonzero,
            "repeated_spin_two_smith_valuations_0_2": selector_nonzero,
            "full_connection_smith_valuations_0_0_2": False,
            "physical_fredholm_realization_constructed": False,
            "green_resolvent_second_order_pole_established": False,
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    dump(RUN, run)

    certificate = {
        "schema": "phase3-axial-qnm-projective-local-selector-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle": "COEFFICIENT_COMPUTED",
        "status": (
            "CERTIFIED_INTRINSIC_REPEATED_SPIN_TWO_EP2"
            if selector_nonzero
            else "FAIL_CLOSED"
        ),
        "inputs": run["inputs"],
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha(RUN),
        },
        "result": {
            "qnm_enclosure": {
                "center_re": disk["center_re"],
                "center_im": disk["center_im"],
                "radius": str(LOCAL_RADIUS),
                "zero_count_with_multiplicity": local_root_count,
                "simple": local_root_count == 1,
            },
            "delta_tau_root_enclosure": str(delta_tau_root),
            "delta_omega_root_enclosure": str(delta_omega_box),
            "kappa_beta_over_alpha_enclosure": (
                str(kappa) if kappa is not None else None
            ),
            "qnm_velocity_enclosure": (
                str(-kappa) if kappa is not None else None
            ),
            "connection_classification": {
                "repeated_spin_two_smith_valuations": (
                    [0, 2] if selector_nonzero else None
                ),
                "geometric_multiplicity": (
                    1 if selector_nonzero else None
                ),
                "algebraic_multiplicity": (
                    2 if selector_nonzero else None
                ),
                "full_3x3_classification": (
                    "conditional on the spin-one Jost factor being a "
                    "local unit at the enclosed QNM"
                ),
            },
        },
        "claim_flags": run["claim_flags"],
        "does_not_establish": [
            "that the spin-one incoming Jost factor is nonzero at this QNM",
            "an unconditional full 3x3 Smith type without that unit gate",
            "an analytic Fredholm realization of the physical QNM problem",
            "a second-order Green-resolvent pole",
            "time-domain boundedness, decay, or stability",
        ],
    }
    dump(OUTPUT, certificate)

    receipt = {
        "schema": "phase3-axial-qnm-projective-local-selector-receipt-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "producer": str(Path(__file__).relative_to(ROOT)),
        "producer_sha256": sha(Path(__file__)),
        "tight_transport_source_sha256": sha(TIGHT_SOURCE),
        "run_sha256": sha(RUN),
        "certificate_sha256": sha(OUTPUT),
        "elapsed_seconds": run["elapsed_seconds"],
        "verification_scope": (
            "high-order validated endpoint transports, local Rouche count, "
            "Cauchy selector bound, and reduced spin-two Smith selection"
        ),
        "higher_tiers_not_run": (
            "no full repository suite; no physical Fredholm or time-domain "
            "claim is promoted"
        ),
    }
    dump(RECEIPT, receipt)
    REPORT.write_text(
        "# Axial QNM projective local selector v1\n\n"
        "The completed projective Evans contour contains one scalar "
        f"spin-two zero. A cancellation-safe order-{DEFAULT_ORDER} endpoint "
        f"transport and local Rouché disk of radius `{LOCAL_RADIUS}` "
        f"{'certify' if parent_link else 'do not yet certify'} that "
        "the same zero is unique and simple in the local disk.\n\n"
        f"The intrinsic tangent enclosure is `{delta_tau_root}` and "
        f"excludes zero: `{delta_tau_nonzero}`. The frequency derivative "
        f"enclosure is `{delta_omega_box}` and excludes zero: "
        f"`{delta_omega_nonzero}`. "
        + (
            "Hence the repeated spin-two connection has Smith valuations "
            "`(0,2)`, geometric multiplicity one, and algebraic multiplicity "
            "two.\n\n"
            if selector_nonzero
            else "The repeated spin-two Smith branch remains fail-closed.\n\n"
        )
        +
        "The corresponding full 3x3 Smith type `(0,0,2)` remains conditional "
        "on a separate certificate that the spin-one Jost factor is a local "
        "unit at this frequency. A physical Fredholm realization and any "
        "Green-resolvent pole statement also remain open.\n"
    )
    return certificate


if __name__ == "__main__":
    document = produce()
    print(json.dumps(document, indent=2, sort_keys=True))

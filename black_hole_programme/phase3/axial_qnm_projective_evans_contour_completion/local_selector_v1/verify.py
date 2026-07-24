#!/usr/bin/env python3
"""Independent verifier for the recorded local projective selector."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ...axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    af,
    inflate,
)
from ...axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
    parse_acb,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = HERE / "local-selector-run.json"
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_acb(payload: dict) -> acb:
    """Decode the producer's round-trip-safe midpoint/radius enclosure."""
    return acb(
        arb(payload["real_mid"])
        + arb(0, arb(payload["real_radius"])),
        arb(payload["imag_mid"])
        + arb(0, arb(payload["imag_radius"])),
    )


def verify() -> None:
    ctx.dps = 60
    run = json.loads(RUN.read_text())
    cert = json.loads(CERT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert cert["run"]["sha256"] == sha(RUN)
    assert receipt["run_sha256"] == sha(RUN)
    assert receipt["certificate_sha256"] == sha(CERT)
    for path, key in (
        (
            ROOT / "black_hole_programme/phase3/"
            "axial_qnm_ecs_inverse_tortoise_v1/certificate.json",
            "ecs_certificate_sha256",
        ),
        (
            ROOT / "black_hole_programme/phase3/"
            "axial_qnm_projective_evans_contour_completion/"
            "chunk_1021_1023_v1/child-grid-aggregate-run.json",
            "aggregate_sha256",
        ),
        (
            ROOT / "black_hole_programme/phase3/"
            "axial_qnm_projective_evans_contour_completion/"
            "full_contour_winding_v1/certificate.json",
            "winding_certificate_sha256",
        ),
        (
            ROOT / "black_hole_programme/certificates/"
            "BH3_ANALYTIC_CONTINUATION_GATE.json",
            "analytic_gate_sha256",
        ),
        (
            ROOT / "black_hole_programme/phase3/"
            "axial_qnm_local_smith_dichotomy/certificate.json",
            "local_smith_certificate_sha256",
        ),
        (HERE / "tight_transport.py", "tight_transport_source_sha256"),
    ):
        assert run["inputs"][key] == sha(path)
        assert cert["inputs"][key] == sha(path)

    center = parse_acb(run["domain"]["local_center"])
    radius = af(Fraction(run["domain"]["local_radius"]))
    delta_center = decode_acb(
        run["local_rouche"]["delta_center_exact"]
    )
    derivative_reference = decode_acb(
        run["local_rouche"]["delta_omega_reference_exact"]
    )
    derivative_box = decode_acb(
        run["local_rouche"]["delta_omega_box_exact"]
    )
    deviation = (derivative_box - derivative_reference).abs_upper()
    reference = derivative_reference.abs_lower() * radius
    perturbation = delta_center.abs_upper() + radius * deviation
    assert reference > perturbation
    assert run["local_rouche"]["passed"]
    assert run["local_rouche"]["zero_count_with_multiplicity"] == 1

    delta_tau_center = decode_acb(
        run["selector"]["delta_tau_center_exact"]
    )
    boundary_sup = arb(
        run["selector"]["parent_boundary_delta_tau_sup_upper"]
    )
    parent_radius = af(Fraction(run["domain"]["parent_radius"]))
    variation = boundary_sup * radius / (parent_radius - radius)
    delta_tau_root = inflate(delta_tau_center, variation)
    recorded_tau = decode_acb(
        run["selector"]["delta_tau_root_enclosure_exact"]
    )
    assert delta_tau_root.overlaps(recorded_tau)
    assert 0 not in delta_tau_root
    assert 0 not in derivative_box
    kappa = delta_tau_root / derivative_box
    assert kappa.overlaps(
        decode_acb(
            run["selector"]["kappa_beta_over_alpha_enclosure_exact"]
        )
    )

    assert center.is_finite()
    assert run["cross_checks"]["parent_winding_number"] == 1
    assert run["cross_checks"]["parent_zero_count_with_multiplicity"] == 1
    assert run["cross_checks"]["same_unique_root_as_parent_contour"]
    flags = cert["claim_flags"]
    assert flags["unique_simple_spin_two_qnm_localized"]
    assert flags["intrinsic_tangent_selector_nonzero"]
    assert flags["repeated_spin_two_smith_valuations_0_2"]
    assert not flags["full_connection_smith_valuations_0_0_2"]
    assert not flags["physical_fredholm_realization_constructed"]
    assert not flags["green_resolvent_second_order_pole_established"]
    assert cert["result"]["connection_classification"][
        "repeated_spin_two_smith_valuations"
    ] == [0, 2]
    print("local projective QNM selector verification: PASS")


if __name__ == "__main__":
    verify()

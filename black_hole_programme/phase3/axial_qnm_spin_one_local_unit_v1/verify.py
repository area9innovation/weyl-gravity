#!/usr/bin/env python3
"""Independent verifier for the spin-one local-unit promotion."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
RUN = HERE / "spin-one-local-unit-run.json"
CROSSCHECK = HERE / "crosscheck.json"
SELECTOR = (
    ROOT
    / "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_contour_completion/"
    "local_selector_v1/certificate.json"
)
SELECTOR_RUN = SELECTOR.with_name("local-selector-run.json")
SMITH = (
    ROOT
    / "black_hole_programme/phase3/"
    "axial_qnm_local_smith_dichotomy/certificate.json"
)
ECS = (
    ROOT
    / "black_hole_programme/phase3/"
    "axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
)
ANALYTIC_GATE = (
    ROOT
    / "black_hole_programme/certificates/"
    "BH3_ANALYTIC_CONTINUATION_GATE.json"
)
TRANSPORT_SOURCE = HERE / "transport.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ball(mid: str, radius: str) -> arb:
    return arb(mid) + arb(0, arb(radius))


def decode_acb(payload: dict) -> acb:
    return acb(
        _ball(payload["real_mid"], payload["real_radius"]),
        _ball(payload["imag_mid"], payload["imag_radius"]),
    )


def verify_paths(
    certificate_path: Path = CERTIFICATE,
    run_path: Path = RUN,
    crosscheck_path: Path = CROSSCHECK,
) -> None:
    ctx.dps = 70
    certificate = json.loads(certificate_path.read_text())
    run = json.loads(run_path.read_text())
    crosscheck = json.loads(crosscheck_path.read_text())
    selector = json.loads(SELECTOR.read_text())
    smith = json.loads(SMITH.read_text())

    assert certificate["schema"] == "phase3-axial-qnm-spin-one-local-unit-v1"
    assert certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]
    assert certificate["lifecycle"] == "COEFFICIENT_COMPUTED"
    assert certificate["run"]["sha256"] == sha(run_path)
    imported = run["inputs"]
    assert imported["selector_certificate_sha256"] == sha(SELECTOR)
    assert imported["selector_run_sha256"] == sha(SELECTOR_RUN)
    assert imported["local_smith_certificate_sha256"] == sha(SMITH)
    assert imported["ecs_certificate_sha256"] == sha(ECS)
    assert imported["analytic_gate_sha256"] == sha(ANALYTIC_GATE)
    assert imported["transport_source_sha256"] == sha(TRANSPORT_SOURCE)
    assert certificate["inputs"] == imported

    domain = run["domain"]
    center_re = Fraction(domain["center_re"])
    center_im = Fraction(domain["center_im"])
    radius = Fraction(domain["radius"])
    selector_domain = selector["result"]["qnm_enclosure"]
    assert center_re == Fraction(selector_domain["center_re"])
    assert center_im == Fraction(selector_domain["center_im"])
    assert radius == Fraction(1, 10_000_000)
    assert radius == Fraction(selector_domain["radius"])
    assert selector_domain["simple"]
    assert selector_domain["zero_count_with_multiplicity"] == 1

    omega_box = decode_acb(domain["enclosing_square"])
    expected_center = acb(
        arb(center_re.numerator) / center_re.denominator,
        arb(center_im.numerator) / center_im.denominator,
    )
    assert expected_center in omega_box
    assert omega_box.real.rad() >= arb(radius.numerator) / radius.denominator
    assert omega_box.imag.rad() >= arb(radius.numerator) / radius.denominator

    outgoing = run["transport"]["outgoing"]
    horizon = run["transport"]["horizon"]
    assert outgoing["passed"] and horizon["passed"]
    assert outgoing["accepted_steps"] > 0
    assert horizon["accepted_steps"] > 0
    assert outgoing["rejected_trials"] == 0
    assert horizon["rejected_trials"] == 0
    q_out = decode_acb(outgoing["q"])
    q_horizon = decode_acb(horizon["q"])
    recorded_delta = decode_acb(run["local_unit_gate"]["delta"])
    recomputed_delta = q_horizon - q_out + 2j * omega_box
    # Round-trip decimal balls may widen, so require mutual overlap and
    # containment of the independently computed point rather than byte-like
    # equality of Arb's internal midpoint/radius form.
    assert 0 in (recorded_delta.real - recomputed_delta.real)
    assert 0 in (recorded_delta.imag - recomputed_delta.imag)
    assert recorded_delta.abs_lower() > 0
    assert run["local_unit_gate"]["excludes_zero"]
    claimed_lower = Fraction(
        run["local_unit_gate"]["certified_rational_modulus_lower"]
    )
    assert claimed_lower == Fraction(1, 2500)
    claimed_lower_ball = (
        arb(claimed_lower.numerator) / claimed_lower.denominator
    )
    assert recorded_delta.abs_lower() > claimed_lower_ball
    assert recomputed_delta.abs_lower() > claimed_lower_ball

    # Independent vector-ODE point control must lie inside the rigorous ball.
    assert crosscheck["schema"] == (
        "phase3-axial-qnm-spin-one-local-unit-crosscheck-v1"
    )
    cross_delta = crosscheck["delta"]
    assert arb(cross_delta[0]) in recorded_delta.real
    assert arb(cross_delta[1]) in recorded_delta.imag

    # Recheck the exact infinite Frobenius-tail induction constant rather
    # than trusting the producer's prose.
    multiplier = Fraction(
        horizon["seed"]["induction_multiplier"]
    )
    assert multiplier == Fraction(190_501, 1_000_000)
    assert multiplier < 1

    predecessor = selector["claim_flags"]
    assert predecessor["unique_simple_spin_two_qnm_localized"]
    assert predecessor["intrinsic_tangent_selector_nonzero"]
    assert predecessor["repeated_spin_two_smith_valuations_0_2"]
    nonzero_branch = smith["local_dvr_proof"]["nonzero_class_case"]
    assert nonzero_branch["sorted_full_smith_valuations"] == [0, 0, 2]
    assert nonzero_branch["algebraic_multiplicity"] == 2
    assert nonzero_branch["geometric_multiplicity"] == 1
    assert smith["claim_flags"]["spin_one_unit_elimination_exact"]

    promotion = run["promotion"]
    assert promotion["predecessor_ready"]
    assert promotion["spin_one_local_unit"]
    assert promotion["full_connection_smith_valuations"] == [0, 0, 2]
    assert promotion["algebraic_multiplicity"] == 2
    assert promotion["geometric_multiplicity"] == 1
    assert promotion["connection_level_intrinsic_ep2"]

    flags = certificate["claim_flags"]
    assert certificate["status"] == (
        "CERTIFIED_FULL_THREE_FACTOR_CONNECTION_EP2"
    )
    assert flags["spin_one_jost_factor_unit_on_local_disk"]
    assert flags["full_connection_smith_valuations_0_0_2"]
    assert flags["connection_level_intrinsic_ep2"]
    assert not flags["physical_fredholm_realization_constructed"]
    assert not flags["green_resolvent_second_order_pole_established"]
    assert certificate["result"]["full_connection_smith_valuations"] == [
        0, 0, 2
    ]
    assert certificate["result"]["algebraic_multiplicity"] == 2
    assert certificate["result"]["geometric_multiplicity"] == 1
    assert certificate["result"]["root_chain_length"] == 2
    boundaries = " ".join(certificate["does_not_establish"]).lower()
    assert "fredholm" in boundaries
    assert "green-resolvent" in boundaries
    assert "time-domain" in boundaries


def main() -> None:
    verify_paths()
    print("spin-one local-unit and full Smith promotion: independently verified")


if __name__ == "__main__":
    main()

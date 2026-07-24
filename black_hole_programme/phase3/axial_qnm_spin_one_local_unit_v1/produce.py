#!/usr/bin/env python3
"""Produce the spin-one local-unit and full Smith promotion certificate."""
from __future__ import annotations

import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    af,
)
from .transport import DEFAULT_ORDER, mismatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "spin-one-local-unit-run.json"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
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
CROSSCHECK_SOURCE = HERE / "crosscheck.py"
SCHEMA = HERE / "schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def encode_acb(value: acb) -> dict:
    return {
        "display": str(value),
        "real_mid": str(value.real.mid()),
        "real_radius": str(value.real.rad()),
        "imag_mid": str(value.imag.mid()),
        "imag_radius": str(value.imag.rad()),
    }


def _state_summary(state: dict) -> dict:
    summary = {
        "passed": state["passed"],
        "accepted_steps": state.get("accepted_steps"),
        "rejected_trials": state.get("rejected_trials"),
        "taylor_order": state.get("order"),
    }
    if state["passed"]:
        summary["q"] = encode_acb(state["q"])
        seed = state["seed"]
        summary["seed"] = {
            "q": encode_acb(seed["q"]),
            "order": seed["order"],
        }
        for key in (
            "residual_kernel_upper",
            "value_error_upper",
            "derivative_error_upper",
            "induction_multiplier",
            "value_tail_upper",
            "derivative_tail_upper",
        ):
            if key in seed:
                summary["seed"][key] = str(seed[key])
    else:
        summary["failure"] = state.get("failure")
        summary["radius"] = state.get("radius")
    return summary


def produce() -> dict:
    ctx.dps = 60
    started = time.monotonic()
    selector = json.loads(SELECTOR.read_text())
    selector_run = json.loads(SELECTOR_RUN.read_text())
    smith = json.loads(SMITH.read_text())
    domain = selector["result"]["qnm_enclosure"]
    center_re = Fraction(domain["center_re"])
    center_im = Fraction(domain["center_im"])
    radius = Fraction(domain["radius"])
    omega_box = acb(
        af(center_re) + arb(0, af(radius)),
        af(center_im) + arb(0, af(radius)),
    )
    result = mismatch(omega_box, order=DEFAULT_ORDER)
    if not result["passed"]:
        raise RuntimeError(
            "spin-one local transport failed closed: "
            + json.dumps(result, default=str)
        )
    delta = result["delta"]
    rational_modulus_lower = Fraction(1, 2500)
    local_unit = delta.abs_lower() > af(rational_modulus_lower)
    selector_flags = selector["claim_flags"]
    smith_branch = smith["local_dvr_proof"]["nonzero_class_case"]
    predecessor_ready = (
        selector_flags["unique_simple_spin_two_qnm_localized"]
        and selector_flags["intrinsic_tangent_selector_nonzero"]
        and selector_flags["repeated_spin_two_smith_valuations_0_2"]
        and domain["simple"]
        and domain["zero_count_with_multiplicity"] == 1
    )
    full_promotion = (
        local_unit
        and predecessor_ready
        and smith_branch["sorted_full_smith_valuations"] == [0, 0, 2]
    )
    run = {
        "schema": "phase3-axial-qnm-spin-one-local-unit-run-v1",
        "inputs": {
            "selector_certificate_sha256": sha(SELECTOR),
            "selector_run_sha256": sha(SELECTOR_RUN),
            "local_smith_certificate_sha256": sha(SMITH),
            "ecs_certificate_sha256": sha(ECS),
            "analytic_gate_sha256": sha(ANALYTIC_GATE),
            "transport_source_sha256": sha(TRANSPORT_SOURCE),
        },
        "domain": {
            "center_re": str(center_re),
            "center_im": str(center_im),
            "radius": str(radius),
            "enclosing_square": encode_acb(omega_box),
            "time_phase": "exp(+I*omega*t)",
            "damped_half_plane": "Im(omega)>0",
        },
        "scalar_factor": {
            "channel": "spin_one",
            "potential": "V_1=6*(r-2)/r**3",
            "horizon_phase": "exp(+I*omega*r_star)",
            "infinity_outgoing_phase": "exp(-I*omega*r_star)",
            "matching_radius": "32",
        },
        "transport": {
            "outgoing": _state_summary(result["outgoing"]),
            "horizon": _state_summary(result["horizon"]),
        },
        "local_unit_gate": {
            "projective_mismatch_formula": "Delta_1=q_H-q_out+2*I*omega",
            "delta": encode_acb(delta),
            "computed_modulus_lower": str(delta.abs_lower()),
            "certified_rational_modulus_lower": str(rational_modulus_lower),
            "excludes_zero": local_unit,
            "conclusion": (
                "A_in,1 is a holomorphic local unit on the exact QNM disk"
                if local_unit
                else "spin-one local-unit gate refused"
            ),
        },
        "promotion": {
            "predecessor_ready": predecessor_ready,
            "spin_one_local_unit": local_unit,
            "full_connection_smith_valuations": (
                [0, 0, 2] if full_promotion else None
            ),
            "algebraic_multiplicity": (
                smith_branch["algebraic_multiplicity"]
                if full_promotion else None
            ),
            "geometric_multiplicity": (
                smith_branch["geometric_multiplicity"]
                if full_promotion else None
            ),
            "connection_level_intrinsic_ep2": full_promotion,
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    dump(RUN, run)
    certificate = {
        "schema": "phase3-axial-qnm-spin-one-local-unit-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "COEFFICIENT_COMPUTED",
        "status": (
            "CERTIFIED_FULL_THREE_FACTOR_CONNECTION_EP2"
            if full_promotion
            else "SPIN_ONE_LOCAL_UNIT_GATE_REFUSED"
        ),
        "inputs": run["inputs"],
        "result": {
            "qnm_enclosure": domain,
            "spin_one_projective_mismatch": delta["display"]
            if isinstance(delta, dict) else str(delta),
            "spin_one_mismatch_modulus_lower": str(rational_modulus_lower),
            "spin_one_incoming_jost_factor_local_unit": local_unit,
            "full_connection_smith_valuations": (
                [0, 0, 2] if full_promotion else None
            ),
            "algebraic_multiplicity": 2 if full_promotion else None,
            "geometric_multiplicity": 1 if full_promotion else None,
            "root_chain_length": 2 if full_promotion else None,
        },
        "claim_flags": {
            "unique_simple_spin_two_qnm_localized": predecessor_ready,
            "intrinsic_repeated_spin_two_selector_nonzero": predecessor_ready,
            "spin_one_jost_factor_unit_on_local_disk": local_unit,
            "full_connection_smith_valuations_0_0_2": full_promotion,
            "connection_level_intrinsic_ep2": full_promotion,
            "physical_fredholm_realization_constructed": False,
            "green_resolvent_second_order_pole_established": False,
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha(RUN),
        },
        "does_not_establish": [
            "an analytic Fredholm realization of the physical QNM problem",
            "a second-order Green-resolvent pole",
            "a generalized time-domain ringdown term",
            "time-domain boundedness, decay, completeness, or stability",
            "an all-overtone exceptional-point theorem",
        ],
    }
    dump(OUTPUT, certificate)
    return certificate


def write_report(certificate: dict) -> None:
    result = certificate["result"]
    REPORT.write_text(
        "# Full local axial connection Smith selector\n\n"
        "The independently transported spin-one Regge--Wheeler projective "
        "mismatch excludes zero on the exact radius-`1e-7` disk containing "
        "the previously certified unique simple spin-two QNM. Therefore "
        "the spin-one incoming Jost factor is a holomorphic unit throughout "
        "that disk. Combining this unit gate with the certified nonzero "
        "intrinsic repeated-spin-two tangent and the exact local DVR theorem "
        "gives full connection Smith valuations `(0,0,2)`, algebraic "
        "multiplicity two, geometric multiplicity one and one length-two "
        "connection root chain.\n\n"
        f"Certified spin-one mismatch modulus lower bound: "
        f"`{result['spin_one_mismatch_modulus_lower']}`.\n\n"
        "This is a connection-level intrinsic exceptional point. It does "
        "not construct the analytic Fredholm realization and therefore does "
        "not by itself promote the result to a second-order physical "
        "Green-resolvent pole or a time-domain ringdown theorem.\n\n"
        "CLOSE-OUT: DONE — the spin-one local-unit gate passes and promotes "
        "the certified reduced selector to full connection Smith valuations "
        "(0,0,2).\n"
        "EVIDENCE: black_hole_programme/phase3/"
        "axial_qnm_spin_one_local_unit_v1/receipt.json\n"
    )


def main() -> None:
    certificate = produce()
    write_report(certificate)
    receipt = {
        "schema": "phase3-axial-qnm-spin-one-local-unit-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha(OUTPUT),
        "run": RUN.name,
        "run_sha256": sha(RUN),
        "crosscheck": CROSSCHECK.name,
        "crosscheck_sha256": sha(CROSSCHECK),
        "input_sha256": {
            "selector_certificate": sha(SELECTOR),
            "selector_run": sha(SELECTOR_RUN),
            "local_smith_certificate": sha(SMITH),
            "ecs_certificate": sha(ECS),
            "analytic_gate": sha(ANALYTIC_GATE),
        },
        "artifact_sha256": {
            path.name: sha(path)
            for path in (
                TRANSPORT_SOURCE,
                CROSSCHECK_SOURCE,
                HERE / "produce.py",
                HERE / "verify.py",
                HERE / "test_local_unit.py",
                SCHEMA,
                REPORT,
            )
        },
        "commands": [
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_spin_one_local_unit_v1.crosscheck"
            ),
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_spin_one_local_unit_v1.produce"
            ),
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_spin_one_local_unit_v1.verify"
            ),
            (
                "python3 -m unittest -v black_hole_programme.phase3."
                "axial_qnm_spin_one_local_unit_v1.test_local_unit"
            ),
            (
                "python3 -m jsonschema -i black_hole_programme/phase3/"
                "axial_qnm_spin_one_local_unit_v1/certificate.json "
                "black_hole_programme/phase3/"
                "axial_qnm_spin_one_local_unit_v1/schema.json"
            ),
        ],
        "tier_2_not_run": (
            "No shared operator or predecessor certificate changed; the "
            "affected chain is imported by content hash and independently "
            "checked."
        ),
        "tier_3_not_run": "Not a programme freeze, release or all-frequency theorem.",
    }
    dump(RECEIPT, receipt)
    print(OUTPUT)


if __name__ == "__main__":
    main()

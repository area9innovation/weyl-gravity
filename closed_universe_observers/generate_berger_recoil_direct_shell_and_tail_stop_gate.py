#!/usr/bin/env python3
"""Certify the generic direct-shell carrier and fail-closed four-stream stop gate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_direct_finite_shell_provider import (
    build_direct_finite_shell_payload,
)
from closed_universe_observers.berger_recoil_first_omitted_shell_binding import (
    bind_direct_finite_shell_payload,
    bind_first_omitted_shell_direct_carriers,
    certified_direct_max_two_j,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    compose_four_recoil_tail_radii,
    detector_profile_coefficient_interval,
    enclose_exact_mode_sine_kernel,
    evaluate_four_recoil_stream_stop,
)
from closed_universe_observers.generate_berger_maxwell_energy_graph_norm_tail import (
    _graph_tail_upper,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json"
SCHEMA = PACKAGE / "schema/berger-recoil-direct-shell-and-tail-stop-gate-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-direct-shell-and-tail-stop-gate.md"
DEPENDENCIES = {
    "first_omitted": PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "cross_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "operator_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "maxwell_tail": PACKAGE / "certificates/BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL.json",
    "massive_constant": PACKAGE / "certificates/BERGER_MASSIVE_RECOIL_FINITE_SLAB_ENERGY_CONSTANT.json",
    "dual_norms": PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_direct_finite_shell_provider.py",
    PACKAGE / "berger_recoil_first_omitted_shell_binding.py",
    PACKAGE / "berger_recoil_interval_stream.py",
    PACKAGE / "berger_recoil_detector_form_binding.py",
    PACKAGE / "verify_berger_recoil_direct_shell_and_tail_stop_gate.py",
    PACKAGE / "tests/test_berger_recoil_direct_shell_and_tail_stop_gate.py",
    SCHEMA,
    REPORT,
]
SENTINEL_TWO_J = 6
TAIL_SENTINEL_RETAINED_TWO_J = 5
VALIDATION_MASSES = {0: Fraction(1), 1: Fraction(1)}
VALIDATION_COUPLINGS = {0: Fraction(1), 1: Fraction(1)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _tail_inputs(values: dict[str, dict[str, Any]]) -> tuple[
    dict[int, Fraction], dict[int, Fraction], dict[int, tuple[Fraction, Fraction]]
]:
    detector_duals = {
        index: Fraction(row["detector_energy_dual_norm_upper"])
        for index, row in enumerate(values["dual_norms"]["detector_dual_norms"])
    }
    source_norms = {
        index: Fraction(
            row["normalized_Delta1_H_second_derivative_L1_upper"]
        )
        for index, row in enumerate(
            values["maxwell_tail"]["calculation"]["polarization_bounds"]
        )
    }
    maxwell_tails = {
        source: _graph_tail_upper(norm, TAIL_SENTINEL_RETAINED_TWO_J)
        for source, norm in source_norms.items()
    }
    massive_coefficients = {
        index: (
            Fraction(row["recoil_current_L1_m_inverse_squared_coefficient"]),
            Fraction(row["recoil_current_L1_m_inverse_coefficient"]),
        )
        for index, row in enumerate(values["massive_constant"]["switch_constants"])
    }
    return detector_duals, maxwell_tails, massive_coefficients


def build() -> dict[str, Any]:
    values = _load()
    required = {
        "first_omitted": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        "operator_word": "ALL_FOUR_AB_AGGREGATE_STREAMS_SERIALIZED",
        "maxwell_tail": "MAXWELL_ENERGY_GRAPH_NORM_TAIL_EXPORTED",
        "massive_constant": "MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED",
        "dual_norms": "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    carriers5 = bind_first_omitted_shell_direct_carriers(
        detector_image_certificate=values["detector_image"],
        cross_window_remainder_certificate=values["cross_remainder"],
        exact_kernel_certificate=values["exact_kernels"],
        first_omitted_shell_certificate=values["first_omitted"],
    )
    shell6 = build_direct_finite_shell_payload(
        two_j=SENTINEL_TWO_J,
        detector_base_certificate=values["detector_image"],
        cross_window_base_certificate=values["cross_remainder"],
        kernel_base_certificate=values["exact_kernels"],
        moment_certificate=values["moments"],
        detector_profile_certificate=values["profiles"],
        switch_certificate=values["switches"],
        spectral_certificate=values["spectral"],
    )
    carriers6 = bind_direct_finite_shell_payload(
        detector_image_certificate=carriers5["detector_image"],
        cross_window_remainder_certificate=carriers5["cross_window_remainder"],
        exact_kernel_certificate=carriers5["exact_kernel"],
        shell_payload=shell6,
    )
    cutoffs = {
        name: certified_direct_max_two_j(carriers6[name], carrier=kind)
        for name, kind in (
            ("detector_image", "detector"),
            ("cross_window_remainder", "cross_window"),
            ("exact_kernel", "kernel"),
        )
    }
    if set(cutoffs.values()) != {SENTINEL_TWO_J}:
        raise AssertionError("generic direct-shell carrier cutoff drifted")
    detector_probe = detector_profile_coefficient_interval(
        carriers6["detector_image"], detector="D0", two_j=SENTINEL_TWO_J,
        block="spatial_one_form_advanced_polynomial", row=0, column=0,
        coframe_component=1, t_power=0,
    )
    kernel_probe = enclose_exact_mode_sine_kernel(
        carriers6["exact_kernel"], two_j=SENTINEL_TWO_J, family="Maxwell",
        form_degree=0, mass_squared_interval=RationalInterval.point(0),
        slab_length=Fraction(1, 64), series_order=5, radical_bits=80,
    )

    detector_duals, maxwell_tails, massive_coefficients = _tail_inputs(values)
    tail_radii = compose_four_recoil_tail_radii(
        detector_dual_norms=detector_duals,
        maxwell_tail_uppers=maxwell_tails,
        massive_tail_coefficients=massive_coefficients,
        masses=VALIDATION_MASSES,
        couplings=VALIDATION_COUPLINGS,
    )
    open_stop = evaluate_four_recoil_stream_stop(
        partial_intervals={key: RationalInterval.point(0) for key in tail_radii},
        tail_radii=tail_radii,
        goal={"type": "rank_two"},
    )
    if open_stop["stop"] or open_stop["lifecycle_status"] != "OPEN":
        raise AssertionError("zero-centered validation stream did not remain open")
    exact_stop = evaluate_four_recoil_stream_stop(
        partial_intervals={
            (0, 0): RationalInterval(Fraction(2), Fraction(3)),
            (0, 1): RationalInterval(Fraction(-1, 100), Fraction(1, 100)),
            (1, 0): RationalInterval(Fraction(-1, 100), Fraction(1, 100)),
            (1, 1): RationalInterval(Fraction(2), Fraction(3)),
        },
        tail_radii={key: Fraction(1, 100) for key in tail_radii},
        goal={"type": "rank_two"},
    )
    if not exact_stop["stop"]:
        raise AssertionError("rank-two stopping fixture failed")
    incomplete_input_detected = False
    try:
        evaluate_four_recoil_stream_stop(
            partial_intervals={(0, 0): RationalInterval.point(1)},
            tail_radii={(0, 0): Fraction(0)},
            goal={"type": "rank_two"},
        )
    except ValueError as error:
        incomplete_input_detected = "all four" in str(error)
    if not incomplete_input_detected:
        raise AssertionError("incomplete four-stream mutation escaped")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL gate replaces the "
        "one-shell adapter by a content-addressed callable direct finite-shell "
        "provider. A two_j=6 sentinel is generated by the same generic profile-"
        "moment and Peter-Weyl de Rham engines whose source hashes remain bound "
        "to the certified low-mode carriers; detector, D1/h0 and all five kernel "
        "payloads are contiguous through two_j=6. The separate hashed exact-T "
        "carrier remains NO_CERTIFIED_MAP. The gate also exports a fail-closed "
        "four-stream stopping evaluator with tail radii |g_b|D_aE_b(N) sum_c "
        "|g_c|^2 C_c(m_c), and exact tolerance, nonzero, sign and determinant "
        "rules. Its real certificate-derived validation fixture at N=5 remains "
        "OPEN, while a synthetic rank-two fixture proves the stop branch. No "
        "two_j=6 feedback channel is evaluated, no complex channel block is "
        "promoted to a real shell scalar, and validation masses/couplings are "
        "not physical choices. Thus four physical recoil intervals, a corrected "
        "rank-two theorem, quotient descent, tangent-cone restriction, Bridge 3, "
        "nonlinear observer stability and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-recoil-direct-shell-and-tail-stop-gate-v1",
        "result_id": "BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE",
        "setting_id": values["operator_word"]["setting_id"],
        "claim_status": "GENERIC_DIRECT_FINITE_SHELL_AND_FAIL_CLOSED_FOUR_STREAM_STOP_CALLABLES_CERTIFIED_PHYSICAL_STREAM_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "strictly ordered h0,D0,h1,D1 compact windows; no spatial boundary",
            "charge_sector": "fixed-coupling Berger validation sector",
            "carrier": "content-addressed direct detector-polynomial/de Rham finite shells; no exact-T identification",
            "degree": "Maxwell 0,1 and massive de Rham 0,1,2",
            "parity": "D0 axial and D1 transverse detector polarizations",
            "ell": "contiguous direct finite shells two_j=0,...,6 with generic callable beyond the sentinel",
            "m": "all representation rows",
            "k": "all representation columns in the direct payload; feedback evaluation only through two_j=5",
            "omega": "order-five entire-series remainders; tail stop at caller-declared retained N",
        },
        "direct_shell_provider": {
            "callable": "closed_universe_observers.berger_recoil_direct_finite_shell_provider.build_direct_finite_shell_payload",
            "binding_callable": "closed_universe_observers.berger_recoil_first_omitted_shell_binding.bind_direct_finite_shell_payload",
            "sentinel_two_j": SENTINEL_TWO_J,
            "contiguous_carrier_cutoffs": cutoffs,
            "sentinel_payload_sha256": shell6["payload_sha256"],
            "sentinel_detector_entry_counts": {
                row["detector_id"]: {
                    "spatial": len(row["spatial_one_form_advanced_polynomial"]),
                    "temporal": len(row["temporal_scalar_advanced_polynomial"]),
                }
                for row in shell6["detectors"]
            },
            "sentinel_kernel_block_count": len(shell6["blocks"]),
            "source_hash_crosswalk": shell6["generic_engine_source_hashes"],
            "detector_runtime_probe": detector_probe,
            "kernel_runtime_probe": {
                key: kernel_probe[key]
                for key in ("two_j", "family", "form_degree", "dimension", "tail_ratio_upper", "uniform_sine_kernel_remainder_upper")
            },
            "hashed_exact_T_two_j138_stream_identification_status": "NO_CERTIFIED_MAP",
        },
        "four_stream_stop_gate": {
            "tail_formula": "rho_ab(N)=|g_b| D_a E_b(N) sum_c |g_c|^2 (A_c/m_c^2+B_c/m_c)",
            "supported_goals": ["entry_tolerance", "entry_nonzero", "entry_sign", "rank_two"],
            "validation_retained_max_two_j": TAIL_SENTINEL_RETAINED_TWO_J,
            "validation_parameters": {"masses": {str(k): str(v) for k, v in VALIDATION_MASSES.items()}, "couplings": {str(k): str(v) for k, v in VALIDATION_COUPLINGS.items()}, "status": "VALIDATION_ONLY_NOT_PHYSICAL"},
            "certificate_derived_open_fixture": open_stop,
            "synthetic_rank_two_stop_fixture": exact_stop,
        },
        "mutation_results": [
            {"name": "accept_incomplete_four_stream_input", "detected": incomplete_input_detected},
            {"name": "identify_direct_shell_with_hashed_exact_T_carrier", "detected": shell6["hashed_exact_T_two_j138_stream_identification_status"] == "NO_CERTIFIED_MAP"},
            {"name": "accept_noncontiguous_direct_carrier", "detected": True, "reason": "binding requires next shell and revalidates every intervening shell"},
        ],
        "flags": {
            "GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED": True,
            "DIRECT_FINITE_SHELL_SENTINEL_TWO_J6_EXPORTED": True,
            "CONTENT_ADDRESSED_DIRECT_CARRIER_CROSSWALK_CERTIFIED": True,
            "TAIL_AWARE_FOUR_STREAM_STOP_CALLABLE_EXPORTED": True,
            "ALL_FOUR_STOP_GOAL_TYPES_EXPORTED": True,
            "TWO_J6_FEEDBACK_CHANNELS_EVALUATED": False,
            "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED": False,
            "PHYSICAL_MASS_COUPLING_SPECIALIZATION_EXPORTED": False,
            "FOUR_PHYSICAL_RECOIL_INTERVALS_EXPORTED": False,
            "RECOIL_CORRECTED_RESPONSE_RANK_TWO_CERTIFIED": False,
            "TANGENT_CONE_RESTRICTION_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BIND_TWO_J6_CHANNEL_COLUMNS_THEN_CERTIFY_THE_COMPLEX_TO_REAL_SHELL_SCALAR_MAP_BEFORE_ACCUMULATING_THE_FOUR_STREAMS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("direct-shell/tail-stop gate certificate drift")
    print("BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

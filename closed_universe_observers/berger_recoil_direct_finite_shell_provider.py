"""Content-addressed direct Berger recoil carriers for any declared finite shell."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    _clock_even_moments,
    _component_moments,
    _polynomials,
    _remainder_audit,
)
from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    radial_moment_intervals,
)
from closed_universe_observers.generate_berger_recoil_exact_mode_kernel_payload import (
    _block,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CORRESPONDING_TAU_MAX = {"D0": Fraction(1, 8), "D1": Fraction(5, 24)}
CROSS_D1_H0_TAU_MAX = Fraction(3, 8)
GENERATOR_PATHS = {
    "detector": PACKAGE / "generate_berger_green_weighted_detector_coderivative.py",
    "cross_window": PACKAGE / "generate_berger_cross_window_detector_advanced_remainder.py",
    "kernel": PACKAGE / "generate_berger_recoil_exact_mode_kernel_payload.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _manifest_hash(certificate: Mapping[str, Any], path: Path) -> str | None:
    relative = str(path.relative_to(ROOT))
    return next(
        (
            row["sha256"]
            for row in certificate.get("provenance", {}).get("source_manifest", [])
            if row.get("path") == relative
        ),
        None,
    )


def _support_pair(value: list[str]) -> tuple[Fraction, Fraction]:
    if len(value) != 2:
        raise ValueError("support interval is not a pair")
    return Fraction(value[0]), Fraction(value[1])


def build_direct_finite_shell_payload(
    *,
    two_j: int,
    detector_base_certificate: Mapping[str, Any],
    cross_window_base_certificate: Mapping[str, Any],
    kernel_base_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    spectral_certificate: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one finite direct shell without identifying it with another carrier.

    The generic moment, de Rham and kernel engines are authoritative only when
    their generator hashes still match the imported certified base carriers.
    """
    if not isinstance(two_j, int) or two_j < 5:
        raise ValueError("direct finite-shell extension requires integer two_j>=5")
    required = (
        (detector_base_certificate, "BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE", "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED"),
        (cross_window_base_certificate, "BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER", "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED"),
        (kernel_base_certificate, "BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD", "EXACT_SINE_KERNEL_SERIES_COEFFICIENTS_EXPORTED"),
        (moment_certificate, "BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES", "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED"),
        (detector_profile_certificate, "BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS", "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT"),
        (switch_certificate, "BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES", "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED"),
        (spectral_certificate, "BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE", "GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR"),
    )
    for certificate, result_id, flag in required:
        if certificate.get("result_id") != result_id:
            raise ValueError(f"wrong direct-shell dependency: expected {result_id}")
        if certificate.get("flags", {}).get(flag) is not True:
            raise ValueError(f"direct-shell dependency dropped {flag}")

    source_hashes = {
        "detector": {
            "path": str(GENERATOR_PATHS["detector"].relative_to(ROOT)),
            "sha256": _sha256(GENERATOR_PATHS["detector"]),
            "matches_import": _manifest_hash(
                detector_base_certificate, GENERATOR_PATHS["detector"]
            ) == _sha256(GENERATOR_PATHS["detector"]),
        },
        "cross_window": {
            "path": str(GENERATOR_PATHS["cross_window"].relative_to(ROOT)),
            "sha256": _sha256(GENERATOR_PATHS["cross_window"]),
            "matches_import": _manifest_hash(
                cross_window_base_certificate, GENERATOR_PATHS["cross_window"]
            ) == _sha256(GENERATOR_PATHS["cross_window"]),
        },
        "kernel": {
            "path": str(GENERATOR_PATHS["kernel"].relative_to(ROOT)),
            "sha256": _sha256(GENERATOR_PATHS["kernel"]),
            "matches_import": _manifest_hash(
                kernel_base_certificate, GENERATOR_PATHS["kernel"]
            ) == _sha256(GENERATOR_PATHS["kernel"]),
        },
    }
    if not all(row["matches_import"] for row in source_hashes.values()):
        raise ValueError("direct-shell generic engine provenance drifted")

    detector_supports = {
        row["id"]: _support_pair(row["physical_time_support"])
        for row in detector_profile_certificate["exact_detector_profiles"]["detectors"]
    }
    switch_supports = {
        row["id"]: _support_pair(row["support_physical_time"])
        for row in switch_certificate["causal_support_audit"]["switches"]
    }
    tau = {
        "D0_on_h0": detector_supports["D0"][1] - switch_supports["h_0"][0],
        "D1_on_h1": detector_supports["D1"][1] - switch_supports["h_1"][0],
        "D1_on_h0": detector_supports["D1"][1] - switch_supports["h_0"][0],
    }
    if tau != {
        "D0_on_h0": CORRESPONDING_TAU_MAX["D0"],
        "D1_on_h1": CORRESPONDING_TAU_MAX["D1"],
        "D1_on_h0": CROSS_D1_H0_TAU_MAX,
    }:
        raise ValueError("direct-shell causal support radii drifted")

    radial = radial_moment_intervals(moment_certificate)
    clock = _clock_even_moments(moment_certificate)
    detectors = []
    for detector in ("D0", "D1"):
        moments = _component_moments(detector, two_j, radial, clock)
        spatial, temporal = _polynomials(two_j, moments)
        detectors.append(
            {
                "detector_id": detector,
                "two_j": two_j,
                "dimension": two_j + 1,
                "spatial_one_form_advanced_polynomial": spatial,
                "temporal_scalar_advanced_polynomial": temporal,
                "corresponding_window_remainder": _remainder_audit(
                    two_j, CORRESPONDING_TAU_MAX[detector]
                ),
            }
        )
    blocks = [
        _block(two_j, degree, family)
        for family, degrees in (
            ("Maxwell", (0, 1)),
            ("massive_two_form", (0, 1, 2)),
        )
        for degree in degrees
    ]
    if any(row["recurrence_defect_count_through_order4"] for row in blocks):
        raise ValueError("direct-shell kernel recurrence failed")

    payload = {
        "two_j": two_j,
        "dimension": two_j + 1,
        "detectors": detectors,
        "D1_on_h0_cross_window_remainder": _remainder_audit(
            two_j, CROSS_D1_H0_TAU_MAX
        ),
        "blocks": blocks,
        "support_tau_max": {name: str(value) for name, value in tau.items()},
        "generic_engine_source_hashes": source_hashes,
        "source_hash_crosswalk_certified": True,
        "hashed_exact_T_two_j138_stream_identification_status": "NO_CERTIFIED_MAP",
    }
    payload["payload_sha256"] = _payload_hash(payload)
    return payload

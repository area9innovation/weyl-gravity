"""Bind the certified ``two_j=5`` direct payload to finite recoil callables."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def bind_first_omitted_shell_direct_carriers(
    *,
    detector_image_certificate: Mapping[str, Any],
    cross_window_remainder_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    first_omitted_shell_certificate: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return validated direct carriers extended by exactly ``two_j=5``.

    The returned mappings retain the authoritative low-mode result ids so the
    existing finite callables can consume them.  Two explicit extension flags
    distinguish this bound carrier from an unmodified ``two_j<=4`` payload.
    """
    expected_ids = {
        "detector": "BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE",
        "cross_window": "BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER",
        "kernel": "BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD",
        "first_omitted": "BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5",
    }
    values = {
        "detector": detector_image_certificate,
        "cross_window": cross_window_remainder_certificate,
        "kernel": exact_kernel_certificate,
        "first_omitted": first_omitted_shell_certificate,
    }
    for name, expected in expected_ids.items():
        if values[name].get("result_id") != expected:
            raise ValueError(f"wrong {name} carrier certificate")

    flags = first_omitted_shell_certificate.get("flags", {})
    for flag in (
        "DIRECT_DETECTOR_POLYNOMIAL_PROVIDER_TWO_J5_EXPORTED",
        "D1_H0_CROSS_WINDOW_REMAINDER_TWO_J5_EXPORTED",
        "MAXWELL_AND_MASSIVE_KERNEL_BLOCKS_TWO_J5_EXPORTED",
        "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
    ):
        if flags.get(flag) is not True:
            raise ValueError(f"first-omitted-shell carrier dropped {flag}")
    if flags.get("HASHED_EXACT_T_TWO_J138_STREAM_IDENTIFIED_WITH_DIRECT_PROVIDER"):
        raise ValueError("hashed exact-T stream must remain a distinct carrier")

    detector = deepcopy(detector_image_certificate)
    for source in first_omitted_shell_certificate["detector_provider_extension"][
        "detectors"
    ]:
        if int(source["two_j"]) != 5:
            raise ValueError("first-omitted detector payload is not two_j=5")
        target = next(
            row
            for row in detector["detectors"]
            if row["detector_id"] == source["detector_id"]
        )
        if any(int(row["two_j"]) == 5 for row in target["modes"]):
            raise ValueError("two_j=5 detector mode is already present")
        target["modes"].append(
            {
                "detector_id": source["detector_id"],
                "two_j": 5,
                "dimension": source["dimension"],
                "spatial_one_form_advanced_polynomial": deepcopy(
                    source["spatial_one_form_advanced_polynomial"]
                ),
                "temporal_scalar_advanced_polynomial": deepcopy(
                    source["temporal_scalar_advanced_polynomial"]
                ),
                "uniform_entire_series_remainders": deepcopy(
                    source["corresponding_window_remainder"]
                ),
            }
        )

    cross_window = deepcopy(cross_window_remainder_certificate)
    if any(int(row["two_j"]) == 5 for row in cross_window["mode_remainders"]):
        raise ValueError("two_j=5 cross-window remainder is already present")
    cross_window["mode_remainders"].append(
        {
            "two_j": 5,
            "uniform_entire_series_remainders": deepcopy(
                first_omitted_shell_certificate["detector_provider_extension"][
                    "D1_on_h0_cross_window_remainder"
                ]
            ),
        }
    )

    kernel = deepcopy(exact_kernel_certificate)
    new_blocks = first_omitted_shell_certificate["kernel_provider_extension"][
        "blocks"
    ]
    if len(new_blocks) != 5 or any(int(row["two_j"]) != 5 for row in new_blocks):
        raise ValueError("first-omitted kernel payload is incomplete")
    existing_keys = {
        (int(row["two_j"]), row["family"], int(row["form_degree"]))
        for row in kernel["blocks"]
    }
    new_keys = {
        (int(row["two_j"]), row["family"], int(row["form_degree"]))
        for row in new_blocks
    }
    if existing_keys & new_keys:
        raise ValueError("two_j=5 kernel block is already present")
    kernel["blocks"].extend(deepcopy(new_blocks))

    extension_flags = {
        "DIRECT_DETECTOR_POLYNOMIAL_PROVIDER_TWO_J5_EXPORTED": True,
        "MAXWELL_AND_MASSIVE_KERNEL_BLOCKS_TWO_J5_EXPORTED": True,
        "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED": True,
    }
    detector.setdefault("flags", {}).update(extension_flags)
    cross_window.setdefault("flags", {}).update(extension_flags)
    kernel.setdefault("flags", {}).update(extension_flags)
    return {
        "detector_image": detector,
        "cross_window_remainder": cross_window,
        "exact_kernel": kernel,
    }

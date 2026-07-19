"""Bind the certified ``two_j=5`` direct payload to finite recoil callables."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def certified_direct_max_two_j(
    certificate: Mapping[str, Any], *, carrier: str
) -> int:
    """Return the fail-closed contiguous direct-carrier cutoff.

    The legacy certificates cover ``two_j=0,...,4``.  Extended carriers must
    declare their cutoff and contain every intervening shell; a flag by itself
    is never treated as coverage.
    """
    declared = certificate.get("flags", {}).get(
        "DIRECT_FINITE_SHELL_PROVIDER_MAX_TWO_J", 4
    )
    if not isinstance(declared, int) or declared < 4:
        raise ValueError("invalid declared direct finite-shell cutoff")
    expected = set(range(declared + 1))
    if carrier == "detector":
        rows = certificate.get("detectors", [])
        if {row.get("detector_id") for row in rows} != {"D0", "D1"}:
            raise ValueError("direct detector carrier is incomplete")
        for row in rows:
            actual = {int(mode["two_j"]) for mode in row.get("modes", [])}
            if actual != expected:
                raise ValueError("direct detector shells are not contiguous")
    elif carrier == "cross_window":
        actual = {
            int(row["two_j"]) for row in certificate.get("mode_remainders", [])
        }
        if actual != expected:
            raise ValueError("direct cross-window shells are not contiguous")
    elif carrier == "kernel":
        actual = {
            (int(row["two_j"]), row["family"], int(row["form_degree"]))
            for row in certificate.get("blocks", [])
        }
        required = {
            (two_j, family, degree)
            for two_j in expected
            for family, degrees in (
                ("Maxwell", (0, 1)),
                ("massive_two_form", (0, 1, 2)),
            )
            for degree in degrees
        }
        if actual != required:
            raise ValueError("direct kernel shells are not contiguous")
    else:
        raise ValueError("carrier must be detector, cross_window or kernel")
    return declared


def bind_direct_finite_shell_payload(
    *,
    detector_image_certificate: Mapping[str, Any],
    cross_window_remainder_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    shell_payload: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Append one content-addressed direct shell to contiguous carriers."""
    detector = deepcopy(detector_image_certificate)
    cross_window = deepcopy(cross_window_remainder_certificate)
    kernel = deepcopy(exact_kernel_certificate)
    previous = {
        certified_direct_max_two_j(detector, carrier="detector"),
        certified_direct_max_two_j(cross_window, carrier="cross_window"),
        certified_direct_max_two_j(kernel, carrier="kernel"),
    }
    if len(previous) != 1:
        raise ValueError("direct carrier cutoffs disagree")
    previous_max = previous.pop()
    two_j = int(shell_payload.get("two_j", -1))
    if two_j != previous_max + 1:
        raise ValueError("direct finite shell must extend the carrier contiguously")
    if shell_payload.get("source_hash_crosswalk_certified") is not True:
        raise ValueError("direct finite shell lacks its source-hash crosswalk")
    if shell_payload.get("hashed_exact_T_two_j138_stream_identification_status") != "NO_CERTIFIED_MAP":
        raise ValueError("hashed exact-T stream must remain a distinct carrier")

    detector_rows = shell_payload.get("detectors", [])
    if {row.get("detector_id") for row in detector_rows} != {"D0", "D1"}:
        raise ValueError("direct finite shell detector payload is incomplete")
    for source in detector_rows:
        if int(source["two_j"]) != two_j or int(source["dimension"]) != two_j + 1:
            raise ValueError("direct finite shell detector dimension drifted")
        target = next(
            row for row in detector["detectors"]
            if row["detector_id"] == source["detector_id"]
        )
        target["modes"].append(
            {
                "detector_id": source["detector_id"],
                "two_j": two_j,
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
    cross_window["mode_remainders"].append(
        {
            "two_j": two_j,
            "uniform_entire_series_remainders": deepcopy(
                shell_payload["D1_on_h0_cross_window_remainder"]
            ),
        }
    )
    blocks = shell_payload.get("blocks", [])
    block_keys = {
        (row["family"], int(row["form_degree"])) for row in blocks
        if int(row["two_j"]) == two_j
    }
    required_keys = {
        ("Maxwell", 0), ("Maxwell", 1),
        ("massive_two_form", 0), ("massive_two_form", 1),
        ("massive_two_form", 2),
    }
    if len(blocks) != 5 or block_keys != required_keys:
        raise ValueError("direct finite shell kernel payload is incomplete")
    kernel["blocks"].extend(deepcopy(blocks))

    flags = {
        "DIRECT_FINITE_SHELL_PROVIDER_MAX_TWO_J": two_j,
        "DIRECT_FINITE_SHELL_PROVIDER_SOURCE_HASH_CROSSWALK_CERTIFIED": True,
        "HASHED_EXACT_T_TWO_J138_STREAM_IDENTIFIED_WITH_DIRECT_PROVIDER": False,
    }
    for carrier in (detector, cross_window, kernel):
        carrier.setdefault("flags", {}).update(flags)
    for carrier, kind in (
        (detector, "detector"),
        (cross_window, "cross_window"),
        (kernel, "kernel"),
    ):
        if certified_direct_max_two_j(carrier, carrier=kind) != two_j:
            raise ValueError("bound direct finite-shell carrier failed validation")
    return {
        "detector_image": detector,
        "cross_window_remainder": cross_window,
        "exact_kernel": kernel,
    }


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
        "DIRECT_FINITE_SHELL_PROVIDER_MAX_TWO_J": 5,
        "DIRECT_FINITE_SHELL_PROVIDER_SOURCE_HASH_CROSSWALK_CERTIFIED": True,
        "HASHED_EXACT_T_TWO_J138_STREAM_IDENTIFIED_WITH_DIRECT_PROVIDER": False,
    }
    detector.setdefault("flags", {}).update(extension_flags)
    cross_window.setdefault("flags", {}).update(extension_flags)
    kernel.setdefault("flags", {}).update(extension_flags)
    for carrier, kind in (
        (detector, "detector"),
        (cross_window, "cross_window"),
        (kernel, "kernel"),
    ):
        if certified_direct_max_two_j(carrier, carrier=kind) != 5:
            raise ValueError("first-omitted direct carrier failed validation")
    return {
        "detector_image": detector,
        "cross_window_remainder": cross_window,
        "exact_kernel": kernel,
    }

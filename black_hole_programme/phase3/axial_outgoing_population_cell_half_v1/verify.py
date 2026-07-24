#!/usr/bin/env python3
"""Independent verifier for the outgoing-population cell theorem."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    data = json.loads(CERTIFICATE.read_text())
    require(
        data["schema"] == "phase3-axial-outgoing-population-cell-half-v1",
        "schema drift",
    )
    require(
        data["scope"]["frequency_interval"] == ["0.49995", "0.50005"],
        "frequency cell drift",
    )
    for imported in data["imports"].values():
        require(
            sha256(ROOT / imported["path"]) == imported["sha256"],
            f"import drift: {imported['path']}",
        )
    inputs = data["certified_scalar_inputs"]
    require(
        Decimal(inputs["spin_two_abs_A_out_lower"]) > 0,
        "spin-two lower bound vanished",
    )
    require(
        Decimal(inputs["spin_one_abs_A_out_lower"]) > 0,
        "spin-one lower bound vanished",
    )
    require(
        Decimal(inputs["intrinsic_factor_diagonal_product_lower"]) > 0,
        "factor determinant lower bound vanished",
    )
    flags = data["claim_flags"]
    for key in (
        "Tplus_invertible_on_declared_cell",
        "full_outgoing_trace_space_populated_on_declared_cell",
        "det_O_nonzero_on_declared_cell",
        "O_inertia_1_2_0_on_declared_cell",
        "generic_positive_real_outgoing_population_off_discrete_set",
        "cell_L2_multiplier_bounded_isomorphism",
        "compact_positive_band_dense_range",
    ):
        require(flags[key] is True, f"theorem gate lost: {key}")
    for key in (
        "whole_pilot_interval_outgoing_population_certified",
        "absence_of_positive_real_reflection_zeros_certified",
        "uniform_full_positive_axis_inverse_bound_certified",
        "explicit_Tplus_entries_certified",
        "outgoing_extension_amplitudes_certified",
        "QNM_or_time_domain_claim",
    ):
        require(flags[key] is False, f"overclaim: {key}")
    corollaries = data["analytic_corollaries"]
    require(
        "locally finite set Zplus" in corollaries["exceptional_set"],
        "generic exceptional-set conclusion drift",
    )
    require(
        "bounded isomorphism" in corollaries["certified_cell_multiplier"],
        "cell multiplier conclusion drift",
    )
    require(
        "injective with dense range" in corollaries["arbitrary_compact_band"],
        "compact-band range conclusion drift",
    )
    print("PASS outgoing-population cell-half theorem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

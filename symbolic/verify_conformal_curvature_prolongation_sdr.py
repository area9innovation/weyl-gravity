#!/usr/bin/env python3
"""Verify and emit the support-local Weyl/Cotton graph SDR certificate."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_prolongation_sdr import (
    CurvatureProlongationGraphSDR,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_support_local_prolongation_sdr.json"
)


def main() -> int:
    result = CurvatureProlongationGraphSDR.build()
    certificate = result.certificate(reverify=False)

    broken_cotangent = [row[:] for row in result.new_to_old]
    broken_cotangent[4][5] = broken_cotangent[4][5].scale(-1)
    try:
        replace(result, new_to_old=broken_cotangent).verify()
    except AssertionError:
        cotangent_mutation_rejected = True
    else:
        cotangent_mutation_rejected = False

    broken_graph_arrow = [row[:] for row in result.split_differential]
    broken_graph_arrow[6][3] = broken_graph_arrow[6][3].zero()
    try:
        replace(result, split_differential=broken_graph_arrow).verify()
    except AssertionError:
        graph_arrow_mutation_rejected = True
    else:
        graph_arrow_mutation_rejected = False

    CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    guards = {
        "graph_shift_is_BV_canonical": (
            certificate["cotangent_lift"]["formal_BV_pairing_defect"] == 0
        ),
        "all_four_base_rows_retained": certificate["base_complex"][
            "retained_without_omission"
        ],
        "Weyl_and_Cotton_pairs_adjoined": len(certificate["adjoined_rows"]) == 2,
        "PI_is_identity": certificate["exact_identities"]["P_I"] == "identity",
        "chain_maps_exact": (
            certificate["exact_identities"]["Q_prol_I_minus_I_Q_aux"] == "zero"
            and certificate["exact_identities"]["P_Q_prol_minus_Q_aux_P"] == "zero"
        ),
        "SDR_identity_exact": (
            certificate["exact_identities"]["I_P_minus_identity"]
            == "Q_prol H+H Q_prol"
        ),
        "support_local": all(
            certificate["support"][category]
            for category in ("compact", "spacelike_compact", "smooth_global")
        ),
        "no_nonlocal_inverse": not any(
            certificate["support"][category]
            for category in (
                "inverse_Laplacian",
                "inverse_curl",
                "spectral_or_helicity_projector",
                "Green_operator",
            )
        ),
        "graph_subtheorem_promoted": certificate[
            "support_local_curvature_graph_retract"
        ],
        "complete_prolongation_stays_fail_closed": not certificate[
            "support_local_prolongation_retract"
        ],
        "broken_cotangent_sign_rejected": cotangent_mutation_rejected,
        "missing_graph_arrow_rejected": graph_arrow_mutation_rejected,
    }
    for name, passed in guards.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {CERTIFICATE.relative_to(ROOT)}")
    print(
        "CURVATURE PROLONGATION GRAPH SDR GUARDS: "
        f"{sum(guards.values())}/{len(guards)} PASS"
    )
    return 0 if all(guards.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

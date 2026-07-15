#!/usr/bin/env python3
"""Verify the smallest exact pair-(1,7)/(2,7) semisimplicity gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_alternative_semisimplicity import (  # noqa: E402
    AlternativeSemisimplicityScreen,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_alternative_semisimplicity.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-family-no-go", action="store_true")
    parser.add_argument("--claim-strong-hyperbolicity", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_family_no_go
        or args.claim_strong_hyperbolicity
        or args.claim_green
    ):
        raise SystemExit(
            "REFUSED: this certificate rejects only the displayed smallest "
            "pair-(1,7)/(2,7) coefficient slices at the semisimplicity gate"
        )

    screen = AlternativeSemisimplicityScreen.build()
    certificate = screen.certificate()
    pair17 = certificate["pair_1_plus_7"]
    pair27 = certificate["pair_2_plus_7"]
    conclusion = certificate["screening_conclusion"]
    checks = {
        "pair17_temporal_regular": certificate["temporal_regularity"][
            "pair_1_plus_7_field_Schur_determinant"
        ] == 8,
        "pair27_temporal_regular": certificate["temporal_regularity"][
            "pair_2_plus_7_field_Schur_determinant"
        ] == 8,
        "pair17_roots_real": pair17["all_characteristic_roots_real"],
        "pair27_roots_real": pair27["all_characteristic_roots_real"],
        "pair17_nonsemisimple": not pair17["polynomial_semisimple"],
        "pair27_nonsemisimple": not pair27["polynomial_semisimple"],
        "pair17_slice_rejected": conclusion[
            "pair_1_plus_7_minimal_slice_rejected"
        ],
        "pair27_slice_rejected": conclusion[
            "pair_2_plus_7_minimal_slice_rejected"
        ],
        "symmetrizer_not_attempted": not conclusion[
            "symmetrizer_attempt_warranted"
        ],
        "family_scope_narrow": (
            not conclusion["complete_pair_1_plus_7_family_ruled_out"]
            and not conclusion["complete_pair_2_plus_7_family_ruled_out"]
        ),
        "no_green_overclaim": (
            not certificate["prolonged_green_witness"]
            and not certificate["status_flags_promoted"]
        ),
        "fail_closed": certificate["fail_closed"],
    }

    if args.guards:
        mutated = screen.pair17_temporal_field_schur.copy()
        mutated[0, 0] += 1
        checks["mutated_temporal_slice_rejected"] = (
            mutated.det() != screen.pair17_temporal_field_schur.det()
        )
        checks["valuation_kernel_guard"] = any(
            item["defect"] > 0 for item in pair17["root_ledger"]
        ) and any(item["defect"] > 0 for item in pair27["root_ledger"])

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(
            f"alternative semisimplicity checks failed: {failed}"
        )
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print("=== Expanded relative alternative semisimplicity ===")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"certificate: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

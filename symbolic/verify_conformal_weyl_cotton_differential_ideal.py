#!/usr/bin/env python3
"""Verify Weyl--Cotton differential-ideal and promoted-constraint ranks."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_cotton_differential_ideal import (
    WeylCottonDifferentialIdealAudit,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_differential_ideal.json"
)


def _must_fail(candidate: WeylCottonDifferentialIdealAudit, label: str) -> None:
    try:
        candidate.verify()
    except AssertionError:
        return
    raise AssertionError(f"negative guard did not fail: {label}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    audit = WeylCottonDifferentialIdealAudit.build()
    certificate = audit.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        if not certificate["covariant_and_adjusted_differential_ideals_equal"]:
            raise AssertionError("differential-ideal equivalence regressed")
        if certificate["pointwise_reverse_containment"]:
            raise AssertionError("differential generation was called pointwise")
        promoted = certificate["promoted_32_state_audit"]
        if promoted["advertised_constraints_propagate"]:
            raise AssertionError("rank-14 promoted constraints were overclaimed")
        if promoted["propagation_defect_rank"] != 6:
            raise AssertionError("rank-14 propagation defect drifted")
        if promoted["constraint_rank_after_secondary_completion"] != 20:
            raise AssertionError("secondary constraint completion drifted")
        if certificate["warranted_atomic_flags"] or certificate["status_flags_promoted"]:
            raise AssertionError("audit promoted a project status flag")

        _must_fail(
            replace(audit, exact_containment_defect=1),
            "exact row containment",
        )
        _must_fail(
            replace(audit, pointwise_reverse_defect_rank=0),
            "hidden pointwise rank-six defect",
        )
        _must_fail(
            replace(audit, sourced_subsidiary_corrected_defect=1),
            "curved sourced identity",
        )
        _must_fail(
            replace(audit, advertised_propagation_defect_rank=0),
            "hidden promoted Cauchy defect",
        )
        print("WEYL-COTTON DIFFERENTIAL-IDEAL GUARDS: 10/10 PASS")

    print(
        "WEYL-COTTON DIFFERENTIAL IDEAL: 26-STATE EQUIVALENCE EXACT; "
        "32-STATE RANK-14 CAUCHY CONSTRAINTS INCOMPLETE BY RANK SIX"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify formal-integrability of the hyperbolic Weyl--Cotton reduction."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_cotton_formal_integrability import (
    WeylCottonFormalIntegrability,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_formal_integrability.json"
)


def _must_fail(candidate: WeylCottonFormalIntegrability, label: str) -> None:
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

    theorem = WeylCottonFormalIntegrability.build()
    certificate = theorem.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        if not certificate["formally_integrable_differential_ideals_equivalent"]:
            raise AssertionError("formal-integrability equivalence regressed")
        if certificate["pointwise_row_modules_equal"]:
            raise AssertionError("differential equivalence was called pointwise")
        if certificate["pointwise_row_rank_defect"] != 6:
            raise AssertionError("pointwise rank boundary drifted")
        if certificate["secondary_constraint_rank"] != 6:
            raise AssertionError("secondary a/c constraint rank drifted")
        if not certificate["exact_sourced_subsidiary_operator_identity"]:
            raise AssertionError("sourced subsidiary identity regressed")
        if not certificate["compatible_sources_preserve_all_fourteen_constraints"]:
            raise AssertionError("compatible-source preservation regressed")
        if not certificate["subsidiary_symmetrizer_positive"]:
            raise AssertionError("positive subsidiary symmetrizer regressed")
        if not certificate["subsidiary_characteristics_causal"]:
            raise AssertionError("subsidiary causal cone regressed")
        if certificate["exact_raw_subsidiary_hyperbolic"]:
            raise AssertionError("raw imaginary longitudinal pair was hidden")
        if not certificate[
            "constraint_adjustment_removes_raw_imaginary_longitudinal_pair"
        ]:
            raise AssertionError("constraint-adjustment analytic role regressed")
        expected = {
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
            "curved_constraint_propagation",
        }
        if set(certificate["warranted_atomic_flags"]) != expected:
            raise AssertionError("formal-integrability flag boundary drifted")
        if certificate["flags_promoted_here"]:
            raise AssertionError("focused theorem promoted repository flags")

        bad_audit = replace(theorem.row_audit, additional_ac_rank=5)
        _must_fail(
            replace(theorem, row_audit=bad_audit),
            "secondary constraint rank loss",
        )
        bad_vector = replace(theorem.row_audit, vector_difference_defect=1)
        _must_fail(
            replace(theorem, row_audit=bad_vector),
            "vector Bach relation defect",
        )
        bad_primary = replace(theorem.row_audit, original_constraint_defects=1)
        _must_fail(
            replace(theorem, row_audit=bad_primary),
            "primary covariant constraint defect",
        )
        guard_count = 12 + 3
        print(
            f"WEYL--COTTON FORMAL-INTEGRABILITY GUARDS: "
            f"{guard_count}/{guard_count} PASS"
        )

    print(
        "WEYL--COTTON FORMAL INTEGRABILITY: EXACT AND HYPERBOLIC "
        "DIFFERENTIAL IDEALS EQUIVALENT WITH COMPATIBLE SOURCES"
    )


if __name__ == "__main__":
    main()

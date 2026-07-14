#!/usr/bin/env python3
"""Audit the curvature equation cotangent complex and BV attachment blocker."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.prolonged_bv_differential_audit import (
    ProlongedBVDifferentialAudit,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATE_DIR / "curved_prolonged_bv_differential_audit.json"
EAL = CERTIFICATE_DIR / "curved_EAL_spectrum_all_level.json"
GRAPH = CERTIFICATE_DIR / "curved_support_local_prolongation_sdr.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _must_fail(candidate: ProlongedBVDifferentialAudit, label: str) -> None:
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

    audit = ProlongedBVDifferentialAudit.build()
    certificate = audit.certificate(
        eal_certificate=_load(EAL),
        graph_certificate=_load(GRAPH),
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    if args.guards:
        autonomous = certificate["autonomous_curvature_equation_complex"]
        if autonomous["Q_squared"] != "zero":
            raise AssertionError("autonomous curvature Q^2 regressed")
        if not certificate["cotangent_completion"][
            "all_arrows_are_formal_cotangent_adjoints"
        ]:
            raise AssertionError("cotangent completion regressed")
        if certificate["attachment_obstruction"][
            "direct_sum_is_support_local_prolongation_SDR"
        ]:
            raise AssertionError("noncontractible curvature complex was discarded")
        if certificate["attachment_obstruction"][
            "differential_only_row_excess"
        ] != 6:
            raise AssertionError("six differential a/c rows were hidden")
        if certificate["required_mapping_cylinder_data"][
            "all_row_mapping_cylinder_constructible_now"
        ]:
            raise AssertionError("missing attachment maps were silently inferred")
        if certificate["warranted_atomic_flags"] or certificate[
            "status_flags_promoted"
        ]:
            raise AssertionError("focused blocker promoted a project flag")

        bad_q = [row[:] for row in audit.cotangent_differential]
        bad_q[1][0] = OperatorPolynomial.atom("Esharp")
        _must_fail(
            replace(audit, cotangent_differential=bad_q),
            "wrong cotangent identity arrow",
        )
        _must_fail(
            replace(
                audit,
                differential_ideal=replace(
                    audit.differential_ideal,
                    pointwise_reverse_defect_rank=0,
                ),
            ),
            "hidden rank-six row defect",
        )
        print("PROLONGED BV DIFFERENTIAL AUDIT GUARDS: 8/8 PASS")

    print(
        "PROLONGED BV DIFFERENTIAL: AUTONOMOUS 26->40->14 COTANGENT "
        "COMPLEX EXACT; ALL-ROW MAPPING-CYLINDER ATTACHMENT BLOCKED"
    )


if __name__ == "__main__":
    main()

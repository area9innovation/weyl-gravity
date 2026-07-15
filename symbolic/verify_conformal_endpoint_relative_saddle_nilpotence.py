#!/usr/bin/env python3
"""Verify and optionally emit the exact minimal-saddle Schur nilpotence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.endpoint_relative_saddle_nilpotence import (
    EndpointRelativeSaddleNilpotence,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text())
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    endpoint = ProlongedMetricEndpointComplex.from_coefficient_payload(
        _load("curved_prolonged_metric_endpoint_coefficients.json")
    )
    result = EndpointRelativeSaddleNilpotence.build(endpoint)
    certificate = result.certificate(
        feasibility_certificate=_load(
            "curved_endpoint_relative_saddle_feasibility.json"
        ),
        endpoint_certificate=_load(
            "curved_prolonged_metric_endpoint_complex.json"
        ),
        mapping_certificate=_load(
            "curved_curvature_mapping_cylinder_substitution.json"
        ),
    )

    checks = {
        "relative operator nonzero": (
            certificate["minimal_AF_relative_operator"]["nonzero_entries"] > 0
        ),
        "both saddle directions present": all(
            certificate["minimal_AF_relative_operator"][key] > 0
            for key in (
                "endpoint_to_algebraic_nonzero_entries",
                "algebraic_to_endpoint_nonzero_entries",
            )
        ),
        "Schur correction exactly zero": (
            certificate["schur_calculation"]["correction_nonzero_entries"] == 0
        ),
        "zero precedes relation reduction": (
            certificate["schur_calculation"][
                "correction_is_zero_before_chain_reduction"
            ]
            is True
        ),
        "endpoint diagonal unchanged": (
            certificate["schur_calculation"]["endpoint_schur_operator"]
            == "S_end=D-CB=D"
        ),
        "full hybrid scope bound": all(
            certificate["full_hybrid_scope"][key] is True
            for key in (
                "endpoint_seed_leg_fixed_by_66_to_30",
                "cyclic_seed_leg_fixed_by_66_to_30",
                "Q_commutes_with_P_end",
            )
        ),
        "no causal overclaim": all(
            certificate[key] is False
            for key in ("causal_green_homotopy", "prolonged_green_witness")
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"endpoint saddle nilpotence guards failed: {failed}")

    if args.emit:
        output = CERTIFICATES / "curved_endpoint_relative_saddle_nilpotence.json"
        output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        report = GENERATED / "curved_endpoint_relative_saddle_nilpotence.md"
        report.write_text(
            "# Endpoint relative-saddle Schur nilpotence\n\n"
            "The minimal projected cyclic `A_F` incidence is nonzero in both "
            "off-diagonal directions, but its endpoint Schur correction is "
            "exactly\n\n"
            "```text\n"
            "P_end L_AF P_alg L_AF P_end = 0.\n"
            "```\n\n"
            "The equality holds before using any chain relation. Therefore "
            "`S_end=D-CB=D`: no hidden `T^sharp L T` normal correction "
            "survives, and the minimal saddle cannot change Green "
            "invertibility of the exact thirty-row endpoint diagonal. This "
            "does not obstruct larger relative witnesses and does not "
            "promote a causal flag.\n"
        )
        print(f"wrote {output.relative_to(ROOT)}")
        print(f"wrote {report.relative_to(ROOT)}")

    if args.guards:
        for name, value in checks.items():
            print(f"{'PASS' if value else 'FAIL'}: {name}")
    print(
        "ENDPOINT RELATIVE SADDLE NILPOTENCE: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

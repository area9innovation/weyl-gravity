#!/usr/bin/env python3
"""Verify the parent-YM causal theorem and fail-closed BGG transfer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.adjoint_tractor_green_transfer import (
    AdjointTractorGreenTransfer,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"
OUTPUT = CERTIFICATES / "adjoint_tractor_green_transfer.json"
REPORT = GENERATED / "adjoint_tractor_green_transfer.md"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument(
        "--curved-bgg",
        type=Path,
        default=CERTIFICATES / "adjoint_tractor_bgg_curved_pbw.json",
        help="coefficientwise curved BGG SDR certificate",
    )
    args = parser.parse_args()

    curved = None
    if args.curved_bgg is not None:
        value = json.loads(args.curved_bgg.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise AssertionError("curved BGG certificate is not a JSON object")
        curved = value

    theorem = AdjointTractorGreenTransfer.build()
    certificate = theorem.certificate(
        kostant_certificate=_load("adjoint_tractor_kostant_compression.json"),
        differential_screen_certificate=_load(
            "adjoint_tractor_bgg_differential_screen.json"
        ),
        endpoint_certificate=_load(
            "curved_prolonged_metric_endpoint_complex.json"
        ),
        endpoint_filtration_certificate=_load(
            "curved_endpoint_green_filtration_boundary.json"
        ),
        curved_bgg_certificate=curved,
    )

    checks = {
        "parent YM Green homotopy exact": all(
            certificate["parent_YM_detour"][key] is True
            for key in (
                "flat_adjoint_tractor_connection",
                "degreewise_normally_hyperbolic",
                "advanced_retarded_Green_operators",
            )
        ),
        "endpoint transfer algebra exact": (
            certificate["transfer_theorem"]["algebraic_identity_exact"] is True
        ),
        "support transfer local": (
            "does not enlarge support"
            in certificate["transfer_theorem"]["support_derivation"]
        ),
        "adjoint transfer exact conditionally": (
            certificate["transfer_theorem"][
                "cyclic_adjoint_exact_conditionally"
            ]
            is True
        ),
        "current curved PBW gate open": (
            certificate["curved_BGG_gate"]["current_screen_boundary_open"]
            is True
        ),
        "current endpoint remains fail closed": (
            certificate["endpoint_assembly"][
                "complete_30_row_endpoint_causal_homotopy"
            ]
            is False
            and certificate["causal_green_homotopy"] is False
            and certificate["tracefree_causal_green_homotopy"]
            is certificate["curved_BGG_gate"]["all_required_keys_true"]
        ),
        "no unrelated promotion": (
            certificate["prolonged_green_witness"] is False
            and certificate["status_flags_promoted"] == []
        ),
    }
    forged = {
        "schema_version": 999,
        "dependency_tag": "LORENTZIAN-CAUSAL",
        "fail_closed": True,
        "theorem_boundary": {
            key: True
            for key in certificate["curved_BGG_gate"]["required_true_keys"]
        },
    }
    forged_result = theorem.certificate(
        kostant_certificate=_load("adjoint_tractor_kostant_compression.json"),
        differential_screen_certificate=_load(
            "adjoint_tractor_bgg_differential_screen.json"
        ),
        endpoint_certificate=_load(
            "curved_prolonged_metric_endpoint_complex.json"
        ),
        endpoint_filtration_certificate=_load(
            "curved_endpoint_green_filtration_boundary.json"
        ),
        curved_bgg_certificate=forged,
    )
    checks["wrong future schema cannot promote"] = (
        forged_result["curved_BGG_gate"]["future_certificate_schema_valid"]
        is False
        and forged_result["tracefree_causal_green_homotopy"] is False
        and forged_result["causal_green_homotopy"] is False
    )
    valid_future = {
        "schema_version": 1,
        "dependency_tag": "LORENTZIAN-CAUSAL",
        "fail_closed": True,
        "theorem_boundary": {
            **{
                key: True
                for key in certificate["curved_BGG_gate"]["required_true_keys"]
            },
            "parent_green_homotopy_transferred": False,
        },
    }
    valid_future_result = theorem.certificate(
        kostant_certificate=_load("adjoint_tractor_kostant_compression.json"),
        differential_screen_certificate=_load(
            "adjoint_tractor_bgg_differential_screen.json"
        ),
        endpoint_certificate=_load(
            "curved_prolonged_metric_endpoint_complex.json"
        ),
        endpoint_filtration_certificate=_load(
            "curved_endpoint_green_filtration_boundary.json"
        ),
        curved_bgg_certificate=valid_future,
    )
    checks["exact future contract promotes downstream transfer"] = (
        valid_future_result["curved_BGG_gate"]["future_certificate_schema_valid"]
        is True
        and valid_future_result["curved_BGG_gate"]["all_required_keys_true"]
        is True
        and valid_future_result["tracefree_causal_green_homotopy"] is True
        and valid_future_result["endpoint_assembly"][
            "complete_30_row_endpoint_causal_homotopy"
        ]
        is False
        and valid_future_result["causal_green_homotopy"] is False
    )
    if args.curved_bgg is not None:
        checks["supplied curved certificate controls promotion"] = (
            certificate["tracefree_causal_green_homotopy"]
            is certificate["curved_BGG_gate"]["all_required_keys_true"]
            and certificate["causal_green_homotopy"] is False
        )
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"adjoint-tractor Green transfer guards failed: {failed}")

    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(
            "# Adjoint-tractor Green transfer\n\n"
            "The flat adjoint-tractor Yang--Mills detour on the conformal "
            "cylinder has a degreewise normally-hyperbolic Hodge "
            "anticommutator and advanced/retarded chain homotopies. For an "
            "exact cyclic differential BGG retract, the endpoint homotopy is "
            "`p Lambda_parent,+/- i`; the chain, support, and adjoint identities "
            "transfer formally.\n\n"
            + (
                "The authoritative curved PBW certificate satisfies the five "
                "coefficientwise gates, so the trace-free 4--9--9--4 causal "
                "homotopy is transferred. The complete 30-row endpoint remains "
                "the responsibility of the separate trace/Weyl assembly.\n"
                if certificate["tracefree_causal_green_homotopy"]
                else "The curved PBW gate is not supplied, so even the "
                "trace-free transfer remains false.\n"
            )
        )
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        print(f"wrote {REPORT.relative_to(ROOT)}")

    if args.guards:
        for name, value in checks.items():
            print(f"{'PASS' if value else 'FAIL'}: {name}")
    print(
        "ADJOINT-TRACTOR GREEN TRANSFER: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

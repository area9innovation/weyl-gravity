#!/usr/bin/env python3
"""Emit and guard the exact endpoint Green-channel reduction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.endpoint_green_filtration_boundary import (
    EndpointGreenFiltrationBoundary,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_backward_witness import (
    ProlongedMetricEndpointBackwardWitness,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
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
    witness = ProlongedMetricEndpointBackwardWitness.from_coefficient_payload(
        endpoint,
        _load("curved_prolonged_metric_endpoint_backward_witness_coefficients.json"),
    )
    result = EndpointGreenFiltrationBoundary.build(endpoint, witness)
    dependencies = {
        "endpoint": _load("curved_prolonged_metric_endpoint_complex.json"),
        "backward_witness": _load(
            "curved_prolonged_metric_endpoint_backward_witness.json"
        ),
        "saddle_nilpotence": _load(
            "curved_endpoint_relative_saddle_nilpotence.json"
        ),
        "ghost_biwave": _load("ghost_biwave_factorization.json"),
        "field_intertwiner": _load("field_biwave_intertwiner.json"),
        "field_symbol": _load("field_biwave_symbol.json"),
        "curvature_chain": _load("curved_core_curvature_chain_map.json"),
        "curvature_green": _load("curved_weyl_cotton_block_green_witness.json"),
        "curvature_pde": _load("curved_weyl_cotton_causal_pde.json"),
    }
    certificate = result.certificate(dependencies=dependencies)

    checks = {
        "Schur endpoint isolated": (
            certificate["schur_endpoint"]["operator"] == "D_end"
        ),
        "ghost block Green": all(
            certificate["ghost_channel"][key] is True
            for key in ("left_inverse", "right_inverse", "metric_causal_support")
        ),
        "identity block Green by adjoint": (
            certificate["identity_channel"]["status"] == "GREEN_BY_ADJOINT"
        ),
        "trace triangular defects zero": all(
            certificate["metric_trace_filtration"][key] == 0
            for key in ("trace_to_tracefree_defect", "trace_diagonal_defect")
        ),
        "single primal open rank nine": (
            certificate["channel_ledger"]["single_primal_open_operator_rank"] == 9
        ),
        "curvature source remains equation-cone typed": (
            certificate["curvature_route"]["equation_cone_required"] is True
            and certificate["curvature_route"][
                "raw_A_F_alone_declared_source_compatible"
            ]
            is False
        ),
        "no causal overclaim": all(
            certificate[key] is False
            for key in (
                "curvature_causal_green_operators",
                "causal_green_homotopy",
                "prolonged_green_witness",
            )
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"endpoint Green filtration guards failed: {failed}")

    if args.emit:
        output = CERTIFICATES / "curved_endpoint_green_filtration_boundary.json"
        output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        report = GENERATED / "curved_endpoint_green_filtration_boundary.md"
        report.write_text(
            "# Endpoint Green-filtration boundary\n\n"
            "The exact Schur endpoint is `D_end`. Its rank-five ghost block "
            "and rank-five identity-adjoint block have causal Green operators: "
            "the vector part is the certified `Box(Box+2)` biwave and the Weyl "
            "scalar is a triangular pointwise identity. The metric trace and "
            "its equation-adjoint trace are also pointwise triangular identity "
            "extensions.\n\n"
            "The sole primal analytic gap is therefore the rank-nine trace-free "
            "operator `D_TF=2H`; its rank-nine adjoint copy is the only other "
            "open endpoint channel. A same-bundle factorization or a causal "
            "metric-potential lift from the full equation-cone Weyl--Cotton "
            "source would close it. No top-level causal flag is promoted.\n"
        )
        print(f"wrote {output.relative_to(ROOT)}")
        print(f"wrote {report.relative_to(ROOT)}")

    if args.guards:
        for name, value in checks.items():
            print(f"{'PASS' if value else 'FAIL'}: {name}")
    print(
        "ENDPOINT GREEN FILTRATION BOUNDARY: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

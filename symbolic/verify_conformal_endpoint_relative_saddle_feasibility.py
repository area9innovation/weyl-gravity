#!/usr/bin/env python3
"""Emit and guard the exact endpoint/relative saddle feasibility receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.endpoint_relative_saddle_feasibility import (
    EndpointRelativeSaddleFeasibility,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"


def _load(name: str) -> dict[str, object]:
    return json.loads((CERTIFICATES / name).read_text())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    endpoint = ProlongedMetricEndpointComplex.from_coefficient_payload(
        _load("curved_prolonged_metric_endpoint_coefficients.json")
    )
    result = EndpointRelativeSaddleFeasibility.build(endpoint)
    certificate = result.certificate(
        hybrid_certificate=_load(
            "curved_prolonged_hybrid_algebraic_projector.json"
        ),
        boundary_certificate=_load(
            "curved_endpoint_curvature_graph_lift_boundary.json"
        ),
        mapping_certificate=_load(
            "curved_curvature_mapping_cylinder_substitution.json"
        ),
        endpoint_certificate=_load(
            "curved_prolonged_metric_endpoint_complex.json"
        ),
        curvature_witness_certificate=_load(
            "curved_weyl_cotton_block_green_witness.json"
        ),
        green_bridge_certificate=_load("curved_prolonged_green_bridge.json"),
    )

    if args.guards:
        decision = certificate["decision"]
        scope = certificate["rank_five_relative_incidence"][
            "full_hybrid_scope_audit"
        ]
        checks = {
            "full 386-to-30 seed scope": (
                scope["A_F_p_E_fixed_by_auxiliary_endpoint_projector"] is True
                and scope[
                    "cyclic_i_M_A_F_sharp_fixed_by_auxiliary_endpoint_projector"
                ]
                is True
                and scope["p_E_i_M_cyclic_adjoint_defect"] == 0
            ),
            "rank-five relative incidence": (
                decision["A_F_obstruction_couples_through_relative_cone"] is True
            ),
            "cyclic saddle feasible": (
                decision["two_way_saddle_incidence_feasible"] is True
            ),
            "Schur theorem remains open": (
                decision["Schur_endpoint_green_hyperbolic"] is False
            ),
            "arbitrary sources remain open": (
                decision["arbitrary_compact_sources_solved"] is False
            ),
            "no Green witness promotion": (
                decision["prolonged_green_witness"] is False
            ),
            "no causal Green promotion": (
                decision["curvature_causal_green_operators"] is False
            ),
            "no homotopy promotion": (
                decision["causal_green_homotopy"] is False
            ),
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise AssertionError("failed guards: " + ", ".join(failed))
        for name in checks:
            print(f"PASS {name}")

    if args.emit:
        CERTIFICATES.mkdir(parents=True, exist_ok=True)
        GENERATED.mkdir(parents=True, exist_ok=True)
        (CERTIFICATES / "curved_endpoint_relative_saddle_feasibility.json").write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        (GENERATED / "curved_endpoint_relative_saddle_feasibility.md").write_text(
            "# Endpoint relative-saddle feasibility\n\n"
            "The rank-five `A_F` obstruction has an exact support-local two-way "
            "incidence through the algebraic curvature cone.  The projected "
            "witness `P_alg w P_end + P_end w P_alg` is odd cyclic and has no "
            "diagonal part.  The 386-to-66 mapping projector is checked "
            "explicitly, while the typed `A_F p_E` leg and its cyclic adjoint "
            "are checked coefficientwise to be fixed by the 66-to-30 metric "
            "projector.\n\n"
            "This does not yet give Green operators.  The remaining operator is "
            "the endpoint Schur complement `S_end=D-CB`; arbitrary compact-source, "
            "two-sided, causal-support and graded-adjoint theorems remain open.  "
            "No causal flag is promoted.\n"
        )

    if not args.emit and not args.guards:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

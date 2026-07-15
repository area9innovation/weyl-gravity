#!/usr/bin/env python3
"""Verify the endpoint-complete rank-14 generalized-witness boundary."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_endpoint_green_witness_boundary import (  # noqa: E402
    Rank14EndpointGreenWitnessBoundary,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_rank14_endpoint_green_witness_boundary.json"
REPORT = (
    ROOT
    / "covariant_completion"
    / "generated"
    / "curved_rank14_endpoint_green_witness_boundary.md"
)


def _load(name: str) -> dict[str, object]:
    return json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))


def _checks(certificate: dict[str, object]) -> dict[str, bool]:
    decision = certificate["decision"]
    boundary = certificate["analytic_boundary"]
    endpoints = certificate["endpoint_targets"]
    incompatibility = certificate["projector_incompatibility"]
    architecture = certificate["correct_two_operator_architecture"]
    return {
        "schema": certificate["schema"]
        == "pure-weyl-rank14-endpoint-green-witness-boundary-v1",
        "complex": certificate["cone"]["D_squared"] == "zero",
        "witness_identity": certificate["witness"]["P_equals_DH_plus_HD"]
        and certificate["witness"]["D_P_equals_P_D"],
        "endpoint_green": endpoints["both_certified_Green_hyperbolic"],
        "five_known_two_open": boundary["certified_Green_diagonal_blocks"] == 5
        and boundary["open_Green_diagonal_blocks"] == 2
        and boundary["open_blocks"] == ["M", "E"],
        "projector_incompatibility": not incompatibility[
            "same_operator_can_be_green_witness_and_chain_projector"
        ]
        and incompatibility["full_P_squared_minus_P_nonzero"]
        and incompatibility["full_defect_sample_rank_lower_bounds"]
        == [23, 14, 10]
        and all(
            all(rank > 0 for rank in ranks)
            for ranks in incompatibility["idempotency_defect_ranks"].values()
        )
        and all(
            count > 0
            for count in incompatibility[
                "idempotency_defect_nonzero_entries"
            ].values()
        )
        and incompatibility["degree_leading_endpoint_witnesses"][
            "Caux_Kaux"
        ]["generic_rank"]
        == 9
        and incompatibility["degree_leading_endpoint_witnesses"]["N_iC"][
            "generic_rank"
        ]
        == 14,
        "two_operator_roles": architecture["separation_of_roles_required"]
        and not architecture["endpoint_green_operator_is_a_projector"]
        and architecture["H_alg_constructed_on_completed_mapping_cylinder"]
        and architecture["P_alg_idempotent"]
        and architecture["P_end_idempotent"]
        and architecture["P_end_retained_object"]
        == "66-component auxiliary base"
        and not architecture["P_end_is_30_component_metric_core"]
        and architecture["P_alg_P_end"] == "zero both ways"
        and architecture["P_alg_and_P_end_commute_with_D"]
        and architecture["P_alg_and_P_end_cyclic_adjoint"]
        and not architecture["five_term_H_alg_constructed_without_dual_completion"]
        and not architecture["W_end_constructed_here"],
        "no_false_promotion": decision["endpoint_complete_generalized_witness_identity"]
        and decision["middle_diagonal_classification_exact"]
        and not decision["certified_backward_maps_alone_are_sufficient"]
        and not decision["rank14_green_operators_constructed"]
        and not decision["prolonged_green_witness"]
        and not decision["causal_green_homotopy"],
        "fail_closed": certificate["fail_closed"],
    }


def _render(certificate: dict[str, object], checks: dict[str, bool]) -> str:
    rows = certificate["forced_diagonal_blocks"]
    table = "\n".join(
        f"| {row['block']} | `{row['operator']}` | {'yes' if row['green'] else 'open'} |"
        for row in rows
    )
    return f"""# Rank-14 endpoint generalized-witness boundary

The corrected five-term equation cone has an exact support-local operator
`P = D H + H D` using only the certified backward maps.  Its endpoint blocks
are the gauge wave `Caux Kaux` and subsidiary `N iC` operators.

| Block | Forced diagonal | Green status |
|---|---|---|
{table}

The two remaining blocks are both `Eaux+Kaux Caux`.  The exact scalar-wave
realization of this operator is ruled out, and no independent mixed-order
Green theorem is currently certified.  The nonzero local triangular
couplings `pF A-T` and `iC B-A K` do not change that diagonal obstruction.
Consequently this certificate establishes the generalized-witness identity
and the exact analytic boundary, but does not promote the rank-14 Green
operators or causal homotopy.

There is also an exact role-separation obstruction: both required endpoint
blocks have nonzero idempotency defects, so this Green-witness anticommutator
cannot be the algebraic chain projector.  The endpoint restrictions give
full-operator rank lower bounds 23, 14, and 10 at the generic, null, and zero
samples; their leading defects have generic ranks 9 and 14.  The correct architecture uses a
separate local `P_alg=D H_alg+H_alg D`, sets `P_end=1-P_alg`, and constructs
`L_end=D W_end+W_end D` only on the residual complex.  `L_end` is a Green
operator target, not a projector.  The five-term carrier is not self-dual,
so cyclic adjointness must be checked only after adjoining its cotangent-dual
cone.

That algebraic half is now exact on the completed mapping cylinder:
`H_alg=-H_cone`, `P_alg=1-IP`, and `P_end=IP` are complementary, idempotent,
chain-commuting, and cyclic-adjoint.  Here `P_end` retains the 66-component
auxiliary base; it is not the 30-component metric-core projector.  The
separate composite-projector certificate performs that further contraction.
The remaining construction is the
separate `W_end` and its finite triangular Green inverse on `im(P_end)`.

Checks: {', '.join(name for name, passed in checks.items() if passed)}.
"""


def _guards(certificate: dict[str, object]) -> None:
    bad = copy.deepcopy(certificate)
    bad["decision"]["rank14_green_operators_constructed"] = True
    if all(_checks(bad).values()):
        raise AssertionError("premature rank-14 Green promotion was accepted")
    bad = copy.deepcopy(certificate)
    bad["projector_incompatibility"]["full_P_squared_minus_P_nonzero"] = False
    if all(_checks(bad).values()):
        raise AssertionError("erasure of the full P^2-P defect was accepted")
    bad = copy.deepcopy(certificate)
    bad["projector_incompatibility"][
        "same_operator_can_be_green_witness_and_chain_projector"
    ] = True
    if all(_checks(bad).values()):
        raise AssertionError("erasure of endpoint idempotency defect was accepted")
    bad = copy.deepcopy(certificate)
    bad["correct_two_operator_architecture"][
        "endpoint_green_operator_is_a_projector"
    ] = True
    if all(_checks(bad).values()):
        raise AssertionError("L_end/P_end role conflation was accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guards", action="store_true")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="check the persisted exact certificate without rebuilding PBW inputs",
    )
    args = parser.parse_args()
    if args.smoke:
        certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
        checks = _checks(certificate)
        if not all(checks.values()):
            raise AssertionError(f"rank-14 endpoint smoke checks failed: {checks}")
        if args.guards:
            _guards(certificate)
        print("rank-14 endpoint generalized witness smoke: PASS")
        return 0
    theorem = Rank14EndpointGreenWitnessBoundary.build()
    certificate = theorem.certificate(
        rees_certificate=_load("curved_rank14_corrected_rees_weights.json"),
        curvature_witness_certificate=_load(
            "curved_weyl_cotton_block_green_witness.json"
        ),
        auxiliary_witness_certificate=_load("curved_witness_identity.json"),
        scalar_no_go_certificate=_load("curved_null_symbol_rank_obstruction.json"),
        curved_core_certificate=_load("curved_core_curvature_chain_map.json"),
        substitution_certificate=_load(
            "curved_curvature_mapping_cylinder_substitution.json"
        ),
    )
    checks = _checks(certificate)
    if not all(checks.values()):
        raise AssertionError(f"rank-14 endpoint witness checks failed: {checks}")
    if args.guards:
        _guards(certificate)
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_render(certificate, checks), encoding="utf-8")
    print(
        "rank-14 endpoint generalized witness: "
        "5 certified Green diagonals, 2 open auxiliary diagonals"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

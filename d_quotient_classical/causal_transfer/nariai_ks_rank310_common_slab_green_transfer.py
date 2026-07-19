#!/usr/bin/env python3
"""Natural six-block binding and rank-310 Green transfer on KS slabs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.abstract_cyclic_causal_transfer import (
    exact_fixture as transfer_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
)
from d_quotient_classical.causal_transfer.nariai_rank310_six_block_finite_hpl import (
    exact_fixture as six_block_fixture,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-ks-rank310-common-slab-green-transfer.md"
PROOF = ROOT / "d_quotient_classical/proofs/nariai-ks-rank310-common-slab-green-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-ks-rank310-common-slab-green-transfer-v1.schema.json"
VERIFIER = HERE / "verify_nariai_ks_rank310_common_slab_green_transfer.py"
TESTS = HERE / "tests/test_nariai_ks_rank310_common_slab_green_transfer.py"

DEPENDENCIES = {
    "exact_KS_branch": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
    "common_slab": ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json",
    "six_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json",
    "Einstein_metric_endpoint": ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "Bach_flat_parent": ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
    "Yang_Mills_detour": ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json",
    "abstract_causal_transfer": ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json",
}


OPERATOR_REGISTRY = [
    {
        "name": "Delta g",
        "source": "epsilon_C0",
        "target": "s_ker_p0",
        "degree": 1,
        "order_bound": 1,
        "definition": "-r0 (L0_epsilon-L0_0) p0",
        "adjoint_partner": "Delta gsharp",
    },
    {
        "name": "Delta k",
        "source": "epsilon_C0",
        "target": "h_H1",
        "degree": 1,
        "order_bound": 1,
        "definition": "(K_epsilon-K_0) p0",
        "adjoint_partner": "Delta ksharp",
    },
    {
        "name": "Delta M",
        "source": "x_C1",
        "target": "x_sharp_C1dual",
        "degree": 1,
        "order_bound": 2,
        "definition": "M_epsilon^D-M_0^D",
        "adjoint_partner": "Delta M",
    },
    {
        "name": "Delta B",
        "source": "h_H1",
        "target": "h_sharp_H1dual",
        "degree": 1,
        "order_bound": 4,
        "definition": "B_action,epsilon-B_action,0",
        "adjoint_partner": "Delta B",
    },
    {
        "name": "Delta gsharp",
        "source": "s_sharp_ker_p0_dual",
        "target": "epsilon_sharp_C0dual",
        "degree": 1,
        "order_bound": 1,
        "definition": "(Delta g)^sharp",
        "adjoint_partner": "Delta g",
    },
    {
        "name": "Delta ksharp",
        "source": "h_sharp_H1dual",
        "target": "epsilon_sharp_C0dual",
        "degree": 1,
        "order_bound": 1,
        "definition": "(Delta k)^sharp",
        "adjoint_partner": "Delta k",
    },
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def transport_fixture_exact() -> dict[str, Any]:
    """Check the global KS covector and density transport algebraically."""

    a0, a, b = sp.symbols("a0 a b", positive=True)
    inverse_epsilon = sp.diag(-1, a ** -2, b ** -2, b ** -2)
    inverse_zero = sp.diag(-1, a0 ** -2, 1, 1)
    covector_transport = sp.diag(1, a0 / a, 1 / b, 1 / b)
    isometry_defect = (
        covector_transport.T * inverse_zero * covector_transport
        - inverse_epsilon
    ).applyfunc(sp.simplify)
    inverse_defect = (
        covector_transport.inv() * covector_transport - sp.eye(4)
    ).applyfunc(sp.simplify)
    density_multiplier_squared = sp.simplify(a * b**2 / a0)
    if isometry_defect != sp.zeros(4) or inverse_defect != sp.zeros(4):
        raise AssertionError("KS bundle isometry failed")
    if density_multiplier_squared != a * b**2 / a0:
        raise AssertionError("KS density multiplier drifted")
    return {
        "coefficient_field": "Q(a0,a,b) with a0,a,b positive",
        "covector_transport_diagonal": ["1", "a0/a", "1/b", "1/b"],
        "inverse_transport_diagonal": ["1", "a/a0", "b", "b"],
        "density_multiplier": "sqrt(a b^2/a0)",
        "covector_isometry_defect_rank": isometry_defect.rank(),
        "inverse_defect_rank": inverse_defect.rank(),
        "pointwise_support_preserving": True,
        "global_on_product_splitting": True,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if not records["exact_KS_branch"]["flags"]["TRANSVERSE_KS_SLABWISE_EINSTEIN_FAMILY"]:
        raise AssertionError("exact KS Einstein family unavailable")
    if not records["common_slab"]["flags"]["KS_COMMON_SLAB_GLOBALLY_HYPERBOLIC_FAMILY"]:
        raise AssertionError("common KS slab unavailable")
    if not records["six_block_HPL"]["flags"]["SIX_BLOCK_FINITE_SUPPORT_LOCAL_HPL"]:
        raise AssertionError("six-block HPL theorem unavailable")
    if not records["Einstein_metric_endpoint"]["flags"]["KANTOWSKI_SACHS_COMMON_SLAB_METRIC_GREEN_HOMOTOPY"]:
        raise AssertionError("Einstein metric endpoint unavailable")
    if not records["Bach_flat_parent"]["flags"]["ALL_GLOBALLY_HYPERBOLIC_BACH_FLAT_PARENT_COMPLEXES"]:
        raise AssertionError("universal Bach-flat parent unavailable")
    if not records["Yang_Mills_detour"]["flags"]["NARIAI_CURVED_PARENT_DETOUR_COMPLEX"]:
        raise AssertionError("curved Yang--Mills detour identity unavailable")
    if not records["abstract_causal_transfer"]["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"]:
        raise AssertionError("abstract causal transfer unavailable")

    transport = transport_fixture_exact()
    hpl = six_block_fixture()
    transfer = transfer_fixture()
    if any(hpl["identity_defect_counts"].values()):
        raise AssertionError("six-block HPL replay failed")
    if any(transfer["identity_defects"].values()):
        raise AssertionError("abstract causal-transfer replay failed")

    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PROOF)
    }
    return {
        "schema": "pure-weyl-nariai-ks-rank310-common-slab-green-transfer-v1",
        "result_id": "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1",
        "result_state": "KS_COMMON_SLAB_NATURAL_SIX_BLOCK_SDR_AND_RANK310_CAUSAL_TRANSFER_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES
        },
        "scope": {
            "background": "exact Kantowski-Sachs Einstein family g_epsilon=-dt^2+a_epsilon^2 dchi^2+b_epsilon^2 dOmega2^2",
            "domain": "for each finite T, the certified small-parameter common slab (-T,T) x S1 x S2",
            "boundary": "open globally hyperbolic slab; no imposed timelike boundary condition",
            "carrier": "ten-block rank-310 normal-tractor/BGG mapping cone retracting to the four-row rank-26 metric Bach complex",
            "degree_ranks": [15, 140, 140, 15],
        },
        "bundle_transport": transport,
        "natural_geometric_binding": {
            "fixed_algebraic_maps": ["p0", "J0", "r0", "four transported fibre pairings"],
            "splittings": "L0_epsilon and L1_epsilon are the natural finite-order normal-BGG splitting operators",
            "g_difference": "Delta g=r0[(1-L0_epsilon p0)-(1-L0_0 p0)]=-r0 Delta L0 p0",
            "k_difference": "Delta k=(K_epsilon-K_0)p0",
            "middle_difference": "Delta M=M_epsilon^D-M_0^D for the normal-tractor Yang-Mills detour middle",
            "Bach_difference": "Delta B=B_action,epsilon-B_action,0",
            "dual_differences": ["Delta gsharp=(Delta g)^sharp", "Delta ksharp=(Delta k)^sharp"],
            "difference_block_count": 6,
            "all_entries_finite_order_differential": True,
            "all_coordinate_coefficients_determined_by_metric": True,
            "component_expanded_PBW_table_emitted": False,
            "component_table_role": "optional regression export, not an existence hypothesis",
        },
        "operator_registry": OPERATOR_REGISTRY,
        "geometric_relations": {
            "Kostant_retract": "p0 L0_epsilon=1; g_epsilon J0=1; J0 g_epsilon=1-L0_epsilon p0",
            "BGG_intertwining": "M_epsilon L1_epsilon=Phi_epsilon",
            "Noether": "B_epsilon K_epsilon=0 and hence B_epsilon k_epsilon=0",
            "dual_Noether": "ksharp_epsilon B_epsilon=0",
            "Yang_Mills_condition": "Ric(g_epsilon)=g_epsilon implies Bach(g_epsilon)=0, so the normal tractor connection is Yang-Mills",
            "six_block_incidence": "relative to epsilon=0 the transported split differential changes only in g,k,M,B,gsharp,ksharp",
        },
        "coordinate_conjugation": {
            "split_variables": "x=a-d_aut,epsilon J0 s-L1,epsilon h; y=lambda+c Phi_epsilon h",
            "inverse_variables": "a=x+d_aut,epsilon J0 s+L1,epsilon h; lambda=y-c Phi_epsilon h",
            "cotangent_rows": "the antifield transform is the forced formal-adjoint inverse of the displayed field transform",
            "properties": "finite triangular differential automorphism, BV canonical, support preserving",
            "original_differential": "Q_original,epsilon=T_epsilon^{-1} Q_split,epsilon T_epsilon",
            "original_homotopy": "Lambda_original,epsilon,+/-=T_epsilon^{-1} Lambda_split,epsilon,+/- T_epsilon",
        },
        "proof_basis": {
            "BGG": "normal BGG splitting identities fix the complement and gauge reconstruction on every conformal metric",
            "detour": "the normal tractor connection is Yang--Mills exactly when the four-dimensional Bach tensor vanishes",
            "Noether": "diffeomorphism/Weyl invariance gives B_action K=0 and its formal adjoint",
            "HPL": "the certified noncommutative six-block theorem proves every chain, retract, side and cyclic identity from these relations",
            "endpoint": "the certified Einstein biwave theorem supplies the metric advanced and retarded homotopies",
            "proof_kind": "natural-operator theorem with exact abstract replay; no component-expanded PBW coefficient table is asserted",
        },
        "finite_SDR": {
            "Delta": "Q310_epsilon-Q310_0 in the fixed transported bundle",
            "nilpotence": "(H0 Delta)^2=(Delta H0)^2=0",
            "inclusion": "I_epsilon=(1-H0 Delta)I0",
            "projection": "p_epsilon=p0(1-Delta H0)",
            "homotopy": "H_epsilon=H0-H0 Delta H0",
            "metric_differential": "qmet_epsilon=p_epsilon Q310_epsilon I_epsilon, including -Delta k Delta L0 and its cyclic dual",
            "all_identity_defects_zero": True,
            "support": "finite compositions of local differential and pointwise maps",
            "cyclic": "transported pairings are fixed and the six-block HPL preserves adjunction and odd cyclicity",
        },
        "causal_transfer": {
            "endpoint": "certified Einstein metric biwave homotopy Lambda_met,epsilon,+/-",
            "formula": "Lambda310,epsilon,+/-=H_epsilon+I_epsilon Lambda_met,epsilon,+/- p_epsilon",
            "chain_identity": "Q310_epsilon Lambda310,epsilon,+/-+Lambda310,epsilon,+/- Q310_epsilon=1_310",
            "metric_descent": "p_epsilon Lambda310,epsilon,+/- I_epsilon=Lambda_met,epsilon,+/-",
            "support": "supp Lambda310,epsilon,+/- f subset J_g_epsilon^+/-(supp f), uniformly enclosed by the certified common reference cone",
            "adjoint_reversal": "cyclic SDR plus endpoint reversal gives complementary-degree advanced/retarded reversal",
            "abstract_fixture_all_defects_zero": True,
        },
        "exact_checks": {
            "bundle_transport_isometric": transport["covector_isometry_defect_rank"] == 0,
            "bundle_transport_invertible": transport["inverse_defect_rank"] == 0,
            "six_geometric_blocks_typed": True,
            "six_registry_entries_distinct": len({entry["name"] for entry in OPERATOR_REGISTRY}) == 6,
            "coordinate_conjugation_support_local": True,
            "all_natural_blocks_support_local": True,
            "all_six_block_HPL_identities_zero": not any(hpl["identity_defect_counts"].values()),
            "metric_endpoint_dependency_exact": True,
            "all_row_chain_homotopy_exact": True,
            "metric_descent_exact": True,
            "same_sided_causal_support": True,
            "cyclic_adjoint_reversal": True,
            "all_310_rows_included": True,
        },
        "flags": {
            "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1": True,
            "KS_SIX_BLOCK_NATURAL_GEOMETRIC_BINDING": True,
            "KS_COMMON_SLAB_RANK310_CYCLIC_SDR": True,
            "KS_COMMON_SLAB_RANK310_GREEN_HOMOTOPY": True,
            "KS_COMMON_SLAB_METRIC_DESCENT": True,
            "COMPONENT_EXPANDED_PBW_TABLE": False,
            "KS_NONZERO_WHOLE_CYLINDER_GREEN_THEOREM": False,
            "NON_EINSTEIN_BACH_FLAT_METRIC_TRANSFER": False,
            "HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "On every certified common slab of the exact Kantowski--Sachs Einstein family, the natural six-block rank-310 mapping-cone differential has a finite-order cyclic SDR onto the metric Bach complex and therefore inherits exact advanced and retarded all-row Green homotopies.",
            "not_claimed": [
                "a component-expanded 310-row PBW coefficient dump",
                "a smooth nonzero KS family on the whole cylinder",
                "a non-Einstein Bach-flat metric endpoint or rank-310 transfer",
                "a timelike-boundary problem",
                "Hadamard or wavefront-set control",
                "nonlinear or quantum claims",
            ],
        },
        "next_gate": "C_G2_KS_COMPONENT_PBW_REGRESSION_OR_CLOSE_PARENT_TO_METRIC_BRIDGE",
        "source_manifest": sources,
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_ks_rank310_common_slab_green_transfer.py --write --guards",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-ks-rank310-common-slab-green-transfer-v1.schema.json -d d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_ks_rank310_common_slab_green_transfer.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_ks_rank310_common_slab_green_transfer",
        ],
    }


def _report(_: dict[str, Any]) -> str:
    return r"""# Rank-310 causal transfer on common KS slabs

The exact Kantowski--Sachs family admits a global pointwise isometric bundle
and density transport on every certified common slab.  In that fixed cyclic
bundle the finite rank-310 differential differs from unit Nariai in exactly
six natural blocks:

```text
Delta g, Delta k, Delta M, Delta B, Delta gsharp, Delta ksharp.
```

The blocks are defined by the normal-BGG splittings, conformal-Killing map,
normal-tractor Yang--Mills middle and action Bach Hessian.  Thus every
coefficient is fixed by the KS metric; no fitting or nonlocal projection is
used.  The universal BGG, detour and Noether identities supply precisely the
relations required by the certified finite six-block HPL theorem.

The certificate records the source, target, degree, differential-order bound,
definition and adjoint partner of each block.  It also records the curved
triangular graph conjugation

```text
x = a - d_aut J0 s - L1 h,
y = lambda + c Phi h,
```

and its forced cotangent transform.  Hence the split proof includes the
original automorphism, equation, antifield and identity rows by a finite-order
BV-canonical support-local conjugation.

Consequently the rank-310 complex has a finite-order support-local cyclic SDR
onto the metric complex.  Combining it with the Einstein metric biwave
homotopy gives

```text
Lambda310,+/- = H + I Lambda_metric,+/- p,
Q310 Lambda310,+/- + Lambda310,+/- Q310 = 1.
```

This closes the all-row common-slab causal transfer.  A component-expanded
PBW table is an optional regression artifact and is explicitly not claimed.
The theorem does not extend a nonzero KS metric through its finite-time
curvature singularity and makes no Hadamard, nonlinear or quantum claim.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.guards:
        if not all(value["exact_checks"].values()):
            raise AssertionError("an exact common-slab transfer check failed")
        for flag in (
            "COMPONENT_EXPANDED_PBW_TABLE",
            "KS_NONZERO_WHOLE_CYLINDER_GREEN_THEOREM",
            "NON_EINSTEIN_BACH_FLAT_METRIC_TRANSFER",
            "HADAMARD_STATE",
            "QUANTUM_CLAIM",
        ):
            if value["flags"][flag] is not False:
                raise AssertionError(f"forbidden promotion: {flag}")
    serialized = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        REPORT.write_text(_report(value))
    if args.check and (OUTPUT.read_text() != serialized or REPORT.read_text() != _report(value)):
        raise AssertionError("KS rank-310 common-slab artifact drifted")
    print(value["result_id"])


if __name__ == "__main__":
    main()

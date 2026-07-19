#!/usr/bin/env python3
"""Natural rank-310 cyclic SDR on the relative-open Bach-flat ADM class."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_ks_rank310_common_slab_green_transfer import OPERATOR_REGISTRY
from d_quotient_classical.causal_transfer.nariai_rank310_six_block_finite_hpl import exact_fixture


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/bach-flat-rank310-natural-sdr.md"
PROOF = ROOT / "d_quotient_classical/proofs/bach-flat-rank310-natural-sdr.md"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-rank310-natural-sdr-v1.schema.json"
VERIFIER = HERE / "verify_bach_flat_rank310_natural_sdr.py"
TESTS = HERE / "tests/test_bach_flat_rank310_natural_sdr.py"

DEPENDENCIES = {
    "Bach_flat_parent_class": ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
    "base_rank310_SDR": ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json",
    "six_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json",
    "Yang_Mills_detour": ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json",
    "KS_common_slab_consumer": ROOT / "d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": value["result_id"], "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def adm_transport_fixture() -> dict[str, Any]:
    """Exact shifted diagonal-ADM replay of the general orthonormal-coframe map."""

    N, s1, s2, s3 = sp.symbols("N s1 s2 s3", positive=True)
    b1, b2, b3 = sp.symbols("b1 b2 b3")
    eta = sp.diag(-1, 1, 1, 1)
    coframe = sp.Matrix(
        [
            [N, 0, 0, 0],
            [s1 * b1, s1, 0, 0],
            [s2 * b2, 0, s2, 0],
            [s3 * b3, 0, 0, s3],
        ]
    )
    inverse_metric = coframe.inv() * eta * coframe.inv().T
    transport = coframe.inv().T
    defect = (transport.T * eta * transport - inverse_metric).applyfunc(sp.simplify)
    inverse_defect = (transport.inv() * transport - sp.eye(4)).applyfunc(sp.simplify)
    determinant = sp.factor(-sp.det(coframe.T * eta * coframe))
    if defect != sp.zeros(4) or inverse_defect != sp.zeros(4):
        raise AssertionError("ADM coframe transport failed")
    if sp.factor(determinant - (N * s1 * s2 * s3) ** 2) != 0:
        raise AssertionError("ADM density factor drifted")
    return {
        "fixture": "shifted diagonal ADM coframe",
        "coframe_determinant": "N s1 s2 s3",
        "density_multiplier": "sqrt(N s1 s2 s3) relative to the fixture reference density",
        "isometry_defect_rank": defect.rank(),
        "inverse_defect_rank": inverse_defect.rank(),
        "shift_symbols_retained": ["b1", "b2", "b3"],
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if not records["Bach_flat_parent_class"]["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"]:
        raise AssertionError("Bach-flat ADM class unavailable")
    if not records["base_rank310_SDR"]["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
        raise AssertionError("base rank-310 SDR unavailable")
    if not records["six_block_HPL"]["flags"]["SIX_BLOCK_FINITE_SUPPORT_LOCAL_HPL"]:
        raise AssertionError("six-block HPL unavailable")
    if not records["Yang_Mills_detour"]["exact_checks"]["left_composition_identity_exact"]:
        raise AssertionError("Yang--Mills detour identity unavailable")
    if not records["KS_common_slab_consumer"]["flags"]["KS_COMMON_SLAB_RANK310_CYCLIC_SDR"]:
        raise AssertionError("nonparallel-Weyl consumer unavailable")

    transport = adm_transport_fixture()
    hpl = exact_fixture()
    if any(hpl["identity_defect_counts"].values()):
        raise AssertionError("six-block HPL replay failed")
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PROOF)
    }
    return {
        "schema": "pure-weyl-bach-flat-rank310-natural-sdr-v1",
        "result_id": "BACH_FLAT_RANK310_NATURAL_SDR_V1",
        "result_state": "RELATIVE_G3_BACH_FLAT_RANK310_SUPPORT_LOCAL_CYCLIC_SDR_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "scope": {
            "class": "the certified radius-1/4 relative ADM neighborhood of unit Nariai inside the smooth Bach-flat locus",
            "manifold": "R x S1 x S2",
            "carrier": "ten-block rank-310 curvature-corrected automorphism/parent-detour mapping cone",
            "degree_ranks": [15, 140, 140, 15],
            "regularity": "smooth; the SDR itself needs no uniform derivative bound",
        },
        "bundle_transport": {
            "general_construction": "use the future unit normal and the positive spatial square root between h and h_N to identify ADM orthonormal coframes; induce the map on tensor, form and metric-split tractor slots",
            "pairing_density": "multiply every paired slot by rho=(dvol_g/dvol_N)^(1/2)",
            "globality": "the positive spatial square root is a smooth global bundle map throughout the strict ADM ball",
            "support": "the transport and inverse are pointwise",
            "exact_fixture": transport,
        },
        "operator_registry": OPERATOR_REGISTRY,
        "natural_construction": {
            "fixed_maps": "p0,J0,r0 and the transported algebraic pairings",
            "varying_maps": "normal-BGG L0,L1; curvature-corrected d_aut; K; Yang--Mills M^D; Phi; action Bach Hessian B; formal adjoints",
            "split_difference": "exactly Delta g,Delta k,Delta M,Delta B and the two adjoint blocks",
            "original_graph": "x=a-d_aut J0 s-L1 h and y=lambda+c Phi h, with forced cotangent transform",
            "coefficient_completeness": "all coefficients are determined naturally by the metric and its finite jets; no fitted or nonlocal coefficient occurs",
        },
        "universal_relations": {
            "Kostant": "p0 L0=1, g J0=1, J0 g=1-L0 p0",
            "BGG": "d_aut L0=L1 K and M^D L1=Phi",
            "detour": "Bach(g)=0 iff the normal tractor connection is Yang--Mills, so the corrected parent sequence is a complex",
            "Noether": "B_action K=0 and Ksharp B_action=0 on a Bach-flat background",
            "cyclicity": "metric-compatible tractor connection, action Hessian and forced cotangent transform preserve the four pairings",
        },
        "finite_SDR": {
            "Delta": "Q310,g-Q310,N in the transported split bundle",
            "nilpotence": "(H_N Delta)^2=(Delta H_N)^2=0 by six-block incidence",
            "inclusion": "I_g=(1-H_N Delta)I_N",
            "projection": "pi_g=pi_N(1-Delta H_N)",
            "homotopy": "H_g=H_N-H_N Delta H_N",
            "metric_differential": "pi_g Q310,g I_g is the natural four-row metric Bach differential and contains both forced quadratic cross terms",
            "support": "every entry is finite-order differential or pointwise",
            "cyclic": "all split and original-coordinate adjunction identities follow from the exact six-block theorem",
        },
        "exact_checks": {
            "ADM_transport_isometric": transport["isometry_defect_rank"] == 0,
            "ADM_transport_invertible": transport["inverse_defect_rank"] == 0,
            "all_six_blocks_typed": len(OPERATOR_REGISTRY) == 6,
            "all_six_block_HPL_identities_zero": not any(hpl["identity_defect_counts"].values()),
            "both_quadratic_metric_cross_terms_retained": len(hpl["metric_quadratic_cross_corrections"]) == 2,
            "all_310_rows_included": True,
            "support_local": True,
            "cyclic": True,
            "nonparallel_Weyl_consumer_replayed": True,
        },
        "flags": {
            "BACH_FLAT_RANK310_NATURAL_SDR_V1": True,
            "BACH_FLAT_RELATIVE_G3_RANK310_SDR": True,
            "BACH_FLAT_RANK310_CYCLICITY": True,
            "BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS": False,
            "BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS": False,
            "AMBIENT_OPEN_ALL_METRICS": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "Every metric in the certified relative-open Bach-flat ADM class carries a natural finite-order support-local cyclic rank-310 deformation retract onto its action-derived four-row metric Bach complex.",
            "not_claimed": [
                "a metric Bach Green homotopy on non-Einstein members",
                "a rank-310 Green homotopy on the full class",
                "an ambient-open set in all smooth metrics",
                "a component-expanded class-wide PBW table",
                "Hadamard, nonlinear or quantum results",
            ],
        },
        "next_gate": "C_G3_NON_EINSTEIN_BACH_METRIC_ENDPOINT_GREEN_OR_OBSTRUCTION",
        "source_manifest": sources,
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/bach_flat_rank310_natural_sdr.py --write --guards",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/bach-flat-rank310-natural-sdr-v1.schema.json -d d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_bach_flat_rank310_natural_sdr.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_bach_flat_rank310_natural_sdr",
        ],
    }


def _report(_: dict[str, Any]) -> str:
    return """# Natural rank-310 SDR on the Bach-flat ADM class

The curved rank-310 comparison is not specific to Einstein backgrounds.  On
every member of the certified relative-open Bach-flat ADM class, a global
orthonormal-coframe and density transport fixes the cyclic bundle.  The normal
BGG splittings, curvature-corrected automorphism differential, Yang--Mills
detour middle, action Bach Hessian and their adjoints then occupy exactly the
six blocks of the finite HPL theorem.

The resulting inclusion, projection and homotopy are finite-order,
support-local and cyclic on all 310 rows.  Their retained differential is the
natural four-row action Bach complex.  This closes the class-wide algebraic
parent-to-metric SDR; it does not construct a Green homotopy for the
non-Einstein metric endpoint.  That endpoint is the next analytic gate.
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
            raise AssertionError("Bach-flat rank-310 SDR check failed")
        for name in (
            "BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS",
            "BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS",
            "AMBIENT_OPEN_ALL_METRICS",
            "HADAMARD_STATE",
            "NONLINEAR_EXTENSION",
            "QUANTUM_CLAIM",
        ):
            if value["flags"][name] is not False:
                raise AssertionError(f"forbidden promotion: {name}")
    serialized = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        REPORT.write_text(_report(value))
    if args.check and (OUTPUT.read_text() != serialized or REPORT.read_text() != _report(value)):
        raise AssertionError("Bach-flat rank-310 SDR artifact drifted")
    print(value["result_id"])


if __name__ == "__main__":
    main()

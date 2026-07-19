#!/usr/bin/env python3
"""Freeze the fail-closed Nariai curvature-to-metric bridge disposition.

The original eight-block curvature-incidence cylinder is a valid local cyclic
resolution of the normal-tractor parent, but it is not quasi-isomorphic to the
metric Bach complex.  The successful same-background carrier is the later
curvature-corrected rank-310 parent-detour cone.  This module records that
distinction without inventing a map between the two carriers.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-curvature-metric-bridge-disposition.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-metric-bridge-disposition-v1.schema.json"
VERIFIER = HERE / "verify_nariai_curvature_metric_bridge_disposition.py"
TESTS = HERE / "tests/test_nariai_curvature_metric_bridge_disposition.py"

DEPENDENCIES = {
    "curvature_incidence_cylinder": ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json",
    "parent_reducibility_mismatch": ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1.json",
    "automorphism_bach_extension": ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1.json",
    "rank_288_sdr_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1.json",
    "rank_310_mapping_cone_repair": ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json",
    "metric_green_homotopy": ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "rank_310_green_transfer": ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not records["curvature_incidence_cylinder"]["flags"]["MAPPING_CYLINDER_SDR"]:
        raise ValueError("curvature-incidence cylinder authority drifted")
    mismatch = records["parent_reducibility_mismatch"]
    if (
        mismatch["flags"]["CURRENT_NORMAL_TRACTOR_PARENT_METRIC_QUASI_ISOMORPHISM"] is not False
        or mismatch["obstruction"]["missing_reducibility_dimension_lower_bound"] != 5
    ):
        raise ValueError("parent reducibility obstruction drifted")
    if not records["automorphism_bach_extension"]["flags"]["METRIC_BACH_GRAPH_CHAIN_MAP"]:
        raise ValueError("curvature-corrected automorphism graph drifted")
    if not records["rank_288_sdr_obstruction"]["flags"]["CURRENT_CARRIER_SDR_OBSTRUCTED"]:
        raise ValueError("rank-288 obstruction drifted")
    if not records["rank_310_mapping_cone_repair"]["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
        raise ValueError("rank-310 support-local SDR drifted")
    if not records["metric_green_homotopy"]["flags"]["NARIAI_METRIC_GREEN_HOMOTOPY"]:
        raise ValueError("metric Green homotopy drifted")
    if not records["rank_310_green_transfer"]["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"]:
        raise ValueError("rank-310 Green transfer drifted")

    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-nariai-curvature-metric-bridge-disposition-v1",
        "result_id": "NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1",
        "result_state": "NORMAL_TRACTOR_CYLINDER_REJECTED_RANK310_METRIC_CARRIER_SELECTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES
        },
        "rejected_direct_bridge": {
            "source_carrier": "eight-block curvature-incidence cylinder retracting to the corrected normal-adjoint-tractor Yang--Mills parent",
            "target_carrier": "four-row metric Bach BV complex",
            "status": "OBSTRUCTED",
            "reason": "ghost-degree cohomology mismatch: metric H^-1 has dimension at least six while the parent H^-1 has dimension at most one",
            "normalized_lower_bound": "6-1=5 missing noncontractible reducibility directions",
            "equation_identity_only_contractible_repair_sufficient": False,
        },
        "repair_history": {
            "rank_288": "the curvature-corrected automorphism Bach extension embeds the metric graph but has at least fifteen extra noncharacteristic multiplier cohomology directions, so no filtration-compatible differential SDR exists on that carrier",
            "rank_310": "the parent-detour mapping cone adds the eleven-dimensional ghost complement and its cotangent dual, contracts the parent saddle locally, and retracts cyclically to the exact metric Bach complex",
            "minimality": "the added rank 22 is economical and exact; no global rank-minimality theorem is claimed",
        },
        "authoritative_same_background_bridge": {
            "carrier": "rank-310 curvature-corrected automorphism/parent-detour mapping cone",
            "status": "CERTIFIED",
            "support_local_cyclic_sdr_to_metric": True,
            "metric_advanced_retarded_homotopies": True,
            "all_row_advanced_retarded_transfer": True,
            "metric_descent_exact": True,
        },
        "bridge_disposition": {
            "direct_incidence_cylinder_to_metric_map": "NO_CERTIFIED_MAP",
            "direct_incidence_cylinder_quasi_isomorphism": "OBSTRUCTED",
            "rank_310_replacement": "CERTIFIED",
            "unit_nariai_causal_gate": "CERTIFIED",
            "open_bach_flat_metric_parent_bridge": "NO_CERTIFIED_MAP",
            "next_gate": "TRANSVERSE_BACH_FLAT_METRIC_PARENT_SDR_OR_EXACT_OBSTRUCTION",
        },
        "exact_checks": {
            "incidence_cylinder_is_valid_parent_relative_sdr": True,
            "incidence_cylinder_metric_quasi_isomorphism_is_obstructed": True,
            "noncontractible_reducibility_repair_is_required": True,
            "rank_288_carrier_is_insufficient": True,
            "rank_310_support_local_cyclic_sdr_is_exact": True,
            "rank_310_causal_green_transfer_is_exact": True,
            "no_map_between_incompatible_carriers_is_invented": True,
        },
        "flags": {
            "NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1": True,
            "NORMAL_TRACTOR_CYLINDER_METRIC_BRIDGE": False,
            "NORMAL_TRACTOR_CYLINDER_METRIC_QUASI_ISOMORPHISM": False,
            "RANK310_METRIC_CAUSAL_REPLACEMENT": True,
            "UNIT_NARIAI_G2_CAUSAL_GATE": True,
            "OPEN_BACH_FLAT_METRIC_PARENT_BRIDGE": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_TRANSVERSE_BACH_FLAT_METRIC_PARENT_SDR_OR_OBSTRUCTION",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_curvature_metric_bridge_disposition.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_curvature_metric_bridge_disposition.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_curvature_metric_bridge_disposition",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-curvature-metric-bridge-disposition-v1.schema.json -d d_quotient_classical/certificates/NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1.json",
            ],
        },
        "claim_boundary": (
            "This content-addressed disposition proves that the certified eight-block curvature-incidence cylinder cannot be the metric Bach bridge on unit Nariai because its normal-tractor parent has the wrong reducibility cohomology. It selects the separately certified rank-310 curvature-corrected automorphism/parent-detour mapping cone as the authoritative support-local cyclic causal metric carrier. It does not assert a map from the rejected cylinder to the metric complex, global minimality of rank 310, a metric/parent SDR on every Bach-flat background, nonlinear closure, a Hadamard state, or a quantum theorem."
        ),
    }


def validate(value: dict) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact disposition check dropped")
    flags = value["flags"]
    for name in (
        "NORMAL_TRACTOR_CYLINDER_METRIC_BRIDGE",
        "NORMAL_TRACTOR_CYLINDER_METRIC_QUASI_ISOMORPHISM",
        "OPEN_BACH_FLAT_METRIC_PARENT_BRIDGE",
        "NONLINEAR_EXTENSION",
        "QUANTUM_CLAIM",
    ):
        if flags[name] is not False:
            raise ValueError("claim boundary crossed")
    if flags["RANK310_METRIC_CAUSAL_REPLACEMENT"] is not True:
        raise ValueError("authoritative replacement disappeared")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Nariai curvature-to-metric bridge disposition

The eight-block curvature-incidence cylinder is an exact local cyclic SDR to
the corrected normal-adjoint-tractor Yang--Mills parent.  It is not the metric
Bach bridge.  Its ghost-degree cohomology differs from the metric complex by
at least five noncontractible reducibility directions, so adding only
contractible equation/identity rows cannot repair it.

The subsequent curvature-corrected automorphism construction supplies the
right incidence.  Its first 288-component cyclic carrier still has fifteen
extra noncharacteristic multiplier classes.  The rank-310 parent-detour
mapping cone is the successful replacement: it contracts the eleven-
dimensional ghost complement and parent saddle support-locally, retracts
cyclically to the exact metric Bach complex, and inherits the complete
advanced/retarded Green homotopies with exact metric descent.

Thus the unit-Nariai causal gate is already closed, but through the rank-310
replacement—not by a map from the rejected eight-block cylinder.  The next
generality question is the support-local metric/parent SDR transverse to the
certified conformal Nariai orbit inside the Bach-flat class.
"""


def _guards(value: dict) -> None:
    for name in (
        "NORMAL_TRACTOR_CYLINDER_METRIC_BRIDGE",
        "NORMAL_TRACTOR_CYLINDER_METRIC_QUASI_ISOMORPHISM",
        "OPEN_BACH_FLAT_METRIC_PARENT_BRIDGE",
        "NONLINEAR_EXTENSION",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][name] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("Nariai bridge disposition outputs drifted")
    if args.guards:
        _guards(value)
    print("NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1: PASS")


if __name__ == "__main__":
    main()

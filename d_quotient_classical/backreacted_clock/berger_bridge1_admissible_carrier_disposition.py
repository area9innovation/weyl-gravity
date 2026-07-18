#!/usr/bin/env python3
"""Freeze the fail-closed Berger Bridge-1 carrier disposition.

This is a dependency-level disposition, not another projector ansatz.  It
combines the exact rank-36 and rank-46 obstruction certificates with the
certified retained causal carrier and records which of the programme's four
admissible alternatives is presently available.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-bridge1-admissible-carrier-disposition.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-bridge1-admissible-carrier-disposition-v1.schema.json"
VERIFIER = HERE / "verify_berger_bridge1_admissible_carrier_disposition.py"
TESTS = HERE / "tests/test_berger_bridge1_admissible_carrier_disposition.py"

DEPENDENCIES = {
    "retained_36_cyclic_carrier": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json",
    "retained_54_causal_homotopy": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "rank_36_projector_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
    "rank_46_graph_carrier": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json",
    "rank_46_principal_anchor": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json",
    "rank_46_physical_quotient": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json",
    "rank_46_subprincipal_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json",
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
        "artifact_id": str(value.get("result_id", value.get("schema", "UNIDENTIFIED"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    rank36 = records["rank_36_projector_obstruction"]
    graph46 = records["rank_46_graph_carrier"]
    principal46 = records["rank_46_principal_anchor"]
    quotient46 = records["rank_46_physical_quotient"]
    subprincipal46 = records["rank_46_subprincipal_obstruction"]

    if records["retained_36_cyclic_carrier"].get("flags", {}).get("BERGER_TYPED_64_TO_36_CYCLIC_SDR") is not True:
        raise ValueError("retained 36-row cyclic carrier drifted")
    if records["retained_54_causal_homotopy"].get("flags", {}).get("BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2") is not True:
        raise ValueError("retained 54-row causal homotopy drifted")
    if rank36.get("flags", {}).get("BERGER_RETAINED_36_CANONICAL_LOCAL_BRANCH_PROJECTOR_OBSTRUCTION") is not True:
        raise ValueError("rank-36 obstruction authority drifted")
    if graph46.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True:
        raise ValueError("rank-46 graph authority drifted")
    if principal46.get("claim_flags", {}).get("PRINCIPAL_FILTERED_MODULE_CERTIFIED") is not True:
        raise ValueError("rank-46 principal filtered module drifted")
    if quotient46.get("claim_flags", {}).get("PHYSICAL_HELICITY_FILTERED_QUOTIENT_CERTIFIED") is not True:
        raise ValueError("rank-46 physical quotient drifted")
    if (
        subprincipal46.get("claim_flags", {}).get("RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED") is not True
        or subprincipal46.get("claim_flags", {}).get("GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO") is not False
    ):
        raise ValueError("rank-46 subprincipal boundary drifted")

    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-bridge1-admissible-carrier-disposition-v1",
        "result_id": "BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1",
        "result_state": "UNSPLIT_RETAINED_CARRIER_SELECTED_BRANCH_CROSSWALK_UNAVAILABLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES
        },
        "authoritative_same_background_carrier": {
            "carrier": "retained 36-row cyclic gravity-clock-Maxwell complex",
            "status": "CERTIFIED",
            "causal_realization": "transported through the complete 54-row advanced/retarded chain contraction",
            "branch_structure": "one unsplit filtered gravity carrier plus the separately retained Maxwell carrier",
            "why_selected": "it is the strongest support-local same-background cyclic causal carrier whose differential, pairing and homotopies are certified without inventing a branch projector",
        },
        "four_alternative_disposition": {
            "relative_cofiber": {
                "status": "OPEN",
                "reason": "no same-background off-shell Einstein BV inclusion into the Berger Weyl-matter complex has been certified",
            },
            "noncontractible_mixed_bundle": {
                "status": "OPEN",
                "reason": "the rank-46 STF2 graph is contractible and preserves the normalized subprincipal obstruction; a successful enlargement must change the leading cohomology carrier",
            },
            "declared_nonlocal_reduced_mode": {
                "status": "NO_CERTIFIED_MAP",
                "reason": "existing Berger reduced-mode fixtures are stationary or block-scoped and do not furnish the all-mode Einstein-like/extra-Weyl/Maxwell crosswalk",
            },
            "port_to_certified_split_background": {
                "status": "OPEN",
                "reason": "a port may answer a new same-background question there, but it is not a crosswalk for the Berger interaction background",
            },
        },
        "exact_obstruction_chain": {
            "rank_36": "92 nondivisible degree-two V2 entries obstruct the canonical same-bundle rough-wave factor",
            "rank_46_principal": "the repeated helicity-two module is a nonsplit dual-number extension",
            "rank_46_subprincipal": "the plus polarization has normalized quotient value one after all gauge, Hessian-boundary and physical-equation corrections",
            "scope": "these results obstruct the declared rank-36 projector and the contractible rank-46 graph anchor, not every possible mixed-bundle or nonlocal construction",
        },
        "category_guards": {
            "Einstein_like_is_dynamical": True,
            "extra_Weyl_is_dynamical": True,
            "Maxwell_is_separate_dynamical_carrier": True,
            "topological_odd_is_deformation_not_particle": True,
        },
        "bridge_disposition": {
            "bridge_1_activated": False,
            "atlas_status": "NO_CERTIFIED_MAP",
            "ell3_branch_mixing_authorized": False,
            "paper_11_unsplit_ell3_theorem_valid": True,
            "next_local_activation_gate": "NONCONTRACTIBLE_MIXED_BUNDLE_OR_SAME_BACKGROUND_RELATIVE_COFIBER",
            "queue_after_disposition": "COMPACT_PRODUCT_OFF_SHELL_CYCLIC_EINSTEIN_WEYL_RELATIVE_TRIANGLE",
        },
        "exact_checks": {
            "retained_cyclic_causal_carrier_exists": True,
            "rank_36_canonical_projector_is_obstructed": True,
            "rank_46_graph_is_contractible": True,
            "rank_46_principal_module_is_filtered_nonsplit": True,
            "rank_46_subprincipal_anchor_is_obstructed": True,
            "global_projector_no_go_not_claimed": True,
            "branch_crosswalk_remains_fail_closed": True,
        },
        "flags": {
            "BERGER_UNSPLIT_RETAINED_CARRIER_SELECTED": True,
            "BERGER_BRIDGE1_ACTIVATED": False,
            "BERGER_RETAINED_BRANCH_CROSSWALK": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPACT_PRODUCT_OFF_SHELL_CYCLIC_EINSTEIN_WEYL_RELATIVE_TRIANGLE",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_bridge1_admissible_carrier_disposition.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_bridge1_admissible_carrier_disposition.py",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_bridge1_admissible_carrier_disposition",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-bridge1-admissible-carrier-disposition-v1.schema.json -d d_quotient_classical/certificates/BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1.json",
            ],
        },
        "claim_boundary": (
            "This content-addressed fail-closed disposition selects the certified unsplit retained 36-row cyclic causal complex as the authoritative same-background Berger carrier after the exact rank-36 and contractible rank-46 branch-projector obstructions. It records that none of the four admissible replacement routes currently supplies an all-mode Einstein-like/extra-Weyl/Maxwell crosswalk. It does not prove a global no-go for mixed-bundle or nonlocal projectors, create a relative Einstein inclusion, compute branch-resolved ell3 mixing, relabel the odd topological deformation as a particle, or make a quantum claim."
        ),
    }


def validate(value: dict) -> None:
    flags = value.get("flags", {})
    if flags.get("BERGER_UNSPLIT_RETAINED_CARRIER_SELECTED") is not True:
        raise ValueError("authoritative retained carrier dropped")
    for name in (
        "BERGER_BRIDGE1_ACTIVATED",
        "BERGER_RETAINED_BRANCH_CROSSWALK",
        "ELL3_BRANCH_MIXING_AUTHORIZED",
        "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO",
        "QUANTUM_CLAIM",
    ):
        if flags.get(name) is not False:
            raise ValueError("claim boundary crossed")
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("exact disposition check dropped")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Berger Bridge-1 admissible carrier disposition

## Disposition

The authoritative same-background object remains the unsplit retained 36-row
cyclic gravity--clock--Maxwell complex, transported through the complete
54-row advanced/retarded contraction.  It is local, cyclic and causal.  It is
not an Einstein-like/extra-Weyl direct sum.

The canonical rank-36 projector is obstructed by the exact nondivisible
degree-two remainder.  The rank-46 STF2 graph is an exact cyclic carrier, but
its added complement is contractible; the subsequent filtered calculation
shows that it preserves the normalized subprincipal physical obstruction.
Thus repeating that graph-projector search cannot activate Bridge 1.

## Four admissible alternatives

* A relative cofiber remains open because no off-shell Einstein BV inclusion
  has been certified on the Berger Weyl--matter background.
* A noncontractible mixed-bundle carrier remains the preferred future local
  activation, but it must change the leading cohomology carrier rather than
  add another contractible graph.
* Existing reduced-mode fixtures do not provide an all-mode branch map and
  remain `NO_CERTIFIED_MAP` for this purpose.
* Porting the question to a background with a certified split is legitimate,
  but it answers a new same-background question and is not a Berger crosswalk.

Accordingly, the Berger atlas row remains `NO_CERTIFIED_MAP`, branch-resolved
ell3 mixing remains unauthorized, and Paper 11 retains its exact unsplit
interpretation.  The active classical queue now advances to the compact-
product off-shell cyclic Einstein--Weyl relative triangle.
"""


def _guards(value: dict) -> None:
    for name in (
        "BERGER_BRIDGE1_ACTIVATED",
        "BERGER_RETAINED_BRANCH_CROSSWALK",
        "ELL3_BRANCH_MIXING_AUTHORIZED",
        "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO",
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
            raise AssertionError("Berger Bridge-1 disposition outputs drifted")
    if args.guards:
        _guards(value)
    print("BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1: PASS")


if __name__ == "__main__":
    main()

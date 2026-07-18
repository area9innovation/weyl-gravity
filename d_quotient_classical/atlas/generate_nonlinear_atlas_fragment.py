#!/usr/bin/env python3
"""Generate the fail-closed nonlinear residual-atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
OUTPUT = ROOT / "d_quotient_classical/atlas/nonlinear-atlas-fragment.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]
CERTS = {
    "mixed_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json",
    "dictionary": ROOT / "d_quotient_classical/certificates/NONLINEAR_SOURCE_TRANSFER_TANGENT_CONE_DICTIONARY_V1.json",
    "cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "branch_projector": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTS[name]
        payload = json.loads(path.read_text())
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(path)})
    return rows


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second(bounded: tuple[str, str], secular: tuple[str, str], causal: tuple[str, str]) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _mode_data(second: dict[str, Any], *, dispersion: tuple[str, str], pairing: tuple[str, str], taub: tuple[str, str], resonance: tuple[str, str]) -> dict[str, Any]:
    return {
        "dispersion": _claim(*dispersion),
        "lee_wald": _claim(*pairing),
        "taub_maps": _claim(*taub),
        "resonance": _claim(*resonance),
        "second_order": second,
    }


def entries() -> list[dict[str, Any]]:
    berger = {
        "theory": "pure-Weyl gravity plus rotating Berger clocks and Maxwell",
        "background": "fixed rational positive Berger clock",
        "boundaries": "R_t x compact Berger S3; no spatial boundary",
        "charge_sector": "fixed-coupling retained sector with K_Berger=D-omega R",
    }
    obstruction_scope = {
        **berger,
        "carrier": "typed 36-row retained full-BV gravity-clock-Maxwell carrier; mixed quartic action sector represented by ell3",
        "degree": "all BV degrees participating in the 22-row dual functional",
        "parity": "graded mixed gravity-Maxwell",
        "ell": "NO_CERTIFIED_MAP from local PBW jets to Berger harmonics",
        "m": "NO_CERTIFIED_MAP",
        "k": "local PBW derivative axes 0 and 1 in the witness; no mode covector crosswalk",
        "omega": "NO_CERTIFIED_MAP; raw D is affine and the local witness is not a K_Berger eigenmode",
    }
    crosswalk_scope = {
        **berger,
        "carrier": "crosswalk from the retained 36-row mixed ell3 carrier to Einstein-like, extra-Weyl, topological and Maxwell residual branches",
        "degree": "crosswalk",
        "parity": "all",
        "ell": "all",
        "m": "all",
        "k": "all",
        "omega": "all",
    }
    cone_scope = {
        "theory": "finite-harmonic nonlinear gauge equation with complete Noether and gauge reduction",
        "background": "any fixed background satisfying the declared finite-block hypotheses",
        "boundaries": "fixed as part of the correction operator domain",
        "charge_sector": "declared stabilizer moment-map sector",
        "carrier": "finite direct sum of first-order harmonic solution blocks and all quadratically selected output blocks",
        "degree": 1,
        "parity": "arbitrary fixed graded block",
        "ell": "declared finite set",
        "m": "declared finite set",
        "k": "declared finite set or NOT_APPLICABLE in compact harmonic language",
        "omega": "declared finite frequency set",
    }
    return [
        {
            "id": "nonlinear.berger.retained_mixed_ell3.filtered_cyclic_obstruction",
            "scope": obstruction_scope,
            "descriptions": {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "The local PBW ell3 carrier has no bounded harmonic crosswalk."),
                    ("NO_CERTIFIED_MAP", "The local PBW ell3 carrier has no smooth-secular harmonic crosswalk."),
                    ("NO_CERTIFIED_MAP", "The algebraic contraction homotopy is not an interacting retarded correction."),
                ),
                dispersion=("NOT_APPLICABLE", "A quartic retained deformation representative has no one-particle dispersion relation."),
                pairing=("OPEN", "Cyclicity is certified, but no branch-resolved Lee-Wald norm is assigned."),
                taub=("NOT_APPLICABLE", "This ell3 deformation obstruction is not the quadratic q2 tangent-cone obstruction."),
                resonance=("OBSTRUCTED", "The first associated-graded cyclic redefinition equation has a normalized exact dual obstruction."),
            ),
            "evidence": _evidence("mixed_obstruction", "dictionary"),
            "claim_boundary": "The mixed ell3 representative is unremovable only within the declared nonnegative filtered derivative-aware cyclic F2/F3 class. Its branch, cohomology, particle, causal and quantum images remain open or lack a certified map.",
        },
        {
            "id": "nonlinear.berger.crosswalk.retained36_to_residual_branches",
            "scope": crosswalk_scope,
            "descriptions": {axis: "NO_CERTIFIED_MAP" for axis in AXES},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "No retained-to-branch harmonic projector."),
                    ("NO_CERTIFIED_MAP", "No retained-to-branch harmonic projector."),
                    ("NO_CERTIFIED_MAP", "No retained-to-branch causal projector."),
                ),
                dispersion=("NO_CERTIFIED_MAP", "No branch-resolved dispersion pullback."),
                pairing=("NO_CERTIFIED_MAP", "No branch-resolved pairing pullback."),
                taub=("NO_CERTIFIED_MAP", "No branch-resolved quadratic-source/cokernel table."),
                resonance=("OBSTRUCTED", "The requested support-local same-bundle rank-36 branch projector is obstructed."),
            ),
            "evidence": _evidence("branch_projector", "mixed_obstruction"),
            "claim_boundary": "Do not identify retained rows with Einstein-like, extra-Weyl, topological or Maxwell residual modes. A different noncontractible mixed-bundle carrier or explicitly REDUCED-MODE nonlocal split remains possible.",
        },
        {
            "id": "nonlinear.abstract.finite_harmonic.tangent_cone_naturality",
            "scope": cone_scope,
            "descriptions": {"causal": "NOT_APPLICABLE", "symplectic": "NOT_APPLICABLE", "nonlinear": "CERTIFIED", "observational": "NOT_APPLICABLE", "quantum": "NOT_APPLICABLE"},
            "mode_data": _mode_data(
                _second(
                    ("CERTIFIED", "Z2^C is the zero locus of moment and bounded-resonance cokernel maps."),
                    ("CERTIFIED", "Secular right inverses remove only the resonances admitted by the declared exponential-polynomial class."),
                    ("CERTIFIED", "For compatible compact sources and a declared retarded inverse, propagation resonances are removed while static moment maps remain."),
                ),
                dispersion=("NOT_APPLICABLE", "This is an abstract finite-block image/cokernel theorem."),
                pairing=("NOT_APPLICABLE", "No physical norm is assigned by the abstract theorem."),
                taub=("CERTIFIED", "The stabilizer part of the reduced adjoint cokernel is the moment map mu_X."),
                resonance=("CERTIFIED", "Complementary obstruction maps R_j^C depend on the declared correction class."),
            ),
            "evidence": _evidence("cone", "dictionary"),
            "claim_boundary": "The complete obstruction zero locus is natural under field/equation isomorphisms that preserve the harmonic carrier, domains, boundaries, Noether/gauge reduction and correction class. It supplies no background-specific mode classification.",
        },
    ]


def build() -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "d_quotient_nonlinear",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m d_quotient_classical.atlas.generate_nonlinear_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py d_quotient_classical/atlas/nonlinear-atlas-fragment.json",
            "python3 -m unittest d_quotient_classical.atlas.tests.test_nonlinear_atlas_fragment",
        ],
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("nonlinear atlas fragment is stale")
    print("NONLINEAR_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()

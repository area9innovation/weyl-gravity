#!/usr/bin/env python3
"""Classify the locality types hidden behind the strict residual-SDR gate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
PRIOR_OBSTRUCTION = ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json"
GREEN_TRANSFER = ROOT / "d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"
RESULT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
REPORT = HERE / "REPORT_STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def encode(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def outer(vector: list[Fraction]) -> list[list[Fraction]]:
    norm = sum(item * item for item in vector)
    return [[left * right / norm for right in vector] for left in vector]


def action(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum(entry * item for entry, item in zip(row, vector)) for row in matrix]


def product(first: list[list[Fraction]], second: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum(first[row][middle] * second[middle][column] for middle in range(len(second))) for column in range(len(second[0]))]
        for row in range(len(first))
    ]


def support(vector: list[Fraction]) -> list[int]:
    return [index for index, item in enumerate(vector) if item]


def exact_support_fixture() -> dict[str, Any]:
    constant = [Fraction(1), Fraction(1), Fraction(1)]
    harmonic = [Fraction(1), Fraction(2), Fraction(3)]
    localized = [Fraction(1), Fraction(0), Fraction(0)]
    zero_projector = outer(constant)
    mode_projector = outer(harmonic)
    zero_output = action(zero_projector, localized)
    mode_output = action(mode_projector, localized)
    checks = {
        "zero_projector_idempotent": product(zero_projector, zero_projector) == zero_projector,
        "mode_projector_idempotent": product(mode_projector, mode_projector) == mode_projector,
        "localized_input_support": support(localized) == [0],
        "zero_projector_expands_support": support(zero_output) == [0, 1, 2],
        "mode_projector_expands_support": support(mode_output) == [0, 1, 2],
    }
    if not all(checks.values()):
        raise AssertionError("support-expansion fixture failed")
    return {
        "constant_projector": [[encode(item) for item in row] for row in zero_projector],
        "harmonic_projector": [[encode(item) for item in row] for row in mode_projector],
        "localized_input": [encode(item) for item in localized],
        "constant_output": [encode(item) for item in zero_output],
        "harmonic_output": [encode(item) for item in mode_output],
        "checks": checks,
    }


def dependency(path: Path, value: dict[str, Any], role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_or_artifact_id": value["result_id"],
        "sha256": sha(path),
        "role": role,
    }


def build() -> dict[str, Any]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    pairing = json.loads(PAIRING.read_text(encoding="utf-8"))
    dfinite = json.loads(DFINITE.read_text(encoding="utf-8"))
    zero_modes = json.loads(ZERO_MODES.read_text(encoding="utf-8"))
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_OBSTRUCTION.read_text(encoding="utf-8"))
    green = json.loads(GREEN_TRANSFER.read_text(encoding="utf-8"))
    expected = {
        graph.get("result_id"): "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1",
        pairing.get("result_id"): "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1",
        dfinite.get("result_id"): "STRICT_DFINITE_RESIDUAL_SDR_V1",
        zero_modes.get("result_id"): "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1",
        centered.get("result_id"): "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1",
        prior.get("result_id"): "CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1",
        green.get("result_id"): "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1",
    }
    if any(actual != wanted for actual, wanted in expected.items()):
        raise ValueError("type-audit dependency identity drift")
    if graph["claim_flags"]["STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED"] is not True:
        raise ValueError("graph SDR is not available")
    if dfinite["claim_flags"]["STRICT_DFINITE_RESIDUAL_SDR_PORTABLE"] is not True:
        raise ValueError("D-finite residual SDR is not available")

    endpoint_rows = pairing["component_basis"]["rows"][:30]
    endpoint_ids = [row["row_id"] for row in endpoint_rows]
    residual_labels = [label for block in dfinite["blocks"] for label in block["residual_basis"]]
    symmetry_labels = [
        *zero_modes["zero_mode_basis"]["canonical_generator_order"],
        *zero_modes["zero_mode_basis"]["canonical_dual_order"],
    ]
    if len(endpoint_ids) != 30 or len(set(endpoint_ids)) != 30:
        raise ValueError("endpoint row dictionary drift")
    if len(residual_labels) != 470 or not all(":W_PLUS:" in label or ":W_MINUS:" in label for label in residual_labels):
        raise ValueError("D-finite residual dictionary drift")
    if len(symmetry_labels) != 30 or set(endpoint_ids).intersection(symmetry_labels):
        raise ValueError("zero-mode/endpoint type separation drift")

    fixture = exact_support_fixture()
    carrier_ledger = [
        {
            "id": "GRAPH_ENDPOINT_FIELDS",
            "kind": "SECTION_SHEAF_COMPONENT_CARRIER",
            "coordinates": 30,
            "coordinate_meaning": "local BV field-component species c, omega, h, h_star, c_star and omega_star; each coordinate is a spacetime-dependent section",
            "map": "the exact graph SDR contracts 386 component species onto these 30 endpoint species",
            "locality": "FINITE_ORDER_SUPPORT_LOCAL",
            "basis_sample": endpoint_ids[:6],
        },
        {
            "id": "DFINITE_WEYL_RESIDUAL",
            "kind": "FINITE_HARMONIC_COEFFICIENT_CARRIER",
            "coordinates": 470,
            "coordinate_meaning": "W+ and W- cohomology coefficients at energies 2 through 6",
            "map": "a blockwise finite harmonic SDR from 4,490 split coefficients",
            "locality": "REDUCED_MODE_NOT_ARBITRARY_SUPPORT",
            "basis_sample": residual_labels[:6],
        },
        {
            "id": "CONFORMAL_KILLING_COTANGENT",
            "kind": "FINITE_LIE_COTANGENT_CARRIER",
            "coordinates": 30,
            "coordinate_meaning": "fifteen conformal-Killing generators and fifteen normalized dual coefficients",
            "map": "the exact M5 residual zero-mode representation",
            "locality": "GLOBAL_ZERO_MODE_COEFFICIENTS",
            "basis_sample": symmetry_labels[:6],
        },
        {
            "id": "CENTERED_CE_COCHAINS",
            "kind": "FINITE_CENTERED_CE_COCHAIN_CARRIER",
            "coordinates": sum(centered["scope"]["centered_cochain_dimensions_C3_C4_C5"]),
            "coordinate_meaning": "ordered C3, C4 and C5 centered Chevalley-Eilenberg cochains used to compute H4",
            "map": "finite transferred coefficient complex",
            "locality": "LOCAL_ALGEBRAIC_AND_REDUCED_MODE_ONLY",
            "basis_sample": ["C3", "C4", "C5"],
        },
    ]
    type_body = {
        "endpoint_row_ids": endpoint_ids,
        "dfinite_energies": dfinite["scope"]["energies"],
        "dfinite_full_dimensions": [block["full_dimension"] for block in dfinite["blocks"]],
        "dfinite_residual_dimensions": [block["residual_dimension"] for block in dfinite["blocks"]],
        "dfinite_total_full_coordinates": dfinite["global_direct_sum"]["full_dimension"],
        "dfinite_total_residual_coordinates": dfinite["global_direct_sum"]["residual_dimension"],
        "zero_mode_generator_coordinates": len(zero_modes["zero_mode_basis"]["canonical_generator_order"]),
        "zero_mode_dual_coordinates": len(zero_modes["zero_mode_basis"]["canonical_dual_order"]),
        "centered_dimensions_C3_C4_C5": centered["scope"]["centered_cochain_dimensions_C3_C4_C5"],
        "dimension_collision": "GRAPH_ENDPOINT_FIELDS and CONFORMAL_KILLING_COTANGENT both display 30, but the first counts section species and the second counts global coefficients; their declared labels are disjoint and no identification is defined.",
    }
    type_census = {**type_body, "sha256": digest(type_body)}
    decision_body = {
        "original_M3_disposition": "REJECT_AS_SINGLE_UNTYPED_SUPPORT_LOCAL_RESIDUAL_SDR_REQUIREMENT",
        "M3L_COMMON_ENDPOINT_SDR_BINDING": {
            "category": "LOCAL-ALGEBRAIC",
            "available_scoped_object": graph["result_id"],
            "object": "bind q1, the 386-to-30 graph endpoint SDR and its cyclic suspension to the common strict manifest",
            "status": "EXACT_OBJECT_EXISTS_COMMON_HASH_BINDING_OPEN",
        },
        "M3R_TYPED_RESIDUAL_COMPARISON": {
            "category": "REDUCED-MODE with a separately declared analytic domain",
            "available_control": dfinite["result_id"],
            "object": "construct a harmonic restriction/comparison diagram from the endpoint section complex to the W+/W- residual coefficient complex, with nonlocal projections labeled explicitly",
            "status": "NOT_CONSTRUCTED",
        },
        "causal_transfer_rule": "Use only support-local bundle-complex SDR maps in the Green-homotopy transfer formula. A harmonic or zero-mode projection may enter a later reduced-mode comparison or residual transfer, not the support-local premise.",
        "gate_effect": "Gate A remains fail closed. The repair changes the type of the missing evidence, not the number of accepted common hashes.",
    }
    architecture_decision = {**decision_body, "sha256": digest(decision_body)}
    result: dict[str, Any] = {
        "$schema": "../schema/strict-residual-sdr-type-and-locality-audit-v1.schema.json",
        "schema": "strict-residual-sdr-type-and-locality-audit-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-residual-sdr-type-and-locality-audit-v1.schema.json",
        "result_id": "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1",
        "result_kind": "CLASSICAL_IMPORT_ARCHITECTURE_TYPE_AUDIT",
        "result_state": "ORIGINAL_M3_SPLIT_INTO_LOCAL_ENDPOINT_SDR_AND_NONLOCAL_RESIDUAL_COMPARISON",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "0e0e5670576da72bcaaf2b6d6189cc1d25287ce5",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can the 386-row graph SDR, D-finite W+/W- residual SDR and thirty-dimensional conformal-Killing cotangent payload be treated as one support-local residual contraction?",
        "answer": "No. The graph object retracts 386 local component species onto 30 local endpoint field species. The D-finite object retracts 4,490 harmonic coefficients onto 470 W+/W- coefficients, and M5 contains 30 global symmetry-cotangent coefficients. The repeated number 30 is a type collision, not a basis bridge. A nonzero projector onto a global constant or harmonic mode expands support, so the declared reduced-mode projections cannot be used as support-local maps in the Green-homotopy transfer theorem. M3 must split into a common binding of the already exact local endpoint SDR and a separately typed, explicitly nonlocal residual comparison.",
        "scope": {
            "theory": "strict pure-Weyl free BV complex",
            "background": "unit conformal cylinder",
            "audit_surface": "graph endpoint fields, finite W+/W- harmonics, conformal-Killing cotangent modes and centered CE cochains",
            "claim_type": "architecture classification and scoped support obstruction",
        },
        "carrier_ledger": carrier_ledger,
        "type_census": type_census,
        "support_locality_obstruction": {
            "lemma": "For a nonzero global mode phi, choose a cutoff chi supported in a proper open set with nonzero pairing against phi. The mode projector sends chi phi to a nonzero global multiple of phi, so its output support is not contained in the input support.",
            "projector_consequence": "If pi iota=1 on a nonzero finite global-mode carrier, P=iota pi is a nonzero projector. The specified harmonic or zero-mode P cannot be support-nonincreasing and therefore cannot be one of the finite-order support-local maps assumed by the causal-transfer theorem.",
            "peetre_context": "Peetre's theorem identifies linear local operators on smooth section sheaves with differential operators; the support-expansion witness already refutes locality for the specified mode projector without requiring a classification of every alternative carrier.",
            "finite_exact_fixture": fixture,
            "prior_repository_control": prior["result_id"],
        },
        "architecture_decision": architecture_decision,
        "foundational_strength": {
            "exact_fixture": "finite rational arithmetic formalizable in PRA",
            "choice_dependency": "none for the exact fixture or the explicit support witness",
            "smooth_locality_context": "classical smooth section sheaves and support; Peetre-type locality is used only as context, not to promote a causal theorem",
            "infinite_or_spectral_dependency": "the actual W+/W- comparison is global harmonic analysis and must remain separately typed",
        },
        "literature_scope": [
            {
                "source_id": "navarro-sancho-2016",
                "title": "Peetre-Slovak's theorem revisited",
                "url": "https://arxiv.org/abs/1411.7499",
                "role": "local operators on smooth section sheaves are differential operators",
            },
            {
                "source_id": "benini-musante-schenkel-2023",
                "title": "Green hyperbolic complexes on Lorentzian manifolds",
                "url": "https://doi.org/10.1007/s00220-023-04807-5",
                "role": "typed retarded/advanced Green homotopies for differential complexes",
            },
        ],
        "provenance": {
            "inputs": [
                dependency(GRAPH, graph, "exact support-local 386-to-30 endpoint graph SDR"),
                dependency(PAIRING, pairing, "386-row component species and pairing dictionary"),
                dependency(DFINITE, dfinite, "finite harmonic W+/W- residual SDR control"),
                dependency(ZERO_MODES, zero_modes, "finite conformal-Killing cotangent payload"),
                dependency(CENTERED, centered, "finite centered CE cochain payload"),
                dependency(PRIOR_OBSTRUCTION, prior, "independent repository support-expansion precedent"),
                dependency(GREEN_TRANSFER, green, "support-local cyclic Green-homotopy transfer contract"),
            ]
        },
        "claim_flags": {
            "STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL": True,
            "GRAPH_ENDPOINT_30_IS_FINITE_RESIDUAL_30": False,
            "DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL": False,
            "ZERO_MODE_PROJECTOR_SUPPORT_LOCAL": False,
            "ORIGINAL_M3_SINGLE_OBJECT_TYPE_CORRECT": False,
            "M3_TYPED_SPLIT_REQUIRED": True,
            "M3L_COMMON_ENDPOINT_SDR_BOUND": False,
            "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "nonexistence of every possible infinite-dimensional local equation-level residual or curvature carrier",
            "nonexistence of a typed harmonic restriction or nonlocal reduced-mode comparison",
            "failure of the certified support-local 386-to-30 graph endpoint SDR",
            "common-snapshot binding of that endpoint SDR",
            "a new causal Green homotopy, Hadamard state, renormalized product, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Bind the exact graph endpoint SDR to the common strict carrier as M3L, and independently construct M3R as a typed harmonic restriction/comparison with every nonlocal projection and function-space domain explicit.",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_residual_sdr_type_audit.py",
            "checks": [
                "all input content hashes", "386/30 endpoint map shapes and row-species labels",
                "4,490/470 D-finite harmonic dimensions and W+/W- labels",
                "thirty conformal-Killing cotangent labels and disjoint type dictionaries",
                "exact rational projector idempotency and support expansion",
                "M3L/M3R split and every fail-closed claim flag", "canonical audit digest",
            ],
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.md",
    }
    result["independent_checker"]["expected_digest"] = digest({
        key: result[key]
        for key in ("carrier_ledger", "type_census", "support_locality_obstruction", "architecture_decision", "claim_flags")
    })
    return result


def report(value: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{item['id']}` | {item['coordinates']:,} | `{item['kind']}` | `{item['locality']}` |"
        for item in value["carrier_ledger"]
    )
    return f"""# Strict residual-SDR type and locality audit

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Decision

The former `M3_RESIDUAL_SDR` request combined objects from different
categories.  It must not be satisfied by identifying equal-looking dimensions
or by relabeling a harmonic projection as support-local.

| Carrier | Coordinates | What they count | Locality |
|---|---:|---|---|
{rows}

The graph `30` counts local BV component species.  The M5 `30` counts fifteen
global conformal-Killing generators and fifteen dual coefficients.  Their
labels are disjoint.  The finite W+/W- residual carrier has 470 coordinates at
energies two through six.

## Locality obstruction

A nonzero constant or harmonic projector expands support.  The certificate
includes two exact rational three-site projectors: each sends a vector
supported only at site zero to a vector supported at all three sites.  The
continuum witness is the same: project a compactly supported cutoff times a
global mode back onto that mode.  Therefore the specified reduced-mode
projection cannot be a support-nonincreasing differential map in a Green
homotopy transfer.

This is a scoped obstruction to the direct promotion of the existing mode
receiver.  It does not rule out a new infinite-dimensional local curvature or
equation-level carrier.

## Repaired gate

- `M3L_COMMON_ENDPOINT_SDR_BINDING`: bind the already exact support-local
  386-to-30 graph SDR to the common strict manifest.
- `M3R_TYPED_RESIDUAL_COMPARISON`: construct the harmonic restriction and
  W+/W- residual comparison separately, label its nonlocal maps
  `REDUCED-MODE`, and state the analytic domains.

No common hash is accepted by this classification.  Hadamard, QME and quantum
residual-transfer stages remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_residual_sdr_type_audit.py --check
python3 quantum-weyl/classical_import/check_strict_residual_sdr_type_audit.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_residual_sdr_type_audit.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

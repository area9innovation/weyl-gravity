#!/usr/bin/env python3
"""Export the source-forced Diff action on the shifted auxiliary fields."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
PREDECESSOR = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-diff-auxiliary-bv-representation-v1.md"

DIM = 4
SYMMETRIC = tuple((mu, nu) for mu in range(DIM) for nu in range(mu, DIM))
ZERO = (0, 0, 0, 0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def derivative(axis: int) -> tuple[int, ...]:
    return tuple(int(index == axis) for index in range(DIM))


def tensor_row(prefix: str, mu: int, nu: int) -> str:
    left, right = sorted((mu, nu))
    return f"{prefix}_{left}{right}"


def collect(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    for item in entries:
        key = (
            item["output_row"], item["ghost_row"], tuple(item["ghost_jet"]),
            item["field_row"], tuple(item["field_jet"]),
        )
        totals[key] += Fraction(item["coefficient"])
    return [
        {
            "output_row": output,
            "ghost_row": ghost,
            "ghost_jet": list(ghost_jet),
            "field_row": field,
            "field_jet": list(field_jet),
            "coefficient": str(coefficient),
        }
        for (output, ghost, ghost_jet, field, field_jet), coefficient in sorted(totals.items())
        if coefficient
    ]


def covector_entries(prefix: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for mu in range(DIM):
        output = f"{prefix}_{mu}"
        for rho in range(DIM):
            entries.extend((
                {
                    "output_row": output, "ghost_row": f"c_{rho}",
                    "ghost_jet": list(ZERO), "field_row": output,
                    "field_jet": list(derivative(rho)), "coefficient": "1",
                },
                {
                    "output_row": output, "ghost_row": f"c_{rho}",
                    "ghost_jet": list(derivative(mu)), "field_row": f"{prefix}_{rho}",
                    "field_jet": list(ZERO), "coefficient": "1",
                },
            ))
    return collect(entries)


def symmetric_covariant_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for mu, nu in SYMMETRIC:
        output = tensor_row("f_hat", mu, nu)
        for rho in range(DIM):
            entries.extend((
                {
                    "output_row": output, "ghost_row": f"c_{rho}",
                    "ghost_jet": list(ZERO), "field_row": output,
                    "field_jet": list(derivative(rho)), "coefficient": "1",
                },
                {
                    "output_row": output, "ghost_row": f"c_{rho}",
                    "ghost_jet": list(derivative(mu)),
                    "field_row": tensor_row("f_hat", rho, nu),
                    "field_jet": list(ZERO), "coefficient": "1",
                },
                {
                    "output_row": output, "ghost_row": f"c_{rho}",
                    "ghost_jet": list(derivative(nu)),
                    "field_row": tensor_row("f_hat", mu, rho),
                    "field_jet": list(ZERO), "coefficient": "1",
                },
            ))
    return collect(entries)


def build() -> dict[str, Any]:
    action, split, predecessor = (json.loads(path.read_text()) for path in (ACTION, SPLIT, PREDECESSOR))
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("curved auxiliary action authority drift")
    if split.get("schema") != "pure-weyl-curved-auxiliary-canonical-split-v1":
        raise ValueError("canonical split authority drift")
    if predecessor.get("result_id") != "CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1":
        raise ValueError("curved source-to-split predecessor drift")
    if action["source"]["gauge_transformations"]["diffeomorphism"] != "Lie derivative on g, phi, b":
        raise ValueError("Diff source transformation drift")
    if split["factorized_curved_Q_split"]["exact_inputs"]["shifted_gauge_defects"]["diffeomorphism"] != 0:
        raise ValueError("shifted Diff naturality is not exact")

    tables = [
        {
            "family_id": "DIFF_C_F_HAT_F_HAT_STAR",
            "field_symbol": "f_hat",
            "tensor_type": "symmetric covariant rank-two tensor",
            "Grassmann_parity": 0,
            "coordinate_formula": "(L_c f_hat)_{mu nu}=c^rho partial_rho f_hat_{mu nu}+f_hat_{rho nu} partial_mu c^rho+f_hat_{mu rho} partial_nu c^rho",
            "ordered_field_action_entries": symmetric_covariant_entries(),
        },
        {
            "family_id": "DIFF_C_V_V_STAR",
            "field_symbol": "v",
            "tensor_type": "covector",
            "Grassmann_parity": 0,
            "coordinate_formula": "(L_c v)_mu=c^rho partial_rho v_mu+v_rho partial_mu c^rho",
            "ordered_field_action_entries": covector_entries("v"),
        },
        {
            "family_id": "DIFF_C_ETA_ETA_STAR",
            "field_symbol": "eta",
            "tensor_type": "odd covector ghost",
            "Grassmann_parity": 1,
            "coordinate_formula": "(L_c eta)_mu=c^rho partial_rho eta_mu+eta_rho partial_mu c^rho",
            "ordered_field_action_entries": covector_entries("eta"),
        },
    ]
    for table in tables:
        table["nonzero_ordered_field_coefficients"] = len(table["ordered_field_action_entries"])
        table["maximum_input_jet_order"] = 1
        table["sha256"] = digest(table["ordered_field_action_entries"])

    naturality = {
        "phi_hat_definition": "phi_hat=phi-A_g^-1 G^b(g,b)",
        "phi_hat_tensor_type": "symmetric covariant rank-two tensor in the receiver convention",
        "reason": "phi, A_g, and G^b are natural tensor operations and the exact shifted Diff defect is zero",
        "v_tensor_type": "covector inherited from b",
        "eta_definition": "eta=xi_0-d sigma",
        "eta_tensor_type": "odd covector under the Diff semidirect action",
        "all_three_actions_source_forced": True,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-diff-auxiliary-bv-representation-v1",
        "result_id": "CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1",
        "result_kind": "AUTHORITATIVE_CLASSICAL_DIFF_AUXILIARY_FIELD_REPRESENTATION_EXPORT",
        "result_state": "THREE_SOURCE_FORCED_DIFF_FIELD_ACTIONS_COMPONENT_SERIALIZED_COTANGENT_RECEIVER_REQUIRED",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl curved generalized-auxiliary BV theory",
            "background": "unit conformal cylinder normal coordinate point",
            "coefficient_field": "Q",
            "spacetime_dimension": DIM,
            "maximum_input_jet_order": 1,
            "support_rule": "each output support lies in the intersection of the two input supports",
        },
        "source_master_terms": [
            "int <f_hat_star,L_c f_hat>",
            "int <v_star,L_c v>",
            "int <eta_star,L_c eta>",
        ],
        "naturality_derivation": naturality,
        "representation_tables": tables,
        "component_summary": {
            "families": 3,
            "ordered_field_coefficients": sum(table["nonzero_ordered_field_coefficients"] for table in tables),
            "by_family": {table["family_id"]: table["nonzero_ordered_field_coefficients"] for table in tables},
        },
        "claim_flags": {
            "THREE_DIFF_AUXILIARY_FIELD_ACTIONS_SOURCE_FORCED": True,
            "THREE_DIFF_AUXILIARY_FIELD_COMPONENT_TABLES_SERIALIZED": True,
            "THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED": False,
            "FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
            "EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the 386-row antifield and c-star component tables",
            "the arity-two q1/q2 identity or cyclicity on the receiver pairing",
            "absence of additional nonlinear Weyl or conformal-boost ghost-antifield families",
            "the complete source q2/q3 pullback, Gate A, Hadamard data, or QME restoration",
        ],
        "canonical_hashes": {
            "representation_tables_sha256": digest(tables),
            "naturality_derivation_sha256": digest(naturality),
        },
        "provenance": {"inputs": [
            {"path": str(ACTION.relative_to(ROOT)), "result_or_artifact_id": action["schema"], "sha256": sha(ACTION), "role": "authoritative curved source action and Diff transformations"},
            {"path": str(SPLIT.relative_to(ROOT)), "result_or_artifact_id": split["schema"], "sha256": sha(SPLIT), "role": "exact natural shifted variables and zero Diff defect"},
            {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": predecessor["result_id"], "sha256": sha(PREDECESSOR), "role": "curved nonlinear source-to-split field map"},
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Import the three field tables onto the fixed 386-row carrier and derive both formal cotangent and Diff-momentum-map rows using its exact odd pairing.",
    }


def render(value: dict[str, Any]) -> str:
    summary = value["component_summary"]
    rows = "\n".join(
        f"| `{table['family_id']}` | {table['tensor_type']} | {table['nonzero_ordered_field_coefficients']} |"
        for table in value["representation_tables"]
    )
    return f"""# Classical Diff auxiliary BV representation v1

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`

The exact curved shift is natural under diffeomorphisms.  Consequently
`f_hat` is a symmetric covariant tensor, while `v` and the odd shifted boost
ghost `eta` are covectors.  Their three Lie-derivative actions are therefore
source-forced rather than fitted.  This export contains
**{summary['ordered_field_coefficients']}** collected rational field-action
coefficients through first jet order.

| Family | Field type | Ordered coefficients |
|---|---|---:|
{rows}

The source export deliberately stops before identifying tensor duals with the
receiver's 386-row antifield coordinates.  That receiver uses a non-diagonal
DeWitt-type auxiliary pairing, so the cotangent and Diff momentum-map rows
must be derived against those exact bytes.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_diff_auxiliary_bv_representation_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_diff_auxiliary_bv_representation_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_diff_auxiliary_bv_representation_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_diff_auxiliary_bv_representation_v1
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

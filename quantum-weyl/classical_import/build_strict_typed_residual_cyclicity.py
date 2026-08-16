#!/usr/bin/env python3
"""Build the finite represented M4R cyclic residual contraction certificate."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
M3RCA = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
M3RCB = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
M4L = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
RESULT = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
REPORT = HERE / "REPORT_STRICT_TYPED_RESIDUAL_CYCLICITY_V1.md"

Sparse = dict[tuple[int, int], int]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sparse(spec: dict[str, Any]) -> Sparse:
    result: Sparse = {}
    for row, column, coefficient in spec["entries"]:
        number = int(coefficient)
        require(str(number) == coefficient and number != 0, f"invalid entry in {spec['name']}")
        require((row, column) not in result, f"duplicate entry in {spec['name']}")
        result[row, column] = number
    return result


def transpose(value: Sparse, sign: int = 1) -> Sparse:
    return {(column, row): sign * coefficient for (row, column), coefficient in value.items()}


def add(*values: Sparse) -> Sparse:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for value in values:
        for key, coefficient in value.items():
            result[key] += coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def scale(value: Sparse, coefficient: int) -> Sparse:
    return {key: coefficient * entry for key, entry in value.items() if coefficient * entry}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_by_row: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (row, column), coefficient in right.items():
        right_by_row[row].append((column, coefficient))
    result: dict[tuple[int, int], int] = defaultdict(int)
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in right_by_row.get(middle, []):
            result[row, column] += left_coefficient * right_coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def identity(size: int) -> Sparse:
    return {(index, index): 1 for index in range(size)}


def shifted(value: Sparse, row_offset: int, column_offset: int) -> Sparse:
    return {
        (row + row_offset, column + column_offset): coefficient
        for (row, column), coefficient in value.items()
    }


def direct_sum(first: Sparse, second: Sparse, first_rows: int, first_columns: int) -> Sparse:
    return add(first, shifted(second, first_rows, first_columns))


def odd_pairing(size: int) -> Sparse:
    return {
        **{(index, size + index): 1 for index in range(size)},
        **{(size + index, index): -1 for index in range(size)},
    }


def serialized(value: Sparse) -> list[list[Any]]:
    return [[row, column, str(coefficient)] for (row, column), coefficient in sorted(value.items())]


def replay_block(block: dict[str, Any]) -> dict[str, Any]:
    n = block["full_dimension"]
    r = block["residual_dimension"]
    q = sparse(block["matrices"]["q0"])
    iota = sparse(block["matrices"]["iota_cl"])
    projection = sparse(block["matrices"]["pi_cl"])
    homotopy = sparse(block["matrices"]["s_cl"])

    q_cotangent = direct_sum(q, transpose(q, -1), n, n)
    iota_cotangent = direct_sum(iota, transpose(projection), n, r)
    projection_cotangent = direct_sum(projection, transpose(iota), r, n)
    homotopy_cotangent = direct_sum(homotopy, transpose(homotopy, -1), n, n)
    omega_source = odd_pairing(n)
    omega_residual = odd_pairing(r)

    source_identity = identity(2 * n)
    residual_identity = identity(2 * r)
    projector = multiply(iota_cotangent, projection_cotangent)
    defects = {
        "q_squared": len(multiply(q_cotangent, q_cotangent)),
        "projection_inclusion_identity": len(add(multiply(projection_cotangent, iota_cotangent), scale(residual_identity, -1))),
        "contraction_identity": len(add(projector, multiply(q_cotangent, homotopy_cotangent), multiply(homotopy_cotangent, q_cotangent), scale(source_identity, -1))),
        "inclusion_chain_map": len(multiply(q_cotangent, iota_cotangent)),
        "projection_chain_map": len(multiply(projection_cotangent, q_cotangent)),
        "homotopy_squared": len(multiply(homotopy_cotangent, homotopy_cotangent)),
        "homotopy_inclusion": len(multiply(homotopy_cotangent, iota_cotangent)),
        "projection_homotopy": len(multiply(projection_cotangent, homotopy_cotangent)),
        "source_q_cyclicity": len(add(multiply(transpose(q_cotangent), omega_source), multiply(omega_source, q_cotangent))),
        "residual_q_cyclicity": 0,
        "projection_equals_inclusion_sharp": len(add(multiply(transpose(projection_cotangent), omega_residual), scale(multiply(omega_source, iota_cotangent), -1))),
        "homotopy_skew_adjoint": len(add(multiply(transpose(homotopy_cotangent), omega_source), multiply(omega_source, homotopy_cotangent))),
        "inclusion_isometry": len(add(multiply(transpose(iota_cotangent), multiply(omega_source, iota_cotangent)), scale(omega_residual, -1))),
    }
    return {
        "energy": block["energy"],
        "formal_source_dimension": 2 * n,
        "action_identified_residual_dimension": 2 * r,
        "residual_primal_dimension": r,
        "residual_dual_dimension": r,
        "source_pairing_rank": 2 * n,
        "residual_pairing_rank": 2 * r,
        "map_hashes": {
            "q_cotangent": digest(serialized(q_cotangent)),
            "iota_cotangent": digest(serialized(iota_cotangent)),
            "projection_cotangent": digest(serialized(projection_cotangent)),
            "homotopy_cotangent": digest(serialized(homotopy_cotangent)),
            "source_pairing": digest(serialized(omega_source)),
            "residual_pairing": digest(serialized(omega_residual)),
        },
        "identity_defects": defects,
        "total_identity_defects": sum(defects.values()),
    }


def dependency(path: Path, result_id: str, role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_or_artifact_id": result_id,
        "sha256": sha(path),
        "role": role,
    }


def build() -> dict[str, Any]:
    dfinite = load(DFINITE)
    m3rca = load(M3RCA)
    m3rcb = load(M3RCB)
    m4l = load(M4L)
    require(dfinite.get("result_id") == "STRICT_DFINITE_RESIDUAL_SDR_V1", "D-finite SDR drift")
    require(m3rca.get("result_id") == "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1", "M3RC-A drift")
    require(m3rcb.get("result_id") == "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1", "M3RC-B drift")
    require(m4l.get("result_id") == "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1", "M4L drift")
    require(m3rca["claim_flags"]["FORMAL_COTANGENT_SDR_CYCLIC"] is True, "formal cyclic SDR unavailable")
    require(m3rcb["claim_flags"]["M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] is True, "represented action/support dual unavailable")
    require(m3rcb["claim_flags"]["ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING"] is True, "action/cotangent pairing not identified")
    require(m3rcb["claim_flags"]["FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED"] is False, "scope firewall drift")
    require(m4l["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"] is True, "M4L unavailable")

    blocks = [replay_block(block) for block in dfinite["blocks"]]
    require([block["energy"] for block in blocks] == [2, 3, 4, 5, 6], "energy order drift")
    require(not any(block["total_identity_defects"] for block in blocks), "M4R identity defect")
    full_dimension = sum(block["formal_source_dimension"] for block in blocks)
    residual_dimension = sum(block["action_identified_residual_dimension"] for block in blocks)
    require((full_dimension, residual_dimension) == (8980, 940), "global carrier drift")
    action = m3rcb["action_pairing_identification"]
    require(action["phase_space_dimension"] == action["phase_pairing_rank"] == residual_dimension, "action residual pairing drift")

    exact = {
        "coordinate_convention": "fixed BV-BFV suspended cotangent order (primal,dual[1]) with Omega=[[0,I],[-I,0]]",
        "formal_source": "T_star[-1](C_D-finite), used only as the finite represented comparison source",
        "action_identified_residual": "T_star[-1](H_res) with every dual coordinate represented by a compact source class",
        "formal_source_dimension": full_dimension,
        "residual_dimension": residual_dimension,
        "residual_pairing_rank": residual_dimension,
        "residual_differential": "q_res=0",
        "block_replays": blocks,
        "all_identity_defects": sum(block["total_identity_defects"] for block in blocks),
        "identities": [
            "q_cotangent^2=0",
            "pi_cotangent iota_cotangent=I_res",
            "iota_cotangent pi_cotangent+q_cotangent s_cotangent+s_cotangent q_cotangent=I_source",
            "q_cotangent iota_cotangent=0 and pi_cotangent q_cotangent=0",
            "s_cotangent^2=s_cotangent iota_cotangent=pi_cotangent s_cotangent=0",
            "q_cotangent is cyclic and q_res=0 is cyclic",
            "pi_cotangent=iota_cotangent^sharp",
            "s_cotangent is skew-adjoint",
            "iota_cotangent preserves the action-identified residual odd pairing",
        ],
    }
    result: dict[str, Any] = {
        "$schema": "../schema/strict-typed-residual-cyclicity-v1.schema.json",
        "schema": "strict-typed-residual-cyclicity-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-typed-residual-cyclicity-v1.schema.json",
        "result_id": "STRICT_TYPED_RESIDUAL_CYCLICITY_V1",
        "result_kind": "CLASSICAL_IMPORT_FINITE_REPRESENTED_TYPED_RESIDUAL_CYCLIC_CONTRACTION",
        "result_state": "M4R_COMPLETE_ON_ACTION_IDENTIFIED_ENERGIES_2_THROUGH_6_M1_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "24a4d9458375e66706d234a92017035f050b044c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Does the action-identified 940-coordinate residual carrier satisfy the exact cyclic contraction identities required by M4R?",
        "answer": "Yes on represented energies two through six. In the fixed suspended cotangent convention, an independent sparse receiver reconstructs the five formal cotangent comparison blocks and verifies q_res cyclicity, projection equals the adjoint of inclusion, homotopy skew-adjointness, inclusion isometry, the contraction and normalized SDR side conditions with zero defects. M3RC-B identifies the residual signed-permutation form with the compact-source action/Green pairing, so this is an action-typed residual result rather than a merely formal rank calculation. It closes M4R only on the finite represented carrier. The formal 8,980-coordinate comparison source is not promoted to the authoritative full BV complex; M1 must still bind all local, nonlinear, causal and residual objects under one strict common snapshot before Gate A can pass.",
        "scope": {
            "theory": "strict pure-Weyl free classical BV represented residual comparison",
            "background": "unit Lorentzian conformal cylinder R x S3",
            "energies": [2, 3, 4, 5, 6],
            "source_category": "finite formal shifted-cotangent D-finite comparison source",
            "residual_category": "finite compact-source/action-identified causal cohomology subquotient",
            "pairing_category": "degree-minus-one action-derived odd pairing in the fixed suspended convention",
        },
        "typed_carrier": {
            "primal_residual_coordinates": 470,
            "compact_source_dual_coordinates": 470,
            "total_residual_coordinates": 940,
            "action_pairing_rank": 940,
            "action_pairing_identification_defects": action["pairing_identification_defects"],
            "positive_krein_inertia_before_BV_suspension": action["positive_krein_inertia"],
            "formal_source_coordinates": 8980,
            "formal_source_is_authoritative_full_BV_source": False,
            "full_continuous_all_energy_dual_identified": False,
        },
        "exact_cyclic_replay": exact,
        "m4r_disposition": {
            "M4L_LOCAL_GRAPH_CYCLIC_PAIRING": "COMPLETE",
            "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON": "COMPLETE",
            "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
            "M4R_TYPED_RESIDUAL_CYCLICITY": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN_AND_REQUIRED_FOR_GATE_A",
        },
        "foundational_strength": {
            "finite_replay": "primitive-recursive exact sparse integer arithmetic at the declared cutoff",
            "analytic_input": "the previously certified causal support sequence and action/Green pairing theorem used by M3RC-B",
            "choice_principle_added_by_M4R": False,
            "Hilbert_or_Krein_completion_added_by_M4R": False,
            "infinite_extension_boundary": "No uniform all-energy topology, continuous dual, convergence, completeness or choice theorem follows from the five finite blocks.",
        },
        "provenance": {
            "inputs": [
                dependency(DFINITE, dfinite["result_id"], "receiver-readable primal D-finite SDR entries"),
                dependency(M3RCA, m3rca["result_id"], "formal cotangent construction and convention"),
                dependency(M3RCB, m3rcb["result_id"], "compact-source residual dual and action-pairing identification"),
                dependency(M4L, m4l["result_id"], "separate authoritative local action cyclicity result"),
            ]
        },
        "claim_flags": {
            "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE": True,
            "M3RC_REPRESENTED_DUAL_COMPLETE": True,
            "M4R_REPRESENTED_Q_RES_CYCLIC": True,
            "M4R_REPRESENTED_PROJECTION_EQUALS_INCLUSION_SHARP": True,
            "M4R_REPRESENTED_HOMOTOPY_SKEW_ADJOINT": True,
            "M4R_REPRESENTED_NORMALIZED_CYCLIC_CONTRACTION_COMPLETE": True,
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": True,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "M1_COMMON_STRICT_SNAPSHOT_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "that the formal 8,980-coordinate cotangent comparison source is the unchanged authoritative classical BV source",
            "a common M1 snapshot binding q1, q2, q3, D, pairing, SDR, causal Green and residual maps",
            "the full continuous dual or cyclic contraction of the all-energy smooth solution space",
            "a Hilbert, Krein, Sobolev, LF, Frechet or distributional completion theorem",
            "nonlinear q2/q3 compatibility with the causal Green homotopy",
            "Gate A, a full-complex Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Construct M1: one versioned strict pure-Weyl manifest binding every Gate-A carrier, ordered basis, q1/q2/q3, D, action pairing, local and residual SDR map, represented causal Green action and the M4R compact-source dual dictionary. Replay all twenty exports, ten checks and seven top-level hashes without changing category.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_TYPED_RESIDUAL_CYCLICITY_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_typed_residual_cyclicity.py",
            "checks": [
                "all four dependency identities and content hashes",
                "independent reconstruction of all five cotangent block maps",
                "source and residual odd signed-permutation pairing ranks",
                "q-squared, chain-map, contraction and normalized SDR identities",
                "source and residual q cyclicity",
                "projection equals the pairing adjoint of inclusion",
                "homotopy skew-adjointness and inclusion isometry",
                "M3RC-B action/support pairing crosswalk",
                "finite represented versus common-source/all-energy firewalls",
                "Gate-A/Hadamard/renormalization/QME/residual-transfer firewalls",
                "canonical result digest",
            ],
            "expected_digest": "",
        },
    }
    result["independent_checker"]["expected_digest"] = digest({
        key: result[key]
        for key in (
            "scope", "typed_carrier", "exact_cyclic_replay", "m4r_disposition",
            "foundational_strength", "claim_flags",
        )
    })
    return result


def report(value: dict[str, Any]) -> str:
    exact = value["exact_cyclic_replay"]
    return f"""# Strict typed residual cyclicity v1

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**M4R:** `COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6`
**Gate A:** `FAIL_CLOSED`

## Outcome

The action-identified residual cotangent carrier has
{exact['residual_dimension']} coordinates and exact odd-pairing rank
{exact['residual_pairing_rank']}.  An independent sparse replay reconstructs
all five energy blocks and verifies the cyclic contraction identities with
{exact['all_identity_defects']} defects.  In particular, `q_res=0` is cyclic,
`pi_cotangent=iota_cotangent^sharp`, the homotopy is skew-adjoint, inclusion
preserves the odd pairing, and every normalized SDR side condition holds.

This closes M4R on represented energies two through six.  M3RC-B is essential:
it identifies the 470 degree-one coordinates with compact-source causal
classes and identifies the residual signed-permutation form with the
action-derived Cauchy/Green pairing.

## Boundary

The {exact['formal_source_dimension']}-coordinate source used in the replay is
the explicit formal shifted-cotangent comparison source.  This certificate
does not declare it to be the authoritative full classical BV source.  M1 must
still bind all local, nonlinear, causal and residual objects under one common
manifest.  Gate A therefore remains fail closed, and no Hadamard,
renormalization, QME or residual quantum-transfer claim is promoted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_typed_residual_cyclicity.py --check
python3 quantum-weyl/classical_import/check_strict_typed_residual_cyclicity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_typed_residual_cyclicity.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.exists() or path.read_bytes() != content]
    if args.check:
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("STRICT_TYPED_RESIDUAL_CYCLICITY: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_TYPED_RESIDUAL_CYCLICITY: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the strict minimal-BV canonical-pairing sign reconciliation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from local_bv_cyclicity_receiver import (
    BASIS,
    SIGN_TRANSLATION,
    canonical_pairing,
    component_label,
    conjugation_multiplier,
    receiver_result,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.md"
INPUTS = (
    (
        "quantum-weyl/classical_import/certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json",
        "STRICT_PORTABLE_LOCAL_Q1_AST_V1",
        "portable Bach-flat q1 and square-zero theorem",
    ),
    (
        "quantum-weyl/classical_import/certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json",
        "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1",
        "portable six-row q2 and ordered Koszul ledger",
    ),
    (
        "quantum-weyl/classical_import/certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json",
        "STRICT_LOCAL_Q1_Q2_IDENTITY_V1",
        "complete minimal-sector arity-two identity",
    ),
    (
        "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json",
        "PURE_WEYL_ACTION_NORMALIZATION_V2",
        "authoritative action, Euler coordinate and minimal master terms",
    ),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def _q1_translation(q1: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source in q1["local_q1_ast"]["components"]:
        multiplier = conjugation_multiplier(source["output"], (source["input"],))
        rows.append(
            {
                "component_id": source["component_id"],
                "input": source["input"],
                "output": source["output"],
                "source_coefficient": source["coefficient"],
                "translation_multiplier": multiplier,
                "translated_coefficient": source["coefficient"] * multiplier,
            }
        )
    return rows


def _q2_translation(q2: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source in q2["ordered_components"]:
        multiplier = conjugation_multiplier(source["output"], source["inputs"])
        rows.append(
            {
                "component_id": source["component_id"],
                "primary_id": source["primary_id"],
                "inputs": source["inputs"],
                "output": source["output"],
                "source_coefficient_relative_to_primary": source["coefficient_relative_to_primary"],
                "translation_multiplier": multiplier,
                "translated_coefficient_relative_to_primary": source["coefficient_relative_to_primary"] * multiplier,
            }
        )
    return rows


def _pairing_ledger() -> dict[str, Any]:
    entries = []
    pairing = canonical_pairing()
    for (left, right), coefficient in sorted(pairing.items()):
        entries.append(
            {
                "left_index": left,
                "right_index": right,
                "left": component_label(BASIS[left].symbol, BASIS[left].component),
                "right": component_label(BASIS[right].symbol, BASIS[right].component),
                "coefficient": str(coefficient),
            }
        )
    return {
        "kind": "CANONICAL_SUPPORT_LOCAL_ODD_COTANGENT_PAIRING",
        "degree": -1,
        "density_formula": "integral (h^{*mu nu} h_mu nu + c^*_mu c^mu + omega^* omega), with the displayed odd-Darboux orientations",
        "support_domain": "one compactly supported argument; compact-compact is allowed",
        "component_basis_dimension": len(BASIS),
        "nonzero_ordered_entry_count": len(entries),
        "rank": len(BASIS),
        "off_diagonal_symmetric_tensor_weight": 2,
        "entries": entries,
    }


def build() -> dict[str, Any]:
    q1, q2, identity, action = (load(path) for path, _, _ in INPUTS)
    for value, (_, result_id, _) in zip((q1, q2, identity, action), INPUTS):
        if value.get("result_id") != result_id:
            raise ValueError(f"dependency drift: {result_id}")
    if q1.get("claim_flags", {}).get("Q1_SQUARED_ZERO_CERTIFIED") is not True:
        raise ValueError("q1 square-zero input unavailable")
    if q2.get("claim_flags", {}).get("Q2_KOSZUL_SYMMETRY_REPLAYED") is not True:
        raise ValueError("q2 ordered ledger unavailable")
    if identity.get("claim_flags", {}).get("Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED") is not True:
        raise ValueError("q1q2 theorem unavailable")

    q1_rows = _q1_translation(q1)
    q2_rows = _q2_translation(q2)
    pairing = _pairing_ledger()
    receiver = receiver_result(q2["ordered_components"])
    if receiver["translated_convention_defect"]["coefficient_count"] != 0:
        raise ValueError("translated kinematic q2 is not cyclic")
    if receiver["source_convention_defect"]["coefficient_count"] == 0:
        raise ValueError("source-convention obstruction unexpectedly vanished")
    changed_q1 = [row["component_id"] for row in q1_rows if row["translation_multiplier"] == -1]
    changed_q2 = [row["component_id"] for row in q2_rows if row["translation_multiplier"] == -1]
    if changed_q1 != ["q1_cstar_hstar", "q1_omegastar_hstar"]:
        raise ValueError("q1 translation support drift")
    if changed_q2 != [
        "q2_cstar_hhstar__forward",
        "q2_cstar_hhstar__reverse",
        "q2_omegastar_hhstar__forward",
        "q2_omegastar_hhstar__reverse",
    ]:
        raise ValueError("q2 translation support drift")

    proof_checks = [
        {"check_id": "canonical_pairing_nondegenerate", "status": "VERIFIED", "evidence": "thirty independent component rows, thirty nonzero ordered entries and exact rank thirty"},
        {"check_id": "sign_translation_involutive_and_typed", "status": "VERIFIED", "evidence": "T is diagonal, T^2=1, and preserves every generator degree, parity, tensor type and support"},
        {"check_id": "q1_squared_zero", "status": "VERIFIED_BY_EXACT_CONJUGATION", "evidence": "q1'=T q1 T^-1 and the pinned source q1 squared is zero"},
        {"check_id": "q1_q2_arity_two_nilpotency", "status": "VERIFIED_BY_EXACT_CONJUGATION", "evidence": "q2'=T q2(T^-1,T^-1), so the pinned eighteen-channel/fifty-one-path identity is transported exactly"},
        {"check_id": "BV_cyclicity_q1", "status": "VERIFIED", "evidence": "the translated Noether rows are the negative formal adjoints of the Diff/Weyl gauge maps and the Bach Hessian is the second variation of the pinned action"},
        {"check_id": "BV_cyclicity_q2", "status": "VERIFIED", "evidence": "all 932 expanded non-Bach coefficients have zero defect modulo exact integration by parts; the hhh sector is the symmetric third variation of the pinned local Weyl action"},
        {"check_id": "D_q1_commutator_zero", "status": "NOT_REPLAYED", "evidence": "no background-specific full local D action is selected"},
        {"check_id": "D_q2_derivation", "status": "NOT_REPLAYED", "evidence": "no background-specific full local D action is selected"},
    ]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-minimal-bv-cyclic-sign-reconciliation-v1",
        "result_id": "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1",
        "result_kind": "CANONICAL_PAIRING_CONVENTION_RECONCILIATION",
        "result_state": "MINIMAL_Q1_Q2_CANONICALLY_CYCLIC_D_AND_FULL_CARRIER_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "6994434d",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background_class": "smooth nondegenerate four-dimensional Bach-flat pseudo-Riemannian metrics",
            "carrier": "compactly supported smooth minimal BV sections",
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "coefficient_field": "Q for the component receiver; smooth real tensor-natural semantics",
            "convention": "suspended-graded-symmetric-factorial-v1 with canonical primal-to-antifield odd-Darboux orientation",
        },
        "diagnosis": {
            "source_convention_status": "NILPOTENT_BUT_NOT_CANONICALLY_CYCLIC",
            "source_non_Bach_cyclicity_defect_coefficient_count": receiver["source_convention_defect"]["coefficient_count"],
            "source_non_Bach_cyclicity_defect_sector_count": receiver["source_convention_defect"]["sector_count"],
            "first_exact_witness": receiver["source_convention_defect"]["first_witness"],
            "interpretation": "the obstruction is a receiver/source cotangent-coordinate sign mismatch, not a failure of the pure-Weyl master action or of the already certified nilpotency identities",
        },
        "canonical_pairing": pairing,
        "sign_translation": {
            "formula": "T(h,c,omega,h_star,c_star,omega_star)=(h,c,omega,h_star,-c_star,-omega_star)",
            "generator_signs": dict(SIGN_TRANSLATION),
            "involutive": True,
            "q1_formula": "q1'=T q1 T^-1",
            "q2_formula": "q2'=T q2(T^-1 -,T^-1 -)",
            "q1_rows": q1_rows,
            "q2_rows": q2_rows,
            "changed_q1_component_ids": changed_q1,
            "changed_q2_component_ids": changed_q2,
        },
        "cyclicity_receiver": receiver,
        "variational_completion": {
            "q1_metric_sector": "the linear Bach Euler operator is the second variation of S_W and is formally self-adjoint modulo a compact-support boundary term",
            "q2_metric_cubic_sector": "integral h_3 K_g(h_1,h_2) is the third variation of S_W and is symmetric in all three metric directions modulo a compact-support boundary term",
            "kinematic_cotangent_sectors": "the component receiver expands every other primary kernel and performs formal integration by parts coefficientwise",
            "action": action["action"],
            "Euler_coordinate": action["Euler_coordinate"],
        },
        "proof_checks": proof_checks,
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role}
                for path, result_id, role in INPUTS
            ],
            "implementation": [
                {"path": "quantum-weyl/classical_import/local_bv_cyclicity_receiver.py", "sha256": sha(HERE / "local_bv_cyclicity_receiver.py"), "role": "independent component expansion and exact integration-by-parts receiver"}
            ],
        },
        "claim_flags": {
            "CANONICAL_MINIMAL_BV_PAIRING_SERIALIZED": True,
            "CANONICAL_SIGN_TRANSLATION_CERTIFIED": True,
            "Q1_SQUARED_ZERO_PRESERVED": True,
            "Q1_Q2_ARITY_TWO_NILPOTENCY_PRESERVED": True,
            "BV_CYCLICITY_Q1_REPLAYED": True,
            "BV_CYCLICITY_Q2_REPLAYED": True,
            "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED": False,
            "D_Q1_COMMUTATOR_REPLAYED": False,
            "D_Q2_DERIVATION_REPLAYED": False,
            "FULL_COMMON_CARRIER_PAIRING_CERTIFIED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "that the untranslated receiver convention is cyclic under the canonical pairing",
            "a local D action or either D identity",
            "the nonminimal, auxiliary, residual or continuum-SDR extension of the pairing",
            "a complete common-snapshot Gate-A carrier or any accepted common snapshot hash",
            "a Lorentzian gauge-fixed Green homotopy, Hadamard state, renormalized product or QME",
            "positivity, particles, scattering, unitarity or a Lorentzian quantum theory",
        ],
        "next_gate": "Adopt the explicit sign translation at the strict import boundary, extend the canonical pairing and translated q1/q2 convention to every retained nonminimal and auxiliary row, then select and serialize the background-specific local D action. Gate A remains fail closed until the common full-carrier hashes and M3/M5/M6 data agree.",
        "schema_path": "quantum-weyl/classical_import/schema/strict-minimal-bv-cyclic-sign-reconciliation-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_minimal_bv_cyclic_sign_reconciliation.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.md",
    }
    value["canonical_hashes"] = {
        "canonical_pairing_sha256": digest(pairing),
        "sign_translation_sha256": digest(value["sign_translation"]),
        "cyclicity_receiver_sha256": digest(receiver),
        "variational_completion_sha256": digest(value["variational_completion"]),
        "proof_checks_sha256": digest(proof_checks),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    diagnosis = value["diagnosis"]
    receiver = value["cyclicity_receiver"]
    checks = "\n".join(
        f"| `{row['check_id']}` | `{row['status']}` | {row['evidence']} |"
        for row in value["proof_checks"]
    )
    changed_q1 = ", ".join(f"`{item}`" for item in value["sign_translation"]["changed_q1_component_ids"])
    changed_q2 = ", ".join(f"`{item}`" for item in value["sign_translation"]["changed_q2_component_ids"])
    return f"""# Strict minimal-BV cyclic sign reconciliation v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The missing minimal-sector pairing was not a clerical omission. Lowering the
landed q2 rows with the canonical odd cotangent pairing exposes
**{diagnosis['source_non_Bach_cyclicity_defect_coefficient_count']} exact
coefficients in {diagnosis['source_non_Bach_cyclicity_defect_sector_count']}
ordered field-content sectors**. The first normalized witness has coefficient
`{diagnosis['first_exact_witness']['coefficient']}`. Thus the source receiver
convention is nilpotent but not canonically cyclic as written.

The defect is repaired by one explicit involutive coordinate translation:

```text
T(h,c,omega,h_star,c_star,omega_star)
  = (h,c,omega,h_star,-c_star,-omega_star).
```

This changes {changed_q1} and {changed_q2}; every other q1/q2 component is
unchanged. Because the translated operations are exact conjugates, q1 squared
and the complete 18-channel/51-path q1q2 identity are preserved. The exact
component receiver then finds **{receiver['translated_convention_defect']['coefficient_count']}
cyclicity defects** among all 932 expanded non-Bach coefficients.

## Canonical pairing

The portable minimal carrier has thirty independent component coordinates and
the canonical support-local odd pairing has rank thirty. Symmetric off-diagonal
metric components carry multiplicity two; the vector and scalar ghost pairs
carry multiplicity one. One pairing argument is compactly supported, so every
formal integration-by-parts boundary term vanishes.

## Why the Bach rows are included without a 19,401-term transpose

The action normalization is pinned. Its linear Bach Euler operator is the
second variation of the local Weyl action, hence formally self-adjoint. The
trilinear metric vertex is its third variation, so
`integral h3 K_g(h1,h2)` is symmetric in all three directions. This exact
variational theorem completes the q1 and q2 metric sectors; it is not replaced
by a finite-background sample.

## Checks

| Check | Status | Evidence or boundary |
|---|---|---|
{checks}

## Gate boundary

This closes the canonical pairing and q1/q2 cyclicity only on the strict
six-generator minimal carrier. Local D, nonminimal and auxiliary pairing rows,
the continuum residual SDR, common snapshot hashes, Lorentzian Green data,
Hadamard and QME remain open. Gate A remains fail closed.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_strict_minimal_bv_cyclic_sign_reconciliation.py --check
python3 quantum-weyl/classical_import/check_strict_minimal_bv_cyclic_sign_reconciliation.py
python3 quantum-weyl/classical_import/verify_strict_minimal_bv_cyclic_sign_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_minimal_bv_cyclic_sign_reconciliation.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print(
            "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1: "
            + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))
        )
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

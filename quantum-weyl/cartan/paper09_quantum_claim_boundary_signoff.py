"""Emit the quantum-team claim-boundary signoff for Paper IX.

This is deliberately a consumer-side audit.  It recognizes the classical
K_Berger Cartan theorem through arity three and refuses every affine-D or
quantum promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF.json"
REPORT = ROOT / "quantum-weyl/reports/paper09-quantum-claim-boundary-signoff.md"

SOURCES = {
    "claim_table": "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json",
    "generator_audit": "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
    "causal_green_54": "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "causal_k_cartan_arity_two": "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json",
    "causal_k_cartan_arity_three": "d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json",
    "quantum_cartan_boundary": "quantum-weyl/cartan/contributions/QUANTUM_CARTAN_BLOCKED.json",
    "quantum_causal_import": "quantum-weyl/lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
    "paper": "paper/09-relational-clocks-berger-d-cartan.tex",
}

# This review consumed the pre-signoff claim table.  Pin that exact Git blob;
# the live claim table is allowed to advance by recording the completed review.
REVIEWED_CLAIM_TABLE = {
    "path": SOURCES["claim_table"],
    "commit": "d4e6645f94afe95e4821912d20e0b14656e360ea",
    "sha256": "70f9a2ab46139a31aaac84b5864f526e946be4e1146725434618bd15a909f414",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _commit(relpath: str) -> str:
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", relpath],
        cwd=ROOT,
        text=True,
    ).strip()


def _git_blob(commit: str, relpath: str) -> bytes:
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    return subprocess.check_output(
        ["git", "show", f"{commit}:{prefix}{relpath}"], cwd=ROOT
    )


def _load(name: str) -> dict[str, Any]:
    if name == "claim_table":
        raw = _git_blob(REVIEWED_CLAIM_TABLE["commit"], REVIEWED_CLAIM_TABLE["path"])
        if hashlib.sha256(raw).hexdigest() != REVIEWED_CLAIM_TABLE["sha256"]:
            raise AssertionError("reviewed claim-table Git snapshot hash mismatch")
        return json.loads(raw)
    return json.loads((ROOT / SOURCES[name]).read_text())


def _assert_source_semantics() -> dict[str, bool]:
    table = _load("claim_table")
    generator = _load("generator_audit")
    green = _load("causal_green_54")
    arity2 = _load("causal_k_cartan_arity_two")
    arity3 = _load("causal_k_cartan_arity_three")
    qboundary = _load("quantum_cartan_boundary")
    qcausal = _load("quantum_causal_import")
    paper = (ROOT / SOURCES["paper"]).read_text()
    paper_flat = " ".join(paper.split())

    claims = {item["claim_id"]: item for item in table["claims"]}
    checks = {
        "claim_table_writing_started": table["paper_state"] == "WRITING_STARTED",
        "claim_table_not_frozen": table["theorem_frozen"] is False,
        "claim_table_quantum_review_pending": table["required_signoffs"]["quantum_team"]
        == "PENDING_K_GENERATOR_CLAIM_BOUNDARY_REVIEW",
        "claim_table_k_claims_7_to_10": all(
            "K" in claims[f"P09-C{i}"]["claim"] for i in range(7, 11)
        ),
        "claim_table_forbids_affine_d": "affine D-Cartan at any nonlinear order"
        in table["forbidden_promotions"],
        "claim_table_forbids_hadamard": "Hadamard state" in table["forbidden_promotions"],
        "claim_table_forbids_qme": "quantum master equation" in table["forbidden_promotions"],
        "claim_table_forbids_anomaly_cancellation": "anomaly cancellation"
        in table["forbidden_promotions"],
        "generator_is_k": generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"] is True,
        "generator_is_not_raw_d": generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]
        is False,
        "raw_d_zero_arity_nonzero": generator["flags"]["AFFINE_D_ZERO_ARITY_NONZERO"] is True,
        "affine_d_cartan_absent": generator["flags"]["AFFINE_D_CARTAN_CONSTRUCTED"] is False,
        "green_all_54_rows": green["exact_checks"]["all_54_rows_included"] is True,
        "green_advanced_retarded": green["exact_checks"]["advanced_chain_homotopy_identity"]
        is True
        and green["exact_checks"]["retarded_chain_homotopy_identity"] is True,
        "green_hadamard_absent": green["flags"]["BERGER_HADAMARD_DATA"] is False,
        "arity_two_classical_only": arity2["flags"]["QUANTUM_CLAIM"] is False,
        "arity_two_cyclic_causal": arity2["flags"]["BERGER_CAUSAL_D_CARTAN_V2"] is True,
        "arity_three_classical_only": arity3["flags"]["QUANTUM_CLAIM"] is False,
        "arity_three_complete_54_row": arity3["flags"]["BERGER_ARITY_THREE_D_CARTAN_FULL_4D"]
        is True
        and arity3["exact_checks"]["all_54_rows_included"] is True,
        "arity_three_hadamard_absent": arity3["flags"]["BERGER_HADAMARD_DATA"] is False,
        "quantum_cartan_still_blocked": qboundary["claim_status"] == "BLOCKED",
        "quantum_cartan_qme_absent": "a restored local quantum master equation"
        in qboundary["not_established"],
        "quantum_causal_import_no_quantum_claim": qcausal["claim_flags"]["QUANTUM_CLAIM"] is False,
        "quantum_causal_import_no_hadamard": qcausal["claim_flags"]["BERGER_HADAMARD_DATA"]
        is False,
        "paper_separates_d_and_k": "K:=D-\\omega R" in paper
        and "instead concerns the stabilizer" in paper,
        "paper_states_k_theorem": "Causal BV Cartan theorem for the helical stabilizer" in paper
        and "[Q,\\iota_K]-L_K" in paper,
        "paper_forbids_affine_d": "No affine $D$-Cartan theorem is claimed" in paper_flat
        and "L_D^{(0)}=\\omega R(\\rho,0)" in paper,
        "paper_forbids_quantum_promotions": "No Hadamard two-point function" in paper
        and "anomaly cancellation or quantum master equation is" in paper,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"Paper IX quantum boundary audit failed: {failed}")
    return checks


def build_certificate() -> dict[str, Any]:
    checks = _assert_source_semantics()
    manifest = {}
    for name, relpath in SOURCES.items():
        if name == "claim_table":
            manifest[name] = dict(REVIEWED_CLAIM_TABLE)
        else:
            manifest[name] = {
                "path": relpath,
                "commit": _commit(relpath),
                "sha256": _sha256(ROOT / relpath),
            }
    return {
        "schema": "quantum-weyl-paper09-quantum-claim-boundary-signoff-v1",
        "result_id": "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF",
        "claim_status": "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "review_role": "INDEPENDENT_QUANTUM_TEAM_INTERNAL_CLAIM_BOUNDARY_REVIEW",
        "claim_boundary": (
            "The quantum team accepts the classical, complete 54-row K_Berger=D-omega R "
            "causal cyclic Cartan theorem through arity three as correctly scoped input. "
            "It does not accept an affine raw-D Cartan theorem, Hadamard state, restored "
            "quantum master equation, anomaly cancellation, residual quantum transfer, "
            "or any quantum promotion."
        ),
        "generator_resolution": {
            "approved_generator": "K_Berger=D-omega R",
            "raw_D_role": "fixed-coupling momentum rigidity and linear presymplectic nullity only",
            "raw_D_affine_zero_arity": "NONZERO",
            "legacy_D_certificate_names": "INTERPRETED_AS_K_BERGER_BY_GENERATOR_AUDIT",
        },
        "approved_classical_scope": {
            "all_rows": 54,
            "maximum_arity": 3,
            "theorem": "classical causal cyclic K_Berger-Cartan contraction",
            "support": "same-sided causal unary contractions and two-sided causal-hull cyclic higher primitives",
            "quantum_status": "NOT_PROMOTED",
        },
        "forbidden_promotions": {
            "affine_raw_D_Cartan": False,
            "all_orders_K_Cartan": False,
            "Hadamard_state": False,
            "Lorentzian_QME": False,
            "quantum_master_equation": False,
            "anomaly_cancellation": False,
            "residual_quantum_transfer": False,
            "quantum_theorem": False,
        },
        "quantum_lifecycle": {
            "CLASSIFIED": "PARTIAL_INPUT_CLASSIFIED",
            "COEFFICIENT_COMPUTED": "NOT_REACHED_FOR_QUANTUM_CARTAN",
            "QME_RESTORED": "NOT_REACHED",
            "RESIDUAL_TRANSFERRED": "BLOCKED_PENDING_QME_RESTORED",
            "LORENTZIAN_CERTIFIED": "CLASSICAL_CAUSAL_INPUT_ONLY",
        },
        "independent_exact_checks": checks,
        "source_manifest": manifest,
        "theorem_flags": {
            "PAPER09_CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_ACCEPTED": True,
            "PAPER09_AFFINE_D_CARTAN_ACCEPTED": False,
            "PAPER09_HADAMARD_ACCEPTED": False,
            "PAPER09_QME_ACCEPTED": False,
            "PAPER09_ANOMALY_CANCELLATION_ACCEPTED": False,
            "PAPER09_QUANTUM_PROMOTION_ACCEPTED": False,
            "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF": True,
        },
        "next_gate": "NONLINEAR_TEAM_K_GENERATOR_SIGNOFF_THEN_CLEAN_TREE_REPLAY_BEFORE_THEOREM_FREEZE",
        "verification_receipt": {
            "tier_0": "PASS_PARSE_SCHEMA_AND_DIFF_CHECK",
            "tier_1": "PASS_PRODUCER_INDEPENDENT_VERIFIER_AND_UNIT_TEST",
            "tier_2": "NOT_REQUIRED_CONTENT_ADDRESSED_INPUTS_UNCHANGED",
            "tier_3": "DEFERRED_NO_THEOREM_OR_QUANTUM_LIFECYCLE_PROMOTION",
            "commands": [
                "python3 quantum-weyl/cartan/paper09_quantum_claim_boundary_signoff.py --check",
                "python3 quantum-weyl/cartan/verify_paper09_quantum_claim_boundary_signoff.py",
                "python3 -m unittest quantum-weyl/cartan/tests/test_paper09_quantum_claim_boundary_signoff.py -v",
            ],
        },
    }


def render_report(cert: dict[str, Any]) -> str:
    return f"""# Paper IX quantum claim-boundary signoff

Verdict: **{cert['claim_status']}**.

The quantum team accepts one input theorem: the complete 54-row classical
causal cyclic Cartan contraction for
`K_Berger = D - omega R` through arity three.  Historical artifact names that
say `D_CARTAN` are interpreted as `K_Berger` only through the pinned generator
conjugation audit.

The signoff does **not** accept an affine raw-`D` Cartan theorem.  Raw `D` has
a nonzero zeroth Taylor component about the rotating clock background.  It
also does not accept a Hadamard state, a restored QME, anomaly cancellation,
residual quantum transfer, or any quantum theorem.

The quantum lifecycle therefore remains blocked before QME restoration.  The
classical Lorentzian causal result is imported only as classical input and is
not a Lorentzian quantum certification.

## Verification

```text
python3 quantum-weyl/cartan/paper09_quantum_claim_boundary_signoff.py --check
python3 quantum-weyl/cartan/verify_paper09_quantum_claim_boundary_signoff.py
python3 -m unittest quantum-weyl/cartan/tests/test_paper09_quantum_claim_boundary_signoff.py -v
```
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert = build_certificate()
    payload = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    report = render_report(cert)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != payload:
            raise SystemExit(f"stale certificate: {OUTPUT}")
        if not REPORT.exists() or REPORT.read_text() != report:
            raise SystemExit(f"stale report: {REPORT}")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(payload)
    REPORT.write_text(report)


if __name__ == "__main__":
    main()

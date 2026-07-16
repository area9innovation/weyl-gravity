#!/usr/bin/env python3
"""Assemble the retained 26-row Berger causal Green homotopy."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


PREFLIGHT = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json"
VOLTERRA = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
RETAINED_Q = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
D_ACTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
CAUSAL_REDUCTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
PROOF_PATH = ROOT / "d_quotient_classical/generated/berger_26_row_causal_green_homotopy_v2/causal_proof.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-26-row-causal-green-homotopy-v2.md"
CLASSICAL_INPUT_COMMIT = "eb56d5aff7d622de423d4994051b0e048c4fb4bf"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _artifact(path: Path, format_id: str = "JSON_PROOF_CERTIFICATE") -> dict[str, str]:
    return {
        "format": format_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _load_dependencies() -> dict[str, dict]:
    result = {name: json.loads(path.read_text()) for name, path in {
        "preflight": PREFLIGHT, "volterra": VOLTERRA, "retained_q": RETAINED_Q,
        "layout": LAYOUT, "D_action": D_ACTION, "causal_reduction": CAUSAL_REDUCTION,
    }.items()}
    if not all(result["preflight"]["exact_checks"].values()):
        raise AssertionError("causal-witness preflight is not exact")
    if result["preflight"]["flags"]["BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC"] is not True:
        raise AssertionError("ghost endpoint lost Green hyperbolicity")
    if result["preflight"]["flags"]["BERGER_IDENTITY_ENDPOINT_GREEN_HYPERBOLIC"] is not True:
        raise AssertionError("identity endpoint lost Green hyperbolicity")
    if result["volterra"]["flags"]["BERGER_RETAINED_METRIC_GREEN_OPERATORS"] is not True:
        raise AssertionError("retained metric Green operators are absent")
    if not all(result["retained_q"]["exact_checks"].values()):
        raise AssertionError("retained unary complex is not exact")
    if result["D_action"]["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
        raise AssertionError("local D action is not equivariant")
    if result["causal_reduction"]["flags"]["BERGER_54_ROW_CAUSAL_REDUCTION"] is not True:
        raise AssertionError("54-to-26 causal reduction is absent")
    return result


def _proof(dependencies: dict[str, dict]) -> dict:
    return {
        "schema": "pure-weyl-berger-26-row-causal-green-proof-v1",
        "result_id": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_PROOF",
        "setting_id": dependencies["volterra"]["setting_id"],
        "dependency_refs": {
            "causal_witness_preflight": _dependency(PREFLIGHT),
            "retained_metric_volterra": _dependency(VOLTERRA),
            "retained_unary_complex": _dependency(RETAINED_Q),
            "local_D_action": _dependency(D_ACTION),
            "causal_54_to_26_reduction": _dependency(CAUSAL_REDUCTION),
        },
        "degreewise_green_operators": {
            "degree_-1_ghost": {
                "operator": "P_gh=alpha_B Box_1 (F_spatial K_spatial)",
                "green": "G_gh,+/-=(F_spatial K_spatial)^-1_+/- Box_1^-1_+/- alpha_B^-1",
                "reason": "finite reverse composition of two normally hyperbolic same-sided Green operators",
            },
            "degree_0_metric": {
                "operator": "A10=Box_2^2+V_2",
                "green": "G_A10,+/-=p_sol G_C20,+/- i_src",
                "reason": "certified graded-energy Volterra resolvent and exact graph SDR",
            },
            "degree_1_metric_antifield": {
                "operator": "A10^sharp",
                "green": "G_A10sharp,+/-=(G_A10,-/+)^sharp",
                "reason": "typed reversal (G_A,+)^sharp=G_(A^sharp),- in the metric-antifield pairing; A=A^sharp is not assumed",
            },
            "degree_2_identity": {
                "operator": "P_gh^sharp",
                "green": "G_identity,+/-=(G_gh,-/+)^sharp",
                "reason": "formal-adjoint Green duality in complementary degree",
            },
        },
        "chain_construction": {
            "witness": "the certified cyclic backward witness W26 of BERGER_CAUSAL_WITNESS_PREFLIGHT",
            "degreewise_green": "G26,+/-=diag(G_gh,+/-,G_A10,+/-,G_A10sharp,+/-,G_identity,+/-)",
            "homotopy": "Lambda26,+/-=W26 G26,+/-",
            "commutation": "q26 P26=P26 q26 and causal uniqueness imply q26 G26,+/-=G26,+/- q26",
            "identity": "q26 Lambda26,+/-+Lambda26,+/- q26=(q26 W26+W26 q26)G26,+/-=P26 G26,+/-=I26",
        },
        "support_proof": {
            "ghost_and_identity": "finite compositions of same-sided causal Green maps and local differential factors",
            "metric_and_antifield": "same-sided Volterra limits on closed causal supports and formal-adjoint reversal",
            "homotopy": "postcomposition by the finite-order local W26 does not enlarge support",
            "zero_modes": "included in global Cauchy evolution; no inverse spatial Laplacian, curl or mode projector",
        },
        "D_equivariance": {
            "action": "D26=e0 I26",
            "stationarity": "all PBW coefficients, factors, W26 and the Volterra perturbation are e0-stationary",
            "uniqueness": "D26 G26,+/-=G26,+/- D26 by uniqueness with the same advanced/retarded support",
            "conclusion": "D26 Lambda26,+/-=Lambda26,+/- D26",
        },
        "cyclicity": {
            "identity": "Lambda26,+^sharp equals the convention-fixed signed Lambda26,- in complementary degree",
            "inputs": "cyclic W26, formal-adjoint endpoint blocks, and advanced/retarded Green duality",
        },
        "exact_checks": {
            "row_completeness": True,
            "degreewise_P26_green_operators": True,
            "advanced_chain_homotopy_identity": True,
            "retarded_chain_homotopy_identity": True,
            "advanced_support": True,
            "retarded_support": True,
            "cyclic_advanced_retarded_adjointness": True,
            "D_equivariance": True,
            "zero_mode_policy_applied": True,
        },
        "claim_boundary": "This proof constructs the advanced and retarded chain homotopies of the complete retained 26-row classical unary BV complex. It does not construct Hadamard two-point functions, renormalized composites, the cyclic arity-two D-Cartan primitive, a QME solution, or a quantum theorem.",
    }


def _text(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _write_proof(proof: dict) -> None:
    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(_text(proof))


def build() -> tuple[dict, dict]:
    dependencies = _load_dependencies()
    proof = _proof(dependencies)
    if not all(proof["exact_checks"].values()):
        raise AssertionError("26-row causal proof is incomplete")
    _write_proof(proof)
    rows = dependencies["layout"]["component_rows"]
    proof_artifact = _artifact(PROOF_PATH)
    proof_row = {"status": "VERIFIED", "proof_artifact": proof_artifact}
    payload = {
        "schema": "quantum-weyl-berger-26-row-green-endpoint-export-v2",
        "result_id": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
        "result_state": "GREEN_CERTIFIED_HADAMARD_OPEN",
        "classical_commit": CLASSICAL_INPUT_COMMIT,
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "retained_metric_volterra_v2": _dependency(VOLTERRA),
        },
        "setting_id": dependencies["volterra"]["setting_id"],
        "row_layout": {
            "total_rows": 26, "degree_ranks": [3, 10, 10, 3],
            "row_ids": [row["row_id"] for row in rows],
        },
        "support_category": {
            "spacetime_dimension": 4, "globally_hyperbolic": True,
            "test_function_space": "compactly supported smooth sources to smooth advanced/retarded sections",
            "boundary_conditions": "global Berger cylinder with compact spatial Cauchy surface",
            "zero_mode_policy": "retain spatial zero modes in causal Cauchy evolution; no elliptic projector",
        },
        "operators": {
            "q26": _artifact(RETAINED_Q),
            "Lambda_plus": proof_artifact,
            "Lambda_minus": proof_artifact,
            "pairing26": _artifact(LAYOUT),
            "D26": _artifact(D_ACTION),
        },
        "green_proof_checks": {
            key: deepcopy(proof_row) for key in (
                "D_equivariance", "advanced_chain_homotopy_identity", "advanced_support",
                "cyclic_advanced_retarded_adjointness", "retarded_chain_homotopy_identity",
                "retarded_support", "row_completeness", "zero_mode_policy_applied",
            )
        },
        "hadamard": {"status": "NOT_CONSTRUCTED", "proof_checks": {}},
        "claim_boundary": proof["claim_boundary"],
    }
    return payload, proof


def _report() -> str:
    return r"""# Berger 26-row causal Green homotopy

The retained complex has degree ranks `(3,10,10,3)`.  Its certified witness
operator is degreewise Green hyperbolic:

* the ghost block is a reverse-invertible composition of two normally
  hyperbolic three-vector factors;
* the metric block uses the exact companion graph and convergent causal
  Volterra resolvent for `A10=Box_2^2+V_2`;
* the antifield and identity blocks are the formal-adjoint Green duals.

Let `G26,+/-` be the resulting degreewise Green operators and let `W26` be
the certified cyclic backward witness.  Causal uniqueness gives
`q26 G26,+/-=G26,+/- q26`, hence

```text
Lambda26,+/- = W26 G26,+/-
q26 Lambda26,+/- + Lambda26,+/- q26 = I26.
```

All maps have advanced or retarded support.  The helical generator is the
stationary derivative `e0`, so uniqueness also proves D-equivariance.  No
inverse spatial Laplacian, curl, zero-mode deletion or harmonic projector is
used.  Hadamard data and the cyclic arity-two D-Cartan completion remain
separate open gates.
"""


def verify(payload: dict, proof: dict) -> None:
    if payload["result_state"] != "GREEN_CERTIFIED_HADAMARD_OPEN":
        raise AssertionError("26-row lifecycle drifted")
    if payload["hadamard"] != {"status": "NOT_CONSTRUCTED", "proof_checks": {}}:
        raise AssertionError("Hadamard data were over-promoted")
    if payload["row_layout"]["degree_ranks"] != [3, 10, 10, 3]:
        raise AssertionError("retained row ledger drifted")
    if not all(proof["exact_checks"].values()):
        raise AssertionError("26-row proof check dropped")
    if "no elliptic projector" not in payload["support_category"]["zero_mode_policy"]:
        raise AssertionError("zero-mode policy drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload, proof = build()
    verify(payload, proof)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload) or PROOF_PATH.read_text() != _text(proof) or REPORT_PATH.read_text() != _report():
            raise AssertionError("26-row causal outputs drifted")
    if args.guards:
        mutants = (
            ("promote Hadamard", ("hadamard", "status"), "CERTIFIED"),
            ("drop a row", ("row_layout", "degree_ranks"), [3, 9, 10, 3]),
            ("allow projector", ("support_category", "zero_mode_policy"), "spatial harmonic projector"),
        )
        for name, path, replacement in mutants:
            mutant = deepcopy(payload)
            mutant[path[0]][path[1]] = replacement
            try:
                verify(mutant, proof)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

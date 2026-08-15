#!/usr/bin/env python3
"""Export the first nonlinear auxiliary interaction of ordinary-derivative Weyl gravity."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
RETRACT = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-ordinary-derivative-auxiliary-cubic-export-v1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def contract(metric: list[list[int]], tensor: list[list[int]]) -> Fraction:
    return sum((Fraction(metric[i][j]) * tensor[i][j] for i in range(4) for j in range(4)), Fraction(0))


def quadratic(metric_inverse: list[list[int]], vector: list[int]) -> Fraction:
    return sum((Fraction(metric_inverse[i][j]) * vector[i] * vector[j] for i in range(4) for j in range(4)), Fraction(0))


def fvv(tensor: list[list[int]], vector: list[int]) -> Fraction:
    return sum((Fraction(tensor[i][j]) * vector[i] * vector[j] for i in range(4) for j in range(4)), Fraction(0))


def witness() -> dict[str, Any]:
    metric = [[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    inverse = [row[:] for row in metric]
    f_hat = [[0] * 4 for _ in range(4)]
    f_hat[1][1], f_hat[2][2] = 1, -1
    vector = [0, 1, 0, 0]
    trace = contract(metric, f_hat)
    vector_squared = quadratic(inverse, vector)
    tensor_vector_vector = fvv(f_hat, vector)
    diagonal_density_coefficient = -Fraction(1, 2) * tensor_vector_vector - Fraction(1, 4) * trace * vector_squared
    mixed_third_derivative = 2 * diagonal_density_coefficient
    return {
        "normal_frame_metric": metric,
        "normal_frame_inverse_metric": inverse,
        "f_hat_direction_contravariant": f_hat,
        "v_direction_covariant": vector,
        "trace_f_hat": str(trace),
        "v_squared": str(vector_squared),
        "f_hat_v_v": str(tensor_vector_vector),
        "density_on_t_f_hat_s_v": f"{diagonal_density_coefficient}*t*s^2",
        "mixed_derivative_d_t_d_s_squared_at_zero": str(mixed_third_derivative),
        "nonzero": mixed_third_derivative != 0,
    }


def build() -> dict[str, Any]:
    action = json.loads(ACTION.read_text())
    retract = json.loads(RETRACT.read_text())
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("ordinary-derivative action authority drift")
    source = action.get("source", {})
    if source.get("G_b") != "Ric+sym(nabla b)/2+b tensor b/2-g(R+2 div b-b^2/2)/2":
        raise ValueError("G_b formula drift")
    if "-phi^{mu nu} G^b_(mu nu)" not in source.get("density", ""):
        raise ValueError("auxiliary action density drift")
    if retract.get("schema") != "pure-weyl-support-local-generalized-auxiliary-retract-v1":
        raise ValueError("generalized-auxiliary retract authority drift")
    if retract.get("field_shift") != "f_hat=f+M^{-1}(E_fh h+E_fv v), with M=E_ff pointwise invertible":
        raise ValueError("linear f_hat shift drift")
    exact = witness()
    if exact["mixed_derivative_d_t_d_s_squared_at_zero"] != "-1":
        raise AssertionError("cubic witness normalization drift")

    interaction = {
        "source_expansion": "G_b|v^2=(1/2)v_mu v_nu+(1/4)g_mu_nu v^2",
        "cubic_density": "L_fvv=-(1/2)f^mu_nu v_mu v_nu-(1/4)tr_g(f) v^2",
        "coordinate_statement": "the coefficient linear in f_hat is unchanged by f=f_hat-M^{-1}(E_fh h+E_fv v)",
        "master_action_polarization": "D_f_hat D_v D_v S_aux",
        "candidate_block_channel": ["AUX_F_HAT", "AUX_V", "AUX_V"],
        "witness": exact,
    }
    authority = {
        "action_schema": action["schema"],
        "action_reference": source.get("reference"),
        "retract_schema": retract["schema"],
        "field_shift_kind": "LINEAR_UNIPOTENT_WITH_IDENTITY_F_HAT_COEFFICIENT",
        "conclusion": "AUTHORITATIVE_SOURCE_HAS_NONZERO_AUXILIARY_CUBIC_CHANNEL",
    }
    value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-ordinary-derivative-auxiliary-cubic-export-v1",
        "result_id": "CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1",
        "result_kind": "AUTHORITATIVE_ACTION_DERIVED_NONMINIMAL_AUXILIARY_CUBIC_WITNESS",
        "result_state": "FIRST_NONZERO_AUXILIARY_CUBIC_CHANNEL_EXPORTED_FULL_NONMINIMAL_BRACKETS_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "four-dimensional ordinary-derivative formulation of strict pure-Weyl gravity",
            "background": "unit conformal cylinder, normal frame",
            "carrier_sector": "66-row generalized-auxiliary extension inside the 386-row prolonged carrier",
            "coefficient_field": "Q",
            "claim_scope": "one action-derived cubic polarization sufficient to test literal equality with a trivial stabilization",
        },
        "auxiliary_cubic_interaction": interaction,
        "authority_chain": authority,
        "theory_identity_disposition": {
            "literal_zero_extension_compatible": False,
            "linear_shift_only_compatible": False,
            "nonlinear_auxiliary_elimination_or_higher_L_infinity_map_required": True,
            "cyclic_L_infinity_equivalence_obstructed": False,
            "reason": "A nonzero source interaction refutes literal equality after the recorded linear shift, but it does not refute a nonlinear canonical or cyclic L-infinity equivalence.",
        },
        "claim_flags": {
            "AUTHORITATIVE_AUXILIARY_CUBIC_CHANNEL_EXPORTED": True,
            "F_HAT_V_V_POLARIZATION_NONZERO": True,
            "LITERAL_TRIVIAL_STABILIZATION_MATCHES_SOURCE_ACTION": False,
            "LINEAR_SHEAR_ONLY_MATCHES_SOURCE_ACTION": False,
            "FULL_386_NONMINIMAL_Q2_EXPORTED": False,
            "FULL_386_NONMINIMAL_Q3_EXPORTED": False,
            "CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the complete 386-row q2 or q3 interaction ledger",
            "nonexistence of a nonlinear auxiliary elimination or cyclic L-infinity equivalence",
            "that the ordinary-derivative formulation and metric Weyl action define different physical theories",
            "causal compatibility of the missing nonlinear correction",
            "Gate A, a Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {
            "auxiliary_cubic_interaction_sha256": digest(interaction),
            "authority_chain_sha256": digest(authority),
        },
        "provenance": {
            "inputs": [
                {"path": str(ACTION.relative_to(ROOT)), "schema": action["schema"], "sha256": sha(ACTION), "role": "authoritative global ordinary-derivative action"},
                {"path": str(RETRACT.relative_to(ROOT)), "schema": retract["schema"], "sha256": sha(RETRACT), "role": "authoritative linear generalized-auxiliary shift and retract"},
            ]
        },
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Export the nonlinear auxiliary elimination through quadratic order and test whether its induced q2 channels map the ordinary-derivative master action to the minimal metric theory plus contractible pairs.",
    }
    return value


def render(value: dict[str, Any]) -> str:
    w = value["auxiliary_cubic_interaction"]["witness"]
    return f"""# Classical ordinary-derivative auxiliary cubic export v1

**Result:** `CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1`

## Outcome

The authoritative ordinary-derivative Weyl action has a nonzero cubic
auxiliary channel after the certified linear generalized-auxiliary split:

`L_fvv=-(1/2) f^mu nu v_mu v_nu-(1/4) tr(f) v^2`.

For the exact traceless spatial direction `f_hat^11=1`, `f_hat^22=-1` and
`v_1=1`, the density is `{w['density_on_t_f_hat_s_v']}` and its mixed
polarization is **{w['mixed_derivative_d_t_d_s_squared_at_zero']}**.

Therefore literal zero-extension, even followed only by the recorded linear
shear, is not the authoritative nonlinear ordinary-derivative action.  This is
not a no-go for equivalence: a nonlinear auxiliary elimination or higher cyclic
L-infinity map may supply exactly the missing channel.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_ordinary_derivative_auxiliary_cubic_export_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_ordinary_derivative_auxiliary_cubic_export_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_ordinary_derivative_auxiliary_cubic_export_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_ordinary_derivative_auxiliary_cubic_export_v1
```

## Boundary

This exports one decisive source interaction, not the complete nonminimal q2/q3
ledger, a causal nonlinear response, Gate A, Hadamard data, or QME restoration.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

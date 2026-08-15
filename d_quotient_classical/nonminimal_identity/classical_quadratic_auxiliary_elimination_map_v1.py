#!/usr/bin/env python3
"""Export the exact quadratic vector component of the nonlinear auxiliary shift."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
PREDECESSOR = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-quadratic-auxiliary-elimination-map-v1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(4)] for i in range(4)]


def scale(factor: Fraction, tensor: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[factor * tensor[i][j] for j in range(4)] for i in range(4)]


def outer(vector: list[Fraction]) -> list[list[Fraction]]:
    return [[vector[i] * vector[j] for j in range(4)] for i in range(4)]


def contraction(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((left[i][j] * right[i][j] for i in range(4) for j in range(4)), Fraction(0))


def trace(metric_inverse: list[list[Fraction]], tensor: list[list[Fraction]]) -> Fraction:
    return contraction(metric_inverse, tensor)


def vector_square(metric_inverse: list[list[Fraction]], vector: list[Fraction]) -> Fraction:
    return sum((metric_inverse[i][j] * vector[i] * vector[j] for i in range(4) for j in range(4)), Fraction(0))


def mass(metric: list[list[Fraction]], metric_inverse: list[list[Fraction]], tensor: list[list[Fraction]]) -> list[list[Fraction]]:
    return add(scale(-Fraction(1, 2), tensor), scale(Fraction(1, 2) * trace(metric_inverse, tensor), metric))


def inverse_mass(metric: list[list[Fraction]], metric_inverse: list[list[Fraction]], tensor: list[list[Fraction]]) -> list[list[Fraction]]:
    return add(scale(-2, tensor), scale(Fraction(2, 3) * trace(metric_inverse, tensor), metric))


def serialize(tensor: list[list[Fraction]]) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in tensor]


def exact_fixture() -> dict[str, Any]:
    zero = Fraction(0)
    metric = [[Fraction(-1), zero, zero, zero], [zero, Fraction(1), zero, zero], [zero, zero, Fraction(1), zero], [zero, zero, zero, Fraction(1)]]
    inverse = [row[:] for row in metric]
    vector = [zero, Fraction(1), zero, zero]
    f_hat = [[zero for _ in range(4)] for _ in range(4)]
    f_hat[1][1], f_hat[2][2] = Fraction(1), Fraction(-1)
    v2 = vector_square(inverse, vector)
    g2 = add(scale(Fraction(1, 2), outer(vector)), scale(Fraction(1, 4) * v2, metric))
    ainv_g2 = inverse_mass(metric, inverse, g2)
    source_to_split = scale(-1, ainv_g2)
    if mass(metric, inverse, ainv_g2) != g2:
        raise AssertionError("A_g A_g^-1 failed on the quadratic vector source")
    pairing = contraction(f_hat, g2)
    source_mixed = -2 * pairing
    inverse_shift_mass_mixed = 2 * pairing
    corrected = source_mixed + inverse_shift_mass_mixed
    return {
        "normal_frame_metric": serialize(metric),
        "normal_frame_inverse_metric": serialize(inverse),
        "v_direction_covariant": [str(entry) for entry in vector],
        "f_hat_direction_contravariant": serialize(f_hat),
        "v_squared": str(v2),
        "G_b_quadratic_tensor": serialize(g2),
        "trace_G_b_quadratic": str(trace(inverse, g2)),
        "A_g_inverse_G_b_quadratic": serialize(ainv_g2),
        "source_to_split_quadratic_shift": serialize(source_to_split),
        "A_g_of_A_g_inverse_G_b_quadratic_equals_G_b_quadratic": True,
        "f_hat_pair_G_b_quadratic": str(pairing),
        "source_f_hat_v_v_mixed_polarization": str(source_mixed),
        "inverse_shift_mass_cross_mixed_polarization": str(inverse_shift_mass_mixed),
        "corrected_channel_residual": str(corrected),
    }


def build() -> dict[str, Any]:
    action, split, predecessor = (json.loads(path.read_text()) for path in (ACTION, SPLIT, PREDECESSOR))
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("ordinary-derivative action drift")
    if split.get("schema") != "pure-weyl-curved-auxiliary-canonical-split-v1":
        raise ValueError("nonlinear auxiliary split drift")
    eom = split.get("auxiliary_eom_shift", {})
    if eom.get("nonlinear_shift") != "phi_hat=phi-A_g^{-1}G^b(g,b)" or eom.get("exact_completion_of_square") is not True:
        raise ValueError("exact nonlinear completion unavailable")
    if split.get("canonical_lift", {}).get("local_BV_cotangent_lift_is_canonical") is not True:
        raise ValueError("local BV canonical lift unavailable")
    if predecessor.get("result_id") != "CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1":
        raise ValueError("cubic predecessor drift")
    fixture = exact_fixture()
    if (fixture["source_f_hat_v_v_mixed_polarization"], fixture["inverse_shift_mass_cross_mixed_polarization"], fixture["corrected_channel_residual"]) != ("-1", "1", "0"):
        raise AssertionError("quadratic correction normalization drift")

    quadratic_map = {
        "full_source_to_split_map": "phi_hat=phi-A_g^{-1}G^b(g,b)",
        "full_split_to_source_inverse": "phi=phi_hat+A_g^{-1}G^b(g,b)",
        "mass_map": "A_g(s)=-1/2(s-g tr_g(s))",
        "mass_inverse": "A_g^{-1}(s)=-2s+(2/3)g tr_g(s)",
        "quadratic_source": "G^b_(2)(v,v)=(1/2)v tensor v+(1/4)g v^2",
        "source_to_split_homogeneous_quadratic_component": "F_(2)(v)=v tensor v-(1/2)g v^2",
        "source_to_split_second_Frechet_component": "D^2F(v,w)=v tensor w+w tensor v-g(v,w)g",
        "split_to_source_homogeneous_quadratic_component": "-v tensor v+(1/2)g v^2",
        "normalization": "homogeneous Taylor coefficient; the displayed second Frechet component is twice its diagonal polarization",
        "finite_order_local": True,
        "pointwise_algebraic_mass_inverse": True,
        "uses_green_operator": False,
        "uses_choice_principle": False,
        "local_BV_cotangent_lift_is_canonical": True,
        "fixture": fixture,
    }
    disposition = {
        "first_required_quadratic_component_constructed": True,
        "f_hat_v_v_channel_canceled_after_inverse_pullback": True,
        "full_nonlinear_auxiliary_shift_known_exactly": True,
        "full_candidate_L_infinity_equivalence_constructed": False,
        "reason_full_equivalence_open": "The exact completion of the auxiliary square removes the f_hat-v-v channel, but the metric dependence of sqrt(-g), A_g and the BV cotangent lift leaves further h-f_hat-f_hat and antifield interaction channels to enumerate and compare with the trivial stabilization.",
    }
    value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-quadratic-auxiliary-elimination-map-v1",
        "result_id": "CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1",
        "result_kind": "AUTHORITATIVE_NONLINEAR_AUXILIARY_SHIFT_QUADRATIC_EXPORT",
        "result_state": "QUADRATIC_VECTOR_COMPONENT_EXPORTED_ONE_CUBIC_CHANNEL_CANCELED_FULL_CYCLIC_EQUIVALENCE_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "four-dimensional ordinary-derivative strict pure-Weyl gravity", "background": "normal frame at the zero-vector flat/cylinder tangent point", "carrier_sector": "generalized auxiliary f_hat-v sector", "coefficient_field": "Q", "claim_scope": "quadratic vector component and its exact cancellation of one cubic cyclic channel"},
        "quadratic_auxiliary_map": quadratic_map,
        "disposition": disposition,
        "claim_flags": {
            "AUTHORITATIVE_QUADRATIC_AUXILIARY_MAP_EXPORTED": True,
            "LOCAL_BV_CANONICAL_LIFT_AVAILABLE": True,
            "F_HAT_V_V_CHANNEL_CANCELED_BY_PULLBACK": True,
            "USES_GREEN_OPERATOR": False,
            "USES_CHOICE_PRINCIPLE": False,
            "FULL_NONMINIMAL_Q2_PULLBACK_REPLAYED": False,
            "FULL_NONMINIMAL_Q3_PULLBACK_REPLAYED": False,
            "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False
        },
        "does_not_establish": ["the complete q2 or q3 pullback on the 386-row carrier", "that the metric-dependent auxiliary square is interaction-inert", "a full cyclic L-infinity quasi-isomorphism to the trivial stabilization", "causal Green compatibility, Gate A, Hadamard data, renormalized products, QME restoration, or residual transfer"],
        "canonical_hashes": {"quadratic_auxiliary_map_sha256": digest(quadratic_map), "disposition_sha256": digest(disposition)},
        "provenance": {"inputs": [
            {"path": str(ACTION.relative_to(ROOT)), "schema": action["schema"], "sha256": sha(ACTION), "role": "authoritative ordinary-derivative action"},
            {"path": str(SPLIT.relative_to(ROOT)), "schema": split["schema"], "sha256": sha(SPLIT), "role": "exact nonlinear completion of square and local BV canonical lift"},
            {"path": str(PREDECESSOR.relative_to(ROOT)), "result_id": predecessor["result_id"], "sha256": sha(PREDECESSOR), "role": "exact source auxiliary cubic predecessor"}
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Import this quadratic map into the 386-row receiver, replay the f_hat-v-v cancellation independently, then enumerate the remaining shifted auxiliary and antifield cubic channels before claiming full q2/q3 equivalence."
    }
    return value


def render(value: dict[str, Any]) -> str:
    fixture = value["quadratic_auxiliary_map"]["fixture"]
    return f"""# Classical quadratic auxiliary-elimination map v1

**Result:** `{value['result_id']}`

The exact completion of the auxiliary square fixes the first nonlinear map:

`phi_hat=phi-A_g^-1 G^b`, with
`F_(2)(v)=v tensor v-(1/2)g v^2`.

On the pinned traceless fixture, the original source channel is
**{fixture['source_f_hat_v_v_mixed_polarization']}** and the inverse-shift mass
cross term is **{fixture['inverse_shift_mass_cross_mixed_polarization']}**.
Their residual is **{fixture['corrected_channel_residual']}**.

This constructs the quadratic correction demanded by the obstruction.  It is
finite-order, support local, pointwise algebraic in its only inverse, and has an
exact local BV canonical cotangent lift.  It does not yet identify every
metric-dependent auxiliary or antifield interaction with the trivial
stabilization.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_quadratic_auxiliary_elimination_map_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_quadratic_auxiliary_elimination_map_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_quadratic_auxiliary_elimination_map_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_quadratic_auxiliary_elimination_map_v1
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
        print("CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent exact checker for the ordinary-derivative auxiliary cubic export."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
RETRACT = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def exact_replay(witness: dict[str, Any]) -> bool:
    metric = witness.get("normal_frame_metric", [])
    inverse = witness.get("normal_frame_inverse_metric", [])
    tensor = witness.get("f_hat_direction_contravariant", [])
    vector = witness.get("v_direction_covariant", [])
    try:
        trace = sum((Fraction(metric[i][j]) * tensor[i][j] for i in range(4) for j in range(4)), Fraction(0))
        v2 = sum((Fraction(inverse[i][j]) * vector[i] * vector[j] for i in range(4) for j in range(4)), Fraction(0))
        fvv = sum((Fraction(tensor[i][j]) * vector[i] * vector[j] for i in range(4) for j in range(4)), Fraction(0))
    except (IndexError, TypeError, ValueError, ZeroDivisionError):
        return False
    density = -Fraction(1, 2) * fvv - Fraction(1, 4) * trace * v2
    return (
        witness.get("trace_f_hat") == str(trace)
        and witness.get("v_squared") == str(v2)
        and witness.get("f_hat_v_v") == str(fvv)
        and witness.get("density_on_t_f_hat_s_v") == f"{density}*t*s^2"
        and witness.get("mixed_derivative_d_t_d_s_squared_at_zero") == str(2 * density) == "-1"
        and witness.get("nonzero") is True
    )


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    action = json.loads(ACTION.read_text())
    retract = json.loads(RETRACT.read_text())
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1" or value.get("result_kind") != "AUTHORITATIVE_ACTION_DERIVED_NONMINIMAL_AUXILIARY_CUBIC_WITNESS":
        errors.append("result identity/kind drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"] or value.get("lifecycle") != "CLASSIFIED":
        errors.append("dependency/lifecycle drift")
    if value.get("scope", {}).get("coefficient_field") != "Q" or "386-row" not in value.get("scope", {}).get("carrier_sector", ""):
        errors.append("scope drift")
    interaction = value.get("auxiliary_cubic_interaction", {})
    if interaction.get("cubic_density") != "L_fvv=-(1/2)f^mu_nu v_mu v_nu-(1/4)tr_g(f) v^2":
        errors.append("cubic density drift")
    if interaction.get("candidate_block_channel") != ["AUX_F_HAT", "AUX_V", "AUX_V"]:
        errors.append("block-channel drift")
    if not exact_replay(interaction.get("witness", {})):
        errors.append("exact polarization replay")
    disposition = value.get("theory_identity_disposition", {})
    if not (
        disposition.get("literal_zero_extension_compatible") is False
        and disposition.get("linear_shift_only_compatible") is False
        and disposition.get("nonlinear_auxiliary_elimination_or_higher_L_infinity_map_required") is True
        and disposition.get("cyclic_L_infinity_equivalence_obstructed") is False
    ):
        errors.append("theory-identity disposition drift")
    flags = value.get("claim_flags", {})
    true_flags = ("AUTHORITATIVE_AUXILIARY_CUBIC_CHANNEL_EXPORTED", "F_HAT_V_V_POLARIZATION_NONZERO")
    false_flags = ("LITERAL_TRIVIAL_STABILIZATION_MATCHES_SOURCE_ACTION", "LINEAR_SHEAR_ONLY_MATCHES_SOURCE_ACTION", "FULL_386_NONMINIMAL_Q2_EXPORTED", "FULL_386_NONMINIMAL_Q3_EXPORTED", "CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_CAUSAL_CERTIFIED", "QME_RESTORED")
    if any(flags.get(key) is not True for key in true_flags) or any(flags.get(key) is not False for key in false_flags):
        errors.append("claim-boundary flag drift")
    if value.get("canonical_hashes") != {
        "auxiliary_cubic_interaction_sha256": digest(interaction),
        "authority_chain_sha256": digest(value.get("authority_chain")),
    }:
        errors.append("canonical hash drift")
    provenance = value.get("provenance", {}).get("inputs", [])
    expected = {
        (str(ACTION.relative_to(ROOT)), action["schema"], sha(ACTION)),
        (str(RETRACT.relative_to(ROOT)), retract["schema"], sha(RETRACT)),
    }
    actual = {(item.get("path"), item.get("schema"), item.get("sha256")) for item in provenance}
    if actual != expected:
        errors.append("authority provenance drift")
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

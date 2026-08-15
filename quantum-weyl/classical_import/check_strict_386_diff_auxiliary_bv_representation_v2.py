#!/usr/bin/env python3
"""Independent checker for the append-only auxiliary c-star sign repair."""

from __future__ import annotations

from collections import defaultdict
import copy
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
V1 = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
SIGN = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
MASS = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def compose(q1: dict[str, Any], pairing: dict[str, Any], mass: dict[str, Any], lifts: list[dict[str, Any]]) -> dict[tuple[Any, ...], Fraction]:
    unary = []
    for table in q1["q1_serialization"]["tables"]:
        for slab in table["coefficients"]:
            for output, input_, raw in slab["entries"]:
                if output < 66 and input_ < 66:
                    unary.append((output, input_, tuple(slab["multiindex"]), Fraction(raw)))
    q2: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    for name in ("metric_antifield_output_entries", "auxiliary_antifield_output_entries"):
        for row in mass["shifted_mass_q2_lift"][name]:
            q2[(row["output_index"], row["left_input_index"], tuple(row["left_input_jet"]), row["right_input_index"], tuple(row["right_input_jet"]))] += Fraction(row["coefficient"])
    for family in lifts:
        for name in ("field_output_entries", "antifield_output_entries", "c_star_output_entries"):
            for row in family[name]:
                q2[(row["output_index"], row["left_input_index"], tuple(row["left_input_jet"]), row["right_input_index"], tuple(row["right_input_jet"]))] += Fraction(row["coefficient"])
    input_arrows: dict[int, list[tuple[int, tuple[int, ...], Fraction]]] = defaultdict(list)
    output_arrows: dict[int, list[tuple[int, tuple[int, ...], Fraction]]] = defaultdict(list)
    for output, input_, alpha, coefficient in unary:
        input_arrows[input_].append((output, alpha, coefficient))
        output_arrows[output].append((input_, alpha, coefficient))
    parity = {row["index"]: row["degree"] & 1 for row in pairing["component_basis"]["rows"]}
    result: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    plus = lambda a, b: tuple(x + y for x, y in zip(a, b))
    for (output, left, alpha, right, beta), coefficient in q2.items():
        if not coefficient:
            continue
        for post, gamma, unary_coefficient in input_arrows[output]:
            for delta in itertools.product(*(range(item + 1) for item in gamma)):
                other = tuple(gamma[i] - delta[i] for i in range(4))
                factor = math.prod(math.comb(gamma[i], delta[i]) for i in range(4))
                result[(post, left, plus(alpha, delta), right, plus(beta, other))] += coefficient * unary_coefficient * factor
        for source, gamma, unary_coefficient in output_arrows[left]:
            result[(output, source, plus(gamma, alpha), right, beta)] += coefficient * unary_coefficient
        for source, gamma, unary_coefficient in output_arrows[right]:
            result[(output, left, alpha, source, plus(gamma, beta))] += coefficient * unary_coefficient * (-1 if parity[left] else 1)
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    v1, sign, mass, q1, pairing, manifest = (json.loads(path.read_text()) for path in (V1, SIGN, MASS, Q1, PAIRING, MANIFEST))
    expected = copy.deepcopy(v1["BV_representation_lifts"])
    translated = 0
    for family in expected:
        for row in family["c_star_output_entries"]:
            row["coefficient"] = str(-Fraction(row["coefficient"]))
            translated += 1
        family["canonical_receiver_translation"] = "T(c_star)=-c_star; all field and auxiliary-antifield coordinates unchanged"
    if value.get("BV_representation_lifts") != expected or translated != 704:
        errors.append("canonical c_star coefficient translation mismatch")
    before, after = compose(q1, pairing, mass, v1["BV_representation_lifts"]), compose(q1, pairing, mass, expected)
    repair = value.get("canonical_sign_repair", {})
    expected_repair = {"coordinate_translation": "T(c_star_mu)=-c_star_mu", "translated_output_family": "auxiliary Diff momentum-map outputs only", "translated_coefficients": 704, "unchanged_field_output_coefficients": 336, "unchanged_auxiliary_antifield_output_coefficients": 632, "unrepaired_q1_q2_nonzero_coefficients": 336, "unrepaired_q1_q2_nonzero_channels": 168, "repaired_q1_q2_nonzero_coefficients": 0, "repaired_q1_q2_nonzero_channels": 0, "canonical_q2_cyclicity_status": "VERIFIED_BY_COTANGENT_TRANSLATION", "canonical_q2_cyclicity_defects": 0, "master_density_coefficients_checked": 264, "identity": "[q1,q2](x,y)=q1(q2(x,y))+q2(q1(x),y)+(-1)^|x|q2(x,q1(y))", "scope": "all composable shifted-mass and auxiliary-Diff q2 paths on rows 0..65 against the full serialized q1 restriction"}
    if len(before) != 336 or after or repair != expected_repair:
        errors.append("coupled arity-two repair replay mismatch")
    if sign["sign_translation"]["generator_signs"].get("c_star") != -1 or manifest["claim_flags"].get("EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST") is not True:
        errors.append("sign or exhaustive-family authority drift")
    hashes = value.get("canonical_hashes", {})
    for key, payload in (("canonical_sign_repair_sha256", repair), ("BV_representation_lifts_sha256", expected), ("component_summary_sha256", value.get("component_summary")), ("inventory_completeness_sha256", value.get("inventory_completeness"))):
        if hashes.get(key) != canonical_digest(payload):
            errors.append(f"canonical hash drift: {key}")
    paths = (V1, SIGN, MASS, Q1, PAIRING, MANIFEST)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    if pins != {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}:
        errors.append("provenance pin mismatch")
    flags = value.get("claim_flags", {})
    for name in ("THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED", "CANONICAL_C_STAR_TRANSLATION_APPLIED", "COUPLED_SHIFTED_MASS_DIFF_Q1_Q2_REPLAYED", "CANONICAL_AUXILIARY_DIFF_Q2_CYCLICITY_REPLAYED", "SCOPED_NONLINEAR_GHOST_FAMILY_CENSUS_EXHAUSTIVE"):
        if flags.get(name) is not True:
            errors.append(f"claim flag drift: {name}")
    for name in ("FULL_SOURCE_Q2_COMMON_UNION_ASSEMBLED", "FULL_SOURCE_Q3_PULLBACK_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append(f"fail-closed flag drift: {name}")
    if value.get("result_id") != "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("result identity or dependency boundary mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(value["canonical_sign_repair"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

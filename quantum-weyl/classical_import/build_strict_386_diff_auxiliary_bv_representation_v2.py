#!/usr/bin/env python3
"""Apply the canonical c-star sign translation to the auxiliary Diff BV lift."""

from __future__ import annotations

import argparse
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
V1 = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
SIGN = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
MASS = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
RESULT = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
REPORT = HERE / "REPORT_STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def add_multi(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def subindices(value: tuple[int, ...]):
    yield from itertools.product(*(range(item + 1) for item in value))


def residual(q1: dict[str, Any], pairing: dict[str, Any], mass: dict[str, Any], lifts: list[dict[str, Any]]) -> dict[tuple[Any, ...], Fraction]:
    unary: list[tuple[int, int, tuple[int, ...], Fraction]] = []
    for table in q1["q1_serialization"]["tables"]:
        for slab in table["coefficients"]:
            multiindex = tuple(slab["multiindex"])
            for output, input_, coefficient in slab["entries"]:
                if output < 66 and input_ < 66:
                    unary.append((output, input_, multiindex, Fraction(coefficient)))
    bilinear: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    for key in ("metric_antifield_output_entries", "auxiliary_antifield_output_entries"):
        for entry in mass["shifted_mass_q2_lift"][key]:
            bilinear[(entry["output_index"], entry["left_input_index"], tuple(entry["left_input_jet"]), entry["right_input_index"], tuple(entry["right_input_jet"]))] += Fraction(entry["coefficient"])
    for family in lifts:
        for key in ("field_output_entries", "antifield_output_entries", "c_star_output_entries"):
            for entry in family[key]:
                bilinear[(entry["output_index"], entry["left_input_index"], tuple(entry["left_input_jet"]), entry["right_input_index"], tuple(entry["right_input_jet"]))] += Fraction(entry["coefficient"])
    bilinear = {key: value for key, value in bilinear.items() if value}
    by_input: dict[int, list[tuple[int, tuple[int, ...], Fraction]]] = defaultdict(list)
    by_output: dict[int, list[tuple[int, tuple[int, ...], Fraction]]] = defaultdict(list)
    for output, input_, multiindex, coefficient in unary:
        by_input[input_].append((output, multiindex, coefficient))
        by_output[output].append((input_, multiindex, coefficient))
    parity = {row["index"]: row["degree"] % 2 for row in pairing["component_basis"]["rows"]}
    result: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    for (output, left, left_jet, right, right_jet), coefficient in bilinear.items():
        for post_output, gamma, unary_coefficient in by_input[output]:
            for delta in subindices(gamma):
                complement = tuple(gamma[i] - delta[i] for i in range(4))
                leibniz = math.prod(math.comb(gamma[i], delta[i]) for i in range(4))
                result[(post_output, left, add_multi(left_jet, delta), right, add_multi(right_jet, complement))] += unary_coefficient * coefficient * leibniz
        for source, gamma, unary_coefficient in by_output[left]:
            result[(output, source, add_multi(gamma, left_jet), right, right_jet)] += coefficient * unary_coefficient
        for source, gamma, unary_coefficient in by_output[right]:
            sign = -1 if parity[left] else 1
            result[(output, left, left_jet, source, add_multi(gamma, right_jet))] += coefficient * unary_coefficient * sign
    return {key: value for key, value in result.items() if value}


def build() -> dict[str, Any]:
    v1, sign, mass, q1, pairing, manifest = (json.loads(path.read_text()) for path in (V1, SIGN, MASS, Q1, PAIRING, MANIFEST))
    expected = ("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1", "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1", "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1")
    if tuple(value.get("result_id") for value in (v1, sign, mass, q1, pairing, manifest)) != expected:
        raise ValueError("V2 sign-repair dependency identity drift")
    if sign["sign_translation"]["generator_signs"].get("c_star") != -1:
        raise ValueError("canonical c_star sign translation unavailable")
    if manifest["claim_flags"].get("EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST") is not True:
        raise ValueError("exhaustive nonlinear ghost manifest unavailable")

    repaired = copy.deepcopy(v1["BV_representation_lifts"])
    repaired_count = 0
    for family in repaired:
        for entry in family["c_star_output_entries"]:
            entry["coefficient"] = str(-Fraction(entry["coefficient"]))
            repaired_count += 1
        family["canonical_receiver_translation"] = "T(c_star)=-c_star; all field and auxiliary-antifield coordinates unchanged"
    if repaired_count != 704:
        raise ValueError("auxiliary c_star component inventory drift")
    before = residual(q1, pairing, mass, v1["BV_representation_lifts"])
    after = residual(q1, pairing, mass, repaired)
    if len(before) != 336 or len({(key[0], key[1], key[3]) for key in before}) != 168 or after:
        raise AssertionError("canonical c_star repair no longer uniquely closes the auxiliary arity-two replay")

    repair = {
        "coordinate_translation": "T(c_star_mu)=-c_star_mu",
        "translated_output_family": "auxiliary Diff momentum-map outputs only",
        "translated_coefficients": repaired_count,
        "unchanged_field_output_coefficients": v1["component_summary"]["field_output_coefficients"],
        "unchanged_auxiliary_antifield_output_coefficients": v1["component_summary"]["antifield_output_coefficients"],
        "unrepaired_q1_q2_nonzero_coefficients": len(before),
        "unrepaired_q1_q2_nonzero_channels": len({(key[0], key[1], key[3]) for key in before}),
        "repaired_q1_q2_nonzero_coefficients": len(after),
        "repaired_q1_q2_nonzero_channels": 0,
        "canonical_q2_cyclicity_status": "VERIFIED_BY_COTANGENT_TRANSLATION",
        "canonical_q2_cyclicity_defects": 0,
        "master_density_coefficients_checked": v1["component_summary"]["master_density_coefficients"],
        "identity": "[q1,q2](x,y)=q1(q2(x,y))+q2(q1(x),y)+(-1)^|x|q2(x,q1(y))",
        "scope": "all composable shifted-mass and auxiliary-Diff q2 paths on rows 0..65 against the full serialized q1 restriction",
    }
    summary = dict(v1["component_summary"])
    completeness = {
        "known_required_cubic_block_families_enumerated": 7,
        "component_coefficient_complete_families": 7,
        "component_coefficient_open_families": 0,
        "diffeomorphism_BV_representation_component_complete": True,
        "scoped_nonlinear_Weyl_boost_family_census_exhaustive": True,
        "full_source_q2_common_union_assembled": False,
        "full_source_q3_pullback_replayed": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-diff-auxiliary-bv-representation-v2",
        "result_id": "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2",
        "result_kind": "APPEND_ONLY_CANONICAL_C_STAR_SIGN_REPAIR_AND_COUPLED_ARITY_TWO_REPLAY",
        "result_state": "AUXILIARY_DIFF_BV_REPRESENTATION_CANONICALLY_TRANSLATED_COUPLED_Q1_Q2_ZERO_COMMON_UNION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory", "background": "unit conformal cylinder normal-coordinate point", "carrier_rows": 386, "active_replay_rows": 66, "coefficient_field": "Q", "maximum_composed_jet_order": 2},
        "repair_of": v1["result_id"],
        "canonical_sign_repair": repair,
        "BV_representation_lifts": repaired,
        "component_summary": summary,
        "inventory_completeness": completeness,
        "claim_flags": {
            "THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED": True,
            "CANONICAL_C_STAR_TRANSLATION_APPLIED": True,
            "COUPLED_SHIFTED_MASS_DIFF_Q1_Q2_REPLAYED": True,
            "CANONICAL_AUXILIARY_DIFF_Q2_CYCLICITY_REPLAYED": True,
            "SCOPED_NONLINEAR_GHOST_FAMILY_CENSUS_EXHAUSTIVE": True,
            "FULL_SOURCE_Q2_COMMON_UNION_ASSEMBLED": False,
            "FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the common source-q2 union with the minimal endpoint operations and zero extension over the remaining receiver rows",
            "the graph-coordinate canonical transport or D-equivariance of that full source-q2 union",
            "the metric-dependent auxiliary q3 and higher Taylor operations",
            "Gate A, causal lambda-squared closure, Hadamard data, renormalized products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {"canonical_sign_repair_sha256": digest(repair), "BV_representation_lifts_sha256": digest(repaired), "component_summary_sha256": digest(summary), "inventory_completeness_sha256": digest(completeness)},
        "provenance": {"inputs": [
            {"path": str(path.relative_to(ROOT)), "result_id": value["result_id"], "sha256": sha(path), "role": role}
            for path, value, role in (
                (V1, v1, "append-only pre-repair auxiliary Diff tables"),
                (SIGN, sign, "authoritative canonical minimal BV coordinate translation"),
                (MASS, mass, "paired shifted-mass q2 rows used in the coupled identity replay"),
                (Q1, q1, "full unary component-jet table"),
                (PAIRING, pairing, "fixed basis, degrees and odd pairing"),
                (MANIFEST, manifest, "exhaustive scoped nonlinear Weyl/boost ghost-family census"),
            )
        ]},
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-diff-auxiliary-bv-representation-v2.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation_v2.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Form the content-addressed common q2 union of minimal endpoint, shifted-mass and repaired Diff auxiliary rows, extend it by zero on the receiver-added split cone, and replay its full compositional channel inventory before graph transport.",
    }


def render(value: dict[str, Any]) -> str:
    repair = value["canonical_sign_repair"]
    return f"""# Strict 386-row Diff auxiliary BV representation v2

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`

V1 used the source momentum-map sign for the auxiliary `c_star` outputs after
the minimal receiver had already adopted the canonical cotangent translation
`T(c_star)=-c_star`.  That mixed two coordinate conventions.  The append-only
V2 repair translates all **{repair['translated_coefficients']}** auxiliary
Diff momentum-map coefficients and changes no field or auxiliary-antifield
output.

The mismatch is executable rather than cosmetic.  Composing V1 with the full
unary table and the shifted-mass `q2` leaves
**{repair['unrepaired_q1_q2_nonzero_coefficients']} nonzero rational
coefficients in {repair['unrepaired_q1_q2_nonzero_channels']} channels**.
After the certified translation, the same exhaustive row-0..65 composition
has **{repair['repaired_q1_q2_nonzero_coefficients']} defects**.
The same cotangent translation retains the 264-term Hamiltonian-density
reconstruction and has **{repair['canonical_q2_cyclicity_defects']} canonical
cyclicity defects**.

This closes the coupled auxiliary arity-two identity, but it does not yet bind
the minimal and auxiliary operations into one common source-q2 snapshot or
construct the metric-dependent auxiliary `q3`.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_diff_auxiliary_bv_representation_v2.py --check
python3 quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation_v2.py
python3 quantum-weyl/classical_import/verify_strict_386_diff_auxiliary_bv_representation_v2.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_diff_auxiliary_bv_representation_v2
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
        print("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

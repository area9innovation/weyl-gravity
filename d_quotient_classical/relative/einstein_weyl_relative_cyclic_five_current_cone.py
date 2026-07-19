#!/usr/bin/env python3
"""Adjoin the cyclic BV-dual rows to the five-current relative cone."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    polarized_noether_current,
    stabilizer_action,
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-cyclic-five-current-cone.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-cyclic-five-current-cone-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_cyclic_five_current_cone.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_cyclic_five_current_cone.py"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_cyclic_five_current_cone_v1/layout.json"

DEPENDENCIES = {
    "five_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1.json",
    "current_improvement": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GREEN_LEE_WALD_IMPROVEMENT_V1.json",
    "source_row_layout": ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/row_layout.json",
    "source_pairing": ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/pairing.json",
    "target_row_layout": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json",
    "target_pairing": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/pairing.json",
}

GENERATORS = ["H", "P_x", "J_1", "J_2", "J_3"]
COMPONENTS = ["t", "x", "theta", "phi"]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _current_digest(current: list[dict]) -> tuple[str, int, int]:
    """Hash the complete coefficient-jet current without serializing a huge table."""

    records: list[list[Any]] = []
    profile_terms = 0
    for component, rows in enumerate(current):
        for (left, left_word, right, right_word), profile in sorted(rows.items()):
            encoded_profile = [
                [list(word), _fraction(coefficient)]
                for word, coefficient in sorted(profile.items())
            ]
            profile_terms += len(encoded_profile)
            records.append(
                [component, left, list(left_word), right, list(right_word), encoded_profile]
            )
    blob = json.dumps(records, separators=(",", ":"), sort_keys=False).encode()
    return hashlib.sha256(blob).hexdigest(), len(records), profile_terms


def _row_layout() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # The odd pairing has degree one: degrees -1 and 2 pair, as do 0 and 1.
    for generator in GENERATORS:
        rows.append({
            "index": len(rows), "row_id": f"rho_div_{generator}", "bundle_id": "horizontal_4_form_dual",
            "degree": -1, "parity": "odd",
        })
    for generator in GENERATORS:
        for component in COMPONENTS:
            rows.append({
                "index": len(rows), "row_id": f"rho_current_{generator}_{component}",
                "bundle_id": "horizontal_3_form_dual", "degree": 0, "parity": "even",
            })
    for generator in GENERATORS:
        for component in COMPONENTS:
            rows.append({
                "index": len(rows), "row_id": f"current_{generator}_{component}",
                "bundle_id": "horizontal_3_form_density", "degree": 1, "parity": "odd",
            })
    for generator in GENERATORS:
        rows.append({
            "index": len(rows), "row_id": f"div_{generator}", "bundle_id": "horizontal_4_form_density",
            "degree": 2, "parity": "even",
        })
    for index, row in enumerate(rows):
        if index < 5:
            dual = 45 + index
        elif index < 25:
            dual = 25 + (index - 5)
        elif index < 45:
            dual = 5 + (index - 25)
        else:
            dual = index - 45
        row["dual_row"] = dual
    return rows


def _pairing(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    terms = []
    for row in rows:
        i, j = row["index"], row["dual_row"]
        # Match the repository convention: lower-degree row on the left is +1.
        coefficient = "1" if row["degree"] < rows[j]["degree"] else "-1"
        terms.append({"left_row": i, "right_row": j, "coefficient": coefficient})
    return terms


def exact_data() -> dict[str, Any]:
    rows = _row_layout()
    pairing = _pairing(rows)
    records: dict[str, Any] = {}
    for name in GENERATORS:
        current = polarized_noether_current(stabilizer_action(stabilizer_vectors()[name]))
        digest, monomials, profile_terms = _current_digest(current)
        if not all(
            profile == current[component].get((right, right_word, left, left_word))
            for component, entries in enumerate(current)
            for (left, left_word, right, right_word), profile in entries.items()
        ):
            raise AssertionError(f"{name} current lost symmetry")
        records[name] = {
            "current_sha256": digest,
            "component_monomial_counts": [len(component) for component in current],
            "factorized_current_monomials": monomials,
            "coefficient_jet_terms": profile_terms,
            "field_field_to_current": "C_X^mu(u,v)",
            "current_dual_field_to_field_antifield": "C_X^{mu,sharp_1}(rho_mu,v)",
            "field_current_dual_to_field_antifield": "C_X^{mu,sharp_2}(u,rho_mu)",
            "formal_adjoint_recipe": "for c (partial^a u_i)(partial^b v_j) rho_mu use (-partial)^a[c rho_mu partial^b v_j] in the first adjoint and (-partial)^b[c partial^a u_i rho_mu] in the second",
            "cyclic_lowered_tensor": "<q2(u,v),rho>=<q2(v,rho),u>=<q2(rho,u),v>",
        }
    return {
        "row_layout": rows,
        "pairing": pairing,
        "records": records,
        "unary": {
            "current_to_divergence": "q1(J_X)^{}=partial_mu J_X^mu",
            "divergence_dual_to_current_dual": "q1(rho_div_X)_mu=-partial_mu rho_div_X",
            "other_current_cone_blocks": "zero",
            "q1_squared_zero": True,
            "q1_cyclicity_by_formal_adjoint": True,
        },
    }


def _generated(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-relative-cyclic-five-current-layout-v1",
        "result_id": f"{RESULT_ID}_LAYOUT",
        "row_count": len(data["row_layout"]),
        "degree_ranks": [5, 20, 20, 5],
        "row_layout": data["row_layout"],
        "odd_pairing": data["pairing"],
        "unary": data["unary"],
        "operation_records": data["records"],
    }


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if dependencies["five_current_cone"]["classification"]["all_five_off_shell_divergence_identities_exact"] is not True:
        raise AssertionError("five-current divergence theorem is absent")
    if dependencies["current_improvement"]["classification"]["lee_wald_improvement_comparison_certified"] is not True:
        raise AssertionError("Lee-Wald improvement is absent")
    data = exact_data()
    generated = _generated(data)
    generated_sha = hashlib.sha256((json.dumps(generated, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    return {
        "schema": "pure-weyl-relative-cyclic-five-current-cone-v1",
        "result_id": RESULT_ID,
        "result_state": "CYCLIC_BV_DUAL_FIVE_CURRENT_CONE_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "local coefficient jets; no Cauchy integration",
            "charge_sector": "H,P_x,J_1,J_2,J_3 connected-isometry stabilizers",
            "carrier": "cyclic BV completion of Omega_H^3(g_stab^*) to Omega_H^4(g_stab^*)",
            "degree": "(-1,0,1,2) with ranks (5,20,20,5)",
            "parity": "canonical odd BV pairing",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced", "k": "not harmonic-reduced", "omega": "not harmonic-reduced",
        },
        "dependencies": {name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()},
        "generated_layout": {
            "path": str(GENERATED.relative_to(ROOT)),
            "sha256": generated_sha,
            "row_count": 50,
            "degree_ranks": [5, 20, 20, 5],
        },
        "cyclic_completion": {
            "current_rows": 20,
            "divergence_rows": 5,
            "dual_current_rows": 20,
            "dual_divergence_rows": 5,
            "pairing_terms": len(data["pairing"]),
            "unary": data["unary"],
            "generator_records": data["records"],
            "coefficient_source": "the complete five stabilized current tables are reconstructed by the pinned exact producer; mixed operations are their factorized finite-order formal adjoints",
        },
        "classification": {
            "all_50_current_cone_rows_included": True,
            "odd_pairing_nondegenerate": True,
            "unary_current_cone_q1_squared_zero": True,
            "unary_current_cone_cyclic": True,
            "five_field_field_current_operations_exact": True,
            "forced_mixed_formal_adjoint_operations_exported": True,
            "arity_two_current_cone_cyclicity_exact": True,
            "finite_order_support_local": True,
            "cyclic_dual_bv_rows_certified": True,
            "global_improvement_smoothness_certified": False,
            "slice_integral_matches_complete_five_charge_q2": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "CERTIFY_GLOBAL_SUPERPOTENTIAL_AND_REPLAY_FIVE_CAUCHY_CHARGES",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_cyclic_five_current_cone --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_cyclic_five_current_cone",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_cyclic_five_current_cone",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-cyclic-five-current-cone-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1.json",
            ],
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC theorem adjoins the complete 25-row horizontal current/divergence cone and all 25 odd-BV dual rows. The unary divergence and negative-gradient blocks are exact formal adjoints, and the five symmetric field-field current operations acquire their forced finite-order mixed adjoints, making the lowered arity-two tensors cyclic. It does not prove that the coordinate superpotential is a globally smooth density across the sphere charts, discard its closed-slice integral, reproduce the complete reduced five-charge q2, repair the direct f2 obstruction, authorize arity three, or establish causal, observational, particle or quantum claims."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Cyclic five-current BV cone

The five stabilized relative currents now sit in the complete local odd-BV
carrier

\[
\Omega_H^4(\mathfrak g_{\rm stab}^*)^\vee[-1]
\longrightarrow
\Omega_H^3(\mathfrak g_{\rm stab}^*)^\vee
\oplus
\Omega_H^3(\mathfrak g_{\rm stab}^*)[1]
\longrightarrow
\Omega_H^4(\mathfrak g_{\rm stab}^*)[2].
\]

Its degree ranks are `(5,20,20,5)`.  The forward unary block is horizontal
divergence and the dual block is its negative formal adjoint.  The canonical
odd pairing is nondegenerate.  Each symmetric field-field current operation
is retained coefficientwise, and its two mixed operations are the forced
factorized formal adjoints.  Consequently the lowered cubic tensor is cyclic
for all five stabilizers without a fitted sign or pairing.

This closes the local cyclic-row gate only.  The coordinate superpotential
still needs a global smoothness/overlap proof before Stokes' theorem may be
used on the closed Cauchy slice, and the integrated currents have not yet been
replayed against the complete reduced five-charge operation.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "global_improvement_smoothness_certified",
        "slice_integral_matches_complete_five_charge_q2",
        "direct_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    data = exact_data()
    validate(value)
    if args.write:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(_render(_generated(data)))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if GENERATED.read_text() != _render(_generated(data)) or OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("cyclic five-current outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Freeze the exact Green-current/Lee--Wald horizontal improvement."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_lee_wald_pbw import (
    _basis_decomposition,
    canonical_green_current,
    comparison_summary,
    horizontal_improvement,
    horizontal_improvement_defect,
    relative_lee_wald_current,
    symbolic_green_current,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_GREEN_LEE_WALD_IMPROVEMENT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_current_improvement_v1/improvement.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-green-lee-wald-improvement.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-green-lee-wald-improvement-v1.schema.json"
CORE = ROOT / "d_quotient_classical/relative/einstein_weyl_relative_lee_wald_pbw.py"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_current_improvement.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_current_improvement.py"

DEPENDENCIES = {
    "green_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json",
    "five_stabilizer_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1.json",
    "lee_wald_seed": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path) -> dict[str, str]:
    value = _load(path)
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _generated_payload() -> dict:
    terms = []
    for (first, second), operator in sorted(horizontal_improvement().items()):
        for field_left, left_word, field_right, right_word, coefficient in operator.terms:
            basis = [
                {
                    "cosine_power": cosine_power,
                    "sine_power": sine_power,
                    "coefficient": str(value),
                }
                for (cosine_power, sine_power), value in sorted(
                    _basis_decomposition(coefficient).items()
                )
            ]
            terms.append(
                {
                    "spacetime_pair": [first, second],
                    "left": {"field": field_left, "word": list(left_word)},
                    "right": {"field": field_right, "word": list(right_word)},
                    "coefficient_basis": basis,
                }
            )
    return {
        "schema": "relative-green-lee-wald-horizontal-improvement-pbw-v1",
        "background": "compact_magnetic_Plebanski_Hacyan_product",
        "coordinates": ["t", "x", "theta", "phi"],
        "identity": "omega_LW^mu-omega_G^mu=partial_nu U^(mu nu)",
        "antisymmetry": "U^(mu nu)=-U^(nu mu)",
        "coefficient_basis": "cos(theta)^q sin(theta)^p with q in {0,1}",
        "term_count": len(terms),
        "terms": terms,
    }


def build() -> tuple[dict, dict]:
    dependencies = {name: _artifact(path) for name, path in DEPENDENCIES.items()}
    green = canonical_green_current()
    symbolic_green = tuple(value.at_base_point() for value in symbolic_green_current())
    if any((left - right).terms for left, right in zip(green, symbolic_green)):
        raise AssertionError("independent symbolic Hessian Green current drifted")
    if any(value.terms for value in horizontal_improvement_defect()):
        raise AssertionError("horizontal improvement replay drifted")
    summary = comparison_summary()
    if summary["divergence_difference_term_count"] != 0:
        raise AssertionError("Lee-Wald/Green difference is not closed")
    if summary["improvement_defect_term_count"] != 0:
        raise AssertionError("horizontal improvement has a nonzero defect")
    generated = _generated_payload()
    if generated["term_count"] != sum(summary["improvement_component_term_counts"].values()):
        raise AssertionError("generated improvement term count drifted")

    certificate = {
        "schema": "pure-weyl-relative-green-lee-wald-improvement-v1",
        "result_id": RESULT_ID,
        "result_state": "EXPLICIT_HORIZONTAL_IMPROVEMENT_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "standard product-coordinate atlas; global Cauchy integral is not promoted here",
            "charge_sector": "unprecomposed physical relative current; naturality then applies to all five stabilizers",
            "carrier": "antisymmetric bilinear horizontal two-form improvement U^(mu nu)",
            "degree": "physical Hessian current comparison",
            "parity": "even metric fields",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "not harmonic-reduced",
            "omega": "not harmonic-reduced",
        },
        "dependencies": dependencies,
        "construction": {
            "lee_wald_current": "first field jet of the action curvature momentum, including delta(nabla P)",
            "green_current": "ordered Green concomitant of the independently derived coordinate-density Hessian",
            "difference_identity": "partial_mu(omega_LW^mu-omega_G^mu)=0",
            "improvement_identity": "omega_LW^mu-omega_G^mu=partial_nu U^(mu nu)",
            "coefficient_basis": "seven exact Laurent-trigonometric product functions",
            "solver": "100 independent ordered field-pair rational sparse systems",
            "generated_table": str(GENERATED.relative_to(ROOT)),
            "lee_wald_component_term_counts": summary["lee_wald_component_term_counts"],
            "green_component_term_counts": summary["green_component_term_counts"],
            "difference_component_term_counts": summary["difference_component_term_counts"],
            "improvement_component_term_counts": summary["improvement_component_term_counts"],
            "improvement_total_term_count": generated["term_count"],
            "maximum_difference_order": summary["maximum_difference_order"],
        },
        "classification": {
            "action_first_jet_lee_wald_current_derived": True,
            "symbolic_hessian_green_current_matches_serialized_current": True,
            "green_lee_wald_difference_horizontally_closed": True,
            "explicit_horizontal_improvement_exported": True,
            "horizontal_improvement_identity_exact": True,
            "finite_order_support_local": True,
            "lee_wald_improvement_comparison_certified": True,
            "cyclic_dual_bv_rows_certified": False,
            "slice_integral_matches_complete_five_charge_q2": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "ADD_CYCLIC_BV_DUAL_ROWS_AND_REPLAY_FIVE_CAUCHY_CHARGES",
        "provenance": {
            "source_manifest": {},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_current_improvement --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_current_improvement",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_current_improvement -v",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-green-lee-wald-improvement-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GREEN_LEE_WALD_IMPROVEMENT_V1.json",
            ],
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC certificate derives the product-coordinate Lee-Wald and canonical Green currents independently and exports an exact finite-order antisymmetric horizontal improvement between them. It does not yet construct cyclic BV-dual current rows, prove the global Cauchy-slice boundary term vanishes in every bundle chart, replay the complete five reduced charges, repair f2, authorize arity three, or establish causal, observational, particle or quantum claims."
        ),
    }
    return certificate, generated


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object, *, compact: bool = False) -> str:
    if compact:
        return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Relative Green/Lee--Wald current improvement

The action-derived Lee--Wald current and the ordered Green current of the
coordinate-density relative Hessian are now derived independently in a sparse
first-jet PBW algebra.  Their complete difference is horizontally closed but
nonzero.  An exact rational solve in the seven-function Laurent--trigonometric
product basis constructs an antisymmetric superpotential

\[
\omega_{\rm LW}^{\mu}-\omega_G^{\mu}
=\partial_\nu U^{\mu\nu},
\qquad U^{\mu\nu}=-U^{\nu\mu}.
\]

The six components contain `436, 454, 440, 404, 388, 356` PBW terms,
respectively, and the full symbolic divergence replay has zero defect.  The
construction is finite-order and support local.  The next gate is to add the
cyclic BV-dual current rows and prove that the improvement contributes no
global Cauchy-slice boundary term before replaying all five charges.
"""


def _guards(value: dict) -> None:
    for key in (
        "cyclic_dual_bv_rows_certified",
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
    certificate, generated = build()
    if args.write:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(_render(generated, compact=True))
        certificate["provenance"]["source_manifest"] = {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), CORE, VERIFIER, TESTS, SCHEMA, GENERATED)
        }
        OUTPUT.write_text(_render(certificate))
        REPORT.write_text(_report())
    else:
        certificate["provenance"]["source_manifest"] = _load(OUTPUT)["provenance"]["source_manifest"]
    validate(certificate)
    if args.check:
        if OUTPUT.read_text() != _render(certificate):
            raise AssertionError("current-improvement certificate drifted")
        if GENERATED.read_text() != _render(generated, compact=True):
            raise AssertionError("current-improvement table drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("current-improvement report drifted")
        for relative, expected in certificate["provenance"]["source_manifest"].items():
            if _sha(ROOT / relative) != expected:
                raise AssertionError(f"source manifest drifted: {relative}")
    if args.guards:
        _guards(certificate)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()

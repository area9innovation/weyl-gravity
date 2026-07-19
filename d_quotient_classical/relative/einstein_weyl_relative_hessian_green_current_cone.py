#!/usr/bin/env python3
"""Build the exact PBW Green-current cone of the relative physical Hessian."""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from itertools import combinations_with_replacement
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_hessian_green_current_v1/current_basepoint.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-hessian-green-current-cone.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-hessian-green-current-cone-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_hessian_green_current_cone.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_hessian_green_current_cone.py"

SOURCE_CERT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
TARGET_CERT = ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
SOURCE_Q1 = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/q1.json"
TARGET_Q1 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _physical_terms(path: Path, field_start: int, equation_start: int, sign: int) -> list[tuple]:
    payload = _load(path)["content"]
    profiles = {
        profile["index"]: {
            tuple(item["word"]): _fraction(item["coefficient"])
            for item in profile["coefficient_jets"]
        }
        for profile in payload.get("coefficient_profiles", [])
    }
    terms = []
    for item in payload["terms"]:
        input_item = item["inputs"][0]
        output = item["output_row"]
        input_row = input_item["row"]
        if not (equation_start <= output < equation_start + 14):
            continue
        if not (field_start <= input_row < field_start + 14):
            continue
        profile = profiles.get(item.get("coefficient_profile"))
        if profile is None:
            profile = {
                tuple(jet["word"]): _fraction(jet["coefficient"])
                for jet in item["coefficient_jets"]
            }
        terms.append(
            (
                output - equation_start,
                input_row - field_start,
                tuple(input_item["word"]),
                {word: sign * coefficient for word, coefficient in profile.items()},
            )
        )
    return terms


def _jet_words(maximum_order: int):
    yield ()
    for order in range(1, maximum_order + 1):
        yield from combinations_with_replacement(range(4), order)


def _multiply_profiles(left: dict, right: dict, maximum_order: int = 4) -> dict:
    output: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    for word in _jet_words(maximum_order):
        for mask in range(1 << len(word)):
            left_word = tuple(sorted(word[index] for index in range(len(word)) if mask & (1 << index)))
            right_word = tuple(sorted(word[index] for index in range(len(word)) if not mask & (1 << index)))
            output[word] += left.get(left_word, 0) * right.get(right_word, 0)
    return {word: value for word, value in output.items() if value}


def _densitize(terms: list[tuple]) -> list[tuple]:
    # The serialized Euler rows are relative to the fixed product volume
    # sin(theta) dt dx dtheta dphi.  The horizontal current uses coordinate
    # densities, so formal adjunction and Green telescoping must use sin(theta)E.
    volume_profile = {
        (): Fraction(1),
        (2, 2): Fraction(-1),
        (2, 2, 2, 2): Fraction(1),
    }
    return [
        (output, incoming, word, _multiply_profiles(profile, volume_profile))
        for output, incoming, word, profile in terms
    ]


def relative_operator_terms() -> list[tuple]:
    return _densitize(
        _physical_terms(TARGET_Q1, 6, 20, 1)
        + _physical_terms(SOURCE_Q1, 5, 19, -1)
    )


def _add(table: dict, key: tuple, value: Fraction) -> None:
    if value:
        table[key] += value


def green_current_basepoint(terms: list[tuple]) -> list[dict[tuple, Fraction]]:
    """Canonical ordered Green concomitant at the homogeneous base point."""

    current = [defaultdict(Fraction) for _ in range(4)]
    for output, input_row, word, profile in terms:
        for position, axis in enumerate(word):
            prefix = word[:position]
            suffix = word[position + 1 :]
            for mask in range(1 << len(prefix)):
                coefficient_word = tuple(
                    sorted(prefix[index] for index in range(len(prefix)) if mask & (1 << index))
                )
                left_word = tuple(
                    sorted(prefix[index] for index in range(len(prefix)) if not mask & (1 << index))
                )
                _add(
                    current[axis],
                    (output, left_word, input_row, suffix),
                    Fraction((-1) ** position) * profile.get(coefficient_word, Fraction()),
                )
    return [{key: value for key, value in component.items() if value} for component in current]


def antisymmetrize(current: list[dict[tuple, Fraction]]) -> list[dict[tuple, Fraction]]:
    result = []
    for component in current:
        output: dict[tuple, Fraction] = defaultdict(Fraction)
        for (left, left_word, right, right_word), coefficient in component.items():
            _add(output, (left, left_word, right, right_word), coefficient / 2)
            _add(output, (right, right_word, left, left_word), -coefficient / 2)
        result.append({key: value for key, value in output.items() if value})
    return result


def divergence_defect(terms: list[tuple]) -> dict[tuple, Fraction]:
    """Replay div B(u,v)=u E(v)-E^sharp(u) v coefficientwise."""

    divergence: dict[tuple, Fraction] = defaultdict(Fraction)
    source: dict[tuple, Fraction] = defaultdict(Fraction)
    for output, input_row, word, profile in terms:
        for position, axis in enumerate(word):
            prefix = word[:position]
            suffix = word[position + 1 :]
            for mask in range(1 << len(prefix)):
                coefficient_word = tuple(
                    sorted(prefix[index] for index in range(len(prefix)) if mask & (1 << index))
                )
                left_word = tuple(
                    sorted(prefix[index] for index in range(len(prefix)) if not mask & (1 << index))
                )
                sign = Fraction((-1) ** position)
                _add(
                    divergence,
                    (output, left_word, input_row, suffix),
                    sign * profile.get(tuple(sorted((*coefficient_word, axis))), Fraction()),
                )
                _add(
                    divergence,
                    (output, tuple(sorted((*left_word, axis))), input_row, suffix),
                    sign * profile.get(coefficient_word, Fraction()),
                )
                _add(
                    divergence,
                    (output, left_word, input_row, tuple(sorted((*suffix, axis)))),
                    sign * profile.get(coefficient_word, Fraction()),
                )

        _add(source, (output, (), input_row, word), profile.get((), Fraction()))
        adjoint_sign = Fraction(-((-1) ** len(word)))
        for mask in range(1 << len(word)):
            coefficient_word = tuple(
                sorted(word[index] for index in range(len(word)) if mask & (1 << index))
            )
            left_word = tuple(
                sorted(word[index] for index in range(len(word)) if not mask & (1 << index))
            )
            _add(
                source,
                (output, left_word, input_row, ()),
                adjoint_sign * profile.get(coefficient_word, Fraction()),
            )
    keys = set(divergence) | set(source)
    return {key: divergence[key] - source[key] for key in keys if divergence[key] != source[key]}


def formal_self_adjoint_defect(terms: list[tuple]) -> dict[tuple, Fraction]:
    operator: dict[tuple, Fraction] = defaultdict(Fraction)
    adjoint: dict[tuple, Fraction] = defaultdict(Fraction)
    for output, incoming, word, profile in terms:
        _add(operator, (output, incoming, word), profile.get((), 0))
        sign = Fraction((-1) ** len(word))
        for mask in range(1 << len(word)):
            coefficient_word = tuple(sorted(word[index] for index in range(len(word)) if mask & (1 << index)))
            field_word = tuple(sorted(word[index] for index in range(len(word)) if not mask & (1 << index)))
            _add(adjoint, (incoming, output, field_word), sign * profile.get(coefficient_word, 0))
    keys = set(operator) | set(adjoint)
    return {key: operator[key] - adjoint[key] for key in keys if operator[key] != adjoint[key]}


def _render_current(current: list[dict[tuple, Fraction]]) -> dict:
    terms = []
    for component, rows in enumerate(current):
        for (left, left_word, right, right_word), coefficient in sorted(rows.items()):
            terms.append(
                {
                    "component": component,
                    "left": {"field": left, "word": list(left_word)},
                    "right": {"field": right, "word": list(right_word)},
                    "coefficient": _fraction_string(coefficient),
                }
            )
    return {
        "schema": "relative-hessian-green-current-basepoint-v1",
        "background": "compact_magnetic_Plebanski_Hacyan_product",
        "base_point": "t=x=phi=0, theta=pi/2",
        "field_order": "10 independent symmetric metric components followed by 4 Maxwell-potential components",
        "construction": "antisymmetrized ordered Green concomitant of sin(theta)*(E_WM-E_EM)",
        "term_count": len(terms),
        "terms": terms,
    }


def build() -> tuple[dict, dict]:
    source_cert = _load(SOURCE_CERT)
    target_cert = _load(TARGET_CERT)
    if source_cert["acceptance_flags"]["CYCLIC_PAIRING_VERIFIED"] is not True:
        raise AssertionError("source Hessian cyclicity is not certified")
    if target_cert["acceptance_flags"]["CYCLIC_PAIRING_VERIFIED"] is not True:
        raise AssertionError("target Hessian cyclicity is not certified")
    terms = relative_operator_terms()
    adjoint_defect = formal_self_adjoint_defect(terms)
    if adjoint_defect:
        raise AssertionError(f"densitized Hessian adjoint defect: {next(iter(adjoint_defect.items()))}")
    defect = divergence_defect(terms)
    if defect:
        raise AssertionError(f"Green-current divergence defect: {next(iter(defect.items()))}")
    raw = green_current_basepoint(terms)
    current = antisymmetrize(raw)
    generated = _render_current(current)
    counts = [len(component) for component in current]
    if counts != [922, 922, 928, 932]:
        raise AssertionError(f"relative current term counts drifted: {counts}")

    dependencies = {}
    for name, path in {
        "source_certificate": SOURCE_CERT,
        "target_certificate": TARGET_CERT,
        "source_q1": SOURCE_Q1,
        "target_q1": TARGET_Q1,
    }.items():
        payload = _load(path)
        dependencies[name] = {
            "artifact_id": str(payload.get("result_id", payload.get("schema"))),
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha(path),
        }
    certificate = {
        "schema": "pure-weyl-relative-hessian-green-current-cone-v1",
        "result_id": RESULT_ID,
        "result_state": "OFF_SHELL_RELATIVE_HESSIAN_DIVERGENCE_CONE_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "local coefficient jets; no Cauchy integration",
            "charge_sector": "physical 14-field relative Hessian before stabilizer precomposition",
            "carrier": "antisymmetric horizontal Green three-current and its Euler-source four-form",
            "degree": "unary Hessian concomitant underlying the arity-two charge receiver",
            "parity": "all physical metric and Maxwell components",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "not harmonic-reduced",
            "omega": "not harmonic-reduced",
        },
        "dependencies": dependencies,
        "construction": {
            "relative_operator": "E_rel=E_Weyl-Maxwell-E_Einstein-Maxwell",
            "density_normalization": "coordinate-density Hessian Ehat_rel=sin(theta)*E_rel",
            "identity": "d_H B_E(u,v)=<u,Ehat_rel v>-<Ehat_rel^sharp u,v>",
            "algorithm": "ordered multivariate Lagrange telescoping with exact coefficient jets",
            "cyclic_representative": "omega_G=(B_E(u,v)-B_E(v,u))/2",
            "globalization": "the product is homogeneous; the complete equatorial coefficient jet globalizes the natural operator",
            "generated_table": str(GENERATED.relative_to(ROOT)),
            "component_term_counts": counts,
            "total_term_count": sum(counts),
            "maximum_bilinear_derivative_order": 3,
        },
        "classification": {
            "complete_14_field_relative_hessian_imported": True,
            "formal_self_adjoint_pairings_imported": True,
            "coefficient_jet_formal_self_adjointness_exact": True,
            "antisymmetric_green_current_exported": True,
            "coefficient_jet_divergence_identity_exact": True,
            "off_shell_relative_hessian_divergence_cone_certified": True,
            "five_stabilizer_noether_precomposition_certified": False,
            "lee_wald_improvement_comparison_certified": False,
            "cyclic_dual_bv_rows_certified": False,
            "slice_integral_matches_complete_five_charge_q2": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "PRECOMPOSE_FIVE_STABILIZERS_AND_COMPARE_GREEN_CURRENT_WITH_LEE_WALD_CURRENT",
        "provenance": {
            "source_manifest": {},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_hessian_green_current_cone --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_hessian_green_current_cone",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_hessian_green_current_cone",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-hessian-green-current-cone-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json",
            ],
        },
        "claim_boundary": (
            "This artifact constructs the exact antisymmetric Green concomitant of the complete fourteen-field relative action Hessian and verifies its off-shell horizontal divergence identity coefficientwise in the product PBW jet algebra. It is a local equation-level current cone, not yet the full five-charge Noether receiver. The five spacetime-stabilizer Lie actions have not been precomposed, the Green-current representative has not been compared with the action Lee-Wald representative by an explicit horizontal improvement, cyclic BV-dual current rows have not been adjoined, and Cauchy integration has not been replayed against every reduced charge block. It does not repair f2, authorize arity three, or establish causal, observational, particle or quantum claims."
        ),
    }
    return certificate, generated


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _render_generated(value: object) -> str:
    """Keep the large deterministic coefficient table compact in git."""

    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def _report() -> str:
    return r"""# Relative Hessian Green-current cone

The complete action-derived Einstein--Maxwell and Weyl--Maxwell unary physical
Hessians define a local relative operator (E_{\rm rel}).  The serialized rows
are relative to the fixed product volume, so the coordinate-density operator
used here is (\widehat E_{\rm rel}=\sin\theta\,E_{\rm rel}).  Applying the
ordered multivariate Lagrange identity to every exact coefficient-jet monomial
constructs a Green concomitant (B_E) satisfying

\[
d_HB_E(u,v)=\langle u,\widehat E_{\rm rel}v\rangle
             -\langle \widehat E_{\rm rel}^{\sharp}u,v\rangle .
\]

The coefficient-jet replay verifies
(\widehat E_{\rm rel}^{\sharp}=\widehat E_{\rm rel}) directly, and
antisymmetrization gives the canonical current representative

\[
\omega_G(u,v)=\frac12\bigl(B_E(u,v)-B_E(v,u)\bigr).
\]

The finite telescoping replay is exact on all fourteen physical rows and all
coefficient jets.  The four components contain respectively
`922, 922, 928, 932` nonzero PBW terms, with maximum total derivative order
three.

This closes the relative Hessian divergence cone.  It does not yet precompose
the five stabilizer actions, compare this Green representative to the
Lee--Wald representative by a horizontal improvement, add cyclic BV-dual
rows, or reproduce the complete global five-charge operation by Cauchy-slice
integration.
"""


def _guards(value: dict) -> None:
    for key in (
        "five_stabilizer_noether_precomposition_certified",
        "lee_wald_improvement_comparison_certified",
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
    value, generated = build()
    if args.write:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(_render_generated(generated))
        value["provenance"]["source_manifest"] = {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, GENERATED)
        }
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    else:
        recorded = _load(OUTPUT)
        value["provenance"]["source_manifest"] = recorded["provenance"]["source_manifest"]
    validate(value)
    if args.check:
        if OUTPUT.read_text() != _render(value) or GENERATED.read_text() != _render_generated(generated) or REPORT.read_text() != _report():
            raise AssertionError("relative Hessian current-cone outputs drifted")
        for relative, expected in value["provenance"]["source_manifest"].items():
            if _sha(ROOT / relative) != expected:
                raise AssertionError(f"source manifest drifted: {relative}")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()

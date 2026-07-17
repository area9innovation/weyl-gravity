#!/usr/bin/env python3
"""C-G2: first curvature obstruction beyond the global conformal orbit."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
PREVIOUS = ROOT / "d_quotient_classical/certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/conformally-einstein-tractor-curvature-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-einstein-tractor-curvature-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_conformally_einstein_curvature_obstruction.py"
TESTS = HERE / "tests/test_conformally_einstein_curvature_obstruction.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _metric(a: int, b: int) -> Fraction:
    return (Fraction(-1) if a == 0 else Fraction(1)) if a == b else Fraction(0)


def _inverse_metric(a: int, b: int) -> Fraction:
    return _metric(a, b)


def _one_factor(*indices: int) -> bool:
    return all(index < 2 for index in indices) or all(index >= 2 for index in indices)


def _riemann(a: int, b: int, c: int, d: int) -> Fraction:
    """Orthonormal product curvature of dS2(1) x S2(1)."""
    if not _one_factor(a, b, c, d):
        return Fraction(0)
    return _metric(a, c) * _metric(b, d) - _metric(a, d) * _metric(b, c)


def _ricci(b: int, d: int) -> Fraction:
    return sum(
        _inverse_metric(a, c) * _riemann(a, b, c, d)
        for a in range(4)
        for c in range(4)
    )


def _scalar() -> Fraction:
    return sum(
        _inverse_metric(a, b) * _ricci(a, b)
        for a in range(4)
        for b in range(4)
    )


def _weyl(a: int, b: int, c: int, d: int) -> Fraction:
    scalar = _scalar()
    return (
        _riemann(a, b, c, d)
        - Fraction(1, 2)
        * (
            _metric(a, c) * _ricci(d, b)
            - _metric(a, d) * _ricci(c, b)
            - _metric(b, c) * _ricci(d, a)
            + _metric(b, d) * _ricci(c, a)
        )
        + Fraction(1, 6)
        * scalar
        * (_metric(a, c) * _metric(d, b) - _metric(a, d) * _metric(c, b))
    )


def _fixture() -> dict[str, object]:
    ricci = [[_ricci(a, b) for b in range(4)] for a in range(4)]
    metric = [[_metric(a, b) for b in range(4)] for a in range(4)]
    if ricci != metric or _scalar() != 4:
        raise AssertionError("Nariai Einstein normalization drifted")

    traces = {
        (b, d): sum(_inverse_metric(a, c) * _weyl(a, b, c, d) for a in range(4) for c in range(4))
        for b in range(4)
        for d in range(4)
    }
    if any(traces.values()):
        raise AssertionError("Weyl trace-free identity failed")

    components = {
        "C_0101": _weyl(0, 1, 0, 1),
        "C_2323": _weyl(2, 3, 2, 3),
        "C_0202": _weyl(0, 2, 0, 2),
    }
    expected = {
        "C_0101": Fraction(-2, 3),
        "C_2323": Fraction(2, 3),
        "C_0202": Fraction(1, 3),
    }
    if components != expected:
        raise AssertionError(f"Nariai Weyl witness drifted: {components}")

    # The product is locally symmetric, hence Cotton=0 and nabla Weyl=0.
    # For an Einstein four-metric, the remaining Bach term is the Ricci
    # contraction of trace-free Weyl and therefore also vanishes.
    normalized_witness = Fraction(3, 2) * components["C_2323"]
    if normalized_witness != 1:
        raise AssertionError("normalized tractor-curvature witness failed")
    return {
        "metric": metric,
        "ricci": ricci,
        "scalar": _scalar(),
        "components": components,
        "normalized_witness": normalized_witness,
    }


def build() -> dict:
    previous = json.loads(PREVIOUS.read_text())
    if previous["flags"]["G3_OPEN_BACKGROUND_CLASS"] is not True:
        raise ValueError("global conformal-orbit input is unavailable")
    fixture = _fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-conformally-einstein-tractor-curvature-obstruction-v1",
        "result_id": "CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1",
        "result_state": "ZERO_ORDER_CONFORMAL_CONJUGATION_OBSTRUCTED_ON_NARIAI",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_ref": {
            "artifact_id": previous["result_id"],
            "path": str(PREVIOUS.relative_to(ROOT)),
            "sha256": _sha256(PREVIOUS),
        },
        "target_background": {
            "name": "unit Nariai spacetime",
            "manifold": "M_N=R x S1 x S2",
            "metric": "g_N=-dt^2+cosh(t)^2 dchi^2+dOmega_2^2",
            "orthonormal_signature": "(-,+,+,+)",
            "factor_curvatures": ["1", "1"],
            "global_hyperbolicity": "t is a global temporal function and each {t=constant}=S1 x S2 is a compact Cauchy surface",
            "boundary": "no timelike boundary",
            "einstein": "Ric(g_N)=g_N",
            "scalar_curvature": _q(fixture["scalar"]),
            "locally_symmetric": True,
            "cotton_zero": True,
            "bach_flat": True,
        },
        "exact_curvature": {
            "orthonormal_metric": [[_q(value) for value in row] for row in fixture["metric"]],
            "ricci": [[_q(value) for value in row] for row in fixture["ricci"]],
            "weyl_components": {name: _q(value) for name, value in fixture["components"].items()},
            "weyl_trace_defect": "0",
            "tractor_curvature": "Omega^T_ab has Weyl block C_abcd and Cotton off-diagonal block; Cotton=0 but C_2323=2/3",
        },
        "obstruction": {
            "attempted_extension": "an invertible zero-order bundle map U satisfying nabla^T_N U=U nabla^T_0, hence extending the C-G2 pointwise conformal/BV conjugation",
            "integrability_equation": "Omega^T_N U=U Omega^T_0",
            "source_curvature": "Omega^T_0=0 because the conformal cylinder is conformally flat",
            "forced_target_condition": "invertibility of U forces Omega^T_N=0",
            "normalized_witness": "(3/2) C_2323",
            "normalized_witness_value": _q(fixture["normalized_witness"]),
            "conclusion": "no such zero-order conformal/tractor conjugation exists, even locally",
        },
        "exact_checks": {
            "target_is_globally_hyperbolic": True,
            "target_is_Einstein": True,
            "target_is_Bach_flat": True,
            "target_Weyl_is_nonzero": True,
            "source_tractor_curvature_zero": True,
            "target_tractor_curvature_nonzero": True,
            "zero_order_intertwiner_obstructed": True,
        },
        "flags": {
            "CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1": True,
            "C_G2_ZERO_ORDER_CONJUGATION_EXTENDS_TO_NARIAI": False,
            "CURVED_DIFFERENTIAL_HPL_CORRECTION_EXISTS": False,
            "NARIAI_GREEN_HOMOTOPY_CONSTRUCTED": False,
            "ALL_BACH_FLAT_BACKGROUNDS_OBSTRUCTED": False,
            "LOCAL_PATCHING_OBSTRUCTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_BACH_FLAT_CURVED_HPL_CORRECTION_OR_OBSTRUCTION",
        "claim_boundary": (
            "This is a normalized local obstruction to extending the certified C-G2 global conformal-orbit theorem by the same invertible zero-order conformal/BV/tractor conjugation. The unit Nariai metric is a globally hyperbolic Einstein and hence Bach-flat control with nonzero Weyl, so its normal tractor connection cannot be pointwise gauge-conjugate to the flat tractor connection of the conformal cylinder. This does not obstruct a curvature-dependent differential HPL map, a larger parent complex, an independently constructed Green homotopy, local patching among conformally flat charts, or causal theory on all conformally Einstein or Bach-flat backgrounds. No Lorentzian-causal promotion is made for Nariai."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/conformally_einstein_curvature_obstruction.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_conformally_einstein_curvature_obstruction.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_conformally_einstein_curvature_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/conformally-einstein-tractor-curvature-obstruction-v1.schema.json -d d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json",
            ],
        },
    }


def _report(value: dict) -> str:
    c = value["exact_curvature"]["weyl_components"]
    return rf"""# Conformally Einstein tractor-curvature obstruction

## Result

The unit Nariai spacetime

\[
g_N=-dt^2+\cosh^2(t)d\chi^2+d\Omega_2^2
\]

is globally hyperbolic with compact Cauchy surface \(S^1\times S^2\), is
Einstein with \(\operatorname{{Ric}}=g_N\), and is therefore Bach-flat.  In
an orthonormal frame its exact Weyl witness is

\[
C_{{0101}}={c['C_0101']},\qquad C_{{2323}}={c['C_2323']},\qquad
C_{{0202}}={c['C_0202']}.
\]

The Cotton tensor vanishes, but the normal tractor curvature does not because
its Weyl block contains \(C_{{2323}}=2/3\).

## Obstruction

An invertible zero-order extension of the C-G2 conjugation would intertwine
the normal tractor connections.  Curvature integrability would then require

\[
\Omega_N^T U=U\Omega_0^T.
\]

The conformal cylinder has \(\Omega_0^T=0\).  Invertibility would force
\(\Omega_N^T=0\), contradicted by the normalized exact witness

\[
\frac32 C_{{2323}}=1.
\]

Thus the pointwise conformal/BV conjugation cannot reach even this Einstein,
Bach-flat background, locally or globally.

## Boundary

This does not obstruct curvature-dependent differential HPL corrections, a
larger parent complex, an independently constructed Nariai Green homotopy, or
patching within the locally conformally flat category.  Accordingly this
certificate carries only `LOCAL-ALGEBRAIC`, not `LORENTZIAN-CAUSAL`.
"""


def verify(value: dict) -> None:
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if value != build():
        raise ValueError("certificate drifted from exact reconstruction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.guards:
        if value["obstruction"]["normalized_witness_value"] != "1":
            raise AssertionError("obstruction witness guard failed")
        if value["flags"]["NARIAI_GREEN_HOMOTOPY_CONSTRUCTED"] is not False:
            raise AssertionError("causal scope guard failed")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    print(f"{value['result_id']}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

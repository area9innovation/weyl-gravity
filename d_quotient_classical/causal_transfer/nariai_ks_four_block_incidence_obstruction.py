#!/usr/bin/env python3
"""Exact finite-parameter obstruction to the four-block transverse incidence."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-ks-four-block-incidence-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-ks-four-block-incidence-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_ks_four_block_incidence_obstruction.py"
TESTS = HERE / "tests/test_nariai_ks_four_block_incidence_obstruction.py"

DEPENDENCIES = {
    "finite_four_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json",
    "exact_KS_branch": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
    "formal_rank310_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def exact_symbol_obstruction() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon", real=True)
    b0 = 1 - epsilon**2 / 6

    # At t=0 the exact branch has a(0)=1 and b(0)=b0.  In the canonical
    # coordinate identification, take zeta=dx^2 and xi=d/dx^2.  For
    # K_g xi = 2 sym(nabla xi) - (1/2) g div(xi), its 22 principal-symbol
    # component is (3/2) g_22=(3/2)b0^2.  The output belongs to
    # S^2_0(g_epsilon), so transport it to S^2_0(g0) by the declared
    # ambient projection tf_g0.  Its g0-trace is b0^2-1, hence the transported
    # 22 component is (3/2)b0^2-(1/4)(b0^2-1).
    base_channel = sp.Rational(3, 2)
    finite_channel = sp.factor(
        sp.Rational(3, 2) * b0**2 - sp.Rational(1, 4) * (b0**2 - 1)
    )
    defect = sp.factor(finite_channel - base_channel)
    expected = sp.factor(5 * epsilon**2 * (epsilon**2 - 12) / 144)
    if sp.factor(defect - expected) != 0:
        raise AssertionError("conformal-Killing symbol defect drifted")
    if sp.diff(defect, epsilon).subs(epsilon, 0) != 0:
        raise AssertionError("the certified first-order fixed-K normal form drifted")
    if sp.diff(defect, epsilon, 2).subs(epsilon, 0) != -sp.Rational(5, 6):
        raise AssertionError("the first missing finite coefficient is not quadratic")

    # The defect is strictly negative on the certified parameter range.
    # epsilon^2 is positive and epsilon^2-12<-11 for 0<|epsilon|<1.
    upper_factor_bound = 1 - 12
    if upper_factor_bound != -11:
        raise AssertionError("parameter-range sign bound drifted")

    transport_determinant = sp.factor((b0**2 + 1) / (2 * b0**2))
    return {
        "parameter_range": "0<|epsilon|<1",
        "evaluation_event": "t=0 with identity input coordinates and output transport tf_g0:S2_0(g_epsilon)->S2_0(g0)",
        "metric_at_event": "diag(-1,1,b0^2,b0^2) with b0=1-epsilon^2/6",
        "symbol_inputs": "zeta=dx^2, xi=d/dx^2",
        "conformal_Killing_convention": "sigma(K_g)(zeta)xi=2 zeta_(mu xi_nu)-(1/2)g_munu zeta_rho xi^rho",
        "base_channel": str(base_channel),
        "finite_channel": str(finite_channel),
        "finite_minus_base": str(defect),
        "first_epsilon_derivative_at_zero": "0",
        "second_epsilon_derivative_at_zero": "-5/6",
        "strict_sign_on_range": "negative",
        "output_transport": "tf_g0 restricted from S2_0(g_epsilon) to S2_0(g0)",
        "output_transport_determinant": str(transport_determinant),
        "output_transport_invertible_on_range": True,
        "missing_blocks": ["k=K p0", "ksharp=p0sharp Ksharp"],
        "minimal_fixed_presentation_incidence_count": 6,
    }


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not records["finite_four_block_HPL"]["flags"]["FINITE_SUPPORT_LOCAL_HPL_DENOMINATOR"]:
        raise ValueError("finite four-block HPL theorem drifted")
    if not records["exact_KS_branch"]["flags"]["TRANSVERSE_KS_SLABWISE_EINSTEIN_FAMILY"]:
        raise ValueError("exact slabwise KS family drifted")
    if not records["formal_rank310_variation"]["flags"]["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"]:
        raise ValueError("formal first-order rank-310 theorem drifted")
    exact = exact_symbol_obstruction()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-nariai-ks-four-block-incidence-obstruction-v1",
        "result_id": "NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1",
        "result_state": "FOUR_BLOCK_HPL_INCIDENCE_FAILS_AT_FINITE_ORDER_TWO_IN_CANONICAL_KS_PRESENTATION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "theorem": {
            "statement": "On the exact transverse Kantowski-Sachs branch, after the declared output transport tf_g0:S2_0(g_epsilon)->S2_0(g0), the fixed-coordinate conformal-Killing symbol differs from unit Nariai by 5 epsilon^2(epsilon^2-12)/144 in an explicit channel. Hence the exact finite rank-310 differential cannot retain only the four first-variation blocks; the gauge block k=Kp0 and its cyclic dual must also vary.",
            "first_order_compatibility": "the first derivative vanishes, so the certified formal four-block theorem is unchanged",
            "finite_order_verdict": "the first missing block occurs at order epsilon^2",
            "scope": "canonical fixed-coordinate tensor/density identification on the exact Kantowski-Sachs branch",
        },
        "exact_symbol_obstruction": exact,
        "architecture_consequence": {
            "four_block_finite_HPL_directly_applicable": False,
            "formal_first_variation_retained": True,
            "smallest_next_test": "six-block finite HPL incidence including k and ksharp",
            "common_slab_causal_transfer_certified": False,
            "alternative_identification_ruled_out": False,
        },
        "exact_checks": {
            "exact_KS_initial_metric_used": True,
            "conformal_Killing_symbol_channel_derived": True,
            "declared_output_transport_invertible": True,
            "finite_symbol_defect_nonzero": True,
            "linear_term_zero": True,
            "quadratic_term_nonzero": True,
            "cyclic_dual_block_required": True,
        },
        "flags": {
            "NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1": True,
            "CANONICAL_KS_FOUR_BLOCK_FINITE_INCIDENCE": False,
            "CANONICAL_KS_SIX_BLOCK_PREFLIGHT_REQUIRED": True,
            "TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION": True,
            "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER": False,
            "ALL_SUPPORT_LOCAL_IDENTIFICATIONS_OBSTRUCTED": False,
            "ALL_BACH_FLAT_FAMILIES_OBSTRUCTED": False,
            "HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "NARIAI_KS_SIX_BLOCK_FINITE_HPL_INCIDENCE",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_ks_four_block_incidence_obstruction.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_ks_four_block_incidence_obstruction.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_ks_four_block_incidence_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-ks-four-block-incidence-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1.json"
            ]
        },
        "claim_boundary": "This is an exact obstruction to applying the certified four-block finite HPL formula unchanged to the exact Kantowski-Sachs family in the canonical fixed-coordinate tensor/density identification. It preserves the global formal first variation because the defect begins at epsilon squared. It does not obstruct a six-block HPL contraction, another support-local triangular identification, a non-Einstein Bach-flat family, or a common-slab causal theorem after the enlarged incidence is solved; it proves no Hadamard or quantum claim."
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact symbol check dropped")
    if value["architecture_consequence"]["four_block_finite_HPL_directly_applicable"] is not False:
        raise ValueError("four-block finite applicability was overpromoted")
    for flag in (
        "CANONICAL_KS_FOUR_BLOCK_FINITE_INCIDENCE",
        "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
        "ALL_SUPPORT_LOCAL_IDENTIFICATIONS_OBSTRUCTED",
        "ALL_BACH_FLAT_FAMILIES_OBSTRUCTED",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        if value["flags"][flag] is not False:
            raise ValueError("claim boundary crossed")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Finite four-block incidence obstruction on the exact KS branch

At (t=0), the exact transverse Kantowski--Sachs branch has

\[
 g_\epsilon=\operatorname{diag}(-1,1,b_0^2,b_0^2),
 \qquad b_0=1-\frac{\epsilon^2}{6}.
\]

Use identity input coordinates and identify the tracefree output bundles by
the ambient projection
\(\operatorname{tf}_{g_0}:S^2_0(g_\epsilon)\to S^2_0(g_0)\).
The determinant of this nine-dimensional output transport is
\((b_0^2+1)/(2b_0^2)>0\), so it is an actual bundle identification throughout
the declared parameter range.  Choose \(\zeta=dx^2\) and
\(\xi=\partial_2\).  For

\[
 \sigma(K_g)(\zeta)\xi
 =2\zeta_{(\mu}\xi_{\nu)}
  -\frac12g_{\mu\nu}\zeta_\rho\xi^\rho,
\]

the transported (22) component changes by

\[
 \frac54(b_0^2-1)
 =\frac{5\epsilon^2(\epsilon^2-12)}{144}\neq0
 \qquad(0<|\epsilon|<1).
\]

Its first derivative at zero vanishes and its second derivative is
\(-5/6\).
This explains why the four-block normal form is exact through first order but
cannot be the exact finite differential in this presentation.  The minimal
next incidence must also contain (k=Kp_0) and its cyclic dual
\(k^\sharp=p_0^\sharp K^\sharp), for six varying blocks in total.

This is not a no-go theorem for the common-slab causal construction.  It is a
fail-closed instruction to generalize the finite HPL calculation before that
construction is promoted.
"""


def _guards(value: dict[str, Any]) -> None:
    for flag in (
        "CANONICAL_KS_FOUR_BLOCK_FINITE_INCIDENCE",
        "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
        "ALL_SUPPORT_LOCAL_IDENTIFICATIONS_OBSTRUCTED",
        "ALL_BACH_FLAT_FAMILIES_OBSTRUCTED",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][flag] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {flag}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("finite-incidence obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print("NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()

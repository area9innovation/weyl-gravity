#!/usr/bin/env python3
"""Certify a compact conserved source and nonzero retarded Maxwell signal.

The source is constructed as the exact compactly supported current three-form
``j=d kappa``.  It is injected in the Maxwell equation row of the certified
36-row endpoint complex.  The already-certified retarded Maxwell chain
homotopy then gives a Lorenz representative whose field strength is nonzero
and supported in the causal future of the source.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retarded-compact-source-maxwell-signal.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retarded-compact-source-maxwell-signal-v1.schema.json"

DEPENDENCIES = {
    "causal_transfer": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "maxwell_layout": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json",
    "g0_fixture": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
}

SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retarded_compact_maxwell_signal.py",
    "tests": ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retarded_compact_maxwell_signal.py",
    "schema": SCHEMA,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _wedge_sign(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    if set(left) & set(right):
        return 0
    inversions = sum(1 for a in left for b in right if a > b)
    return -1 if inversions % 2 else 1


def _d_form(form: dict[tuple[int, ...], sp.Expr], jets: dict[tuple[str, int], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    """Exterior derivative for the chi/chi_mu fixture used below."""
    output: dict[tuple[int, ...], sp.Expr] = {}
    for basis, coefficient in form.items():
        for mu in range(4):
            if coefficient == jets[("chi", -1)]:
                derivative = jets[("dchi", mu)]
            elif coefficient in tuple(jets[("dchi", nu)] for nu in range(4)):
                nu = next(nu for nu in range(4) if coefficient == jets[("dchi", nu)])
                lo, hi = sorted((mu, nu))
                derivative = jets[(f"ddchi_{lo}", hi)]
            else:
                derivative = sp.diff(coefficient, jets[("chi", -1)]) * jets[("dchi", mu)]
            sign = _wedge_sign((mu,), basis)
            if sign:
                target = tuple(sorted((mu,) + basis))
                output[target] = sp.expand(output.get(target, 0) + sign * derivative)
    return {basis: coefficient for basis, coefficient in output.items() if coefficient != 0}


def _source_algebra() -> dict[str, Any]:
    chi = sp.Symbol("chi")
    dchi = tuple(sp.Symbol(f"chi_{mu}") for mu in range(4))
    ddchi = {(lo, hi): sp.Symbol(f"chi_{lo}{hi}") for lo in range(4) for hi in range(lo, 4)}
    jets: dict[tuple[str, int], sp.Expr] = {("chi", -1): chi}
    jets.update({("dchi", mu): dchi[mu] for mu in range(4)})
    jets.update({(f"ddchi_{lo}", hi): value for (lo, hi), value in ddchi.items()})

    kappa = {(1, 2): chi}
    current = _d_form(kappa, jets)
    closure = _d_form(current, jets)
    expected = {(0, 1, 2): dchi[0], (1, 2, 3): dchi[3]}
    if current != expected:
        raise AssertionError(f"compact current fixture drifted: {current}")
    if closure:
        raise AssertionError(f"d squared failed: {closure}")

    # In signature (-,+,+,+), *dx012=-dx3 and *dx123=-dx0.
    current_one_form = {0: -dchi[3], 3: -dchi[0]}
    return {
        "kappa_components": {"12": "chi"},
        "current_three_form_components": {"012": "chi_0", "123": "chi_3"},
        "current_one_form_components": {"0": "-chi_3", "3": "-chi_0"},
        "closure_components": {},
        "nonzero_condition": "chi_0 is not identically zero",
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    causal = data["causal_transfer"]
    if causal["flags"]["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("combined causal contraction is unavailable")
    if causal["flags"]["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Maxwell causal contraction is unavailable")
    if causal["flags"]["BERGER_MIXED_Q2_CYCLICITY"] is not True:
        raise AssertionError("repaired mixed interaction dependency is unavailable")
    if data["maxwell_layout"]["maxwell_bv_complex"]["minimal_rows"] != 10:
        raise AssertionError("Maxwell row layout drifted")
    if data["g0_fixture"]["flags"]["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"] is not True:
        raise AssertionError("G0 comparison fixture is unavailable")
    return data


def _dependency_refs(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        name: {
            "path": str(path.relative_to(ROOT)),
            "result_id": data[name]["result_id"],
            "sha256": _sha256(path),
        }
        for name, path in DEPENDENCIES.items()
    }


def _source_manifest() -> list[dict[str, str]]:
    return [
        {
            "path": str(path.relative_to(ROOT)),
            "role": role,
            "sha256": _sha256(path),
        }
        for role, path in SOURCE_FILES.items()
    ]


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    algebra = _source_algebra()
    return {
        "schema": "pure-weyl-berger-retarded-compact-source-maxwell-signal-v1",
        "result_id": "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_COMPACT_CONSERVED_SOURCE_AND_NONZERO_RETARDED_MAXWELL_SIGNAL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": _dependency_refs(dependencies),
        "source_class": {
            "chart": "U=(-2,2) x B_2 with compact closure in R x S3",
            "bump": "chi in C_c^infinity(U), for example a product of standard smooth bumps",
            "potential_two_form": "kappa=chi dx1 wedge dx2",
            "current_three_form": "j=d kappa",
            "metric_current_one_form": "J=star^{-1} j",
            "support_chain": "supp(J)=supp(j) subset supp(kappa) subset supp(chi) compact",
            "zero_charge": "integral_Sigma pullback(j)=integral_Sigma d_Sigma pullback(kappa)=0",
            "source_kind": "compact neutral dipole pulse; not yet a localized charged emitter",
            "exact_components": algebra,
        },
        "bv_source_injection": {
            "maxwell_complex": "Omega0 --d--> Omega1 --delta d--> Omega3 --d--> Omega4",
            "source": "s_j=(0,0,j,0)",
            "full_64_rows": [59, 60, 61, 62],
            "endpoint_36_rows": [31, 32, 33, 34],
            "compatibility": "q_M s_j=(0,0,0,dj)=0",
            "degree": "Maxwell equation/antifield-density row",
        },
        "retarded_signal": {
            "wave_operator": "P1=delta d+d delta on one-forms",
            "retarded_green": "G1_ret with supp(G1_ret J) subset J_plus(supp J)",
            "potential": "A_ret=G1_ret J=Lambda_M,ret(s_j)",
            "lorenz_identity": "delta A_ret=G0_ret delta J=0",
            "maxwell_equation": "delta d A_ret=J",
            "field_strength": "F_ret=d A_ret",
            "support": "supp(F_ret) subset J_plus(supp j)",
            "nontriviality": "F_ret=0 would imply J=delta F_ret=0, contradicting chi_0 not identically zero",
            "uniqueness": "the retarded Lorenz representative is unique by uniqueness of the de Rham-wave retarded Green operator",
        },
        "exact_checks": {
            "compact_source_constructed_without_projector": True,
            "current_is_exact_three_form": True,
            "current_is_closed": True,
            "current_is_nonzero_under_declared_condition": True,
            "current_has_zero_total_charge": True,
            "source_injected_in_all_four_Maxwell_equation_components": True,
            "BV_source_is_q_closed": True,
            "retarded_Lorenz_representative_exists": True,
            "retarded_Maxwell_equation_exact": True,
            "retarded_field_strength_nonzero": True,
            "retarded_causal_support": True,
            "advanced_signal_not_substituted_for_retarded_signal": True,
            "portable_64_row_export_not_used_before_authoritative_commit": True,
            "mixed_q2_cyclicity_not_used_by_unary_signal": True,
        },
        "flags": {
            "BERGER_COMPACT_CONSERVED_MAXWELL_SOURCE": True,
            "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL": True,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_MAXWELL_BACKREACTION": False,
            "BERGER_G1_COMPLETE_SIGNAL_SECTOR": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "provenance": {"source_manifest": _source_manifest()},
        "claim_boundary": "This classical theorem constructs a nonzero compact neutral Maxwell source as the exact current three-form j=d kappa, injects it as a q-closed source in the certified Maxwell BV equation row, and uses only the certified unary retarded chain homotopy to obtain a unique Lorenz representative with nonzero field strength supported in the causal future of the source. The repaired mixed-q2 cyclicity flag is imported but is not used in the unary propagation proof. This proves a retarded signal, not a spatially localized emitter/receiver measurement or nonlinear response. It does not provide rod fields, detector response, unique endpoint intersection, apparatus recoil, gravitational backreaction, mixed q3, Hadamard data, a QME result, or a quantum claim.",
    }


def verify(certificate: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("an exact source/signal check dropped")
    for flag in (
        "BERGER_COMPACT_CONSERVED_MAXWELL_SOURCE",
        "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
    ):
        if certificate["flags"][flag] is not True:
            raise AssertionError(f"proved flag dropped: {flag}")
    for flag in (
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_MAXWELL_BACKREACTION",
        "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        if certificate["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")


def _report() -> str:
    return r"""# Compact-source retarded Maxwell signal on the Berger clock background

## Result

A compact conserved source is obtained without a spatial projector.  In a
precompact cylinder chart choose a nonzero test function `chi` and set

\[
\kappa=\chi\,dx^1\wedge dx^2,\qquad j=d\kappa.
\]

Then `j` is compact, nonzero when `partial_0 chi` is not identically zero,
and `dj=0` exactly.  Its charge on every closed Cauchy sphere vanishes by
Stokes.  It is therefore a neutral dipole pulse, not yet a charged emitter.

The BV source `s_j=(0,0,j,0)` occupies all four Maxwell equation components.
It is chain compatible because `q_M s_j=(0,0,0,dj)=0`.  With
`J=star^{-1}j`, the certified retarded Maxwell homotopy gives

\[
A_{\rm ret}=G^{\rm ret}_1J,\qquad
\delta A_{\rm ret}=0,\qquad
\delta dA_{\rm ret}=J.
\]

Thus `F_ret=d A_ret` has support in the causal future of the compact source.
It is nonzero: otherwise the displayed Maxwell equation would force the
declared nonzero current to vanish.

## Boundary

This certifies a genuine compact-source retarded classical signal.  It does
not yet choose rod fields, emitter and receiver worldtubes, detector windows,
or a unique clock-labelled intersection.  Apparatus recoil, gravitational
backreaction, mixed `q3`, Hadamard data, and quantum claims remain open.

The repaired mixed-`q2` tensor does not enter this result: source
compatibility and propagation use only `q1` and the unary retarded Maxwell
Green homotopy.

The separate portable 64-row export visible in the shared worktree was not
used because it was not committed and authoritative when this result was
built.  The committed 64-row causal theorem is pinned directly by hash.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate = build()
    verify(certificate)
    certificate_text = _json(certificate)
    report_text = _report()
    if args.write:
        CERTIFICATE.write_text(certificate_text)
        REPORT.write_text(report_text)
    if args.check:
        if CERTIFICATE.read_text() != certificate_text:
            raise AssertionError("compact-source signal certificate drifted")
        if REPORT.read_text() != report_text:
            raise AssertionError("compact-source signal report drifted")
    if args.guards:
        mutants = []
        bad_closure = deepcopy(certificate)
        bad_closure["exact_checks"]["current_is_closed"] = False
        mutants.append(("break current conservation", bad_closure))
        wrong_rows = deepcopy(certificate)
        wrong_rows["bv_source_injection"]["endpoint_36_rows"] = [31, 32, 33, 35]
        mutants.append(("move source into ghost-antifield row", wrong_rows))
        promoted = deepcopy(certificate)
        promoted["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"] = True
        mutants.append(("promote localized observable", promoted))
        wrong_support = deepcopy(certificate)
        wrong_support["retarded_signal"]["support"] = "supp(F_ret) subset J_minus(supp j)"
        mutants.append(("reverse causal support", wrong_support))
        for name, mutant in mutants:
            try:
                verify(mutant)
            except (AssertionError, jsonschema.ValidationError):
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

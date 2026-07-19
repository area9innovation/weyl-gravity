#!/usr/bin/env python3
"""Obstruct the direct support-local upgrade of candidate-13 mode receivers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/candidate13-reduced-source-support-local-upgrade-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/candidate13-reduced-source-support-local-upgrade-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_candidate13_reduced_source_support_local_upgrade_obstruction.py"
TESTS = HERE / "tests/test_candidate13_reduced_source_support_local_upgrade_obstruction.py"
CROSSWALK = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1.json"
TRIANGLE = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json"
ZERO_BLOCK = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {"artifact_id": value["result_id"], "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def exact_fixture() -> dict[str, object]:
    constant = sp.ones(3, 1)
    p_zero = constant * constant.T / 3
    mode = sp.Matrix([1, 2, 3])
    p_mode = mode * mode.T / (mode.dot(mode))
    local_input = sp.Matrix([1, 0, 0])
    zero_output = p_zero * local_input
    mode_output = p_mode * local_input
    support = lambda vector: [index for index, value in enumerate(vector) if value != 0]
    checks = {
        "zero_projector_idempotent": p_zero * p_zero == p_zero,
        "mode_projector_idempotent": p_mode * p_mode == p_mode,
        "localized_input_support": support(local_input) == [0],
        "zero_projector_expands_support": support(zero_output) == [0, 1, 2],
        "mode_projector_expands_support": support(mode_output) == [0, 1, 2],
    }
    if not all(checks.values()):
        raise AssertionError("exact support-expansion fixture failed")
    return {
        "zero_projector": [[str(x) for x in row] for row in p_zero.tolist()],
        "mode_projector": [[str(x) for x in row] for row in p_mode.tolist()],
        "input": [str(x) for x in local_input],
        "zero_output": [str(x) for x in zero_output],
        "mode_output": [str(x) for x in mode_output],
        "checks": checks,
    }


def build() -> dict[str, object]:
    crosswalk = json.loads(CROSSWALK.read_text())
    triangle = json.loads(TRIANGLE.read_text())
    zero_block = json.loads(ZERO_BLOCK.read_text())
    if crosswalk["dependency_tags"] != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise AssertionError("candidate-13 category drifted")
    if crosswalk["derived_source_pullback"]["CAUSAL_RETARDED"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 causal cell was already promoted")
    if not crosswalk["classification"]["bounded_derived_source_pullback_is_origin"]:
        raise AssertionError("candidate-13 bounded-origin refinement unavailable")
    if not triangle["acceptance_flags"]["SUPPORT_LOCAL_MAPPING_COFIBER"]:
        raise AssertionError("unary relative triangle locality unavailable")
    fixture = exact_fixture()
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    return {
        "schema": "pure-weyl-candidate13-reduced-source-support-local-upgrade-obstruction-v1",
        "result_id": "CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1",
        "result_state": "SPECIFIED_REDUCED_MODE_RECEIVER_HAS_NO_DIRECT_SUPPORT_LOCAL_DIFFERENTIAL_UPGRADE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            "candidate13_derived_source": _dependency(CROSSWALK),
            "support_local_unary_triangle": _dependency(TRIANGLE),
            "finite_generic_zero_block": _dependency(ZERO_BLOCK),
        },
        "scope": crosswalk["scope"],
        "receiver_audit": {
            "bounded_domain": "the certified bounded pullback is exactly the origin on the declared candidate-13 carrier; this makes its solution set trivial but does not localize the global receiver used to define it",
            "zero_frequency_components": "mu_H, mu_Px, mu_J1, mu_J2, mu_J3 and R_c are extracted from spatially integrated or zero-frequency harmonic coefficients",
            "finite_frequency_components": "R_13,1,...,R_13,18 are adjoint-cokernel Fourier/harmonic coefficients",
            "smooth_inverse": "secular t exp(i Omega t) representatives require the globally selected frequency component",
            "bounded_inverse": "modewise division on the finite quasiperiodic carrier requires the same global spectral decomposition",
        },
        "support_obstruction": {
            "lemma": "A nonzero projector onto a global constant or harmonic mode cannot be support-nonincreasing: a section supported in a proper open set can have nonzero mode pairing, while its projected mode is nonzero outside that set.",
            "temporal_witness": "The zero-frequency mean of a compactly supported time test function with nonzero integral is a nonzero constant and therefore has all-time support.",
            "spatial_witness": "On closed S1 x S2, choose chi supported in a proper chart and a target harmonic phi with integral chi |phi|^2 nonzero; Pi_phi(chi phi) is a global multiple of phi.",
            "finite_exact_fixture": fixture,
            "conclusion": "The declared candidate-13 bounded/smooth receiver and its modewise inverses cannot themselves be differentials or homotopies in a support-local finite-rank bundle complex.",
        },
        "category_disposition": {
            "unary_relative_triangle": "CERTIFIED_SUPPORT_LOCAL",
            "candidate13_bounded_pullback": "CERTIFIED_REDUCED_MODE_ORIGIN_ONLY",
            "candidate13_smooth_pullback": "CERTIFIED_REDUCED_MODE_NONTRIVIAL",
            "direct_upgrade_of_declared_receiver": "OBSTRUCTED",
            "causal_retarded_crosswalk": "NO_CERTIFIED_MAP",
            "admissible_future_repairs": "a new local equation-level cofiber, a larger noncontractible mixed-bundle carrier, or a separately declared nonlocal REDUCED-MODE map",
        },
        "exact_checks": fixture["checks"],
        "flags": {
            "CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1": True,
            "DECLARED_MODE_PROJECTORS_SUPPORT_LOCAL": False,
            "DIRECT_REDUCED_RECEIVER_TO_LOCAL_BV_UPGRADE": False,
            "CANDIDATE13_CAUSAL_RETARDED_CROSSWALK": False,
            "ALTERNATIVE_LOCAL_COFIBER_GLOBALLY_OBSTRUCTED": False,
            "ARITY_THREE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "The exact candidate-13 bounded/smooth derived-source artifact cannot be promoted directly to a support-local BV/causal cofiber because its zero- and finite-frequency receiver maps necessarily expand support.",
            "not_claimed": [
                "nonexistence of every possible local equation-level relative cofiber",
                "nonexistence of a larger noncontractible mixed-bundle carrier",
                "failure of the certified unary support-local relative triangle",
                "a causal obstruction for the underlying Einstein-Maxwell or Weyl-Maxwell field theories",
                "an arity-three, observable, particle or quantum theorem",
            ],
        },
        "next_gate": "NEW_LOCAL_EQUATION_LEVEL_COFIBER_OR_RETAIN_REDUCED_MODE_ONLY",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in sources},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/candidate13_reduced_source_support_local_upgrade_obstruction.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_candidate13_reduced_source_support_local_upgrade_obstruction.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_candidate13_reduced_source_support_local_upgrade_obstruction",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/candidate13-reduced-source-support-local-upgrade-obstruction-v1.schema.json -d d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json",
        ],
    }


def _report() -> str:
    return """# Candidate-13 reduced-source support-local upgrade obstruction

The candidate-13 derived-source pullbacks are exact in their declared
finite-harmonic categories: the bounded pullback is now certified to be the
origin, while the smooth-secular pullback is nontrivial.  Their receiver
cannot be promoted *as written* to a support-local BV or causal cofiber.

Their six zero-frequency receivers and eighteen finite-frequency receivers
are obtained by global Fourier/harmonic projection.  A nonzero global-mode
projector expands support: a field supported in a proper chart can have a
nonzero pairing with the mode, while its projection is nonzero wherever the
global mode is.  The time-mean projector similarly sends a compactly
supported test function of nonzero integral to a constant.  Exact rational
three-site projectors provide a finite audit of the same support defect.

Thus the unary same-background relative triangle remains support-local, and
both candidate-13 pullback statements remain valid `REDUCED-MODE` theorems,
but the declared receiver and modewise inverses do not define a local causal
subcomplex.  A genuinely new equation-level cofiber or noncontractible
mixed-bundle carrier remains possible; this certificate does not obstruct
those alternatives.
"""


def write() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_report())


def check() -> None:
    value = build()
    if json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("candidate-13 category obstruction drifted")
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)


def guards() -> None:
    schema = Draft202012Validator(json.loads(SCHEMA.read_text()))
    value = build()
    for key in ("DIRECT_REDUCED_RECEIVER_TO_LOCAL_BV_UPGRADE", "CANDIDATE13_CAUSAL_RETARDED_CROSSWALK", "ALTERNATIVE_LOCAL_COFIBER_GLOBALLY_OBSTRUCTED"):
        bad = json.loads(json.dumps(value))
        bad["flags"][key] = True
        try:
            schema.validate(bad)
        except Exception:
            continue
        raise AssertionError(f"schema accepted forbidden promotion: {key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check:
        check()
    if args.guards:
        guards()
    if not (args.write or args.check or args.guards):
        print(json.dumps(build(), indent=2, sort_keys=True))

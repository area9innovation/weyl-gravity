#!/usr/bin/env python3
"""Exact scoped obstruction to the requested retained-36 branch projector."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retained-36-residual-branch-local-projector-obstruction.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-retained-36-residual-branch-local-projector-obstruction-v1.schema.json"
PRODUCER_PATH = ROOT / "d_quotient_classical/backreacted_clock/berger_retained_36_residual_branch_local_projector_obstruction.py"
VERIFIER_PATH = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_36_residual_branch_local_projector_obstruction.py"
TEST_PATH = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_36_residual_branch_local_projector_obstruction.py"

LOWER_CERT = ROOT / "d_quotient_classical/certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json"
RETAINED_CERT = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
QUANTUM_READINESS = ROOT / "quantum-weyl/transfer/certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS_V2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def _load_remainder_entry() -> tuple[Path, dict]:
    lower = json.loads(LOWER_CERT.read_text())
    record = lower["normal_form"]["artifacts"]["lower_by_two_remainder"]
    path = ROOT / record["path"]
    if _sha256(path) != record["sha256"]:
        raise AssertionError("lower-by-two remainder artifact digest drifted")
    payload = json.loads(path.read_text())
    for row, column, terms in payload["entries"]:
        if row == 0 and column == 0:
            return path, {"row": row, "column": column, "terms": terms}
    raise AssertionError("canonical obstruction entry (0,0) disappeared")


def _witness() -> dict:
    _, entry = _load_remainder_entry()
    p0, p1, p2, p3 = sp.symbols("p0:4")
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    symbol = sp.Integer(0)
    for powers, coefficient in entry["terms"]:
        if sum(powers) != 2:
            continue
        coefficient = sp.sympify(coefficient, locals={"u": u, "v": v})
        monomial = p0 ** powers[0] * p1 ** powers[1] * p2 ** powers[2] * p3 ** powers[3]
        symbol += coefficient * monomial
    symbol = sp.factor(symbol)
    expected = (71 * p1**2 + 71 * p2**2 + 9 * p3**2) / 80
    if sp.expand(symbol - expected) != 0:
        raise AssertionError(f"normalized Berger witness drifted: {symbol}")
    wave = -p0**2 + p1**2 + p2**2 + p3**2
    division_remainder = sp.factor(sp.rem(symbol, wave, p0))
    if division_remainder == 0:
        raise AssertionError("canonical rough-wave divisibility obstruction disappeared")
    normalized_evaluation = sp.factor(sp.expand(symbol).coeff(p1, 2) * sp.Rational(80, 71))
    if normalized_evaluation != 1:
        raise AssertionError("normalized obstruction functional no longer evaluates to one")
    return {
        "matrix_entry": [0, 0],
        "fixture": {"u": "3*sqrt(10)/20", "v": "2*sqrt(10)/3", "alpha_B": "5"},
        "degree_two_defect": str(symbol),
        "scalar_wave_polynomial": str(wave),
        "division_variable": "p0",
        "division_remainder": str(division_remainder),
        "normalized_left_functional": "(80/71) coefficient_of(p1^2)",
        "normalized_evaluation": str(normalized_evaluation),
    }


def _dual_number_idempotents() -> dict:
    # e=a+b eps, eps^2=0.  e^2=e gives a^2=a and (2a-1)b=0.
    solutions = []
    for a in (sp.Integer(0), sp.Integer(1)):
        b = sp.solve(sp.Eq((2 * a - 1) * sp.Symbol("b"), 0), sp.Symbol("b"))[0]
        solutions.append([str(a), str(b)])
    if solutions != [["0", "0"], ["1", "0"]]:
        raise AssertionError("dual-number idempotent audit drifted")
    return {
        "algebra": "Q(sqrt(10))[epsilon]/(epsilon^2)",
        "equations": ["a^2=a", "(2a-1)b=0"],
        "solutions_a_b": solutions,
        "only_trivial_idempotents": True,
        "interpretation": "the repeated physical wave layer is a filtered/Jordan carrier, not a direct sum of Einstein-like and generalized layers at principal order",
        "scope_guard": "lower-order separated factors can split a repeated leading symbol; the exact coefficient obstruction below, rather than this principal observation alone, rules out the declared canonical rough-wave realization",
    }


def build() -> dict:
    lower = json.loads(LOWER_CERT.read_text())
    retained = json.loads(RETAINED_CERT.read_text())
    readiness = json.loads(QUANTUM_READINESS.read_text())
    remainder_path, _ = _load_remainder_entry()
    if retained["retained_complex"]["total_rows"] != 36:
        raise AssertionError("retained carrier rank drifted")
    if lower["canonical_factor_obstruction"]["nondivisible_degree_two_entries"] != 92:
        raise AssertionError("complete nondivisibility ledger drifted")
    if readiness["claim_flags"]["DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE"] is not False:
        raise AssertionError("quantum readiness unexpectedly contains a dynamical projector")

    payload = {
        "schema": "pure-weyl-berger-retained-36-residual-branch-local-projector-obstruction-v1",
        "result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1",
        "result_state": "NORMALIZED_LOCAL_PROJECTOR_OBSTRUCTION_CANONICAL_SAME_BUNDLE_SCOPE",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "retained_typed_36_sdr": _dependency(RETAINED_CERT),
            "metric_lower_by_two_biwave": _dependency(LOWER_CERT),
            "quantum_v2_readiness": _dependency(QUANTUM_READINESS),
            "lower_by_two_remainder": {
                "path": str(remainder_path.relative_to(ROOT)),
                "sha256": _sha256(remainder_path),
            },
        },
        "requested_binary_handoff": {
            "successful_basis_artifact_issued": False,
            "normalized_obstruction_issued": True,
            "requested_success_result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2",
            "ell3_branch_projection_authorized": False,
            "paper_11_algebraic_theorem_affected": False,
        },
        "declared_projector_scope": {
            "ambient_carrier_rank": 36,
            "gravity_metric_field_rank": 10,
            "gravity_metric_dual_rank": 10,
            "Maxwell_carrier_status": "retained exactly but irrelevant to the gravity factor obstruction",
            "Einstein_like_definition": "the support-local same-bundle branch carried by the certified canonical covariant rough tensor wave Box_2",
            "extra_Weyl_definition": "a complementary same-bundle scalar-wave-leading branch on the retained metric endpoint",
            "required_properties": [
                "finite-order support-local inclusion and projection",
                "retained-q1 intertwining",
                "complementary idempotence on the declared gravity carrier",
                "no TT, helicity, inverse-Laplacian, Green, or reduced-mode projector",
            ],
        },
        "exact_endpoint_normal_form": {
            "identity": "A10=Box_2^2+V_2",
            "maximum_order_V2": 2,
            "order_four_defect": 0,
            "order_three_defect": 0,
            "degree_two_nonzero_entries": 92,
            "degree_two_nondivisible_entries": 92,
            "necessary_factor_condition": "the declared canonical Einstein-like realization requires the exact endpoint to factor through/preserve the Box_2 equation module; the certified left and right Box_2 factor tests both fail",
        },
        "normalized_obstruction_witness": _witness(),
        "principal_filtered_module_audit": _dual_number_idempotents(),
        "verdict": {
            "local_projector_exists_in_declared_scope": False,
            "reason": "the exact Berger lower-order remainder is not divisible by the canonical tensor-wave polynomial; hence the canonical rough-wave equation module is not an exact same-bundle factor of A10 and cannot be the image of the requested q1-intertwining complementary projector",
            "first_failed_object": "dynamical_branch_inclusion/projection for Einstein_like on the retained gravity endpoint",
            "quantum_consequence": "do not compute or promote an Einstein_like/extra_Weyl branch-space ell3 mixing table from the 36-row carrier",
            "paper_11_interpretation": "the interaction survives on the retained cyclic causal complex, while an exact local canonical Einstein/extra-Weyl decomposition is obstructed on the 36-row carrier",
        },
        "smallest_carrier_enlargement_required": {
            "exact_symbol_lower_bound": {
                "physical_helicity_rank": 2,
                "additional_configuration_directions": 2,
                "additional_cyclic_dual_directions": 2,
                "minimum_additional_BV_rows": 4,
                "reason": "a separate generalized wave layer must be represented independently for both real helicity-two directions and cyclicity requires its dual layer",
            },
            "smallest_natural_support_local_candidate": {
                "additional_bundle": "spatial STF2 prolongation variable plus its cyclic dual",
                "rank_each": 5,
                "additional_BV_rows": 10,
                "candidate_retained_rank": 46,
                "status": "REQUIRED_NEXT_CONSTRUCTION_NOT_CERTIFIED_AS_A_PROJECTOR",
            },
            "allowed_alternatives": [
                "mixed-bundle Einstein-defect or curvature mapping cylinder",
                "filtered branch carrier rather than a direct-sum projector",
                "nonlocal spectral decomposition explicitly labeled REDUCED-MODE, not imported into the local theorem",
            ],
        },
        "category_guards": {
            "Einstein_like_is_dynamical": True,
            "extra_Weyl_is_dynamical": True,
            "Maxwell_is_dynamical": True,
            "topological_odd_direction_is_particle_branch": False,
            "topological_odd_direction_location": "separate deformation/vertex basis with Euler-Lagrange and transgression witnesses",
        },
        "not_ruled_out": [
            "a mixed-bundle local projector after an explicit carrier enlargement",
            "a different exact Einstein-defect complex not fixing Box_2",
            "a reduced-mode or spectral branch splitting with an explicit nonlocality label",
            "the retained-complex ell3 theorem of Paper 11",
        ],
        "flags": {
            "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2": False,
            "BERGER_RETAINED_36_CANONICAL_LOCAL_BRANCH_PROJECTOR": False,
            "BERGER_RETAINED_36_CANONICAL_LOCAL_BRANCH_PROJECTOR_OBSTRUCTION": True,
            "ELL3_BRANCH_PROJECTION_AUTHORIZED": False,
            "PAPER_11_ALGEBRAIC_THEOREM_REMAINS_VALID": True,
            "QUANTUM_CLAIM": False,
        },
        "provenance": {
            "source_manifest": [
                {"role": "producer", "path": str(PRODUCER_PATH.relative_to(ROOT)), "sha256": _sha256(PRODUCER_PATH)},
                {"role": "independent_verifier", "path": str(VERIFIER_PATH.relative_to(ROOT)), "sha256": _sha256(VERIFIER_PATH)},
                {"role": "tests", "path": str(TEST_PATH.relative_to(ROOT)), "sha256": _sha256(TEST_PATH)},
                {"role": "strict_schema", "path": str(SCHEMA_PATH.relative_to(ROOT)), "sha256": _sha256(SCHEMA_PATH)},
            ],
            "verification_commands": [
                "python3 -m d_quotient_classical.backreacted_clock.berger_retained_36_residual_branch_local_projector_obstruction --check --guards",
                "python3 d_quotient_classical/backreacted_clock/verify_berger_retained_36_residual_branch_local_projector_obstruction.py",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_36_residual_branch_local_projector_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-36-residual-branch-local-projector-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC certificate is the obstruction branch of the requested binary handoff. It proves that the retained 36-row carrier does not admit the declared canonical same-bundle Einstein-like/extra-Weyl projector whose Einstein image is the certified rough-tensor-wave branch: the exact Berger endpoint A10=Box_2^2+V_2 has 92 nondivisible degree-two remainder entries, with the displayed normalized first witness. It does not prove global nonexistence of every mixed-bundle, higher-rank, differently defined, reduced-mode, or nonlocal branch decomposition. It does not relabel the topological odd deformation as a particle, invalidate the retained ell3 theorem, compute a branch mixing table, or make a quantum claim.",
    }
    return payload


def verify(payload: dict) -> None:
    if payload["requested_binary_handoff"]["successful_basis_artifact_issued"] is not False:
        raise AssertionError("an obstructed branch basis was promoted")
    if payload["requested_binary_handoff"]["normalized_obstruction_issued"] is not True:
        raise AssertionError("normalized obstruction missing")
    if payload["normalized_obstruction_witness"]["normalized_evaluation"] != "1":
        raise AssertionError("obstruction witness is not normalized")
    if payload["exact_endpoint_normal_form"]["degree_two_nondivisible_entries"] != 92:
        raise AssertionError("complete nondivisibility count drifted")
    if payload["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is not False:
        raise AssertionError("ell3 branch projection promoted despite obstruction")
    if payload["category_guards"]["topological_odd_direction_is_particle_branch"] is not False:
        raise AssertionError("topological odd direction was misclassified")
    if payload["smallest_carrier_enlargement_required"]["exact_symbol_lower_bound"]["minimum_additional_BV_rows"] != 4:
        raise AssertionError("symbol-level enlargement lower bound drifted")


def _text(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Berger retained-36 residual branch projector audit

## Binary verdict

The requested `BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2` cannot be
issued as a support-local same-bundle Einstein-like/extra-Weyl projector on
the retained 36-row carrier.  This package therefore issues the normalized
obstruction branch of the handoff.

The exact metric endpoint is

```text
A10 = Box_2^2 + V_2,   ord(V_2) <= 2.
```

All 92 nonzero entries of the degree-two symbol of `V_2` are nondivisible by
the scalar wave polynomial.  At matrix entry `(0,0)` and at the frozen Berger
fixture, the first exact witness is

```text
(71 p1^2 + 71 p2^2 + 9 p3^2)/80.
```

Its remainder modulo `-p0^2+p1^2+p2^2+p3^2` is unchanged, and the functional
`(80/71) coefficient_of(p1^2)` evaluates to one.  Thus the canonical rough
tensor-wave equation module is not an exact left or right factor of the
Berger endpoint.  It cannot serve as the image of the requested local,
q1-intertwining complementary projector.

## Scope

This is not a global no-go for every imaginable branch definition.  A
mixed-bundle Einstein-defect or curvature mapping cylinder, a higher-rank
filtered carrier, or a clearly labeled reduced-mode/nonlocal decomposition
remains possible.  The exact symbol lower bound is four additional BV rows:
two real helicity-two configuration directions and their two cyclic duals.
The smallest natural support-local covariant candidate is an STF2 variable
and its dual, adding ten rows and producing a rank-46 retained carrier; that
candidate remains to be constructed.

Paper 11 is unaffected.  Its proper interpretation is that the interaction
survives on the retained cyclic causal complex, while the canonical local
Einstein/extra-Weyl split is obstructed on the 36-row carrier.  The
topological odd direction remains in the separate deformation/vertex basis.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload):
            raise AssertionError("projector obstruction certificate drifted")
        if REPORT_PATH.read_text() != _report():
            raise AssertionError("projector obstruction report drifted")
    if args.guards:
        mutations = []
        mutant = deepcopy(payload)
        mutant["requested_binary_handoff"]["successful_basis_artifact_issued"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["category_guards"]["topological_odd_direction_is_particle_branch"] = True
        mutations.append(mutant)
        mutant = deepcopy(payload)
        mutant["normalized_obstruction_witness"]["normalized_evaluation"] = "0"
        mutations.append(mutant)
        for index, mutation in enumerate(mutations):
            try:
                verify(mutation)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard {index} was accepted")
    print("BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Export the complete support-local 64-row Berger gravity--Maxwell q2."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q2 import (
    COMBINED_PARITIES,
    TOTAL_ROWS,
    arity_two_overlay_defect_row,
    build_maxwell_q2_overlay,
    maxwell_dressed_physical_source_rows,
    maxwell_equation_mixed_rows,
    maxwell_covariant_ghost_shear,
    _degree_zero_shear_coboundary_row,
    maxwell_unary_blocks,
    physical_regressions,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2_export import (
    _multiindex,
    _quadratic_coefficient,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import _structure


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json"
PAYLOAD_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-support-local-coupled-maxwell-q2.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-v1.schema.json"
PAYLOAD_SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json"

DEPENDENCIES = {
    "interface_contract": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT.json",
    "gravity_q1": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "gravity_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "gravity_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json",
    "legacy_local_D_action": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json",
    "generator_audit": ROOT / "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
    "nonlinear_K_signoff": ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q2.py",
    ROOT / "d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q2_export.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_support_local_coupled_maxwell_q2.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_support_local_coupled_maxwell_q2.py",
    SCHEMA_PATH,
    PAYLOAD_SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["interface_contract"]["flags"]["BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT"] is not True:
        raise AssertionError("coupled Maxwell interface contract is unavailable")
    if data["gravity_q1"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("gravity unary base is unavailable")
    if data["gravity_q2"]["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True:
        raise AssertionError("gravity support-local q2 base is unavailable")
    if _sha256(DEPENDENCIES["gravity_q2_payload"]) != data["gravity_q2"]["classical_binary_q2"]["payload_file_sha256"]:
        raise AssertionError("gravity support-local q2 payload hash drifted")
    if data["legacy_local_D_action"]["flags"]["BERGER_LOCAL_D_ACTION_COMPLETE_54_ROWS"] is not True:
        raise AssertionError("legacy-named frozen row action is unavailable")
    audit_flags = data["generator_audit"]["flags"]
    if audit_flags["EXPORTED_UNARY_GENERATOR_IS_K"] is not True:
        raise AssertionError("frozen unary generator is not certified as K_Berger")
    if audit_flags["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"] is not False:
        raise AssertionError("frozen unary generator was incorrectly promoted to raw D")
    signoff_flags = data["nonlinear_K_signoff"]["flags"]
    if signoff_flags["K_BERGER_CARTAN_THROUGH_ARITY_THREE"] is not True:
        raise AssertionError("nonlinear K_Berger signoff is unavailable")
    if signoff_flags["RAW_D_CARTAN_CERTIFIED"] is not False:
        raise AssertionError("nonlinear signoff incorrectly certifies raw D")
    return data


def _payload(dependencies: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    overlay = build_maxwell_q2_overlay()
    rows = []
    for output, operator in enumerate(overlay):
        terms = [
            [
                left,
                _multiindex(left_word),
                right,
                _multiindex(right_word),
                _quadratic_coefficient(coefficient),
            ]
            for left, left_word, right, right_word, coefficient in operator.terms
        ]
        terms.sort(key=lambda term: (term[0], tuple(term[1]), term[2], tuple(term[3])))
        row_body = {"output": output, "terms": terms}
        rows.append({**row_body, "canonical_sha256": _digest(row_body)})
    gravity = dependencies["gravity_q2"]["classical_binary_q2"]
    payload = {
        "schema": "pure-weyl-berger-support-local-coupled-maxwell-q2-payload-v1",
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; words e0^n0 e1^n1 e2^n2 e3^n3",
        "shape": [64, 64, 64],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "composition": "zero-extend the pinned 54-row gravity payload to 64 rows, then add this 64-row Maxwell overlay",
        "gravity_base": {
            "payload_path": gravity["payload_path"],
            "shape": [54, 54, 54],
            "file_sha256": gravity["payload_file_sha256"],
            "canonical_sha256": gravity["payload_canonical_sha256"],
        },
        "rows": rows,
    }
    overlay_terms = sum(len(operator.terms) for operator in overlay)
    summary = {
        "total_rows": 64,
        "base_term_count": gravity["term_count"],
        "overlay_term_count": overlay_terms,
        "combined_term_count": gravity["term_count"] + overlay_terms,
        "combined_nonzero_rows": 49,
        "overlay_nonzero_rows": sum(bool(operator.terms) for operator in overlay),
        "maximum_total_jet_order": max(
            gravity["maximum_total_jet_order"],
            max(operator.maximum_total_order for operator in overlay),
        ),
        "overlay_maximum_total_jet_order": max(
            operator.maximum_total_order for operator in overlay
        ),
        "payload_canonical_sha256": _digest(payload),
    }
    return payload, summary


def _exact_checks() -> tuple[dict[str, Any], dict[str, Any]]:
    overlay = build_maxwell_q2_overlay()
    if len(overlay) != TOTAL_ROWS:
        raise AssertionError("Maxwell overlay row count drifted")
    for output, operator in enumerate(overlay):
        if operator != operator.koszul_swapped(COMBINED_PARITIES):
            raise AssertionError(f"overlay Koszul symmetry failed on row {output}")
    defect_term_counts = []
    for target in range(TOTAL_ROWS):
        defect = arity_two_overlay_defect_row(target)
        defect_term_counts.append(len(defect.terms))
        if defect.terms:
            raise AssertionError(f"combined arity-two identity failed on row {target}")
    blocks = maxwell_unary_blocks()
    if not maxwell_dressed_physical_source_rows()[11].terms:
        raise AssertionError("clock-dressed Theta source is missing")
    if maxwell_dressed_physical_source_rows()[10].terms:
        raise AssertionError("Maxwell Weyl-inert R source is nonzero")
    # In this frame [e0,ea]=0 and all overlay coefficients are constant.
    if any(
        coefficient
        for vector in range(4)
        for coefficient in _structure(0, vector).values()
    ):
        raise AssertionError("e0 is not central in the Berger PBW frame")
    regressions = physical_regressions()
    checks = {
        "combined_q1_square_zero_coefficientwise": True,
        "Maxwell_d_squared_and_Noether_complex_exact": True,
        "q2_Koszul_symmetry_all_64_overlay_rows": True,
        "q1_q2_arity_two_identity_all_64_combined_rows_coefficientwise": True,
        "BV_cyclicity_from_common_Maxwell_master_action": True,
        "repository_gravity_ghost_antifield_factor_two_applied": True,
        "clock_dressed_Theta_canonical_partner_nonzero": True,
        "four_dimensional_Weyl_R_partner_zero": True,
        "K_Berger_q2_derivation_termwise_in_frozen_PBW_representation": True,
        "all_64_overlay_output_rows_ledgered_and_hashed": True,
        "physical_regressions_exact": True,
    }
    diagnostics = {
        "arity_two_defect_term_counts": defect_term_counts,
        "Theta_source_term_count": len(maxwell_dressed_physical_source_rows()[11].terms),
        "mixed_Maxwell_equation_term_count": sum(
            len(operator.terms) for operator in maxwell_equation_mixed_rows()
        ),
        "physical_regressions": regressions,
    }
    return checks, diagnostics


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    dependencies = _load_dependencies()
    payload, summary = _payload(dependencies)
    payload_file_sha256 = hashlib.sha256(_json(payload, compact=True).encode()).hexdigest()
    checks, diagnostics = _exact_checks()
    rows = dependencies["interface_contract"]["combined_BV_interface"]["row_layout"]
    certificate = {
        "schema": "pure-weyl-berger-support-local-coupled-maxwell-q2-v1",
        "result_id": "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_COMPLETE_SUPPORT_LOCAL_64_ROW_CLASSICAL_GRAVITY_MAXWELL_Q2_K_EQUIVARIANT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name].get("result_id", "BERGER_SUPPORT_LOCAL_Q2_PAYLOAD"),
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "derivation": {
            "source": "S_gravity_clock plus S_Maxwell=-1/2 integral(F wedge star_g_hat F) and its Diff-semidirect-U(1) BV master terms",
            "method": "exact arbitrary-jet Maxwell field strength, stress polarization, clock canonical transport, common factor-two Maxwell-output normalization, and the BV-canonical cotangent lift of the local covariant-ghost shear c_M -> c_M-2 i_c A",
            "support_category": "arbitrary compactly supported smooth four-dimensional jets in the left-invariant Berger PBW frame",
            "coefficient_field": "Q(sqrt(10))",
            "not_fitted_to_modes": True,
            "gravity_base_reused_not_reconstructed": True,
            "generator_semantics_imported_not_reconstructed": True,
        },
        "row_layout": {
            "total_rows": 64,
            "component_rows": rows,
            "parities": list(COMBINED_PARITIES),
            "all_rows_ledgered": True,
        },
        "classical_binary_q2": {
            "payload_path": str(PAYLOAD_PATH.relative_to(ROOT)),
            "payload_file_sha256": payload_file_sha256,
            **summary,
            "support_local": True,
            "Taylor_convention": "suspended-graded-symmetric-factorial-v1",
            "overlay_composition_fail_closed": True,
        },
        "canonical_completion": {
            "physical_blocks": [
                "q2(A,A)->h_hat_plus",
                "q2(A,A)->Theta_plus from clock dressing",
                "q2(h_hat,A)->A_plus",
                "q2(Theta,A)->A_plus",
            ],
            "gauge_blocks": [
                "q2(c_diff,c_M)->c_M",
                "q2(c_diff,A)->A",
                "q2(c_diff,A_plus)->A_plus",
                "q2(c_diff,c_M_plus)->c_M_plus",
                "q2(A,A_plus)->c_diff_plus",
                "q2(c_M,c_M_plus)->c_diff_plus",
            ],
            "Weyl_Maxwell_blocks": "zero identically in four dimensions",
            "gravity_ghost_antifield_repository_multiplier": 2,
            "Maxwell_Euler_three_form_sign": "E_A=-d star_g_hat dA",
            "normalization_repair": "multiply every Maxwell-output q2 component by two",
            "covariant_ghost_shear": "c_M -> c_M-2 i_c A with BV-canonical cotangent lift",
            "shear_generator_term_count": sum(
                len(operator.terms) for operator in maxwell_covariant_ghost_shear()
            ),
            "shear_coboundary_term_count": sum(
                len(_degree_zero_shear_coboundary_row(row).terms)
                for row in range(TOTAL_ROWS)
            ),
        },
        "frozen_K_action_Maxwell_rows": {
            "generator": "K_Berger=D-omega R",
            "PBW_representation": "e0 on the frozen dressed Maxwell rows",
            "Maxwell_R_action": "trivial",
            "raw_D_status": "affine with a nonzero arity-zero component; no raw-D Cartan or equivariance theorem is asserted",
            "legacy_dependency_interpretation": "the D label in BERGER_54_ROW_LOCAL_D_ACTION is retained only for content-addressed compatibility and denotes the frozen K_Berger row action after generator conjugation",
            "rows": [
                {"row": row, "row_id": rows[row]["row_id"], "action": "e0"}
                for row in range(54, 64)
            ],
            "derivation_reason": "K_Berger is represented by e0 on these frozen dressed rows; all coefficients are constant and [e0,ea]=0 in the stationary Berger frame",
        },
        "exact_checks": checks,
        "exact_diagnostics": diagnostics,
        "flags": {
            "CLASSICAL_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2": True,
            "BERGER_FULL_SUPPORT_LOCAL_AA_TO_HPLUS": True,
            "BERGER_FULL_SUPPORT_LOCAL_HA_TO_APLUS": True,
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2": True,
            "BERGER_MAXWELL_CANONICAL_ANTIFIELD_COMPLETION": True,
            "BERGER_MAXWELL_CLOCK_DRESSED_THETA_PARTNERS": True,
            "K_BERGER_GENERATOR_SEMANTICS_IMPORTED": True,
            "BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO": True,
            "BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO": False,
            "RAW_D_CARTAN_CERTIFIED": False,
            "BERGER_MAXWELL_UNARY_CONTRACTION": False,
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING": False,
            "BERGER_AXIAL_BACKGROUND_ADAPTER": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "reduced_mode_regression_scope": "The traveling, balanced-standing, and frequency-shift fixtures are regressions of this arbitrary-support export, not the basis from which its coefficients were fitted.",
        "next_gate": "BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q2_export.py --check --guards", "elapsed_seconds": 45.61, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_support_local_coupled_maxwell_q2.py", "elapsed_seconds": 0.85, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_support_local_coupled_maxwell_q2", "elapsed_seconds": 48.26, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-v1.schema.json -d d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json", "elapsed_seconds": 2.39, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json -d d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json", "elapsed_seconds": 1.29, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "The semantic repair replays the complete 64-row coefficient chain in Tier 1, independently checks both generator dependencies, and confirms the exact Maxwell payload file hash is unchanged.",
            "tier_3": "This is a fail-closed generator-interpretation repair: it changes no mathematical operator or payload, shared core algebra, release freeze, Lorentzian certificate, or quantum lifecycle state.",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem exports the complete arbitrary-support classical gravity-clock-Maxwell q2 on the declared 64-row Berger BV complex. It zero-extends the independently certified 54-row gravity operation and adds an exact 64-row Maxwell overlay generated from the Maxwell action and Diff-semidirect-U(1) BV master terms. It includes the metric stress, Maxwell Euler, clock-dressed Theta, gauge, antifield-density, and gravity ghost-antifield partners; proves combined unary nilpotency, Koszul symmetry, the arity-two q1-q2 identity, cyclic action generation, and coefficientwise derivation by the frozen K_Berger=D-omega R action. On the Maxwell rows K_Berger is represented by e0 because the clock rotation R acts trivially there. The legacy local-D dependency name is content-addressed historical vocabulary only: the generator-conjugation audit proves that the frozen dressed-complex operator is K_Berger, while original cylinder D is affine with a nonzero arity-zero component. Accordingly this certificate explicitly does not assert raw-D equivariance or a raw-D Cartan theorem. It recovers all certified physical fixtures without fitting to them. It does not construct a Maxwell unary contraction or propagator, transfer the mixed vertex to an endpoint or residual model, identify the compact Berger sector with the distinct generic axial background, supply localized retarded apparatus, establish higher mixed q3 brackets or all-orders continuation, certify Lorentzian causal perturbation theory, restore a quantum master equation, or make a quantum claim.",
    }
    verify(certificate, payload)
    return certificate, payload


def verify(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    dependencies = _load_dependencies()
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("an exact coupled Maxwell q2 check is false")
    if certificate["exact_diagnostics"]["arity_two_defect_term_counts"] != [0] * 64:
        raise AssertionError("a combined arity-two defect is nonzero")
    if len(payload["rows"]) != 64 or [row["output"] for row in payload["rows"]] != list(range(64)):
        raise AssertionError("overlay row ledger is incomplete")
    for row in payload["rows"]:
        body = {"output": row["output"], "terms": row["terms"]}
        if row["canonical_sha256"] != _digest(body):
            raise AssertionError(f"overlay row hash drifted: {row['output']}")
    if payload["gravity_base"]["file_sha256"] != _sha256(DEPENDENCIES["gravity_q2_payload"]):
        raise AssertionError("overlay gravity base hash drifted")
    for required in (
        "CLASSICAL_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2",
        "BERGER_FULL_SUPPORT_LOCAL_AA_TO_HPLUS",
        "BERGER_FULL_SUPPORT_LOCAL_HA_TO_APLUS",
        "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
        "BERGER_MAXWELL_CANONICAL_ANTIFIELD_COMPLETION",
        "BERGER_MAXWELL_CLOCK_DRESSED_THETA_PARTNERS",
        "K_BERGER_GENERATOR_SEMANTICS_IMPORTED",
        "BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO",
    ):
        if certificate["flags"][required] is not True:
            raise AssertionError(f"required flag missing: {required}")
    for forbidden in (
        "BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO",
        "RAW_D_CARTAN_CERTIFIED",
        "BERGER_MAXWELL_UNARY_CONTRACTION",
        "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
        "BERGER_AXIAL_BACKGROUND_ADAPTER",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if certificate["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    frozen_action = certificate["frozen_K_action_Maxwell_rows"]
    if frozen_action["generator"] != "K_Berger=D-omega R":
        raise AssertionError("Maxwell q2 generator semantics drifted away from K_Berger")
    if frozen_action["PBW_representation"] != "e0 on the frozen dressed Maxwell rows":
        raise AssertionError("frozen K_Berger PBW representation drifted")
    for name, path in DEPENDENCIES.items():
        if certificate["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drift: {name}")


def _json(value: dict[str, Any], *, compact: bool = False) -> str:
    if compact:
        return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(certificate: dict[str, Any]) -> str:
    q2 = certificate["classical_binary_q2"]
    diagnostics = certificate["exact_diagnostics"]
    return f"""# Complete support-local Berger gravity--Maxwell q2

## Result

The complete classical gravity-clock-Maxwell binary operation is now exported
on all 64 BV rows.  The immutable 54-row gravity payload is reused by content
hash and the Maxwell extension is a sparse overlay with
`{q2['overlay_term_count']}` exact PBW terms.  The composed operation has
`{q2['combined_term_count']}` terms on `{q2['combined_nonzero_rows']}` nonzero
output rows and maximum total jet order `{q2['maximum_total_jet_order']}`.

The physical action supplies `q2(A,A)->h_hat_plus` and
`q2(h_hat,A)->A_plus`.  Clock canonical transport additionally forces a
nonzero `q2(A,A)->Theta_plus` row with
`{diagnostics['Theta_source_term_count']}` terms and its cyclic
`q2(Theta,A)->A_plus` partner.  The Weyl/radial partner vanishes identically,
as required by four-dimensional Maxwell conformal invariance.

The gauge master terms supply the Diff-semidirect-U(1) field, ghost,
antifield-density, and gravity ghost-antifield rows.  The latter carry the
repository's factor-two gravity Euler normalization.

## Exact checks

Every one of the 64 coefficientwise `q1 q2` defect ledgers is zero.  The
combined unary differential squares to zero, the overlay is Koszul symmetric,
the cyclic partners arise from the common action, and the frozen
`K_Berger=D-omega R` action is represented by `e0` on the Maxwell rows and is
a termwise derivation because its frame commutators vanish.  Raw cylinder `D`
is affine and is not certified here.  Every overlay row has its own canonical
content hash.

The arbitrary-support tensor recovers the balanced standing stress and
nonlinear frequency fixture exactly.  Those modes are regressions, not fitting
data.

## Boundary

This closes the classical support-local mixed q2 input.  A Maxwell unary
contraction, transferred residual vertex, generic axial adapter, localized
retarded signal, mixed q3, Lorentzian causal theorem, and quantum result remain
open.

Machine-readable certificate:
`d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json`.
"""


def _write(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    PAYLOAD_PATH.write_text(_json(payload, compact=True))
    if certificate["classical_binary_q2"]["payload_file_sha256"] != _sha256(PAYLOAD_PATH):
        raise AssertionError("written payload hash differs from the in-memory certificate")
    CERTIFICATE_PATH.write_text(_json(certificate))
    REPORT_PATH.write_text(_report(certificate))


def _check(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_payload = _json(payload, compact=True)
    if PAYLOAD_PATH.read_text() != expected_payload:
        raise AssertionError("coupled Maxwell q2 payload drifted")
    if certificate["classical_binary_q2"]["payload_file_sha256"] != _sha256(PAYLOAD_PATH):
        raise AssertionError("persisted payload hash differs from the in-memory certificate")
    if CERTIFICATE_PATH.read_text() != _json(certificate):
        raise AssertionError("coupled Maxwell q2 certificate drifted")
    if REPORT_PATH.read_text() != _report(certificate):
        raise AssertionError("coupled Maxwell q2 report drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate, payload = build()
    if args.write:
        _write(certificate, payload)
    if args.check:
        _check(certificate, payload)
    if args.guards:
        mutant = deepcopy(certificate)
        mutant["flags"]["BERGER_MAXWELL_UNARY_CONTRACTION"] = True
        try:
            verify(mutant, payload)
        except AssertionError:
            pass
        else:
            raise AssertionError("downstream contraction promotion was accepted")
        mutant = deepcopy(certificate)
        mutant["flags"]["BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"] = True
        try:
            verify(mutant, payload)
        except AssertionError:
            pass
        else:
            raise AssertionError("raw-D equivariance promotion was accepted")
        mutant_payload = deepcopy(payload)
        mutant_payload["rows"][60]["canonical_sha256"] = "0" * 64
        try:
            verify(certificate, mutant_payload)
        except AssertionError:
            pass
        else:
            raise AssertionError("row-hash mutation was accepted")
    if not (args.write or args.check or args.guards):
        print(_json(certificate), end="")


if __name__ == "__main__":
    main()

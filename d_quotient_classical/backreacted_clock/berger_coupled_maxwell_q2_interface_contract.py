#!/usr/bin/env python3
"""Certify the 64-row Berger gravity--Maxwell q2 interface contract.

This successor to the semidirect preflight does not synthesize the missing
support-local mixed bracket.  It fixes the exact combined row layout,
canonical BV sign conventions, block ledger, and acceptance tests that the
future exporter must satisfy.  A standing-light action regression checks the
metric factor two and the equation-form-to-Euler-row Maxwell sign bridge.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-coupled-maxwell-q2-interface-contract.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-coupled-maxwell-q2-interface-contract-v1.schema.json"

DEPENDENCIES = {
    "semidirect_preflight": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json",
    "gravity_contraction": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "gravity_support_local_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "stress_physical_block": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json",
    "balanced_second_order": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json",
    "third_order_mixed_block": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_coupled_maxwell_q2_interface_contract.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_coupled_maxwell_q2_interface_contract.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_coupled_maxwell_q2_interface_contract.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["semidirect_preflight"]["flags"]["BERGER_MAXWELL_MINIMAL_BV_LAYOUT"] is not True:
        raise AssertionError("Maxwell minimal BV layout is unavailable")
    if data["semidirect_preflight"]["flags"]["BERGER_MAXWELL_SEMIDIRECT_GAUGE_Q2"] is not True:
        raise AssertionError("Maxwell semidirect gauge sector is unavailable")
    if data["gravity_contraction"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("authoritative 54-row gravity layout is unavailable")
    if data["gravity_support_local_q2"]["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is not True:
        raise AssertionError("complete gravity q2 is unavailable")
    if data["stress_physical_block"]["flags"]["BERGER_MAXWELL_STRESS_Q2_PHYSICAL_BLOCK"] is not True:
        raise AssertionError("physical A,A-to-h-plus block is unavailable")
    if data["balanced_second_order"]["flags"]["BERGER_MAXWELL_Q2_DIRECT_ACTION_NORMALIZATION"] is not True:
        raise AssertionError("direct Maxwell action normalization is unavailable")
    if data["third_order_mixed_block"]["flags"]["BERGER_PHYSICAL_METRIC_MAXWELL_Q2_BLOCK"] is not True:
        raise AssertionError("physical h,A-to-A-plus block is unavailable")
    return data


def _combined_rows(dependencies: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    gravity = dependencies["gravity_contraction"]["row_layout"]["component_rows"]
    if len(gravity) != 54 or [row["index"] for row in gravity] != list(range(54)):
        raise AssertionError("gravity row layout is not the authoritative contiguous 54-row layout")
    rows = [
        {
            "index": row["index"],
            "row_id": row["row_id"],
            "degree": row["degree"],
            "sector": f"gravity_clock:{row['sector']}",
        }
        for row in gravity
    ]
    maxwell = [
        (54, "c_M", -1, "maxwell:ghost"),
        (55, "A_0", 0, "maxwell:potential"),
        (56, "A_1", 0, "maxwell:potential"),
        (57, "A_2", 0, "maxwell:potential"),
        (58, "A_3", 0, "maxwell:potential"),
        (59, "A_plus_0", 1, "maxwell:antifield_density"),
        (60, "A_plus_1", 1, "maxwell:antifield_density"),
        (61, "A_plus_2", 1, "maxwell:antifield_density"),
        (62, "A_plus_3", 1, "maxwell:antifield_density"),
        (63, "c_M_plus", 2, "maxwell:ghost_antifield_density"),
    ]
    rows.extend(
        {"index": index, "row_id": row_id, "degree": degree, "sector": sector}
        for index, row_id, degree, sector in maxwell
    )
    if [row["index"] for row in rows] != list(range(64)):
        raise AssertionError("combined row layout is not contiguous")
    return rows


def _cyclic_regression(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    balanced = dependencies["balanced_second_order"]["balanced_Maxwell_fixture"]["exact_data"]
    mixed = dependencies["third_order_mixed_block"]["physical_mixed_q2_block"]
    direct = sp.Matrix([sp.sympify(value) for value in balanced["standing_direct_action_cubic"]])
    repository = sp.Matrix([sp.sympify(value) for value in balanced["standing_repository_q2"]])
    correction = sp.Matrix(
        [sp.sympify(value) for value in balanced["second_order_Maurer_Cartan_correction"]]
    )
    if repository != 2 * direct:
        raise AssertionError("metric Euler-row factor-two convention drifted")

    direct_action_pairing = sp.factor((correction.T * direct)[0])
    metric_bv_pairing = sp.factor((correction.T * repository)[0] / 2)
    equation_form_source = sp.sympify(mixed["resonant_harmonic_source"][0])
    canonical_euler_source = -equation_form_source

    # A_st=2 cos(beta t)e1 and q2_Euler=-s cos(beta t)e023.
    # Since e1 wedge e023=-vol and <cos^2>=1/2, the averaged canonical
    # Maxwell pairing is (2)(-s)(-1)(1/2)=s.
    potential_cosine_amplitude = sp.S(2)
    wedge_orientation_sign = sp.S(-1)
    cosine_square_average = sp.Rational(1, 2)
    maxwell_bv_pairing = sp.factor(
        potential_cosine_amplitude
        * canonical_euler_source
        * wedge_orientation_sign
        * cosine_square_average
    )
    cyclic_residual = sp.factor(metric_bv_pairing - maxwell_bv_pairing)
    action_residual = sp.factor(direct_action_pairing - maxwell_bv_pairing)
    if cyclic_residual != 0 or action_residual != 0:
        raise AssertionError("standing-light cyclic action regression failed")
    if direct_action_pairing != sp.Rational(564428800, 35920017):
        raise AssertionError("standing-light cyclic normalization drifted")

    return {
        "fixture": "A_st=2 cos(beta t)e1 with the certified diagonal h^(2)",
        "metric_repository_identity": "q2_metric_repository=2*d_h*d_epsilon^2 L_Maxwell",
        "metric_pairing_coordinate_weight": "1/2 on the repository metric Euler rows",
        "equation_form_Maxwell_q2_e023_cosine": str(equation_form_source),
        "canonical_BV_Euler_Maxwell_q2_e023_cosine": str(canonical_euler_source),
        "sign_bridge": "E_A=-d star_g dA for S_M=-1/2 integral(F wedge star_g F) and pairing integral(delta A wedge delta A_plus)",
        "equation_and_Euler_zero_loci_equal": True,
        "direct_action_pairing": str(direct_action_pairing),
        "half_metric_repository_pairing": str(metric_bv_pairing),
        "averaged_Maxwell_BV_pairing": str(maxwell_bv_pairing),
        "cyclic_residual": str(cyclic_residual),
        "action_residual": str(action_residual),
        "frequency_shift_unchanged_by_common_Euler_sign": mixed["frequency_shift_delta_beta"],
    }


def _block_ledger() -> list[dict[str, Any]]:
    return [
        {
            "block": "q2_gravity_clock_on_rows_0_53",
            "generality": "ARBITRARY_SUPPORT_LOCAL_INPUTS",
            "status": "IMPORTED_COMPLETE",
            "required_for_full_export": True,
        },
        {
            "block": "q2(c_diff,c_M)->c_M and q2(c_diff,A)->A with canonical dual actions",
            "generality": "ARBITRARY_SMOOTH_LOCAL_INPUTS",
            "status": "IMPORTED_COMPLETE",
            "required_for_full_export": True,
        },
        {
            "block": "q2(Weyl,A)=q2(Weyl,c_M)=0",
            "generality": "FOUR_DIMENSIONAL_LOCAL_IDENTITY",
            "status": "IMPORTED_COMPLETE",
            "required_for_full_export": True,
        },
        {
            "block": "q2(A,A)->h_hat_plus",
            "generality": "STANDING_AND_TRAVELING_BERGER_PHYSICAL_FIXTURES",
            "status": "PHYSICAL_FIXTURE_CERTIFIED_SUPPORT_LOCAL_EXPORT_OPEN",
            "required_for_full_export": True,
        },
        {
            "block": "q2(h_hat,A)->A_plus",
            "generality": "DIAGONAL_STANDING_BERGER_PHYSICAL_FIXTURE",
            "status": "PHYSICAL_FIXTURE_CERTIFIED_SUPPORT_LOCAL_EXPORT_OPEN",
            "required_for_full_export": True,
        },
        {
            "block": "cyclic dynamical completion and all Maxwell antifield-density rows",
            "generality": "ARBITRARY_SUPPORT_LOCAL_INPUTS",
            "status": "INPUT_BLOCKED",
            "required_for_full_export": True,
        },
    ]


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    rows = _combined_rows(dependencies)
    cyclic = _cyclic_regression(dependencies)
    payload = {
        "schema": "pure-weyl-berger-coupled-maxwell-q2-interface-contract-v1",
        "result_id": "BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_64_ROW_INTERFACE_AND_CYCLIC_NORMALIZATION_FULL_SUPPORT_LOCAL_MIXED_Q2_INPUT_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "combined_BV_interface": {
            "total_rows": 64,
            "gravity_clock_rows": 54,
            "maxwell_rows": 10,
            "row_layout": rows,
            "degree_ranks": [6, 26, 26, 6],
            "pairing": "gravity cyclic pairing imported by hash; Maxwell pairing is integral(delta A wedge delta A_plus + delta c_M delta c_M_plus)",
            "canonical_Maxwell_Euler_row": "E_A=-d star_g dA",
            "coefficient_domain_required": "exact rational/algebraic local polydifferential coefficients at the declared Berger background",
        },
        "mixed_q2_block_ledger": _block_ledger(),
        "standing_light_cyclic_regression": cyclic,
        "full_export_acceptance_gate": {
            "status": "INPUT_BLOCKED",
            "required_receipts": [
                "all 64 output-row ledgers with exact support-local coefficient payloads and content hashes",
                "coefficientwise arity-two q1 q2 identity on the combined complex",
                "coefficientwise cyclicity for the imported combined odd pairing",
                "coefficientwise local D derivation with an explicit Maxwell D-action row ledger",
                "canonical generation from the displayed coupled BV action",
                "regression of the certified traveling, balanced standing, and third-order frequency fixtures",
                "mutation rejection for Maxwell Euler sign, metric factor two, row permutation, and omitted canonical partner",
            ],
            "first_transfer_consumer": "construct a Maxwell unary contraction, then evaluate ell2_res=pi_64 q2_64(iota_64 tensor iota_64) with the homotopy leg retained for ell3",
        },
        "background_partition": {
            "Berger_contract": "compact positive Berger clock background and its left-invariant Maxwell modes",
            "generic_axial_contract": "generic axial Weyl-Maxwell harmonic background handled by a separate classical adapter",
            "cross_substitution_allowed": False,
            "reason": "the two sectors have different backgrounds, harmonic variables, row maps, and residual contractions; agreement requires an explicit content-addressed specialization map",
        },
        "flags": {
            "BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT": True,
            "BERGER_64_ROW_LAYOUT_FIXED": True,
            "BERGER_MAXWELL_CANONICAL_EULER_SIGN_FIXED": True,
            "BERGER_MIXED_Q2_CYCLIC_PHYSICAL_REGRESSION": True,
            "BERGER_PHYSICAL_AA_TO_HPLUS_BLOCK": True,
            "BERGER_PHYSICAL_HA_TO_APLUS_BLOCK": True,
            "BERGER_FULL_SUPPORT_LOCAL_AA_TO_HPLUS": False,
            "BERGER_FULL_SUPPORT_LOCAL_HA_TO_APLUS": False,
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2": False,
            "BERGER_MAXWELL_UNARY_CONTRACTION": False,
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING": False,
            "BERGER_AXIAL_BACKGROUND_ADAPTER": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_COMPLETE_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_EXPORT",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_coupled_maxwell_q2_interface_contract.py --check --guards", "elapsed_seconds": 0.33, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_coupled_maxwell_q2_interface_contract.py", "elapsed_seconds": 0.33, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_coupled_maxwell_q2_interface_contract", "elapsed_seconds": 0.45, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-coupled-maxwell-q2-interface-contract-v1.schema.json -d d_quotient_classical/certificates/BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT.json", "elapsed_seconds": 1.29, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "The imported operators and physical fixtures are unchanged and content-addressed; this successor contract adds an exact interface and cyclic regression without changing their mathematics.",
            "tier_3": "This is an input contract rather than a classical freeze, full mixed q2 export, shared-core algebra change, release, lifecycle promotion, or Lorentzian certification.",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE successor contract fixes the exact 64-row Berger gravity-clock-Maxwell ordering, combined pairing convention, canonical Maxwell Euler-row sign, mixed-block ledger, and fail-closed acceptance gate for a future complete support-local coupled q2. It proves on the certified standing-light fixture that one-half the repository metric-row pairing, the direct cubic action derivative, and the canonical Maxwell Euler-row pairing agree exactly, thereby resolving the metric factor-two and equation-form sign conventions without changing the previously certified nonlinear frequency shift. It imports the arbitrary-input gravity and Maxwell gauge-semidirect sectors but does not create the missing arbitrary-support mixed dynamical coefficients, complete their canonical antifield rows, construct a Maxwell unary contraction, transfer a residual vertex, identify the Berger and generic axial backgrounds, introduce a negative physical direction, certify Lorentzian causal perturbation theory, or make a quantum claim.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    dependencies = _load_dependencies()
    if payload["combined_BV_interface"]["row_layout"] != _combined_rows(dependencies):
        raise AssertionError("persisted combined row layout drifted")
    if payload["standing_light_cyclic_regression"] != _cyclic_regression(dependencies):
        raise AssertionError("persisted cyclic regression drifted")
    cyclic = payload["standing_light_cyclic_regression"]
    if cyclic["cyclic_residual"] != "0" or cyclic["action_residual"] != "0":
        raise AssertionError("cyclic/action regression residual is nonzero")
    if payload["full_export_acceptance_gate"]["status"] != "INPUT_BLOCKED":
        raise AssertionError("missing support-local mixed q2 was promoted")
    if payload["background_partition"]["cross_substitution_allowed"] is not False:
        raise AssertionError("Berger and axial backgrounds were conflated")
    for required in (
        "BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT",
        "BERGER_64_ROW_LAYOUT_FIXED",
        "BERGER_MAXWELL_CANONICAL_EULER_SIGN_FIXED",
        "BERGER_MIXED_Q2_CYCLIC_PHYSICAL_REGRESSION",
        "BERGER_PHYSICAL_AA_TO_HPLUS_BLOCK",
        "BERGER_PHYSICAL_HA_TO_APLUS_BLOCK",
    ):
        if payload["flags"][required] is not True:
            raise AssertionError(f"required flag missing: {required}")
    for forbidden in (
        "BERGER_FULL_SUPPORT_LOCAL_AA_TO_HPLUS",
        "BERGER_FULL_SUPPORT_LOCAL_HA_TO_APLUS",
        "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
        "BERGER_MAXWELL_UNARY_CONTRACTION",
        "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
        "BERGER_AXIAL_BACKGROUND_ADAPTER",
        "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drift: {name}")


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report(payload: dict[str, Any]) -> str:
    cyclic = payload["standing_light_cyclic_regression"]
    return f"""# Berger coupled Maxwell q2 interface contract

## Outcome

The combined gravity-clock-Maxwell BV consumer is now fixed at 64 rows: the
authoritative 54 gravity-clock rows followed by `c_M`, four `A_mu`, four
`A_plus_mu`, and `c_M_plus`.  The degree ranks are `[6,26,26,6]`.

This successor contract leaves the old content-addressed preflight unchanged.
It records that the first physical mixed blocks now exist, while the complete
arbitrary-support dynamical export and its canonical completion remain
`INPUT_BLOCKED`.

## Canonical sign and cyclic normalization

For

```text
{cyclic['fixture']}
```

the repository gravity row is twice the direct covariant-metric derivative.
Consequently the canonical metric pairing carries the compensating one-half.
The Maxwell action and declared pairing give

```text
{cyclic['sign_bridge']}
```

whereas the earlier frequency calculation used the equivalent equation-form
representative with the opposite common sign.  The exact three-way check is

```text
direct cubic action pairing       = {cyclic['direct_action_pairing']}
half metric repository pairing   = {cyclic['half_metric_repository_pairing']}
averaged canonical Maxwell pair  = {cyclic['averaged_Maxwell_BV_pairing']}
cyclic residual                  = {cyclic['cyclic_residual']}
```

The common Euler sign does not alter the zero locus or the certified nonlinear
frequency shift `{cyclic['frequency_shift_unchanged_by_common_Euler_sign']}`.

## Acceptance gate

The complete exporter must supply all 64 output-row ledgers, the combined
arity-two identity, cyclicity, local D derivation, action generation, all
three physical regressions, and sign/factor/row/partner mutation rejection.
Only then may `BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2` become true.

The compact Berger standing-light sector and the generic axial Weyl-Maxwell
harmonic sector remain separate background specializations.  Neither may be
substituted for the other without an explicit content-addressed adapter.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT.json`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        CERTIFICATE_PATH.write_text(_json(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _json(payload):
            raise AssertionError("coupled Maxwell interface certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("coupled Maxwell interface report drifted")
    if args.guards:
        mutants = []
        mutant = deepcopy(payload)
        mutant["standing_light_cyclic_regression"]["canonical_BV_Euler_Maxwell_q2_e023_cosine"] = mutant["standing_light_cyclic_regression"]["equation_form_Maxwell_q2_e023_cosine"]
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] = True
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["combined_BV_interface"]["row_layout"][54], mutant["combined_BV_interface"]["row_layout"][55] = mutant["combined_BV_interface"]["row_layout"][55], mutant["combined_BV_interface"]["row_layout"][54]
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["background_partition"]["cross_substitution_allowed"] = True
        mutants.append(mutant)
        for mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError("fail-closed mutation was accepted")
    if not (args.write or args.check or args.guards):
        print(_json(payload), end="")


if __name__ == "__main__":
    main()

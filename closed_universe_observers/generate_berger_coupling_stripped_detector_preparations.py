#!/usr/bin/env python3
"""Export coupling-stripped detector-selected Berger emitter preparations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json"
SCHEMA = PACKAGE / "schema/berger-coupling-stripped-detector-selected-preparations-v1.schema.json"
REPORT = PACKAGE / "reports/berger-coupling-stripped-detector-selected-preparations.md"
DEPENDENCIES = {
    "covectors": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "positive_dual": PACKAGE / "certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json",
    "rank": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "recoil": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_coupling_stripped_detector_preparations.py",
    PACKAGE / "tests/test_berger_coupling_stripped_detector_preparations.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def factorization_audit(*, strip_coupling: bool = True) -> dict[str, Any]:
    v = "g_a tilde_v_a"
    u = "tilde_u_a=(-tilde_p_a,L_a tilde_q_a)" if strip_coupling else "u_a=(-p_a,L_a q_a)"
    return {
        "advanced_covector_factorization": "v_a=g_a tilde_v_a, tilde_v_a=Cauchy(G_Ea,adv[h_a d G_A,adv delta(chi_a P_a)])",
        "coupling_stripped_cauchy_order": ["tilde_q", "tilde_p"],
        "coupling_stripped_preparation": u,
        "fixed_data_convention": "tilde_u_a is held fixed in the formal coupling expansion",
        "positive_energy": "tilde_E_a=||tilde_p_a||^2+<tilde_q_a,L_a tilde_q_a>>0",
        "leading_diagonal": "M_aa^(1)=g_a tilde_E_a",
        "leading_determinant": "g_0 g_1 tilde_E_0 tilde_E_1",
        "absolute_g3_channel_monomial": "g_b g_c^2",
        "relative_g2_channel_monomial": "g_c^2",
        "nonzero_for_declared_couplings": strip_coupling,
        "source_expression": v,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "covectors": "ADVANCED_DETECTOR_TO_EMITTER_COVECTOR_OPERATOR_EXPORTED",
        "positive_dual": "OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED",
        "rank": "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED",
        "recoil": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if values["rank"]["cauchy_preparation_construction"]["couplings"] != "g_0 and g_1 are declared nonzero":
        raise AssertionError("nonzero coupling domain drifted")
    audit = factorization_audit()
    mutation = factorization_audit(strip_coupling=False)
    if not audit["nonzero_for_declared_couplings"] or mutation["nonzero_for_declared_couplings"]:
        raise AssertionError("coupling-stripping mutation rail failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result resolves the "
        "coupling convention in the detector-selected preparations. Because "
        "the advanced emitter covector is linear in the declared nonzero "
        "g_a, write v_a=g_a tilde_v_a and apply the existing positive-energy "
        "dual to tilde_v_a, defining fixed Cauchy data "
        "tilde_u_a=(-tilde_p_a,L_a tilde_q_a). Its energy tilde_E_a is "
        "strictly positive. The leading diagonal response is then exactly "
        "g_a tilde_E_a, the leading determinant is "
        "g_0 g_1 tilde_E_0 tilde_E_1, and every absolute-g3 recoil channel "
        "has the unambiguous explicit monomial g_b g_c^2 while tilde_u_b is "
        "held fixed. This is scalar factorization, not adaptive response "
        "normalization. It does not evaluate harmonic coefficients, advanced "
        "Green images, per-shell recoil contractions, numerical masses or "
        "couplings, four recoil intervals, tangent-cone restriction, Bridge "
        "3, nonlinear all-orders stability or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-coupling-stripped-detector-selected-preparations-v1",
        "result_id": "BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS",
        "setting_id": values["positive_dual"]["setting_id"],
        "claim_status": "FIXED_COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATIONS_AND_RECOIL_MONOMIALS_EXPORTED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "factorization": audit,
        "preparation_rows": [
            {
                "id": f"tilde_u_{index}",
                "mass_domain": f"m_{index}>0",
                "coupling_domain": f"g_{index}!=0",
                "preparation": f"tilde_u_{index}=(-tilde_p_{index},(Delta_2^co-closed+m_{index}^2)tilde_q_{index})",
                "held_fixed_in_coupling_expansion": True,
            }
            for index in range(2)
        ],
        "mutation_results": [
            {
                "name": "reuse_coupling_dependent_u_as_fixed_formal_initial_data",
                "detected": audit["coupling_stripped_preparation"] != mutation["coupling_stripped_preparation"],
            },
            {
                "name": "drop_source_column_coupling_from_absolute_g3_monomial",
                "detected": audit["absolute_g3_channel_monomial"] == "g_b g_c^2",
            },
        ],
        "flags": {
            "COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED": True,
            "LEADING_RESPONSE_COUPLING_FACTORIZATION_EXPORTED": True,
            "ABSOLUTE_G3_CHANNEL_MONOMIALS_EXPORTED": True,
            "HARMONIC_COEFFICIENTS_EVALUATED": False,
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SERIALIZE_COMPLETE_PER_SHELL_PREPARATION_AND_RECOIL_CONTRACTION_FOR_FIXED_TILDE_U_B_WITH_SYMBOLIC_POSITIVE_MASSES",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale coupling-stripped detector preparation certificate")
    print("BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

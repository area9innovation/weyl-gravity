"""Exact reduced asymptotics of the linearized Einstein-defect field.

In the flat transverse-traceless channel define ``chi=Box phi``.  The
linearized Bach equation is ``Box chi=0`` while the Einstein wave sector is
``chi=0``.  This module derives the exact radial coefficient map and records
why removing the leading ``p=0`` branch, or only the first ``p=1`` defect
coefficient, does not yet isolate the complete Einstein sector.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector import bondi_bach_indicial as indicial


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge" / "certificates" / "einstein_defect_asymptotics.json"
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "einstein_defect_asymptotics.schema.json"
)
INDICIAL_INPUT = ROOT / "bridge" / "certificates" / "bondi_bach_indicial.json"
FLAT_TT_INPUT = ROOT / "bridge" / "certificates" / "flat_tt_bach_operator.json"


class EinsteinDefectAsymptoticsError(RuntimeError):
    """Raised when the reduced defect theorem or its scope guards fail."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EinsteinDefectAsymptoticsError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _wave_action(
    expression: sp.Expr, u: sp.Symbol, r: sp.Symbol, angular: sp.Expr
) -> sp.Expr:
    """Independently apply the scalar flat wave operator in retarded coordinates."""

    return sp.expand(
        -2 * sp.diff(expression, u, r)
        + sp.diff(expression, r, 2)
        + 2 * (sp.diff(expression, r) - sp.diff(expression, u)) / r
        - angular * expression / r**2
    )


def defect_map_coefficients(
    weight: sp.Expr, index: sp.Expr, angular: sp.Expr
) -> tuple[sp.Expr, sp.Expr]:
    """Coefficients of ``d_u f_j`` and ``f_(j-1)`` in ``g_j``."""

    current_a = indicial.wave_coefficients(weight + index, angular)[0]
    previous_b = indicial.wave_coefficients(weight + index - 1, angular)[1]
    return sp.factor(current_a), sp.factor(previous_b)


def defect_wave_coefficients(
    weight: sp.Expr, index: sp.Expr, angular: sp.Expr
) -> tuple[sp.Expr, sp.Expr]:
    """Coefficients of ``d_u g_j`` and ``g_(j-1)`` in ``Box chi``."""

    defect_weight = weight + 1
    current_a = indicial.wave_coefficients(defect_weight + index, angular)[0]
    previous_b = indicial.wave_coefficients(
        defect_weight + index - 1, angular
    )[1]
    return sp.factor(current_a), sp.factor(previous_b)


def _factorization_check() -> dict[str, Any]:
    p, j, angular = sp.symbols("p j L", real=True)
    s_current = p + j

    map_a, map_b = defect_map_coefficients(p, j, angular)
    wave_a, wave_b = defect_wave_coefficients(p, j, angular)
    previous_map_a, previous_map_b = defect_map_coefficients(
        p, j - 1, angular
    )

    composed = (
        sp.factor(wave_a * map_a),
        sp.factor(wave_a * map_b + wave_b * previous_map_a),
        sp.factor(wave_b * previous_map_b),
    )
    expected = (
        sp.factor(indicial.biwave_coefficients(s_current, angular)[0]),
        sp.factor(indicial.biwave_coefficients(s_current - 1, angular)[1]),
        sp.factor(indicial.biwave_coefficients(s_current - 2, angular)[2]),
    )
    _require(composed == expected, "Box chi recurrence does not equal Box^2 phi")

    return {
        "identity": "Box^2 phi=Box chi with chi=Box phi",
        "coefficient_order": ["d_u^2 f_j", "d_u f_(j-1)", "f_(j-2)"],
        "composed_coefficients": [str(value) for value in composed],
        "biwave_coefficients": [str(value) for value in expected],
        "defect_weight": "p+1",
        "status": "PASS",
    }


def _direct_series_check() -> dict[str, Any]:
    u, r = sp.symbols("u r", positive=True, real=True)
    angular = sp.symbols("L", real=True)
    term_count = 6
    checked_weights = [0, 1, 2]

    for weight in checked_weights:
        functions = [
            sp.Function(f"f_{weight}_{index}")(u) for index in range(term_count)
        ]
        phi = sum(
            r ** (-weight - index) * function
            for index, function in enumerate(functions)
        )
        chi = _wave_action(phi, u, r, angular)
        bach = _wave_action(chi, u, r, angular)

        defect_coefficients: list[sp.Expr] = []
        for index, function in enumerate(functions):
            map_a, map_b = defect_map_coefficients(weight, index, angular)
            expected = map_a * sp.diff(function, u)
            if index > 0:
                expected += map_b * functions[index - 1]
            actual = sp.expand(chi).coeff(r, -(weight + index + 1))
            _require(
                sp.simplify(actual - expected) == 0,
                f"defect map failed at p={weight}, j={index}",
            )
            defect_coefficients.append(expected)

        for index, coefficient in enumerate(defect_coefficients):
            wave_a, wave_b = defect_wave_coefficients(weight, index, angular)
            expected = wave_a * sp.diff(coefficient, u)
            if index > 0:
                expected += wave_b * defect_coefficients[index - 1]
            actual = sp.expand(bach).coeff(r, -(weight + index + 2))
            _require(
                sp.simplify(actual - expected) == 0,
                f"defect wave recurrence failed at p={weight}, j={index}",
            )

    return {
        "method": "direct Box extraction from finite phi series, followed by direct Box chi",
        "checked_integer_weights": checked_weights,
        "terms_per_weight": term_count,
        "defect_map": "PASS",
        "defect_wave_recurrence": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "pure-weyl-einstein-defect-asymptotics-v1",
        "wrong Einstein-defect schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"defect certificate is missing field {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema id mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    provenance = payload.get("provenance", {})
    _require(
        provenance.get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    _require(payload.get("dependency_tags") == ["REDUCED-MODE"], "wrong dependency tag")
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get(
        "required", []
    )
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    _require(all(isinstance(flags[key], bool) for key in required_flags), "nonboolean claim flag")
    _require(flags.get("einstein_defect_factorization_derived") is True, "factorization absent")
    _require(flags.get("kappa_zero_sufficient_for_einstein") is False, "kappa was overpromoted")
    _require(
        flags.get("all_characteristic_defect_data_classified") is False,
        "defect boundary data were overpromoted",
    )


def build_certificate() -> dict[str, Any]:
    upstream = _load(INDICIAL_INPUT)
    flat = _load(FLAT_TT_INPUT)
    _require(
        upstream.get("schema") == "pure-weyl-bondi-bach-indicial-v2",
        "indicial v2 premise is missing",
    )
    _require(
        upstream.get("claim_flags", {}).get("p1_non_einstein_obstruction_identified")
        is True,
        "upstream p=1 obstruction is missing",
    )
    _require(
        upstream.get("claim_flags", {}).get(
            "fixed_boundary_metric_isolates_full_einstein_sector"
        )
        is False,
        "upstream boundary selection was overpromoted",
    )
    _require(
        flat.get("operator_identity") == "B_1(h_TT)=-(1/4) Box^2 h_TT",
        "flat TT Bach identity is missing",
    )
    _require(
        flat.get("curvature_identities", {}).get("linearized_scalar") == "0",
        "flat TT scalar-curvature premise failed",
    )

    p, j, angular = sp.symbols("p j L", real=True)
    map_a, map_b = defect_map_coefficients(p, j, angular)
    defect_a, defect_b = defect_wave_coefficients(p, j, angular)

    # p=0: g_0=-2 f_0', g_1=-L f_0 because the f_1' coefficient vanishes.
    _require(
        defect_map_coefficients(0, 0, angular) == (-2, 2 - angular),
        "wrong p=0 leading defect map",
    )
    _require(
        defect_map_coefficients(0, 1, angular) == (0, -angular),
        "wrong p=0 next defect map",
    )

    # p=1: g_0=0, g_1=kappa, g_2=rho.  Box chi then gives
    # 4 kappa'=0 and 6 rho'+(6-L)kappa=0.
    _require(
        defect_map_coefficients(1, 0, angular) == (0, -angular),
        "wrong p=1 leading zero",
    )
    _require(
        defect_map_coefficients(1, 1, angular) == (2, -angular),
        "wrong p=1 kappa map",
    )
    _require(
        defect_map_coefficients(1, 2, angular) == (4, 2 - angular),
        "wrong p=1 rho map",
    )
    _require(
        defect_wave_coefficients(1, 1, angular) == (4, 2 - angular),
        "wrong kappa propagation row",
    )
    _require(
        defect_wave_coefficients(1, 2, angular) == (6, 6 - angular),
        "wrong rho propagation row",
    )

    certificate = {
        "schema": "pure-weyl-einstein-defect-asymptotics-v1",
        "schema_path": (
            "bridge/einstein_sector/schema/einstein_defect_asymptotics.schema.json"
        ),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "REDUCED_EINSTEIN_DEFECT_ASYMPTOTICS",
        "result_state": "PROVED_REDUCED_DEFECT_FACTORIZATION",
        "dependency_tags": ["REDUCED-MODE"],
        "provenance": {
            "input_base_commit": "efa5708d91b235c5c2cfe056c536f2194a2d23dc",
            "generator_path": "bridge/einstein_sector/einstein_defect_asymptotics.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            "bondi_bach_indicial": {
                "path": str(INDICIAL_INPUT.relative_to(ROOT)),
                "sha256": _sha256(INDICIAL_INPUT),
            },
            "flat_tt_bach": {
                "path": str(FLAT_TT_INPUT.relative_to(ROOT)),
                "sha256": _sha256(FLAT_TT_INPUT),
            },
        },
        "geometric_definition": {
            "defect_field": "chi_mn=Box h_mn^TT",
            "linearized_ricci_relation": "chi_mn=-2 Ric_1_mn",
            "linearized_scalar_curvature": "R_1=0",
            "bach_equation": "B_1=-(1/4) Box chi=0",
            "einstein_equation": "chi=0",
            "exact_inclusion": "ker(chi) is contained in ker(Box chi)",
        },
        "radial_defect_map": {
            "phi_series": "phi=sum_(j>=0) r^(-p-j) f_j Y_L",
            "chi_series": "chi=sum_(j>=0) r^(-p-j-1) g_j Y_L",
            "index_convention": "f_j=g_j=0 for j<0",
            "g_j_terms": [
                {"field": "d_u f_j", "coefficient": str(map_a)},
                {"field": "f_(j-1)", "coefficient": str(map_b)},
            ],
            "einstein_condition": "g_j=0 for every j",
        },
        "defect_wave_recurrence": {
            "equation_rule": "sum of the listed terms equals zero",
            "terms": [
                {"field": "d_u g_j", "coefficient": str(defect_a)},
                {"field": "g_(j-1)", "coefficient": str(defect_b)},
            ],
            "factorization_check": _factorization_check(),
            "direct_series_check": _direct_series_check(),
        },
        "p0_defect": {
            "leading_coefficients": [
                "g_0=-2 d_u f_0",
                "g_1=-L f_0",
            ],
            "chi_leading": "chi=-2 r^-1 d_u f_0-r^-2 L f_0+O(r^-3)",
            "boundary_interpretation": (
                "nonzero p=0 changes the unphysical boundary metric; removing it "
                "also removes this leading source-like defect family"
            ),
        },
        "p1_defect_tower": {
            "leading_zero": "g_0=0",
            "kappa": "g_1=kappa=2 d_u f_1-L f_0",
            "rho": "g_2=rho=4 d_u f_2+(2-L) f_1",
            "first_defect_rows": [
                "4 d_u kappa=0",
                "6 d_u rho+(6-L) kappa=0",
            ],
            "kappa_zero_consequence": (
                "kappa=0 implies only d_u rho=0; it does not imply rho=0"
            ),
            "static_single_term": (
                "chi=r^-3 kappa Y_L with d_u kappa=0 solves Box chi=0 "
                "without subleading terms when L=6"
            ),
            "classification": (
                "kappa and higher g_j are Einstein-defect coefficients inside "
                "the p=1 metric falloff; their tensor, gauge, charge, and phase-space "
                "status is open"
            ),
        },
        "boundary_selection_consequence": {
            "fixed_boundary_metric": "removes the leading p=0 metric branch",
            "remaining_condition": (
                "all admissible characteristic and corner data of chi must vanish"
            ),
            "not_sufficient": [
                "p=1 falloff",
                "fixed unphysical boundary metric alone",
                "kappa=0 alone",
            ],
            "candidate_cauchy_condition": [
                "chi restricted to Sigma is zero",
                "nabla_n chi restricted to Sigma is zero",
            ],
            "causal_null_infinity_theorem": "OPEN",
        },
        "full_tensor_completion_gate": {
            "status": "OPEN_FAIL_CLOSED",
            "required_replacement": (
                "chi_mn must be expanded with the full Bondi metric, tensor/spin-2 "
                "harmonics, residual Diff x Weyl action, and all Bach constraints"
            ),
        },
        "claim_flags": {
            "einstein_defect_factorization_derived": True,
            "radial_defect_map_derived": True,
            "p0_leading_defect_identified": True,
            "p1_kappa_and_rho_identified": True,
            "kappa_zero_sufficient_for_einstein": False,
            "fixed_boundary_metric_isolates_einstein": False,
            "kappa_proved_physical_particle": False,
            "full_tensor_defect_expansion_constructed": False,
            "all_characteristic_defect_data_classified": False,
            "causal_zero_defect_theorem_proved": False,
            "einstein_scattering_equivalence_proved": False,
        },
        "scope_guards": [
            "exact for formal inverse-radius series of each flat Cartesian TT scalar amplitude",
            "not a full tensor Bondi-gauge calculation",
            "kappa is an Einstein-defect coefficient, not a certified particle or charge",
            "formal radial continuation is not null-infinity causal well-posedness",
            "the displayed L=6 single term is an exterior formal mode and may be singular in the interior",
            "no nonlinear Einstein-defect propagation theorem",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.einstein_defect_asymptotics "
            "--verify bridge/certificates/einstein_defect_asymptotics.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

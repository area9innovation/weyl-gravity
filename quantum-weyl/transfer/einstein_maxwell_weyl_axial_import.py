"""Pinned exact import of the generic axial Weyl--Maxwell extra module."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
BRIDGE_COMMIT = "e2b7e20bdf545dafeb1059d627c33c07bee91040"

OPERATOR_CERTIFICATE = "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
GREEN_CERTIFICATE = "bridge/certificates/einstein_maxwell_weyl_axial_green_current.json"
PAIRING_CERTIFICATE = "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json"
LEE_WALD_CERTIFICATE = "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json"
LEE_WALD_FIXTURE = "bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json"
OPERATOR_SCHEMA = "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_operator.schema.json"
GREEN_SCHEMA = "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_green_current.schema.json"
PAIRING_SCHEMA = "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_extra_green_pairing.schema.json"
LEE_WALD_SCHEMA = "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_lee_wald_completion.schema.json"
LEE_WALD_FIXTURE_SCHEMA = "bridge/einstein_sector/schema/weyl_maxwell_axial_general_lee_wald_fixture.schema.json"
REGISTRATION = "d_quotient_programme/contributions/einstein-maxwell-weyl-axial-extra-green-pairing.json"

PINNED_ARTIFACTS = {
    "operator_certificate": OPERATOR_CERTIFICATE,
    "green_current_certificate": GREEN_CERTIFICATE,
    "extra_pairing_certificate": PAIRING_CERTIFICATE,
    "Lee_Wald_completion_certificate": LEE_WALD_CERTIFICATE,
    "Lee_Wald_direct_fixture": LEE_WALD_FIXTURE,
    "operator_schema": OPERATOR_SCHEMA,
    "green_current_schema": GREEN_SCHEMA,
    "extra_pairing_schema": PAIRING_SCHEMA,
    "Lee_Wald_completion_schema": LEE_WALD_SCHEMA,
    "Lee_Wald_direct_fixture_schema": LEE_WALD_FIXTURE_SCHEMA,
    "operator_producer": "bridge/einstein_sector/einstein_maxwell_weyl_axial_operator.py",
    "green_current_producer": "bridge/einstein_sector/einstein_maxwell_weyl_axial_green_current.py",
    "extra_pairing_producer": "bridge/einstein_sector/einstein_maxwell_weyl_axial_extra_green_pairing.py",
    "Lee_Wald_completion_producer": "bridge/einstein_sector/einstein_maxwell_weyl_axial_lee_wald_completion.py",
    "Lee_Wald_direct_fixture_producer": "bridge/einstein_sector/weyl_maxwell_axial_general_lee_wald_fixture.py",
    "operator_verifier": "bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_operator.py",
    "operator_tests": "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_axial_operator.py",
    "green_current_tests": "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_axial_green_current.py",
    "extra_pairing_tests": "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_axial_extra_green_pairing.py",
    "Lee_Wald_completion_tests": "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_axial_lee_wald_completion.py",
    "Lee_Wald_direct_fixture_tests": "bridge/einstein_sector/tests/test_weyl_maxwell_axial_general_lee_wald_fixture.py",
    "classical_report": "notes/einstein-maxwell-weyl-axial-operator-report.md",
    "programme_registration": REGISTRATION,
}


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{BRIDGE_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned axial Weyl--Maxwell artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned axial Weyl--Maxwell JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": BRIDGE_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


LAM, K, OMEGA, OMEGA1, OMEGA2 = sp.symbols(
    "lambda k omega omega1 omega2", real=True
)
T, X = sp.symbols("T X", real=True)
LOCALS = {
    "lambda": LAM,
    "lam": LAM,
    "k": K,
    "omega": OMEGA,
    "omega1": OMEGA1,
    "omega2": OMEGA2,
    "I": sp.I,
    "pi": sp.pi,
}


def _expr(value: str) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=LOCALS)


def _matrix(values: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[_expr(value) for value in row] for row in values])


def _zero(value: sp.Expr | sp.MatrixBase) -> bool:
    if isinstance(value, sp.MatrixBase):
        return value.applyfunc(lambda item: sp.factor(sp.expand(item))) == sp.zeros(
            value.rows, value.cols
        )
    return sp.factor(sp.expand(value)) == 0


def _shell_reduce(value: sp.Expr) -> sp.Expr:
    shell = sp.Poly(OMEGA**2 - K**2 - LAM + sp.Rational(2, 3), OMEGA)
    return sp.factor(sp.rem(sp.Poly(sp.expand(value), OMEGA), shell).as_expr())


JetKey = tuple[int, int, int, int, int, int]


def _add(store: dict[JetKey, sp.Expr], key: JetKey, value: sp.Expr) -> None:
    if value == 0:
        return
    updated = sp.factor(store.get(key, sp.S.Zero) + value)
    if updated == 0:
        store.pop(key, None)
    else:
        store[key] = updated


def _differential_operator(fourier: sp.Matrix) -> sp.Matrix:
    return fourier.subs({OMEGA: sp.I * T, K: -sp.I * X}, simultaneous=True).applyfunc(
        lambda value: sp.factor(sp.expand(value))
    )


def _rhs_jet_coefficients(operator: sp.Matrix) -> dict[JetKey, sp.Expr]:
    rhs: dict[JetKey, sp.Expr] = {}
    for row in range(operator.rows):
        for column in range(operator.cols):
            polynomial = sp.Poly(sp.expand(operator[row, column]), T, X)
            for (time_order, space_order), coefficient in polynomial.terms():
                _add(rhs, (row, 0, 0, column, time_order, space_order), coefficient)
                _add(rhs, (column, time_order, space_order, row, 0, 0), -coefficient)
    return rhs


def _current_terms(records: object) -> dict[JetKey, sp.Expr]:
    if not isinstance(records, list):
        raise ValueError("Green-current terms are not a list")
    result: dict[JetKey, sp.Expr] = {}
    required = {
        "u_component",
        "u_t_order",
        "u_x_order",
        "v_component",
        "v_t_order",
        "v_x_order",
        "coefficient",
    }
    for record in records:
        if not isinstance(record, dict) or set(record) != required:
            raise ValueError("Green-current term shape drifted")
        key = (
            int(record["u_component"]),
            int(record["u_t_order"]),
            int(record["u_x_order"]),
            int(record["v_component"]),
            int(record["v_t_order"]),
            int(record["v_x_order"]),
        )
        _add(result, key, _expr(str(record["coefficient"])))
    return result


def _verify_green_identity(fourier: sp.Matrix, current: dict[str, Any]) -> None:
    operator = _differential_operator(fourier)
    if not _zero(operator - operator.subs({T: -T, X: -X}, simultaneous=True).T):
        raise ValueError("differential operator lost formal self-adjointness")
    time_current = _current_terms(current.get("time_current_terms"))
    space_current = _current_terms(current.get("space_current_terms"))
    if (
        current.get("time_current_term_count") != len(time_current)
        or current.get("space_current_term_count") != len(space_current)
        or current.get("jet_identity_remainder") != []
        or current.get("off_shell_identity_verified") is not True
    ):
        raise ValueError("Green-current count or declared identity drifted")
    divergence: dict[JetKey, sp.Expr] = {}
    for (left, ut, ux, right, vt, vx), coefficient in time_current.items():
        _add(divergence, (left, ut + 1, ux, right, vt, vx), coefficient)
        _add(divergence, (left, ut, ux, right, vt + 1, vx), coefficient)
    for (left, ut, ux, right, vt, vx), coefficient in space_current.items():
        _add(divergence, (left, ut, ux + 1, right, vt, vx), coefficient)
        _add(divergence, (left, ut, ux, right, vt, vx + 1), coefficient)
    rhs = _rhs_jet_coefficients(operator)
    defect = {
        key: sp.factor(divergence.get(key, 0) - rhs.get(key, 0))
        for key in set(divergence) | set(rhs)
        if sp.factor(divergence.get(key, 0) - rhs.get(key, 0)) != 0
    }
    if defect:
        raise ValueError("off-shell Green identity replay failed")


def _verify_schema(schema: dict[str, Any], identifier: str) -> None:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id") != identifier
        or schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError(f"strict bridge schema drifted: {identifier}")


def validate_bridge_payloads(
    operator: object,
    green: object,
    pairing: object,
    Lee_Wald: object,
    Lee_Wald_fixture: object,
    schemas: object,
    registration: object,
) -> dict[str, bool]:
    """Independently replay the pinned operator, current and pairing claims."""

    if not all(
        isinstance(value, dict)
        for value in (
            operator,
            green,
            pairing,
            Lee_Wald,
            Lee_Wald_fixture,
            schemas,
            registration,
        )
    ):
        raise ValueError("axial Weyl--Maxwell import input is not an object")
    operator = dict(operator)
    green = dict(green)
    pairing = dict(pairing)
    Lee_Wald = dict(Lee_Wald)
    Lee_Wald_fixture = dict(Lee_Wald_fixture)
    schemas = dict(schemas)
    registration = dict(registration)
    for name, identifier in (
        ("operator", "einstein-maxwell-weyl-axial-operator-v1"),
        ("green", "einstein-maxwell-weyl-axial-green-current-v1"),
        ("pairing", "einstein-maxwell-weyl-axial-extra-green-pairing-v1"),
        ("Lee_Wald", "einstein-maxwell-weyl-axial-lee-wald-completion-v1"),
        ("Lee_Wald_fixture", "weyl-maxwell-axial-general-lee-wald-fixture-v1"),
    ):
        schema = schemas.get(name)
        if not isinstance(schema, dict):
            raise ValueError(f"missing bridge schema: {name}")
        _verify_schema(schema, identifier)

    if (
        operator.get("result_id") != "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR"
        or operator.get("result_state")
        != "GENERIC_AXIAL_OPERATOR_NOETHER_SMITH_AND_EXTRA_SOLUTION_MODULE_CERTIFIED_GREEN_AND_PAIRING_OPEN"
        or green.get("result_id") != "EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT"
        or green.get("result_state")
        != "GENERIC_AXIAL_REDUCED_AND_UNGAUGED_OFF_SHELL_LOCAL_GREEN_IDENTITIES_CERTIFIED"
        or pairing.get("result_id") != "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING"
        or pairing.get("result_state")
        != "GENERIC_AXIAL_EXTRA_MODULE_NONRADICAL_POSITIVE_IN_REDUCED_HESSIAN_GREEN_CONVENTION"
        or any(
            payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
            or payload.get("lifecycle_state") != "CLASSIFIED"
            for payload in (operator, green, pairing)
        )
    ):
        raise ValueError("axial Weyl--Maxwell result identity drifted")

    algebra = operator.get("operator_algebra", {})
    hessian = _matrix(algebra.get("gauge_fixed_Hessian_operator", []))
    if hessian.shape != (4, 4):
        raise ValueError("axial reduced Hessian shape drifted")
    adjoint = hessian.subs({OMEGA: -OMEGA, K: -K}, simultaneous=True).T
    if not _zero(hessian - adjoint) or algebra.get("formal_self_adjoint") is not True:
        raise ValueError("axial formal-adjoint identity failed")
    if not _zero(hessian.det() - _expr(algebra.get("determinant", "nan"))):
        raise ValueError("axial Hessian determinant replay failed")
    p = _expr(algebra.get("monic_extra_factor_p", "nan"))
    q = _expr(algebra.get("Einstein_master_factor_q", "nan"))
    expected_p = OMEGA**2 - K**2 - LAM + sp.Rational(2, 3)
    expected_q = (OMEGA**2 - K**2 - LAM) ** 2 - 2 * LAM
    if not _zero(p - expected_p) or not _zero(q - expected_q):
        raise ValueError("axial Smith factors drifted")
    invariants = [_expr(value) for value in algebra.get("Smith_invariant_factors_over_F_omega", [])]
    if len(invariants) != 4 or not _zero(invariants[2] - p) or not _zero(invariants[3] - p * q):
        raise ValueError("axial invariant-factor classification drifted")

    modules = operator.get("source_and_extra_modules", {})
    representatives = _matrix(modules.get("extra_representatives_order_Ht_Hx_Qt_Qx", []))
    if representatives.shape != (2, 4):
        raise ValueError("axial extra representatives drifted")
    for vector in representatives.tolist():
        image = hessian * sp.Matrix(vector)
        if any(_shell_reduce(value) != 0 for value in image):
            raise ValueError("axial extra representative left the p-shell kernel")
    operator_classification = operator.get("classification", {})
    if (
        operator_classification.get("Einstein_solution_module_is_a_proper_submodule") is not True
        or operator_classification.get("two_extra_algebraic_polarizations") is not True
        or operator_classification.get("extra_particle_certified") is not False
        or operator_classification.get("quantum_claim") is not False
    ):
        raise ValueError("axial operator claim boundary drifted")

    reduced_fourier = hessian
    ungauged_fourier = _matrix(operator.get("ungauged_Noether_lift", {}).get("ungauged_Hessian_operator", []))
    if ungauged_fourier.shape != (6, 6):
        raise ValueError("axial ungauged Hessian shape drifted")
    _verify_green_identity(reduced_fourier, green.get("reduced_current", {}))
    _verify_green_identity(ungauged_fourier, green.get("ungauged_current", {}))
    green_classification = green.get("classification", {})
    if (
        green_classification.get("arbitrary_off_shell_jets") is not True
        or green_classification.get("reduced_off_shell_local_Green_identity") is not True
        or green_classification.get("ungauged_off_shell_local_Green_identity") is not True
        or green_classification.get("direct_four_dimensional_action_Hessian") is not False
        or green_classification.get("Lorentzian_causal_claim") is not False
    ):
        raise ValueError("axial Green-current claim boundary drifted")

    pairing_data = pairing.get("pairing", {})
    if pairing_data.get("representatives") != modules.get("extra_representatives_order_Ht_Hx_Qt_Qx"):
        raise ValueError("operator/pairing representative binding drifted")
    coordinate = _matrix(pairing_data.get("coordinate_Jt_Gram", []))
    normalized = _matrix(pairing_data.get("normalized_Gram", []))
    if coordinate.shape != (2, 2) or normalized.shape != (2, 2):
        raise ValueError("axial extra Gram matrix shape drifted")
    if not _zero(normalized - normalized.T):
        raise ValueError("axial normalized Gram matrix is not symmetric")
    if any(_shell_reduce(value) != 0 for value in coordinate - (-sp.I * OMEGA) * normalized):
        raise ValueError("axial Green-current normalization replay failed")
    determinant = _shell_reduce(normalized.det())
    expected_determinant = LAM**4 * (LAM - 2) * (9 * LAM - 2) / 3
    if not _zero(determinant - expected_determinant) or not _zero(
        determinant - _expr(pairing_data.get("determinant", "nan"))
    ):
        raise ValueError("axial extra pairing determinant replay failed")
    expected_minor = LAM * ((3 * LAM - 2) ** 2 * K**2 + 9 * LAM**2 * (LAM - 2)) / 6
    if not _zero(normalized[0, 0] - expected_minor):
        raise ValueError("axial extra first principal minor replay failed")
    sign = pairing_data.get("physical_sign_check", {})
    pairing_classification = pairing.get("classification", {})
    if (
        sign.get("signature") != [2, 0]
        or sign.get("first_principal_minor_positive") is not True
        or sign.get("determinant_positive") is not True
        or pairing_classification.get("extra_module_nonradical_for_reduced_Green_current") is not True
        or pairing_classification.get("reduced_Green_signature_positive_two") is not True
        or pairing_classification.get("direct_four_dimensional_Lee_Wald_match") is not False
        or pairing_classification.get("physical_norm_or_ghost_claim") is not False
        or pairing_classification.get("particle_claim") is not False
        or pairing_classification.get("Lorentzian_causal_claim") is not False
    ):
        raise ValueError("axial extra pairing claim boundary drifted")

    if (
        Lee_Wald.get("result_id")
        != "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION"
        or Lee_Wald.get("result_state")
        != "GENERIC_AXIAL_DIRECT_4D_LEE_WALD_MATCH_EXTRA_NONRADICAL_AND_FULL_BLOCK_SIGNATURE_CERTIFIED"
        or Lee_Wald_fixture.get("result_id")
        != "WEYL_MAXWELL_AXIAL_GENERAL_LEE_WALD_FIXTURE"
        or Lee_Wald_fixture.get("result_state")
        != "DIRECT_4D_LEE_WALD_EQUALS_HARMONIC_NORM_TIMES_REDUCED_GREEN_AT_ELL2_ELL3_ELL4"
        or any(
            payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
            or payload.get("lifecycle_state") != "CLASSIFIED"
            for payload in (Lee_Wald, Lee_Wald_fixture)
        )
    ):
        raise ValueError("axial Lee--Wald result identity drifted")
    direct = Lee_Wald.get("direct_current_match", {})
    generic_matrix = _matrix(direct.get("generic_reduced_Green_matrix", []))
    if (
        generic_matrix.shape != (4, 4)
        or direct.get("generic_direct_match") is not True
        or direct.get("spectral_degree_bound") != 2
        or direct.get("interpolation_nodes") != [6, 12, 20]
        or direct.get("improvement_remainder_after_compact_S2_integration") != "0"
    ):
        raise ValueError("axial direct Lee--Wald interpolation contract drifted")
    samples = Lee_Wald_fixture.get("samples", {})
    for ell, eigenvalue in (("2", 6), ("3", 12), ("4", 20)):
        sample = samples.get(ell, {})
        reduced_sample = _matrix(sample.get("reduced_Green_matrix", []))
        direct_sample = _matrix(sample.get("direct_integrated_matrix", []))
        harmonic_norm = _expr(sample.get("harmonic_norm", "nan"))
        if (
            sample.get("lambda") != eigenvalue
            or sample.get("independent_frequencies_retained") is not True
            or reduced_sample.shape != (4, 4)
            or direct_sample.shape != (4, 4)
            or not _zero(reduced_sample - generic_matrix.subs(LAM, eigenvalue))
            or not _zero(direct_sample - harmonic_norm * reduced_sample)
        ):
            raise ValueError(f"axial direct Lee--Wald sample replay failed at ell={ell}")
    solution_pairing = Lee_Wald.get("full_solution_pairing", {})
    classification = Lee_Wald.get("classification", {})
    if (
        solution_pairing.get("mixed_Einstein_to_extra_shell_remainders") != ["0", "0"]
        or solution_pairing.get("mixed_extra_to_Einstein_shell_remainders") != ["0", "0"]
        or solution_pairing.get("mixed_blocks_zero_without_frequency_inversion") is not True
        or solution_pairing.get("Einstein_branch_signature_for_lambda_ge_6") != [1, 1]
        or solution_pairing.get("extra_branch_signature_for_lambda_ge_6") != [2, 0]
        or solution_pairing.get("complete_generic_axial_target_signature") != [3, 1]
        or classification.get("direct_four_dimensional_Lee_Wald_match") is not True
        or classification.get("generic_extra_module_direct_Lee_Wald_nonradical") is not True
        or classification.get("Einstein_extra_symplectic_orthogonality") is not True
        or classification.get("direct_second_variation_action_density_computed") is not False
        or classification.get("final_residual_quotient_computed") is not False
        or classification.get("Lorentzian_causal_claim") is not False
        or classification.get("positive_frequency_Hilbert_space_or_particle_claim") is not False
        or classification.get("quantum_ghost_or_unitarity_claim") is not False
    ):
        raise ValueError("axial direct Lee--Wald claim boundary drifted")
    completion_inputs = Lee_Wald.get("provenance", {}).get("inputs", {})
    for name, relative in (
        ("operator", OPERATOR_CERTIFICATE),
        ("green_current", GREEN_CERTIFICATE),
        ("extra_pairing", PAIRING_CERTIFICATE),
        ("direct_fixture", LEE_WALD_FIXTURE),
    ):
        record = completion_inputs.get(name, {})
        if (
            record.get("path") != relative
            or record.get("sha256") != hashlib.sha256(_git_blob(relative)).hexdigest()
        ):
            raise ValueError(f"axial Lee--Wald provenance drifted: {name}")

    evidence = registration.get("evidence", {})
    if (
        registration.get("schema") != "pure-weyl-d-quotient-team-contribution-v1"
        or registration.get("claim_status") != "CERTIFIED"
        or registration.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        or evidence.get("commit") != "9f078dac3ceba7dcb9e07a91cc350683c48e5ba2"
        or evidence.get("path") != PAIRING_CERTIFICATE
        or evidence.get("sha256") != hashlib.sha256(_git_blob(PAIRING_CERTIFICATE)).hexdigest()
    ):
        raise ValueError("axial extra pairing programme registration drifted")

    return {
        "strict_bridge_schemas_pinned": True,
        "programme_registration_pinned": True,
        "formal_adjoint_replayed": True,
        "Hessian_determinant_replayed": True,
        "Smith_p_and_q_factors_replayed": True,
        "two_extra_p_shell_kernel_representatives_replayed": True,
        "reduced_off_shell_Green_identity_replayed": True,
        "ungauged_off_shell_Green_identity_replayed": True,
        "operator_pairing_representatives_bound": True,
        "pairing_normalization_replayed": True,
        "pairing_determinant_replayed": True,
        "physical_lambda_sign_decomposition_replayed": True,
        "direct_4D_Lee_Wald_samples_replayed": True,
        "generic_Lee_Wald_interpolation_replayed": True,
        "Einstein_extra_orthogonality_replayed": True,
        "complete_axial_signature_three_one_replayed": True,
        "particle_ghost_causal_and_quantum_claims_fail_closed": True,
    }


def build_import() -> dict[str, Any]:
    operator = _git_json(OPERATOR_CERTIFICATE)
    green = _git_json(GREEN_CERTIFICATE)
    pairing = _git_json(PAIRING_CERTIFICATE)
    Lee_Wald = _git_json(LEE_WALD_CERTIFICATE)
    Lee_Wald_fixture = _git_json(LEE_WALD_FIXTURE)
    schemas = {
        "operator": _git_json(OPERATOR_SCHEMA),
        "green": _git_json(GREEN_SCHEMA),
        "pairing": _git_json(PAIRING_SCHEMA),
        "Lee_Wald": _git_json(LEE_WALD_SCHEMA),
        "Lee_Wald_fixture": _git_json(LEE_WALD_FIXTURE_SCHEMA),
    }
    checks = validate_bridge_payloads(
        operator,
        green,
        pairing,
        Lee_Wald,
        Lee_Wald_fixture,
        schemas,
        _git_json(REGISTRATION),
    )
    pairing_data = pairing["pairing"]
    return {
        "schema": "quantum-weyl-einstein-maxwell-weyl-axial-import-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_MODULE_IMPORT",
        "result_state": "GENERIC_AXIAL_EXTRA_MODULE_AND_DIRECT_LEE_WALD_PAIRING_IMPORTED_CAUSAL_RESIDUAL_AND_INTERACTING_GATES_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "bridge_source": {
            "commit": BRIDGE_COMMIT,
            "artifacts": {
                name: _artifact(relative) for name, relative in PINNED_ARTIFACTS.items()
            },
        },
        "exact_import_checks": checks,
        "linearized_coupled_branch": {
            "setting": operator["domain"],
            "field_order": operator["operator_algebra"]["coefficient_order"],
            "Einstein_Maxwell_solution_module_is_proper_submodule": True,
            "canonical_extra_module": "(F[omega]/(p))^2",
            "extra_algebraic_polarizations": 2,
            "extra_shell": pairing_data["shell"],
            "off_shell_reduced_and_ungauged_Green_identities": True,
        },
        "reduced_pairing_verdict": {
            "normalization": pairing_data["normalization"],
            "determinant": pairing_data["determinant"],
            "physical_domain": pairing_data["physical_sign_check"]["domain"],
            "signature": pairing_data["physical_sign_check"]["signature"],
            "nonradical": pairing_data["nondegenerate_for_all_physical_ell_ge_2"],
            "direct_four_dimensional_Lee_Wald_match": True,
        },
        "direct_Lee_Wald_verdict": {
            "Einstein_extra_symplectic_orthogonality": True,
            "extra_signature": [2, 0],
            "Einstein_signature": [1, 1],
            "complete_generic_axial_target_signature": [3, 1],
            "negative_direction_location": "one Einstein-image master branch, not the extra block",
            "final_residual_quotient_computed": False,
        },
        "physical_interpretation": {
            "linearized_coupled_metric_Maxwell_branch_available": True,
            "direct_compact_Lee_Wald_pairing_available": True,
            "interacting_light_model_available": False,
            "mixed_gravity_photon_q2_or_q3_transferred": False,
            "extra_particle_certified": False,
            "extra_physical_norm_or_ghost_classified": False,
            "Lorentzian_causal_boundary_selected": False,
            "quantum_claim": False,
        },
        "claim_flags": {
            "GENERIC_AXIAL_WEYL_MAXWELL_OPERATOR_IMPORTED": True,
            "GENERIC_AXIAL_EXTRA_MODULE_IMPORTED": True,
            "REDUCED_GREEN_EXTRA_MODULE_NONRADICAL": True,
            "DIRECT_FOUR_DIMENSIONAL_LEE_WALD_MATCH": True,
            "MIXED_GRAVITY_MAXWELL_NONLINEAR_VERTEX": False,
            "PHYSICAL_PARTICLE_OR_GHOST_CLASSIFICATION": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": "This pinned LOCAL-ALGEBRAIC/REDUCED-MODE import independently replays the generic axial Weyl--Maxwell operator, two extra p-shell representatives, reduced and ungauged off-shell Green identities, the nonradical (2,0) extra pairing, and the direct compact four-dimensional Lee--Wald match. The complete generic axial signature is (3,1); the negative direction lies in an Einstein-image master branch rather than the new extra block. This establishes a linearized coupled metric--Maxwell branch, not interacting photons. Mixed q2/q3 transfer, final residual descent, causal boundary selection, a positive-frequency Hilbert space, particle or ghost interpretation, QME restoration, and quantum unitarity remain open.",
        "next_gate": "EINSTEIN_MAXWELL_WEYL_AXIAL_MIXED_VERTEX_RESIDUAL_AND_CAUSAL_IMPORT",
    }

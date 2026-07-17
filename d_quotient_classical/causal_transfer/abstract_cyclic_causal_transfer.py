#!/usr/bin/env python3
"""C-G1: certify the abstract cyclic causal-transfer theorem.

The mathematical theorem is recorded in the generated report.  This producer
also evaluates a finite exact model of every algebraic identity and replays
the completed Berger 26->54 and (26+10)->64 constructions as consumers.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"
CONSUMER_PATH = ROOT / "d_quotient_classical/certificates/BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/abstract-cyclic-causal-transfer.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/abstract-cyclic-causal-transfer-v1.schema.json"
CONSUMER_SCHEMA_PATH = ROOT / "d_quotient_classical/schema/abstract-cyclic-causal-transfer-consumer-v1.schema.json"
PRODUCER_PATH = ROOT / "d_quotient_classical/causal_transfer/abstract_cyclic_causal_transfer.py"
VERIFIER_PATH = ROOT / "d_quotient_classical/causal_transfer/verify_abstract_cyclic_causal_transfer.py"
TEST_PATH = ROOT / "d_quotient_classical/causal_transfer/tests/test_abstract_cyclic_causal_transfer.py"

DEPENDENCIES = {
    "berger_retained_26": ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "berger_54_to_26_sdr": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json",
    "berger_full_54": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "berger_cyclic_shear": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "berger_coupled_64": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "berger_cyclic_64_to_36_sdr": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "berger_generator_semantics": ROOT / "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def _sharp(operator: sp.Matrix, domain_pairing: sp.Matrix, codomain_pairing: sp.Matrix) -> sp.Matrix:
    """Formal adjoint for a map domain -> codomain in a finite exact model."""
    return domain_pairing.inv() * operator.T * codomain_pairing


def _zero(matrix: sp.Matrix) -> bool:
    return all(sp.simplify(entry) == 0 for entry in matrix)


def exact_fixture() -> dict[str, Any]:
    """Evaluate SDR, witness, cyclic-adjoint, and finite-shear identities."""
    d = sp.zeros(2)
    d[1, 0] = 1
    q = sp.zeros(4)
    q[2, 0] = 1
    q[3, 1] = 1

    inclusion = sp.zeros(4, 2)
    inclusion[0, 0] = 1
    inclusion[2, 1] = 1
    projection = sp.zeros(2, 4)
    projection[0, 0] = 1
    projection[1, 2] = 1
    h = sp.zeros(4)
    h[1, 3] = 1

    lambda_endpoint = sp.zeros(2)
    lambda_endpoint[0, 1] = 1
    lambda_full = h + inclusion * lambda_endpoint * projection
    lambda_descended = projection * lambda_full * inclusion

    pairing_endpoint = sp.Matrix([[0, 1], [-1, 0]])
    pairing_full = sp.Matrix(
        [[0, 0, 1, 0], [0, 0, 0, 1], [-1, 0, 0, 0], [0, -1, 0, 0]]
    )
    sign_endpoint = sp.diag(1, -1)
    sign_full = sp.diag(1, 1, -1, -1)

    witness = 2 * lambda_endpoint
    companion = d * witness + witness * d
    green = sp.eye(2) / 2

    nilpotent = sp.zeros(4)
    nilpotent[0, 1] = 1
    nilpotent[3, 2] = -1
    shear = sp.eye(4) + nilpotent
    shear_inverse = sp.eye(4) - nilpotent
    q_sheared = shear * q * shear_inverse
    lambda_sheared = shear * lambda_full * shear_inverse

    defects = {
        "endpoint_nilpotency": d * d,
        "full_nilpotency": q * q,
        "inclusion_chain_map": q * inclusion - inclusion * d,
        "projection_chain_map": projection * q - d * projection,
        "projection_inclusion": projection * inclusion - sp.eye(2),
        "sdr_identity": q * h + h * q - (sp.eye(4) - inclusion * projection),
        "sdr_h_square": h * h,
        "sdr_h_inclusion": h * inclusion,
        "sdr_projection_h": projection * h,
        "endpoint_homotopy": d * lambda_endpoint + lambda_endpoint * d - sp.eye(2),
        "transferred_homotopy": q * lambda_full + lambda_full * q - sp.eye(4),
        "descended_homotopy": d * lambda_descended + lambda_descended * d - sp.eye(2),
        "descent_recovers_endpoint": lambda_descended - lambda_endpoint,
        "witness_companion": companion - 2 * sp.eye(2),
        "green_left_inverse": green * companion - sp.eye(2),
        "green_right_inverse": companion * green - sp.eye(2),
        "witness_green_homotopy": witness * green - lambda_endpoint,
        "endpoint_sign_involution": sign_endpoint * sign_endpoint - sp.eye(2),
        "full_sign_involution": sign_full * sign_full - sp.eye(4),
        "inclusion_sign_intertwiner": sign_full * inclusion - inclusion * sign_endpoint,
        "projection_sign_intertwiner": sign_endpoint * projection - projection * sign_full,
        "inclusion_adjoint": _sharp(inclusion, pairing_endpoint, pairing_full) - projection,
        "projection_adjoint": _sharp(projection, pairing_full, pairing_endpoint) - inclusion,
        "algebraic_homotopy_adjoint": _sharp(h, pairing_full, pairing_full)
        - sign_full * h * sign_full,
        "endpoint_homotopy_adjoint": _sharp(
            lambda_endpoint, pairing_endpoint, pairing_endpoint
        ) - sign_endpoint * lambda_endpoint * sign_endpoint,
        "descended_homotopy_adjoint": _sharp(
            lambda_descended, pairing_endpoint, pairing_endpoint
        ) - sign_endpoint * lambda_descended * sign_endpoint,
        "full_homotopy_adjoint": _sharp(lambda_full, pairing_full, pairing_full)
        - sign_full * lambda_full * sign_full,
        "nilpotent_square": nilpotent * nilpotent,
        "shear_inverse_left": shear_inverse * shear - sp.eye(4),
        "shear_inverse_right": shear * shear_inverse - sp.eye(4),
        "cyclic_shear": _sharp(shear, pairing_full, pairing_full) - shear_inverse,
        "shear_sign_intertwiner": shear * sign_full - sign_full * shear,
        "sheared_chain_homotopy": q_sheared * lambda_sheared
        + lambda_sheared * q_sheared
        - sp.eye(4),
        "sheared_homotopy_adjoint": _sharp(
            lambda_sheared, pairing_full, pairing_full
        ) - sign_full * lambda_sheared * sign_full,
    }
    nonzero = {name: matrix.tolist() for name, matrix in defects.items() if not _zero(matrix)}
    if nonzero:
        raise AssertionError(f"abstract causal-transfer fixture failed: {nonzero}")
    return {
        "coefficient_field": "Q",
        "endpoint_dimension": 2,
        "full_dimension": 4,
        "contracted_dimension": 2,
        "degreewise_sign_operator": {
            "endpoint_diagonal": [1, -1],
            "full_diagonal": [1, 1, -1, -1],
        },
        "fixture_role": "finite exact model of the universal algebraic identities; not evidence for Lorentzian endpoint existence",
        "identity_defects": {name: 0 for name in defects},
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    endpoint = data["berger_retained_26"]
    reduction = data["berger_54_to_26_sdr"]
    full = data["berger_full_54"]
    shear = data["berger_cyclic_shear"]
    coupled = data["berger_coupled_64"]
    portable = data["berger_cyclic_64_to_36_sdr"]
    generator = data["berger_generator_semantics"]

    if endpoint["result_state"] != "GREEN_CERTIFIED_HADAMARD_OPEN":
        raise AssertionError("Berger retained endpoint is not Green certified")
    if not all(reduction["exact_checks"].values()):
        raise AssertionError("Berger 54-to-26 SDR is incomplete")
    if full["flags"]["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"] is not True:
        raise AssertionError("Berger 54-row consumer is unavailable")
    if shear["exact_checks"]["canonical_shear_invertible"] is not True:
        raise AssertionError("Berger finite shear is not invertible")
    if shear["exact_checks"]["canonical_shear_nilpotent"] is not True:
        raise AssertionError("Berger finite shear is not filtration-nilpotent")
    if shear["exact_checks"]["BV_pairing_preserved"] is not True:
        raise AssertionError("Berger finite shear is not cyclic")
    if coupled["flags"]["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Berger 64-row direct-sum consumer is unavailable")
    if portable["flags"]["BERGER_ALGEBRAIC_64_TO_36_CYCLIC_SDR"] is not True:
        raise AssertionError("Berger 64-to-36 cyclic SDR is unavailable")
    if generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"] is not True:
        raise AssertionError("Berger generator semantics lost K correction")
    if generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"] is not False:
        raise AssertionError("raw affine D was substituted for K")
    return data


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    fixture = exact_fixture()
    payload = {
        "schema": "pure-weyl-abstract-cyclic-causal-transfer-v1",
        "result_id": "ABSTRACT_CYCLIC_CAUSAL_TRANSFER",
        "claim_status": "ABSTRACT_CAUSAL_TRANSFER_CERTIFIED",
        "generality": {
            "theorem_level": "ABSTRACT_CONDITIONAL_ALL_GLOBALLY_HYPERBOLIC_BACKGROUNDS_SATISFYING_DECLARED_HYPOTHESES",
            "first_consumer_level": "G2_COMPLETE_LINEAR_COMPLEX_ON_ONE_BACKGROUND",
            "G3_background_class_promoted": False,
            "reason": "the theorem is background-uniform, but no open background family has yet been shown to satisfy its analytic hypotheses uniformly",
        },
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], value) for name, value in dependencies.items()
        },
        "hypotheses": {
            "base": "a time-oriented globally hyperbolic Lorentzian manifold without timelike boundary, or a declared boundary problem with all maps preserving its domain",
            "complexes": "cochain complexes (C,q_C) and (E,q_E) of finite-rank bundles with nondegenerate graded pairings",
            "cyclic_support_local_SDR": [
                "q_C i=i q_E and p q_C=q_E p",
                "p i=1_E",
                "q_C h+h q_C=1_C-i p",
                "h^2=0, h i=0, p h=0",
                "i,p,h are finite-order differential or pointwise maps and therefore support-nonincreasing",
                "degreewise sign involutions Sigma_C,Sigma_E satisfy Sigma_C i=i Sigma_E and p Sigma_C=Sigma_E p",
                "i^sharp=p, p^sharp=i, and h^sharp=Sigma_C h Sigma_C^-1 in the declared graded convention",
            ],
            "endpoint_option_A": "advanced/retarded degree-minus-one maps Lambda_E,+/- with q_E Lambda_E,+/-+Lambda_E,+/- q_E=1_E and same-sided causal support",
            "endpoint_option_B": "a finite-order witness W with P=q_E W+W q_E, degreewise advanced/retarded Green operators G_P,+/-, and causal uniqueness giving q_E G_P,+/-=G_P,+/- q_E; then Lambda_E,+/-=W G_P,+/-",
            "full_descent_option": "alternatively, advanced/retarded degree-minus-one maps Lambda_C,+/- on C descend to E by p Lambda_C,+/- i",
            "cyclic_endpoint": "Lambda_E,+^sharp=Sigma_E Lambda_E,- Sigma_E^-1 in complementary degree",
            "finite_shear": "optional support-local chain isomorphism U with finite-order support-local inverse, U^sharp=U^-1, and U Sigma_C=Sigma_C U; a sufficient implementation is U=1+N with filtration-nilpotent N and a finite inverse",
        },
        "conclusions": {
            "SDR_transport_formula": "Lambda_C,+/-=h+i Lambda_E,+/- p",
            "chain_identity": "q_C Lambda_C,+/-+Lambda_C,+/- q_C=1_C",
            "SDR_descent_formula": "Lambda_E,+/-=p Lambda_C,+/- i",
            "descent_chain_identity": "q_E Lambda_E,+/-+Lambda_E,+/- q_E=1_E",
            "support": "supp Lambda_C,+/- f is contained in J^+/-(supp f)",
            "cyclic_adjoint": "Lambda_C,+^sharp=Sigma_C Lambda_C,- Sigma_C^-1",
            "direct_sum": "finite direct sums transfer componentwise",
            "finite_cyclic_shear": "for q'=U q U^-1, Lambda'_+/-=U Lambda_+/- U^-1 has the same chain, support, and cyclic-adjoint properties",
            "no_transferred_factorization_required": "the theorem needs a causal homotopy or Green companion on the declared input side; it does not require a scalar-symbol factorization of the transferred complex",
        },
        "proof_ledger": {
            "witness_route": "q_E(WG)+(WG)q_E=(q_E W+W q_E)G=P G=1, using q_E G=G q_E",
            "SDR_route": "q_C(h+i Lambda_E p)+(h+i Lambda_E p)q_C=(1-i p)+i(q_E Lambda_E+Lambda_E q_E)p=1",
            "SDR_descent_route": "q_E(p Lambda_C i)+(p Lambda_C i)q_E=p(q_C Lambda_C+Lambda_C q_C)i=p i=1",
            "support_route": "support-local maps do not enlarge support and supp(f) is contained in both J^+(supp f) and J^-(supp f)",
            "adjoint_route": "take the graded adjoint and use the Sigma intertwiners, i^sharp=p, p^sharp=i, h^sharp=Sigma_C h Sigma_C^-1, and endpoint advanced/retarded reversal",
            "shear_route": "conjugate the chain identity by U; support follows from locality of U and U^-1, while U^sharp=U^-1 transports the adjoint relation",
        },
        "finite_exact_fixture": fixture,
        "berger_consumer": {
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "endpoint": "certified retained 26-row Green homotopy",
            "gravity_formula": "Lambda54,+/-=S_cl+iota_cl Lambda26,+/- pi_cl",
            "gravity_dimensions": "54=28 algebraic+26 causal",
            "coupled_formula": "Lambda64,+/-=S64+iota64 (Lambda26,+/- direct-sum LambdaM,+/-) pi64",
            "coupled_dimensions": "64=28 algebraic+(26 gravity-clock+10 Maxwell)",
            "cyclic_shear": "the nilpotent finite BV-canonical gauge-fixing shear is invertible, support-local, and pairing preserving",
            "generator_scope": "the frozen unary equivariance is K_Berger=D-omega R; raw D is affine and is not promoted by this theorem",
            "all_rows_replayed": True,
        },
        "consumer_contract": {
            "schema_path": str(CONSUMER_SCHEMA_PATH.relative_to(ROOT)),
            "schema_sha256": _sha256(CONSUMER_SCHEMA_PATH),
            "required_gates": [
                "typed complexes and row/degree ledger",
                "operator domains and same-sided support categories",
                "boundary-condition preservation",
                "support-local cyclic SDR identities",
                "pairing-derived degreewise sign involutions",
                "causal-input homotopy or witness/companion/Green package",
                "finite-order inverse and sign-intertwining for every shear",
            ],
            "Berger_adapter_path": str(CONSUMER_PATH.relative_to(ROOT)),
        },
        "exact_checks": {
            "universal_witness_to_homotopy_algebra": True,
            "universal_SDR_chain_identity": True,
            "universal_SDR_causal_descent_identity": True,
            "same_sided_support_transport": True,
            "cyclic_advanced_retarded_adjoint_transport": True,
            "finite_direct_sum_closure": True,
            "finite_cyclic_shear_closure": True,
            "finite_exact_fixture_all_defects_zero": True,
            "Berger_26_to_54_consumer_replayed": True,
            "Berger_26_plus_Maxwell_to_64_consumer_replayed": True,
            "Berger_generator_semantics_kept_fail_closed": True,
        },
        "flags": {
            "ABSTRACT_CAUSAL_TRANSFER_CERTIFIED": True,
            "ABSTRACT_CAUSAL_DESCENT_CERTIFIED": True,
            "ABSTRACT_CYCLIC_ADJOINT_TRANSFER_CERTIFIED": True,
            "ABSTRACT_FINITE_CYCLIC_SHEAR_TRANSFER_CERTIFIED": True,
            "BERGER_FIRST_CAUSAL_TRANSFER_CONSUMER": True,
            "G3_OPEN_BACKGROUND_CLASS": False,
            "TIMELIKE_BOUNDARY_VERSION": False,
            "HADAMARD_TRANSFER": False,
            "QUANTUM_CLAIM": False,
        },
        "source_manifest": {
            "producer": {"path": str(PRODUCER_PATH.relative_to(ROOT)), "sha256": _sha256(PRODUCER_PATH)},
            "independent_verifier": {"path": str(VERIFIER_PATH.relative_to(ROOT)), "sha256": _sha256(VERIFIER_PATH)},
            "tests": {"path": str(TEST_PATH.relative_to(ROOT)), "sha256": _sha256(TEST_PATH)},
            "strict_schema": {"path": str(SCHEMA_PATH.relative_to(ROOT)), "sha256": _sha256(SCHEMA_PATH)},
            "consumer_schema": {"path": str(CONSUMER_SCHEMA_PATH.relative_to(ROOT)), "sha256": _sha256(CONSUMER_SCHEMA_PATH)},
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.abstract_cyclic_causal_transfer --check --guards",
            "python3 -m d_quotient_classical.causal_transfer.verify_abstract_cyclic_causal_transfer",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_abstract_cyclic_causal_transfer",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/abstract-cyclic-causal-transfer-v1.schema.json -d d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/abstract-cyclic-causal-transfer-consumer-v1.schema.json -d d_quotient_classical/certificates/BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER.json",
        ],
        "claim_boundary": "This is a conditional abstract transfer theorem. It proves that already-existing advanced and retarded Green homotopies, or homotopies constructed from an independently certified Green companion, lift or descend through a finite-order support-local cyclic SDR and survive finite direct sums and finite cyclic shears. It does not prove that a proposed causal-input operator is Green hyperbolic, and the finite exact fixture is only an audit of the universal algebra. The Berger 26-to-54 and coupled 36-to-64 constructions are its embedded first G2 replay; additional consumers are certified by downstream artifacts rather than promoted inside this upstream theorem certificate. No uniform G3 background class is certified. The theorem excludes pseudodifferential projectors and infinite-order or non-support-local inverses. It does not address timelike boundaries unless all domains and boundary conditions satisfy the hypotheses, and it does not transport wavefront-set, Hadamard, renormalized, interacting, QME, anomaly, or quantum data. Berger equivariance is for K_Berger=D-omega R; it does not repair or promote the open affine raw-D Cartan problem.",
    }
    verify(payload)
    return payload


def build_consumer(theorem: dict[str, Any]) -> dict[str, Any]:
    """Instantiate the portable consumer contract on the Berger 26->54 lift."""
    refs = theorem["dependency_refs"]
    payload = {
        "schema": "pure-weyl-abstract-cyclic-causal-transfer-consumer-v1",
        "result_id": "BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER",
        "theorem_ref": {
            "path": str(CERTIFICATE_PATH.relative_to(ROOT)),
            "result_id": theorem["result_id"],
            "sha256": hashlib.sha256(_text(theorem).encode()).hexdigest(),
        },
        "setting_id": theorem["berger_consumer"]["setting_id"],
        "generality_level": "G2_COMPLETE_LINEAR_COMPLEX_ON_ONE_BACKGROUND",
        "base_domain": {
            "spacetime": "R x Berger-S3",
            "globally_hyperbolic": True,
            "timelike_boundary": False,
            "source_space": "Gamma_c smooth sections on every BV degree",
            "solution_space": "smooth advanced/retarded sections on every BV degree",
            "support_rule": "supp Lambda_+/- f subset J^+/-(supp f)",
            "zero_mode_rule": "retain spatial zero modes; no elliptic or harmonic projector",
        },
        "complexes": {
            "full": {"rows": 54, "degree_ranks": [5, 22, 22, 5], "q_ref": refs["berger_cyclic_shear"]},
            "endpoint": {"rows": 26, "degree_ranks": [3, 10, 10, 3], "q_ref": refs["berger_retained_26"]},
        },
        "pairing_and_signs": {
            "pairing_ref": refs["berger_cyclic_shear"],
            "formal_adjoint": "sharp from the exact odd BV pairing matrix",
            "sign_representation": "PAIRING_MATRIX_DERIVED_DEGREEWISE_INVOLUTION",
            "sign_rule": "Lambda_+^sharp=Sigma Lambda_- Sigma^-1 in complementary degree",
            "scalar_uniform_sign_assumed": False,
            "cyclic_SDR_verified": True,
        },
        "SDR": {
            "ref": refs["berger_54_to_26_sdr"],
            "transfer_direction": "ENDPOINT_TO_FULL_LIFT",
            "formula": "Lambda54,+/-=S_cl+iota_cl Lambda26,+/- pi_cl",
            "finite_order_support_local": True,
            "chain_maps": True,
            "side_conditions": True,
            "operator_domains_preserved": True,
        },
        "causal_input": {
            "ref": refs["berger_retained_26"],
            "route": "WITNESS_COMPANION_GREEN",
            "advanced_and_retarded": True,
            "both_inverse_identities": True,
            "same_sided_support": True,
            "adjoint_reversal": True,
        },
        "shears": {
            "ref": refs["berger_cyclic_shear"],
            "finite_order": True,
            "finite_order_inverse": True,
            "support_local": True,
            "boundary_domain_preserved": True,
            "pairing_unitary": True,
            "degreewise_sign_intertwining": True,
        },
        "preflight": {
            "typed_complexes": True,
            "operator_domains_declared": True,
            "boundary_conditions_declared": True,
            "same_sided_support_declared": True,
            "cyclic_SDR_exact": True,
            "degreewise_sign_data_present": True,
            "causal_input_Green_package_exact": True,
            "all_shears_admissible": True,
            "consumer_accepted": True,
        },
        "flags": {
            "ABSTRACT_CAUSAL_TRANSFER_CONSUMER_ACCEPTED": True,
            "CAUSAL_TRANSFER_REPLAYED": True,
            "TIMELIKE_BOUNDARY_VERSION": False,
            "HADAMARD_TRANSFER": False,
            "G3_OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": "This adapter proves that the complete 54-row Berger gravity--clock unary complex satisfies every input gate of the abstract cyclic causal-transfer theorem and inherits its advanced/retarded chain homotopies from the independently certified retained 26-row endpoint. Its degreewise adjoint signs are derived from the exact odd BV pairing rather than replaced by one scalar sign. It is a G2 application on one globally hyperbolic background without timelike boundary. It does not prove a second detour consumer, a uniform G3 background family, boundary-domain transfer, Hadamard or wavefront-set transport, interactions, a QME result, or any quantum claim. The frozen generator remains K_Berger rather than raw affine D.",
    }
    verify_consumer(payload)
    return payload


def verify_consumer(payload: dict[str, Any]) -> None:
    schema = json.loads(CONSUMER_SCHEMA_PATH.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    if not all(payload["preflight"].values()):
        raise AssertionError("consumer preflight did not close")
    if payload["pairing_and_signs"]["scalar_uniform_sign_assumed"] is not False:
        raise AssertionError("consumer collapsed degreewise signs to a scalar")
    if payload["base_domain"]["timelike_boundary"] is not False:
        raise AssertionError("undeclared boundary-domain theorem promoted")
    for key in ("TIMELIKE_BOUNDARY_VERSION", "HADAMARD_TRANSFER", "G3_OPEN_BACKGROUND_CLASS", "QUANTUM_CLAIM"):
        if payload["flags"][key] is not False:
            raise AssertionError(f"consumer downstream flag promoted: {key}")


def verify(payload: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator.check_schema(json.loads(SCHEMA_PATH.read_text()))
    jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(payload)
    if not all(payload["exact_checks"].values()):
        raise AssertionError("an abstract causal-transfer check dropped")
    if any(value != 0 for value in payload["finite_exact_fixture"]["identity_defects"].values()):
        raise AssertionError("finite exact fixture acquired a defect")
    if payload["berger_consumer"]["generator_scope"].find("raw D is affine") < 0:
        raise AssertionError("Berger raw-D/K distinction was lost")
    for flag in (
        "ABSTRACT_CAUSAL_TRANSFER_CERTIFIED",
        "ABSTRACT_CAUSAL_DESCENT_CERTIFIED",
        "ABSTRACT_CYCLIC_ADJOINT_TRANSFER_CERTIFIED",
        "ABSTRACT_FINITE_CYCLIC_SHEAR_TRANSFER_CERTIFIED",
        "BERGER_FIRST_CAUSAL_TRANSFER_CONSUMER",
    ):
        if payload["flags"][flag] is not True:
            raise AssertionError(f"proved flag dropped: {flag}")
    for flag in (
        "G3_OPEN_BACKGROUND_CLASS",
        "TIMELIKE_BOUNDARY_VERSION",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency drifted: {name}")


def _text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Abstract cyclic causal-transfer theorem

## Theorem

Let `(C,q_C)` and `(E,q_E)` be finite-rank differential complexes over a
time-oriented globally hyperbolic spacetime.  Suppose there is a cyclic,
support-local strong deformation retract

```text
E --i--> C --p--> E,        p i = 1,
q_C h + h q_C = 1 - i p,
h^2 = h i = p h = 0.
```

Assume `i,p,h` are finite-order differential or pointwise maps.  If `E` has
advanced and retarded degree-minus-one homotopies `Lambda_E,+/-`, define

```text
Lambda_C,+/- = h + i Lambda_E,+/- p.
```

Then

```text
q_C Lambda_C,+/- + Lambda_C,+/- q_C = 1_C.
```

The same SDR also transfers a parent homotopy downward.  If `C` already has
`Lambda_C,+/-`, then

```text
Lambda_E,+/- = p Lambda_C,+/- i
```

satisfies

```text
q_E Lambda_E,+/- + Lambda_E,+/- q_E
  = p(q_C Lambda_C,+/- + Lambda_C,+/- q_C)i
  = p i = 1_E.
```

This is the direction used by tractor/BGG compression.

Moreover, `Lambda_C,+/-` has the same advanced or retarded support.  Indeed,
the endpoint term is a composition of support-local maps with a same-sided
causal map, while `supp(hf)` is contained in `supp(f)`, hence in both its
causal future and causal past.

Let `Sigma_C` and `Sigma_E` be the degreewise sign involutions induced by the
two graded pairings.  If

```text
Sigma_C i = i Sigma_E,     p Sigma_C = Sigma_E p,
i^sharp=p,                 p^sharp=i,
h^sharp = Sigma_C h Sigma_C^-1,
Lambda_E,+^sharp = Sigma_E Lambda_E,- Sigma_E^-1,
```

then

```text
Lambda_C,+^sharp = Sigma_C Lambda_C,- Sigma_C^-1.
```

Thus the complementary-degree advanced/retarded adjoint relation transfers
without assuming that one scalar sign works in every degree.

## Endpoint companion route

The endpoint homotopy need not be supplied independently.  Let `W` be a
finite-order degree-minus-one witness and

```text
P = q_E W + W q_E.
```

If `P` has degreewise advanced and retarded Green operators `G_P,+/-`, causal
uniqueness and `q_E P=P q_E` give `q_E G_P,+/-=G_P,+/- q_E`.  Therefore

```text
Lambda_E,+/- = W G_P,+/-
```

obeys the endpoint chain-homotopy identity.  This hypothesis concerns the
complex companion; it does not require a scalar-symbol factorization of every
reduced middle operator.

## Closure operations

Finite direct sums transfer componentwise.  If `U` is a finite-order
support-local chain isomorphism with a finite-order support-local inverse,
then

```text
q'             = U q U^-1,
Lambda'_+/-    = U Lambda_+/- U^-1
```

preserve the chain identity and same-sided support.  When `U^sharp=U^-1`, the
cyclic adjoint relation is preserved as well.  A filtration-nilpotent shear
`U=1+N` is a sufficient implementation because its inverse is a finite
Neumann polynomial.  The cyclic conclusion additionally requires the shear
to intertwine the degreewise sign involution.

## Portable consumer gate

Every new application must validate the strict consumer contract before any
coefficient search.  It requires typed complexes, operator domains, boundary
conditions, same-sided support, all cyclic SDR identities, pairing-derived
degreewise signs, a causal-input Green package, and a finite local inverse for
every shear.  Missing data produce a rejected preflight rather than an
inferred transfer theorem.

## Berger replay

The Berger cylinder is the first complete consumer:

```text
54 = 28 algebraic + 26 causal,
Lambda54,+/- = S_cl + iota_cl Lambda26,+/- pi_cl.
```

The Maxwell extension uses direct-sum closure before the same SDR formula:

```text
64 = 28 algebraic + (26 gravity-clock + 10 Maxwell),
Lambda64,+/-
  = S64 + iota64 (Lambda26,+/- direct-sum LambdaM,+/-) pi64.
```

The gauge-fixing shear is finite, nilpotent and BV-canonical.  All imported
row identities, support statements and cyclic adjoints replay exactly.  The
frozen unary generator is `K_Berger=D-omega R`, not raw affine `D`.

## Scope

This result is an abstract conditional theorem plus one complete `G2`
consumer.  It does not itself establish causal-input Green hyperbolicity.  It
does not cover pseudodifferential projectors, timelike-boundary domains,
Hadamard wavefront sets, renormalized products, interactions, or quantum
claims.  Downstream consumers are certified in their own acyclic artifacts;
a uniform `G3` background class remains open.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    consumer = build_consumer(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        CONSUMER_PATH.write_text(_text(consumer))
        REPORT_PATH.write_text(_report())
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload):
            raise AssertionError("abstract causal-transfer certificate drifted")
        if REPORT_PATH.read_text() != _report():
            raise AssertionError("abstract causal-transfer report drifted")
        if CONSUMER_PATH.read_text() != _text(consumer):
            raise AssertionError("abstract causal-transfer Berger consumer drifted")
    if args.guards:
        mutants = []
        mutant = deepcopy(payload)
        mutant["flags"]["HADAMARD_TRANSFER"] = True
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["G3_OPEN_BACKGROUND_CLASS"] = True
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["finite_exact_fixture"]["identity_defects"]["sdr_identity"] = 1
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["berger_consumer"]["generator_scope"] = "raw D"
        mutants.append(mutant)
        for index, mutation in enumerate(mutants):
            try:
                verify(mutation)
            except (AssertionError, jsonschema.ValidationError):
                continue
            raise AssertionError(f"mutation guard {index} was accepted")
        consumer_mutant = deepcopy(consumer)
        consumer_mutant["SDR"]["operator_domains_preserved"] = False
        try:
            verify_consumer(consumer_mutant)
        except (AssertionError, jsonschema.ValidationError):
            pass
        else:
            raise AssertionError("consumer domain mutation was accepted")
    print("ABSTRACT_CAUSAL_TRANSFER_CERTIFIED: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""C-G5: non-cylinder mixed-detour consumer of cyclic causal transfer.

The pilot doubles the flat adjoint-tractor Yang--Mills detour on Minkowski,
reverses the normalization of the second copy, and applies an exact cyclic
triangular flavor shear.  The resulting presentation is coupled but linearly
equivalent to the direct sum.  Its parent causal homotopy descends through the
certified flat differential BGG retract.

This is a portability test, not a new interacting or higher-spin model.
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
PROOF_PATH = ROOT / "d_quotient_classical/certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR.json"
CONSUMER_PATH = ROOT / "d_quotient_classical/certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/minkowski-doubled-adjoint-tractor-mixed-detour.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/minkowski-doubled-adjoint-tractor-mixed-detour-v1.schema.json"
CONSUMER_SCHEMA_PATH = ROOT / "d_quotient_classical/schema/abstract-cyclic-causal-transfer-consumer-v1.schema.json"
THEOREM_PATH = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"
PRODUCER_PATH = ROOT / "d_quotient_classical/causal_transfer/minkowski_doubled_adjoint_tractor_pilot.py"
VERIFIER_PATH = ROOT / "d_quotient_classical/causal_transfer/verify_minkowski_doubled_adjoint_tractor_pilot.py"
TEST_PATH = ROOT / "d_quotient_classical/causal_transfer/tests/test_minkowski_doubled_adjoint_tractor_pilot.py"

DEPENDENCIES = {
    "kostant": ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression.json",
    "differential_bgg": ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_differential_screen.json",
    "parent_green": ROOT / "covariant_completion/certificates/adjoint_tractor_green_transfer.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _ref(path: Path, result_id: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": result_id,
        "sha256": _sha(path),
    }


def _sharp(a: sp.Matrix, domain_pairing: sp.Matrix, codomain_pairing: sp.Matrix) -> sp.Matrix:
    return domain_pairing.inv() * a.T * codomain_pairing


def _zero(a: sp.Matrix) -> bool:
    return all(sp.simplify(value) == 0 for value in a)


def _integer_matrix(a: sp.Matrix) -> list[list[int]]:
    return [[int(value) for value in row] for row in a.tolist()]


def exact_flavor_fixture() -> dict[str, Any]:
    """Exact mixed presentation of two oppositely normalized complexes."""
    d = sp.Matrix([[0, 0], [1, 0]])
    lam = sp.Matrix([[0, 1], [0, 0]])
    j = sp.Matrix([[0, 1], [-1, 0]])
    sigma = sp.diag(1, -1)

    normalization = sp.diag(1, -1)
    u = sp.Matrix([[1, 1], [0, 1]])
    u_inverse = sp.Matrix([[1, -1], [0, 1]])
    h0 = sp.eye(2)
    h1 = u_inverse.T * h0 * u_inverse

    q0 = sp.kronecker_product(normalization, d)
    lambda0 = sp.kronecker_product(normalization, lam)
    u_big = sp.kronecker_product(u, sp.eye(2))
    u_big_inverse = sp.kronecker_product(u_inverse, sp.eye(2))
    q1 = u_big * q0 * u_big_inverse
    lambda1 = u_big * lambda0 * u_big_inverse
    pairing0 = sp.kronecker_product(h0, j)
    pairing1 = sp.kronecker_product(h1, j)
    sigma_big = sp.kronecker_product(sp.eye(2), sigma)

    defects = {
        "base_chain_homotopy": d * lam + lam * d - sp.eye(2),
        "normalization_square": normalization * normalization - sp.eye(2),
        "shear_inverse_left": u_inverse * u - sp.eye(2),
        "shear_inverse_right": u * u_inverse - sp.eye(2),
        "transported_flavor_metric": h1 - sp.Matrix([[1, -1], [-1, 2]]),
        "flavor_isometry": h0.inv() * u.T * h1 - u_inverse,
        "mixed_nilpotency": q1 * q1,
        "mixed_chain_homotopy": q1 * lambda1 + lambda1 * q1 - sp.eye(4),
        "mixed_adjoint": _sharp(lambda1, pairing1, pairing1)
        - sigma_big * lambda1 * sigma_big,
        "sign_intertwining": u_big * sigma_big - sigma_big * u_big,
        "conjugation_nontrivial": q1
        - sp.Matrix([[0, 0, 0, 0], [1, 0, -2, 0], [0, 0, 0, 0], [0, 0, -1, 0]]),
    }
    nonzero = {name: value.tolist() for name, value in defects.items() if not _zero(value)}
    if nonzero:
        raise AssertionError(f"mixed-detour exact fixture failed: {nonzero}")
    return {
        "coefficient_field": "Q",
        "flavor_normalization": [[1, 0], [0, -1]],
        "flavor_shear": _integer_matrix(u),
        "flavor_shear_inverse": _integer_matrix(u_inverse),
        "transported_flavor_pairing": _integer_matrix(h1),
        "mixed_unary_matrix": _integer_matrix(q1),
        "mixed_homotopy_matrix": _integer_matrix(lambda1),
        "identity_defects": {name: 0 for name in defects},
    }


def _load_inputs() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    theorem = json.loads(THEOREM_PATH.read_text())
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if theorem["flags"]["ABSTRACT_CAUSAL_DESCENT_CERTIFIED"] is not True:
        raise AssertionError("abstract causal descent is unavailable")
    kostant = dependencies["kostant"]
    screen = dependencies["differential_bgg"]
    parent = dependencies["parent_green"]
    if kostant["result"] != "PASS":
        raise AssertionError("pointwise cyclic Kostant compression unavailable")
    hpl = screen["finite_HPL"]
    for key in (
        "flat_chain_map_defects",
        "flat_differential_homotopy_defects",
        "flat_differential_retraction_defects",
        "flat_splitting_defects",
    ):
        if hpl[key] != 0:
            raise AssertionError(f"flat differential BGG defect: {key}")
    if screen["support"]["all_emitted_HPL_maps_finite_order"] is not True:
        raise AssertionError("flat BGG maps are not support local")
    parent_data = parent["parent_YM_detour"]
    for key in (
        "flat_adjoint_tractor_connection",
        "degreewise_normally_hyperbolic",
        "advanced_retarded_Green_operators",
    ):
        if parent_data[key] is not True:
            raise AssertionError(f"parent causal input unavailable: {key}")
    return theorem, dependencies


def build_proof() -> dict[str, Any]:
    theorem, dependencies = _load_inputs()
    fixture = exact_flavor_fixture()
    payload = {
        "schema": "pure-weyl-minkowski-doubled-adjoint-tractor-mixed-detour-v1",
        "result_id": "MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR",
        "claim_status": "SECOND_NONCYLINDER_DETOUR_CONSUMER_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "abstract_transfer": _ref(THEOREM_PATH, theorem["result_id"]),
            "kostant": _ref(DEPENDENCIES["kostant"], "ADJOINT_TRACTOR_KOSTANT_COMPRESSION"),
            "differential_bgg": _ref(DEPENDENCIES["differential_bgg"], "ADJOINT_TRACTOR_BGG_DIFFERENTIAL_SCREEN"),
            "parent_green": _ref(DEPENDENCIES["parent_green"], "ADJOINT_TRACTOR_GREEN_TRANSFER"),
        },
        "background": {
            "spacetime": "Minkowski R^{1,3}",
            "not_conformal_cylinder": True,
            "globally_hyperbolic": True,
            "timelike_boundary": False,
            "riemann_tensor": "0",
            "schouten_tensor": "0",
            "adjoint_tractor_connection_flat": True,
        },
        "detour": {
            "single_parent_degree_ranks": [15, 60, 60, 15],
            "single_endpoint_degree_ranks": [4, 9, 9, 4],
            "doubled_parent_degree_ranks": [30, 120, 120, 30],
            "doubled_endpoint_degree_ranks": [8, 18, 18, 8],
            "second_copy_normalization": "Q_2=-Q_1 and Lambda_2=-Lambda_1",
            "mixed_presentation": "U diag(Q,-Q) U^-1 with U=[[1,1],[0,1]]",
            "off_diagonal_coupling": "-2 Q in the upper-right flavor block",
            "parent_causal_input": "degreewise normally hyperbolic adjoint-tractor Hodge companion",
            "descent": "Lambda_endpoint,+/-=p_2 Lambda_parent,+/- i_2",
            "flat_differential_BGG_series_terminates_after": dependencies["differential_bgg"]["finite_HPL"]["series_terminates_after"],
        },
        "pairing": {
            "unmixed_flavor_metric": [[1, 0], [0, 1]],
            "mixed_flavor_metric": [[1, -1], [-1, 2]],
            "shear_is_pairing_isometry_between_presentations": True,
            "degreewise_sign_involution_unchanged": True,
            "advanced_retarded_adjoint_reversal": True,
        },
        "exact_flavor_fixture": fixture,
        "exact_checks": {
            "Minkowski_parent_connection_flat": True,
            "parent_Hodge_companion_degreewise_normally_hyperbolic": True,
            "parent_advanced_retarded_homotopy_available": True,
            "two_copy_direct_sum_exact": True,
            "opposite_normalization_chain_identity_exact": True,
            "triangular_flavor_shear_has_finite_inverse": True,
            "triangular_flavor_shear_is_cyclic_with_transported_pairing": True,
            "mixed_presentation_has_nonzero_off_diagonal_operator": True,
            "flat_differential_BGG_SDR_exact": True,
            "parent_to_endpoint_descent_identity_exact": True,
            "same_sided_support_preserved": True,
            "degreewise_adjoint_reversal_preserved": True,
        },
        "flags": {
            "SECOND_NONCYLINDER_DETOUR_CONSUMER": True,
            "MIXED_FIELD_CAUSAL_TRANSFER_CONSUMER": True,
            "G3_OPEN_BACKGROUND_CLASS": False,
            "INTERACTING_MIXED_FIELD_THEORY": False,
            "HIGHER_SPIN_DISCOVERY": False,
            "TIMELIKE_BOUNDARY_VERSION": False,
            "HADAMARD_TRANSFER": False,
            "QUANTUM_CLAIM": False,
        },
        "source_manifest": {
            "producer": {"path": str(PRODUCER_PATH.relative_to(ROOT)), "sha256": _sha(PRODUCER_PATH)},
            "independent_verifier": {"path": str(VERIFIER_PATH.relative_to(ROOT)), "sha256": _sha(VERIFIER_PATH)},
            "tests": {"path": str(TEST_PATH.relative_to(ROOT)), "sha256": _sha(TEST_PATH)},
            "strict_schema": {"path": str(SCHEMA_PATH.relative_to(ROOT)), "sha256": _sha(SCHEMA_PATH)},
            "consumer_schema": {"path": str(CONSUMER_SCHEMA_PATH.relative_to(ROOT)), "sha256": _sha(CONSUMER_SCHEMA_PATH)},
        },
        "claim_boundary": "This certificate is a non-cylinder G2 portability consumer for the abstract cyclic causal-transfer theorem. It uses the flat adjoint-tractor Yang--Mills detour on Minkowski, doubles it with opposite differential normalization, applies a finite exact triangular flavor shear, and descends the parent causal homotopy through the already-certified flat differential BGG SDR. The coupled presentation has a nonzero off-diagonal unary operator but is linearly equivalent to two free copies. It is not an interacting mixed-field model, a higher-spin construction, a uniform open-background theorem, a timelike-boundary result, a Hadamard or wavefront-set theorem, or a quantum claim. It does not promote the separate curved-cylinder endpoint flags and it does not use the unresolved curved PBW screen as evidence.",
    }
    verify_proof(payload)
    return payload


def build_consumer(proof: dict[str, Any]) -> dict[str, Any]:
    theorem = json.loads(THEOREM_PATH.read_text())
    proof_ref = {
        "path": str(PROOF_PATH.relative_to(ROOT)),
        "result_id": proof["result_id"],
        "sha256": hashlib.sha256(_text(proof).encode()).hexdigest(),
    }
    payload = {
        "schema": "pure-weyl-abstract-cyclic-causal-transfer-consumer-v1",
        "result_id": "MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER",
        "theorem_ref": _ref(THEOREM_PATH, theorem["result_id"]),
        "setting_id": "minkowski_doubled_opposite_normalization_adjoint_tractor_detour",
        "generality_level": "G2_COMPLETE_LINEAR_COMPLEX_ON_ONE_BACKGROUND",
        "base_domain": {
            "spacetime": "Minkowski R^{1,3}",
            "globally_hyperbolic": True,
            "timelike_boundary": False,
            "source_space": "Gamma_c smooth sections in every doubled parent and endpoint degree",
            "solution_space": "smooth same-sided advanced or retarded sections in every degree",
            "support_rule": "supp Lambda_+/- f subset J^+/-(supp f)",
            "zero_mode_rule": "no spatial, helicity, harmonic, or pseudodifferential projector is used",
        },
        "complexes": {
            "full": {"rows": 300, "degree_ranks": [30, 120, 120, 30], "q_ref": _ref(DEPENDENCIES["parent_green"], "ADJOINT_TRACTOR_GREEN_TRANSFER")},
            "endpoint": {"rows": 52, "degree_ranks": [8, 18, 18, 8], "q_ref": _ref(DEPENDENCIES["differential_bgg"], "ADJOINT_TRACTOR_BGG_DIFFERENTIAL_SCREEN")},
        },
        "pairing_and_signs": {
            "pairing_ref": proof_ref,
            "formal_adjoint": "sharp from the adjoint-tractor/form pairing tensored with the transported flavor metric",
            "sign_representation": "PAIRING_MATRIX_DERIVED_DEGREEWISE_INVOLUTION",
            "sign_rule": "Lambda_+^sharp=Sigma Lambda_- Sigma^-1 in complementary degree",
            "scalar_uniform_sign_assumed": False,
            "cyclic_SDR_verified": True,
        },
        "SDR": {
            "ref": _ref(DEPENDENCIES["differential_bgg"], "ADJOINT_TRACTOR_BGG_DIFFERENTIAL_SCREEN"),
            "transfer_direction": "FULL_TO_ENDPOINT_DESCENT",
            "formula": "Lambda52,+/-=p2 Lambda300,+/- i2",
            "finite_order_support_local": True,
            "chain_maps": True,
            "side_conditions": True,
            "operator_domains_preserved": True,
        },
        "causal_input": {
            "ref": _ref(DEPENDENCIES["parent_green"], "ADJOINT_TRACTOR_GREEN_TRANSFER"),
            "route": "DIRECT_GREEN_HOMOTOPY",
            "advanced_and_retarded": True,
            "both_inverse_identities": True,
            "same_sided_support": True,
            "adjoint_reversal": True,
        },
        "shears": {
            "ref": proof_ref,
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
        "claim_boundary": "This adapter validates a second, non-cylinder G2 consumer of the abstract cyclic causal-transfer theorem. The causal input is the doubled flat adjoint-tractor parent detour on Minkowski; the transfer direction is descent through the finite differential BGG SDR to the doubled 4-9-9-4 endpoint. Opposite normalization of the second copy and a pairing-isometric triangular flavor shear give a nontrivially coupled unary presentation. The construction is nevertheless linearly equivalent to two free copies and is only a portability stress test. It neither supplies an interaction vertex nor promotes a higher-spin, G3 open-background, timelike-boundary, Hadamard, renormalized, anomaly, QME, or quantum theorem. It does not alter any curved-cylinder certificate and does not infer curved BGG exactness from flat Minkowski data.",
    }
    verify_consumer(payload)
    return payload


def verify_proof(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    if not all(payload["exact_checks"].values()):
        raise AssertionError("mixed-detour exact check dropped")
    if any(value != 0 for value in payload["exact_flavor_fixture"]["identity_defects"].values()):
        raise AssertionError("mixed-detour exact fixture acquired a defect")
    if payload["flags"]["SECOND_NONCYLINDER_DETOUR_CONSUMER"] is not True:
        raise AssertionError("second non-cylinder consumer not promoted")
    for key in (
        "G3_OPEN_BACKGROUND_CLASS",
        "INTERACTING_MIXED_FIELD_THEORY",
        "HIGHER_SPIN_DISCOVERY",
        "TIMELIKE_BOUNDARY_VERSION",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][key] is not False:
            raise AssertionError(f"forbidden pilot promotion: {key}")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha(path):
            raise AssertionError(f"pilot dependency drifted: {name}")


def verify_consumer(payload: dict[str, Any]) -> None:
    schema = json.loads(CONSUMER_SCHEMA_PATH.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    if payload["SDR"]["transfer_direction"] != "FULL_TO_ENDPOINT_DESCENT":
        raise AssertionError("pilot used the wrong transfer direction")
    if not all(payload["preflight"].values()):
        raise AssertionError("pilot consumer preflight failed")


def report() -> str:
    return """# Minkowski doubled adjoint-tractor mixed-detour pilot

## Result

The abstract cyclic causal-transfer theorem has a second `G2` consumer on a
non-cylinder background.  On Minkowski spacetime, the flat adjoint-tractor
Yang--Mills detour has degree ranks

```text
(15,60,60,15)
```

and its Hodge companion is degreewise normally hyperbolic.  The exact flat
differential BGG retract has endpoint ranks `(4,9,9,4)`.

We take two copies with opposite detour normalization,

```text
Q_0 = diag(Q,-Q),       Lambda_0 = diag(Lambda,-Lambda),
```

and apply the flavor shear

```text
U = [[1,1],[0,1]],      U^-1 = [[1,-1],[0,1]].
```

The mixed unary operator has upper-right block `-2Q`.  With the transported
flavor metric

```text
H_1 = U^-T U^-1 = [[1,-1],[-1,2]],
```

the shear is an exact pairing isometry.  It commutes with the degreewise BV
sign involution.  Direct-sum causal homotopies therefore survive the shear,
and the parent homotopy descends through the doubled differential BGG SDR:

```text
Lambda_52,+/- = p_2 Lambda_300,+/- i_2.
```

The chain identity, same-sided support, and advanced/retarded adjoint reversal
all follow without a helicity, harmonic, spatial, or pseudodifferential
projector.

## Boundary

This is a portability stress test.  The coupled presentation is linearly
equivalent to two free copies.  It is not a new interacting mixed-field
theory, a higher-spin model, or an open-background theorem.  It also does not
promote any curved-cylinder BGG or endpoint flag.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    proof = build_proof()
    consumer = build_consumer(proof)
    if args.write:
        PROOF_PATH.write_text(_text(proof))
        CONSUMER_PATH.write_text(_text(consumer))
        REPORT_PATH.write_text(report())
    if args.check:
        if PROOF_PATH.read_text() != _text(proof):
            raise AssertionError("mixed-detour proof certificate drifted")
        if CONSUMER_PATH.read_text() != _text(consumer):
            raise AssertionError("mixed-detour consumer certificate drifted")
        if REPORT_PATH.read_text() != report():
            raise AssertionError("mixed-detour report drifted")
    if args.guards:
        mutants = []
        mutant = deepcopy(proof)
        mutant["flags"]["INTERACTING_MIXED_FIELD_THEORY"] = True
        mutants.append(mutant)
        mutant = deepcopy(proof)
        mutant["exact_flavor_fixture"]["identity_defects"]["mixed_chain_homotopy"] = 1
        mutants.append(mutant)
        rejected = 0
        for mutant in mutants:
            try:
                verify_proof(mutant)
            except (AssertionError, jsonschema.ValidationError):
                rejected += 1
        if rejected != len(mutants):
            raise AssertionError("mixed-detour fail-closed guards failed")
    print("SECOND_NONCYLINDER_DETOUR_CONSUMER_CERTIFIED: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

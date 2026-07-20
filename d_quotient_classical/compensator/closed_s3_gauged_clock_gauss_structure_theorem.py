#!/usr/bin/env python3
"""Exact closed-S3 compact-Gauss and relative-clock structure theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1.json"
)

IMPORTS = (
    {
        "path": (
            "d_quotient_classical/compensator/"
            "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1.json"
        ),
        "sha256": (
            "3b7b1f86392f0d5daeec4b1adac99a0e16e472ff37b44253908a20c53aad1404"
        ),
        "source_commit": "6cc041fadaaf6259142aa8f30a2f75879cf92dd3",
        "result_id": "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1",
        "result_state": "SCOPED_SEPARATED_SCALE_U1_MINIMAL_GOOD_LOCUS_EMPTY",
    },
    {
        "path": (
            "d_quotient_classical/compensator/"
            "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1.json"
        ),
        "sha256": (
            "e597c687ae064ac6809b674c056aa08d0167a9184b6addb95b5b7330c33dcc62"
        ),
        "source_commit": "2b1609cedc77e85dd71967fb46e49a4595c75763",
        "result_id": "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1",
        "result_state": "SCOPED_TWO_FIELD_MINIMAL_CHARGE_MATRIX_GOOD_LOCUS_EMPTY",
    },
    {
        "path": (
            "d_quotient_classical/compensator/"
            "COMPENSATOR_TWO_FIELD_FULL_BV_CAUSAL_GATE_V1.json"
        ),
        "sha256": (
            "f1c859640f8e03c8ce5a9cc171635701eea880dc0a790282facba15c7cd9a9b8"
        ),
        "source_commit": "4812910c60b2fc641d79e93144bb23c684c90fb5",
        "result_id": "COMPENSATOR_TWO_FIELD_FULL_BV_CAUSAL_GATE_V1",
        "result_state": "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
    },
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> str:
    value = sp.factor(value)
    if not bool(value.is_Rational):
        raise AssertionError(f"non-rational exact fixture value: {value}")
    return str(value)


def _matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[_q(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _snf_factors(matrix: sp.Matrix) -> list[int]:
    diagonal = smith_normal_form(matrix, domain=ZZ)
    return [
        abs(int(diagonal[i, i]))
        for i in range(min(diagonal.rows, diagonal.cols))
        if diagonal[i, i] != 0
    ]


def _fixture(
    fixture_id: str,
    q_rows: list[list[int]],
    n_rows: list[list[int]],
    masses: list[int],
    pi_rows: list[int],
) -> dict[str, Any]:
    q = sp.Matrix(q_rows)
    m = sp.diag(*[sp.Integer(value) for value in masses])
    rank = int(q.rank())
    relative_dimension = q.rows - rank
    n = (
        sp.zeros(q.rows, 0)
        if relative_dimension == 0
        else sp.Matrix(n_rows)
    )
    pi = (
        sp.zeros(0, 1)
        if relative_dimension == 0
        else sp.Matrix(pi_rows)
    )
    if n.rows != q.rows or n.cols != q.rows - rank:
        raise AssertionError(f"{fixture_id}: wrong relative basis dimension")
    if q.T * n != sp.zeros(q.cols, n.cols):
        raise AssertionError(f"{fixture_id}: relative basis is not in ker Q^T")
    if int(n.rank()) != n.cols:
        raise AssertionError(f"{fixture_id}: relative basis is dependent")

    p = n * pi
    velocity = m.inv() * p
    relative_velocity = n.T * velocity
    inverse_reduced_metric = n.T * m.inv() * n
    reduced_metric = (
        sp.zeros(0, 0)
        if relative_dimension == 0
        else inverse_reduced_metric.inv()
    )
    energy = sp.Rational(1, 2) * (p.T * m.inv() * p)[0]
    reduced_energy = (
        sp.Rational(1, 2)
        * (relative_velocity.T * reduced_metric * relative_velocity)[0]
    )
    raw_d = (velocity.T * p)[0]
    if q.T * p != sp.zeros(q.cols, 1):
        raise AssertionError(f"{fixture_id}: Gauss law failed")
    if sp.factor(energy - reduced_energy) != 0:
        raise AssertionError(f"{fixture_id}: reduced energy mismatch")
    if sp.factor(raw_d - (relative_velocity.T * pi)[0]) != 0:
        raise AssertionError(f"{fixture_id}: raw-D reduction mismatch")
    if relative_dimension and any(
        value <= 0 for value in reduced_metric.cholesky().diagonal()
    ):
        raise AssertionError(f"{fixture_id}: reduced metric not positive")

    return {
        "fixture_id": fixture_id,
        "Q": q_rows,
        "rank": rank,
        "smith_invariant_factors": _snf_factors(q),
        "relative_dimension": q.rows - rank,
        "integer_relative_character_basis_N": n_rows,
        "phase_inertia_M": _matrix_rows(m),
        "reduced_inverse_metric_A_equals_NT_Minv_N": _matrix_rows(
            inverse_reduced_metric
        ),
        "reduced_metric_Grel_equals_Ainv": _matrix_rows(reduced_metric),
        "relative_momentum_Pi": [_q(value) for value in pi],
        "phase_momentum_p_equals_N_Pi": [_q(value) for value in p],
        "horizontal_velocity_v_equals_Minv_p": [_q(value) for value in velocity],
        "relative_velocity_psidot_equals_NT_v": [
            _q(value) for value in relative_velocity
        ],
        "gauss_QT_p": [_q(value) for value in q.T * p],
        "kinetic_energy": _q(energy),
        "reduced_kinetic_energy": _q(reduced_energy),
        "raw_D_phase_moment_map": _q(raw_d),
        "positive_reduced_metric": True,
    }


def _sigma_projector_fixture() -> dict[str, Any]:
    g = sp.Matrix(
        [
            [2, sp.Rational(1, 2), 0],
            [sp.Rational(1, 2), 3, sp.Rational(1, 3)],
            [0, sp.Rational(1, 3), 4],
        ]
    )
    k = sp.Matrix([0, 1, 1])
    vertical_gram = (k.T * g * k)[0]
    projector = sp.eye(3) - k * (sp.Rational(1, 1) / vertical_gram) * k.T * g
    horizontal_vectors: list[sp.Matrix] = []
    for vector in (k.T * g).nullspace():
        scale = math.lcm(*[int(value.q) for value in vector])
        entries = [int(value * scale) for value in vector]
        divisor = math.gcd(*[abs(value) for value in entries])
        entries = [value // divisor for value in entries]
        horizontal_vectors.append(sp.Matrix(entries))
    horizontal = sp.Matrix.hstack(*horizontal_vectors)
    reduced = horizontal.T * g * horizontal
    if (
        projector * projector != projector
        or projector * k != sp.zeros(3, 1)
        or k.T * g * projector != sp.zeros(1, 3)
        or g * projector != projector.T * g
        or not g.is_positive_definite
        or not reduced.is_positive_definite
    ):
        raise AssertionError("full sigma-model quotient fixture failed")
    return {
        "field_coordinates": ["rho", "theta1", "theta2"],
        "full_positive_kinetic_G": _matrix_rows(g),
        "gauge_K": [_q(value) for value in k],
        "vertical_Gram_KT_G_K": _q(vertical_gram),
        "horizontal_projector_P_G": _matrix_rows(projector),
        "horizontal_basis_H": _matrix_rows(horizontal),
        "reduced_metric_HT_G_H": _matrix_rows(reduced),
        "identities": {
            "P_squared_equals_P": True,
            "P_K_equals_zero": True,
            "KT_G_P_equals_zero": True,
            "G_P_equals_PT_G": True,
            "full_G_positive": True,
            "reduced_metric_positive": True,
        },
    }


def _check_imports() -> list[dict[str, Any]]:
    imported: list[dict[str, Any]] = []
    for declaration in IMPORTS:
        path = ROOT / declaration["path"]
        actual = _sha(path)
        source = json.loads(path.read_text())
        if (
            actual != declaration["sha256"]
            or source["result_id"] != declaration["result_id"]
            or source["result_state"] != declaration["result_state"]
        ):
            raise AssertionError(f"import drifted: {declaration['path']}")
        imported.append({**declaration, "actual_sha256": actual})
    if json.loads((ROOT / IMPORTS[-1]["path"]).read_text())[
        "activation_condition_satisfied"
    ]:
        raise AssertionError("conditional full gate unexpectedly activated")
    return imported


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["result_state"] != (
        "CERTIFIED_FINITE_HOMOGENEOUS_GAUSS_RELATIVE_CLOCK_STRUCTURE_THEOREM"
    ):
        raise AssertionError("structure theorem state promoted or narrowed")
    for record in payload["imports"]:
        if (
            _sha(ROOT / record["path"]) != record["sha256"]
            or record["actual_sha256"] != record["sha256"]
        ):
            raise AssertionError("import hash validation failed")
    for fixture in payload["exact_fixtures"]:
        if fixture["relative_dimension"] != len(
            fixture["integer_relative_character_basis_N"][0]
        ):
            raise AssertionError("relative dimension drifted")
        if any(value != "0" for value in fixture["gauss_QT_p"]):
            raise AssertionError("Gauss fixture promoted")
        if fixture["kinetic_energy"] != fixture["reduced_kinetic_energy"]:
            raise AssertionError("reduced kinetic energy drifted")
        reduced = fixture["reduced_metric_Grel_equals_Ainv"]
        if reduced:
            matrix = sp.Matrix(
                [[sp.Rational(value) for value in row] for row in reduced]
            )
            if not matrix.is_positive_definite:
                raise AssertionError("positive reduced metric drifted")
    counterflow = next(
        item
        for item in payload["exact_fixtures"]
        if item["fixture_id"] == "two_equal_charges_counterflow_clock"
    )
    if (
        counterflow["phase_momentum_p_equals_N_Pi"] != ["1", "-1"]
        or counterflow["relative_velocity_psidot_equals_NT_v"] != ["5/6"]
        or counterflow["reduced_metric_Grel_equals_Ainv"] != [["6/5"]]
    ):
        raise AssertionError("counterflow witness drifted")
    sigma = payload["exact_sigma_model_projector_fixture"]
    g = sp.Matrix(
        [
            [sp.Rational(value) for value in row]
            for row in sigma["full_positive_kinetic_G"]
        ]
    )
    k = sp.Matrix([sp.Rational(value) for value in sigma["gauge_K"]])
    projector = sp.Matrix(
        [
            [sp.Rational(value) for value in row]
            for row in sigma["horizontal_projector_P_G"]
        ]
    )
    if (
        projector * projector != projector
        or projector * k != sp.zeros(k.rows, 1)
        or k.T * g * projector != sp.zeros(1, g.cols)
        or not all(sigma["identities"].values())
    ):
        raise AssertionError("sigma-model projector drifted")
    terminal = payload["terminal_verdict"]
    if (
        terminal["total_compact_gauge_charge_on_closed_S3"] != "ZERO"
        or terminal["individual_phase_momenta_forced_zero"]
        or terminal["boundary_or_external_source_needed_for_relative_clock"]
        or not terminal[
            "boundary_or_external_source_needed_for_nonzero_total_gauge_charge"
        ]
        or terminal["full_BV_or_causal_successor_activated"]
    ):
        raise AssertionError("terminal Gauss/clock disposition promoted")
    flags = payload["claim_flags"]
    if (
        not flags["FINITE_HOMOGENEOUS_STRUCTURE_THEOREM"]
        or not flags["POSITIVE_NEUTRAL_RELATIVE_CLOCK_ALLOWED"]
        or flags["NONZERO_TOTAL_GAUGE_CHARGE_ON_CLOSED_SOURCE_FREE_S3"]
        or flags["MODEL_SPECIFIC_ACTION_SELECTED"]
        or flags["FULL_BV_OR_CAUSAL_PARENT"]
        or flags["HADAMARD_OR_QUANTUM"]
    ):
        raise AssertionError("claim boundary promoted")
    expected_hashes = {
        "imports_sha256": _digest(payload["imports"]),
        "charge_lattice_sha256": _digest(payload["charge_lattice"]),
        "gauss_sha256": _digest(payload["integrated_gauss"]),
        "clock_criterion_sha256": _digest(payload["clock_criterion"]),
        "reduced_mechanics_sha256": _digest(payload["reduced_mechanics"]),
        "moment_maps_sha256": _digest(payload["moment_maps"]),
        "fixtures_sha256": _digest(payload["exact_fixtures"]),
        "sigma_projector_sha256": _digest(
            payload["exact_sigma_model_projector_fixture"]
        ),
        "terminal_verdict_sha256": _digest(payload["terminal_verdict"]),
        "claim_boundary_sha256": _digest(payload["claim_boundary"]),
    }
    if payload["content_hashes"] != expected_hashes:
        raise AssertionError("content hash validation failed")


def build() -> dict[str, Any]:
    imports = _check_imports()
    fixtures = [
        _fixture(
            "one_charged_phase_no_relative_clock",
            [[1]],
            [[]],
            [2],
            [],
        ),
        _fixture(
            "two_equal_charges_counterflow_clock",
            [[1], [1]],
            [[1], [-1]],
            [2, 3],
            [1],
        ),
        _fixture(
            "one_charged_plus_one_neutral_clock",
            [[1], [0]],
            [[0], [1]],
            [2, 3],
            [1],
        ),
        _fixture(
            "three_phases_two_gauges",
            [[1, 0], [0, 1], [1, 1]],
            [[-1], [-1], [1]],
            [2, 3, 5],
            [1],
        ),
    ]
    sigma_projector = _sigma_projector_fixture()

    charge_lattice = {
        "data": (
            "Q is an n by r integer matrix defining the torus homomorphism "
            "gamma -> Q gamma on phase angles; k=rank_Q(Q)."
        ),
        "smith_normal_form": (
            "There exist U in GL(n,Z) and V in GL(r,Z) with "
            "U Q V=diag(d1,...,dk,0), 0<d1|...|dk."
        ),
        "continuous_gauge_rank": "k",
        "continuous_gauge_reducibility": "r-k",
        "finite_kernel_order_when_k_equals_r": "product_i d_i",
        "faithful_effective_action_condition": "k=r and every d_i=1",
        "relative_character_lattice": "L=ker_Z(Q^T)",
        "relative_character_lattice_rank": "rank_Z(L)=n-k",
        "relative_phase_torus_dimension": "n-k",
        "nonprimitive_effect": (
            "d_i>1 changes finite isotropy/kernel data but not the continuous "
            "relative-phase dimension."
        ),
        "scope_of_snf_equivalence": (
            "SNF classifies the compact gauge homomorphism. It does not "
            "identify kinetic matrices or potentials that are not carried "
            "through the same integral field-basis transformation."
        ),
    }

    gauss = {
        "general_two_derivative_homogeneous_phase_lagrangian": (
            "L_phase=Vol(S3)[1/2 v^T M(rho,psi) v"
            "+dotrho^T C(rho,psi) v-V(rho,psi)], "
            "v=dottheta+Q A0"
        ),
        "phase_momentum": "p=M v+C^T dotrho",
        "local_constraint": (
            "d_spatial star E_alpha+(Q^T j_phase)_alpha="
            "(j_external)_alpha"
        ),
        "integrated_source_free_closed_S3_constraint": "Q^T p=0",
        "proof": (
            "A0 is a Lagrange multiplier and the spatial divergence integrates "
            "to zero because boundary(S3)=empty. Smooth U(1) bundles over S3 "
            "are topologically trivial because H^2(S3,Z)=0."
        ),
        "does_not_imply": "p_i=0 or v_i=0 separately when n-k>0",
        "with_sources_or_boundary_convention": (
            "Q^T P_phase+q_external=Phi_boundary; on closed S3 "
            "Phi_boundary=0, so an external charge permits scalar charge only "
            "through exact total cancellation."
        ),
    }

    clock_criterion = {
        "fixed_moduli_definitions": (
            "M is the nonsingular symmetric phase inertia; "
            "H_M=ker_R(Q^T M); N is a primitive integer basis matrix for "
            "ker_Z(Q^T); psi=N^T theta."
        ),
        "moving_moduli_affine_solution": (
            "For p=M v+C^T dotrho, v0=-M^{-1}C^T dotrho gives p=0; every "
            "Gauss solution is v=v0+h with h in H_M. Thus moving moduli shift "
            "the affine origin but do not change the n-rank(Q) homogeneous "
            "relative-clock directions."
        ),
        "given_velocity_necessary_and_sufficient": {
            "zero_total_gauge_charge": "Q^T M v=0",
            "physically_nontrivial_relative_motion": "N^T v != 0",
            "equivalent_nonvertical_condition": "v not in im_R(Q)",
        },
        "positive_inertia_theorem": (
            "If M>0 then H_M is the M-orthogonal complement of im(Q), "
            "H_M intersects im(Q) only at zero, and a nonzero physical "
            "relative clock exists iff n-rank(Q)>0."
        ),
        "all_selected_velocity_components_nonzero": (
            "For S subset {1,...,n}, one v in H_M with v_i!=0 for every i in "
            "S exists iff e_i is not in im_R(M Q) for every i in S."
        ),
        "all_selected_momentum_components_nonzero": (
            "One p in ker_R(Q^T) with p_i!=0 for every i in S exists iff e_i "
            "is not in im_R(Q) for every i in S."
        ),
        "component_criterion_proof": (
            "Each forbidden zero component is a proper hyperplane in the "
            "constraint kernel exactly when its coordinate functional is "
            "nonzero there. A finite union of proper real hyperplanes cannot "
            "cover a vector space."
        ),
        "one_field_corollary": (
            "For n=rank(Q)=1 and M>0, H_M=0; the one-field charged phase "
            "velocity vanishes."
        ),
        "many_field_correction": (
            "Zero total compact charge does not kill relative clocks. If "
            "n-rank(Q)>0, positivity itself permits them without an indefinite "
            "cancellation, boundary flux or external source."
        ),
    }

    reduced_mechanics = {
        "gauss_solution": "p=N Pi",
        "relative_velocity": "dotpsi=N^T M^{-1} N Pi=A Pi",
        "A": "A=N^T M^{-1} N",
        "reduced_phase_metric": "G_rel=A^{-1}",
        "reduced_lagrangian": (
            "L_rel=Vol(S3)[1/2 dotpsi^T G_rel dotpsi-V_rel]"
        ),
        "reduced_hamiltonian": (
            "H_rel=Vol(S3)[1/2 Pi^T A Pi+V_rel]"
        ),
        "positive_inertia_proof": (
            "For z!=0, z^T A z=(N z)^T M^{-1}(N z)>0; hence A and G_rel "
            "are positive definite."
        ),
        "declared_indefinite_case": (
            "If M is nonsingular indefinite, the same formulas apply when A "
            "is nonsingular. The relative sector is healthy exactly when "
            "A>0 (equivalently G_rel>0); an indefinite charge cancellation "
            "alone is not a healthy clock. If A is singular, a further Dirac "
            "reduction is required and no health claim is emitted."
        ),
        "general_sigma_model_extension": (
            "For full field-space kinetic G and gauge Killing matrix "
            "K=(0,Q), the horizontal projector is "
            "P_G=I-K(K^T G K)^{-1}K^T G whenever the vertical Gram matrix is "
            "invertible. A positive G induces a positive quotient metric."
        ),
        "potential_condition": (
            "Gauge invariance allows phase Fourier characters only from "
            "L=ker_Z(Q^T). Arbitrary nonzero reduced initial velocity gives "
            "local evolving solutions. Uniform helical motion additionally "
            "requires a continuous relative symmetry direction of V and a "
            "transverse critical point; a phase-independent V supplies it."
        ),
    }

    moment_maps = {
        "phase_symplectic_potential": (
            "Theta_phase=Vol(S3) p^T delta theta="
            "Vol(S3) Pi^T delta psi on Q^T p=0"
        ),
        "compact_gauge_moment_map": "mu_gamma=Vol(S3) gamma^T Q^T p=0",
        "stationary_raw_D_variation": (
            "delta H_D^phase=Vol(S3) v_bar^T delta p="
            "Vol(S3) dotpsi_bar^T delta Pi"
        ),
        "stationary_raw_D_hamiltonian": (
            "H_D^phase=Vol(S3) dotpsi_bar^T Pi, up to a background constant"
        ),
        "K_Berger_phase_stabilizer": (
            "If dotpsi_bar=w generates a continuous symmetry R_w of V, "
            "K_Berger=D-R_w and delta H_K_Berger^phase=0."
        ),
        "gauge_invariance": (
            "v_bar -> v_bar+Q lambda changes v_bar^T p by "
            "lambda^T Q^T p=0."
        ),
        "claim_scope": (
            "These are the exact phase-sector contributions. A full "
            "gravitational K_Berger moment map, pairing or causal carrier is "
            "not inferred."
        ),
    }

    terminal = {
        "result": "POSITIVE_RELATIVE_CLOCKS_SURVIVE_ZERO_TOTAL_GAUGE_CHARGE",
        "total_compact_gauge_charge_on_closed_S3": "ZERO",
        "individual_phase_momenta_forced_zero": False,
        "relative_clock_exists_with_positive_inertia_iff": "n-rank(Q)>0",
        "boundary_or_external_source_needed_for_relative_clock": False,
        "boundary_or_external_source_needed_for_nonzero_total_gauge_charge": True,
        "full_BV_or_causal_successor_activated": False,
        "next_gate": (
            "A model-specific successor may import this theorem only after it "
            "selects an action whose scale/trace gate passes. Compact Gauss "
            "alone is no longer a valid reason to reject a many-field neutral "
            "relative clock."
        ),
    }
    claim_boundary = (
        "This theorem covers finitely many smooth homogeneous complex scalars "
        "with integer compact-Abelian charge matrix, a smooth Abelian "
        "connection, gauge-invariant two-derivative sigma-model kinetic and "
        "potential terms, and fixed-modulus phase reduction on closed S3. "
        "It proves an integrated Gauss and finite-dimensional quotient theorem, "
        "not a nonhomogeneous PDE, global monotonic-clock, full BV, causal, "
        "Hadamard, anomaly/QME, particle, scattering, positivity-of-gravity or "
        "unitarity result. Uniform helical solutions require the stated "
        "potential symmetry. Boundaries, sources, higher derivatives and "
        "singular kinetic matrices obey different gates explicitly recorded "
        "above."
    )

    payload = {
        "schema": "pure-weyl-closed-s3-gauged-clock-gauss-structure-v1",
        "result_id": "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1",
        "result_state": (
            "CERTIFIED_FINITE_HOMOGENEOUS_GAUSS_RELATIVE_CLOCK_STRUCTURE_THEOREM"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "scope": {
            "spatial_manifold": "closed smooth S3",
            "field_count": "finite n>=1",
            "compact_gauge_count": "finite r>=0",
            "charge_domain": "integer Q in Mat_{n by r}(Z)",
            "carrier": "smooth homogeneous phase/modulus mechanics",
            "derivative_order": 2,
            "kinetic_branches": [
                "positive definite",
                "nonsingular declared indefinite",
            ],
            "external_sources": False,
            "boundary": False,
        },
        "charge_lattice": charge_lattice,
        "integrated_gauss": gauss,
        "clock_criterion": clock_criterion,
        "reduced_mechanics": reduced_mechanics,
        "moment_maps": moment_maps,
        "exact_fixtures": fixtures,
        "proof_obligations": {
            "three_import_hashes": "PASS",
            "smith_rank_and_relative_dimension": "PASS",
            "gauss_constraint": "PASS",
            "positive_quotient_metric": "PASS",
            "two_field_counterflow_witness": "PASS",
            "charged_plus_neutral_witness": "PASS",
            "three_field_two_gauge_witness": "PASS",
            "raw_D_reduction": "PASS",
            "full_sigma_model_projector": "PASS",
            "source_and_boundary_split": "PASS",
        },
        "exact_sigma_model_projector_fixture": sigma_projector,
        "terminal_verdict": terminal,
        "claim_flags": {
            "FINITE_HOMOGENEOUS_STRUCTURE_THEOREM": True,
            "POSITIVE_NEUTRAL_RELATIVE_CLOCK_ALLOWED": True,
            "NONZERO_TOTAL_GAUGE_CHARGE_ON_CLOSED_SOURCE_FREE_S3": False,
            "MODEL_SPECIFIC_ACTION_SELECTED": False,
            "FULL_BV_OR_CAUSAL_PARENT": False,
            "HADAMARD_OR_QUANTUM": False,
        },
        "claim_boundary": claim_boundary,
    }
    payload["content_hashes"] = {
        "imports_sha256": _digest(imports),
        "charge_lattice_sha256": _digest(charge_lattice),
        "gauss_sha256": _digest(gauss),
        "clock_criterion_sha256": _digest(clock_criterion),
        "reduced_mechanics_sha256": _digest(reduced_mechanics),
        "moment_maps_sha256": _digest(moment_maps),
        "fixtures_sha256": _digest(fixtures),
        "sigma_projector_sha256": _digest(sigma_projector),
        "terminal_verdict_sha256": _digest(terminal),
        "claim_boundary_sha256": _digest(claim_boundary),
    }
    validate_payload(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("generated closed-S3 Gauss theorem drifted")
        print(f"{payload['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered)
    print(OUTPUT)


if __name__ == "__main__":
    main()

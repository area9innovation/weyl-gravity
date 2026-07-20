"""Classify the physical moment-map intersection of the locked all-m carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_source_explore import (
    POLAR_EXTRA,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-exceptional-all-m-moment-intersection-fragment.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-exceptional-all-m-moment-intersection-v1.schema.json"
INPUT_COMMIT = "6c3831061f22447cfb4bbbe7e6d4791cdab18e0d"
INPUTS = {
    "all_m_incidence": ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1.json",
    "joined_obstruction_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json",
    "moment_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "sign_theorem": ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json",
    "exceptional_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "generic_zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
    "exceptional_nonzero_k": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "difference_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json",
}
EXPECTED_HASHES = {
    "all_m_incidence": "b4eed34422acf0574ec9098d1893ac5c5c496bfdf223e8e77bd483ef6adc7ab4",
    "joined_obstruction_map": "723083a24436059f19ae70f53287e6141c58f54b27eae50064896fd12eba7fbb",
    "moment_bridge": "047594a9019eb68a000ecce1799063789714db632c41e67e48d37bdf0fc3657a",
    "sign_theorem": "26fae23935261735385d6a7796d5f10db3404f863d2bdf85c7b5d0869afd0006",
    "exceptional_self": "17f28c0a6b71e2edd0f786367741e5e7221953aa98ed1583c6ae2a6f227f2e6a",
    "generic_zero_block": "29e017cd35d0560eeb4b769c1a0d73570a9799fd877c566d0b4438e3d18313af",
    "exceptional_nonzero_k": "4d3839689270af952808b14adef4f00fcbabeb69ef17efcf7e6d18b7747340a3",
    "polar_current": "327cfacb304218b894b622f08a8ad0a2d8cb370a1cb041c69f58e343ac33ac76",
    "difference_matrix": "172555aa986df0b888f805c488efa69543586ddff548bd1b8bf5cc15ffffce40",
}


class MomentIntersectionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MomentIntersectionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected object: {path}")
    return value


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _input_gate(records: dict[str, dict[str, Any]]) -> None:
    for name, path in INPUTS.items():
        _require(_sha256(path) == EXPECTED_HASHES[name], f"{name} content hash changed")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", INPUT_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    _require(ancestor.returncode == 0, "required input commit is not an ancestor of HEAD")
    _require(
        records["all_m_incidence"]["classification"]["locked_two_fibre_difference_incidence_classified"],
        "all-m incidence theorem changed",
    )
    _require(
        records["joined_obstruction_map"]["classification"]["complete_branch_labelled_obstruction_map_joined"],
        "joined obstruction map changed",
    )
    _require(
        records["moment_bridge"]["classification"]["generic_H_Px_J_selection_rules_certified"],
        "generic moment-map selection rules changed",
    )
    _require(
        records["sign_theorem"]["classification"]["exceptional_extra_ell1_all_k_both_parities_negative"],
        "exceptional sign theorem changed",
    )
    _require(
        records["sign_theorem"]["classification"]["generic_extra_all_ell_all_k_both_parities_negative"],
        "generic sign theorem changed",
    )
    _require(
        records["exceptional_self"]["classification"]["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"],
        "exceptional self-resonance theorem changed",
    )
    _require(
        records["generic_zero_block"]["classification"]["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"],
        "generic bounded zero-block theorem changed",
    )


def _normalization(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    exceptional = records["exceptional_nonzero_k"]["theorem"]["action_pairing"]["Gram"]
    _require(exceptional["axial"]["extra"] == "4*(3*k**2 + 4)", "exceptional axial current changed")
    _require(exceptional["polar"]["extra"] == "4*(3*k**2 + 4)", "exceptional polar current changed")
    exceptional_k0 = records["sign_theorem"]["harmonic_sign_ledger"]["exceptional_extra_ell1"]["k_zero_Gram"]
    _require(exceptional_k0 == ["16", "3"], "exceptional rest normalization changed")

    lam, momentum = sp.symbols("lambda k", real=True)
    local = {"lam": lam, "k": momentum}
    polar_gram = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=local) for value in row]
            for row in records["polar_current"]["shell_pairing"]["extra_Hermitian_current_Gram"]
        ]
    )
    y_rest_weight = sp.factor(polar_gram[0, 0].subs({lam: 6, momentum: 0}))
    _require(y_rest_weight == 22464, "polar-extra e2 rest current weight changed")
    omega_e = sp.symbols("omega_e", real=True)
    polar_basis = sp.Matrix(
        [
            [
                sp.sympify(
                    value.replace("lambda", "lam"),
                    locals={"lam": lam, "k": momentum, "omega_e": omega_e},
                )
                for value in row
            ]
            for row in records["polar_current"]["shell_pairing"]["extra_basis_order_At_B_Ct_U"]
        ]
    )
    current_first_rest = tuple(
        sp.factor(value)
        for value in polar_basis[:, 0].subs({lam: 6, momentum: 0})
    )
    _require(current_first_rest == POLAR_EXTRA["e2"], "direct-source e2/current-basis bridge changed")
    _require(
        records["difference_matrix"]["sparse_matrix"]["unique_control_amplitude"] == "ell2 polar e2",
        "locked control-amplitude label changed",
    )

    z = sp.symbols("z", real=True)
    p2 = sp.legendre(2, z)
    v1_axis_norm = sp.integrate(z**2, (z, -1, 1)) * 2 * sp.pi
    v2_axis_norm = sp.integrate(p2**2, (z, -1, 1)) * 2 * sp.pi
    axis_tensor = sp.diag(sp.Rational(-1, 2), sp.Rational(-1, 2), 1)
    v2_trace_coefficient = sp.factor(v2_axis_norm / sp.trace(axis_tensor**2))
    _require(v1_axis_norm == 4 * sp.pi / 3, "V1 angular norm changed")
    _require(v2_axis_norm == 4 * sp.pi / 5, "V2 axis angular norm changed")
    _require(v2_trace_coefficient == 8 * sp.pi / 15, "V2 STF angular form changed")
    return {
        "transported_exceptional_current_weights": {"axial": "16", "polar": "3"},
        "transported_polar_extra_e2_current_weight": str(y_rest_weight),
        "direct_source_e2_equals_polar_current_first_basis_at_rest": [
            str(value) for value in current_first_rest
        ],
        "W1": "W1(x,z)=(4*pi/3)*x^dagger*z",
        "W2": "W2(Y,Z)=(8*pi/15)*tr(Y^dagger*Z)",
        "V1_axis_norm": str(v1_axis_norm),
        "V2_axis_norm": str(v2_axis_norm),
        "V2_trace_coefficient": str(v2_trace_coefficient),
        "transport_lemma": "For a co-propagating SO(1,1)-transported on-shell representative the conserved current is proportional to p^mu. Dividing Omega_t by positive omega makes the Hermitian current weight invariant, so the rest weights apply in the transported coefficient normalization used by the locked functional.",
    }


def _rotation_data() -> dict[str, Any]:
    generators = [
        sp.Matrix([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
        sp.Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]]),
    ]
    return {
        "real_cartesian_generators_Ja": [_matrix_strings(value) for value in generators],
        "Hermitian_V1_generators": "T1_a=-i*J_a",
        "Hermitian_V2_action": "T2_a(Y)=-i*(J_a*Y-Y*J_a)",
    }


def _moment_maps() -> dict[str, Any]:
    return {
        "direction_set": {
            "k=0": "one fibre; + and - labels coincide and are not double-counted",
            "|k|>0": "s=+1 and s=-1 are independent positive-frequency travelling fibres; reality supplies their negative-frequency conjugates",
        },
        "definitions": {
            "omega": "sqrt(k^2+4/3)>0",
            "E_s": "16*W1(x_ax,s,x_ax,s)+3*W1(x_pol,s,x_pol,s)",
            "Q_s": "22464*W2(Y_s,Y_s)",
            "A_s,a": "16*W1(x_ax,s,T1_a*x_ax,s)+3*W1(x_pol,s,T1_a*x_pol,s)",
            "B_s,a": "22464*W2(Y_s,T2_a(Y_s))",
        },
        "five_maps": {
            "mu_H": "-(L/4)*sum_s[omega^2*E_s+(2*omega)^2*Q_s]",
            "mu_Px": "(L/4)*sum_s s*[k*omega*E_s+(2*k)*(2*omega)*Q_s]",
            "mu_Ja": "(L/4)*sum_s[omega*A_s,a+2*omega*B_s,a], a=1,2,3",
        },
        "reality_and_phase": {
            "physical_slice": "dagger is ordinary complex conjugate transpose on positive-frequency amplitudes; negative-frequency coefficients are their reality conjugates",
            "phase_independence": "mu_H is invariant under every independent travelling-node phase",
            "Hermiticity": "T1_a and T2_a are Hermitian for W1 and W2, so all five maps are real",
        },
        "strict_sign": {
            "identity": "-4*mu_H/L=sum_s[omega^2*(16*W1(x_ax,s,x_ax,s)+3*W1(x_pol,s,x_pol,s))+4*omega^2*22464*W2(Y_s,Y_s)]",
            "positive_coefficients": ["L>0", "omega^2=k^2+4/3>0", "16>0", "3>0", "22464>0", "W1 positive", "W2 positive"],
            "conclusion": "mu_H=0 iff x_ax,s=x_pol,s=Y_s=0 for every retained direction s",
        },
    }


def _shell_census() -> dict[str, Any]:
    mu = sp.symbols("mu")

    def q(lam: int, value: sp.Rational | int) -> sp.Expr:
        return sp.factor(mu**2 - 2 * lam * mu + lam * (lam - 2)).subs(mu, value)

    xy_mu = sp.Integer(12)
    yy_mu = sp.Rational(64, 3)
    xy_q = {str(lam): str(sp.factor(q(lam, xy_mu))) for lam in (6, 12)}
    yy_q = {str(lam): str(sp.factor(q(lam, yy_mu))) for lam in (6, 12, 20)}
    _require(all(sp.sympify(value) != 0 for value in xy_q.values()), "X-Y sum hit a q shell")
    _require(all(sp.sympify(value) != 0 for value in yy_q.values()), "Y-Y sum hit a q shell")
    return {
        "co_propagating_invariant_masses_squared": {
            "X_plus_X": "16/3: the L=2 p-primary self resonance",
            "Y_minus_X": "4/3: the L=1 exceptional locked difference resonance",
            "X_plus_Y": "12: off every L=1,2,3 target shell",
            "Y_plus_Y": "64/3: off every L=0,1,2,3,4 target shell",
        },
        "q_polynomial": "q_lambda(mu)=mu^2-2*lambda*mu+lambda*(lambda-2)",
        "X_plus_Y_q_residuals": xy_q,
        "Y_plus_Y_q_residuals": yy_q,
        "p_shell_comparisons": {
            "X_plus_Y_mu_12": "not in {16/3,34/3} for L=2,3",
            "Y_plus_Y_mu_64_over_3": "not in {16/3,34/3,58/3} for L=2,3,4",
        },
        "zero_frequency": {
            "generic_circle_pressure": "R_c(Y)=(1/2)*(2*k)^2*22464*W2(Y,Y)",
            "Wilson_acceleration": "R_W=0",
            "remaining_static_rows": "the joined obstruction map retains the five stabilizer rows; any additional same-carrier quadratic row vanishes at the physical common-zero origin",
        },
        "opposite_direction_cross_channels": {
            "status": "COEFFICIENTS_NOT_CERTIFIED",
            "exact_intersection_effect": "none: the strict mu_H identity forces both directional fibres to zero before any opposite-direction shell row is imposed",
            "not_claimed": "no classification of the resonance-only complex variety for opposite travelling directions",
        },
    }


def _complex_incidence() -> dict[str, Any]:
    rank_three = sp.diag(1, 1, -2)
    rank_two = sp.diag(1, -1, 0)
    isotropic = sp.Matrix([1, sp.I, 0])
    rank_one = isotropic * isotropic.T
    witnesses = {
        "rank_3": rank_three,
        "rank_2": rank_two,
        "rank_1_complex": rank_one,
        "rank_0": sp.zeros(3),
    }
    _require(rank_three.rank() == 3 and sp.trace(rank_three) == 0, "rank-three witness changed")
    _require(rank_two.rank() == 2 and sp.trace(rank_two) == 0, "rank-two witness changed")
    _require(rank_one.rank() == 1 and sp.trace(rank_one) == 0, "rank-one witness changed")
    return {
        "exceptional_self_equations": {
            "q_s": "q_s=(sqrt(3)/4)*x_pol,s",
            "even": "STF(x_ax,s*x_ax,s^T-q_s*q_s^T)=0",
            "cross": "STF(x_ax,s*q_s^T+q_s*x_ax,s^T)=0",
            "exact_zero_locus": "x_ax,s=x_pol,s=0",
        },
        "locked_difference_equations": {
            "axial": "Y_s*conj(x_ax,s)=0",
            "polar": "Y_s*conj(x_pol,s)=0",
            "coefficients": ["-768/5", "-864/5"],
        },
        "certified_co_propagating_resonance_ideal": {
            "radical": "<components of x_ax,s, components of x_pol,s>",
            "prime_quotient": "C[Y_s] for each direction s",
            "reason": "the exceptional self ideal has zero locus x=0; the locked equations then vanish identically and the remaining co-propagating positive sums are off shell",
        },
        "rank_stratum_witnesses_with_x_zero": {
            name: _matrix_strings(value) for name, value in witnesses.items()
        },
        "rank_one_disposition": {
            "complex_resonance_incidence": "SURVIVES with x_ax=x_pol=0 and Y=v*v^T for nonzero isotropic v",
            "real_STF_slice_before_Taub": "ABSENT because a nonzero real symmetric rank-one matrix has nonzero trace",
            "physical_Taub_slice": "ABSENT because mu_H<0 for every nonzero complex positive-frequency Y",
        },
    }


def _intersection_theorem(direction_count: int) -> dict[str, Any]:
    variable_count = 22 * direction_count
    return {
        "correction_class": "BOUNDED_OR_FINITE_QUASIPERIODIC",
        "physical_common_zero": "x_ax,s=x_pol,s=Y_s=0 for every retained direction s",
        "necessity": "mu_H is one of the five required adjoint-cokernel/Taub components and its exact sum-of-squares identity is strictly negative away from the origin",
        "sufficiency": "at u=0 every quadratic source functional vanishes and v=0 solves L v=-(1/2)D^2E[u,u]",
        "real_radical": {
            "statement": "the real radical of the complete physical obstruction ideal is the maximal ideal of the origin",
            "number_of_real_generators": variable_count,
            "per_direction": "Re/Im of 3 axial dipole, 3 polar dipole and 5 STF quadrupole coefficients",
            "ordinary_complex_primary_decomposition_warning": "mu_H contains conjugates and defines a real-algebraic physical slice; it is not replaced by a holomorphic complex ideal",
        },
        "rank_orbit_phase_classification": {
            "rank_Y_1_2_3": "all excluded on the physical common zero",
            "rank_Y_0": "survives only with both exceptional vectors zero",
            "SO3_orbit": "the sole surviving orbit is the fixed origin",
            "phases": "all phase strata collapse at the origin",
            "axial_polar_alignment": "irrelevant at the origin; no nonzero aligned or transverse stratum survives",
            "momentum_pairing": "for |k|>0, mu_Px and rotations may cancel between directions, but the two negative mu_H contributions add and force both directions to zero",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _input_gate(records)
    direction_count = 2
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "einstein-maxwell-weyl-exceptional-all-m-moment-intersection-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1",
        "result_state": "LOCKED_ALL_M_PHYSICAL_MOMENT_RESONANCE_INTERSECTION_IS_ORIGIN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_LOCKED_EXCEPTIONAL_GENERIC_ALL_M_BOTH_TRAVEL_DIRECTIONS",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "one fixed closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "exceptional axial/polar ell=1 extra modes at momentum s*k and the contributing transported polar-extra e2 ell=2 STF modes at s*2k, with s=+/- retained separately for |k|>0",
            "degree": 2,
            "parity": "both exceptional parities and the unique contributing generic polar-extra multiplicity; all certified zero branch-parity columns retained",
            "ell": "1 and 2 inputs; all quadratically allowed output L",
            "m": "all m in Cartesian V1 and STF V2 coordinates",
            "k": "one allowed |k| on one fixed circumference; k=0 is one fibre and |k|>0 retains independent positive-frequency +/- travelling fibres",
            "omega": "omega=sqrt(k^2+4/3) and 2*omega on the locked generic shell",
        },
        "input_gate": {
            "required_commit": INPUT_COMMIT,
            "required_commit_is_ancestor": True,
            "exact_hashes": EXPECTED_HASHES,
        },
        "current_normalization": _normalization(records),
        "rotation_representations": _rotation_data(),
        "moment_maps": _moment_maps(),
        "certified_bounded_functional_ledger": _shell_census(),
        "complex_resonance_incidence": _complex_incidence(),
        "physical_intersection_theorem": {
            "k_zero": _intersection_theorem(1),
            "nonzero_abs_k_with_both_directions": _intersection_theorem(direction_count),
        },
        "complete_obstruction_join": {
            "imported_codomain": "stab* direct-sum polynomial_growth direct-sum characteristic_shell",
            "all_certified_same_carrier_rows_retained": True,
            "redundancy_argument": "Every certified P or R row is quadratic and hence vanishes at the origin. Since the required mu_H row already has physical zero set {0}, adjoining any certified or future same-carrier quadratic row cannot change the physical common zero.",
            "bounded_verdict": "OBSTRUCTED for every nonzero physical tangent in the declared carrier; the zero tangent has the trivial correction",
            "smooth_secular_verdict": "OBSTRUCTED for every nonzero physical tangent because stabilizer moment maps remain necessary when secular terms are allowed",
            "causal_retarded_verdict": "NO_CERTIFIED_MAP",
        },
        "paper_13_disposition": {
            "status": "SCOPED_COROLLARY_CERTIFIED",
            "statement": "The locked exceptional/generic pure-extra all-m carrier has physical bounded tangent cone {0}, although its resonance-only complex incidence has nontrivial STF rank strata.",
            "freeze_effect": "does not freeze the complete finite-harmonic cone; it closes one exceptional cross-fibre face and sharpens the nonlinear atlas row",
        },
        "classification": {
            "input_commit_and_all_m_certificate_imported_exactly": True,
            "five_stabilizer_moment_maps_computed_in_cartesian_coordinates": True,
            "positive_and_negative_travel_directions_retained_separately": True,
            "complex_locked_rank_strata_classified": True,
            "rank_one_complex_stratum_survives_resonance_incidence": True,
            "rank_one_real_STF_stratum_absent": True,
            "physical_common_zero_is_origin": True,
            "real_radical_maximal_ideal_certified": True,
            "all_certified_same_carrier_functionals_joined": True,
            "opposite_direction_resonance_only_complex_variety_classified": False,
            "larger_multiple_abs_momentum_union_classified": False,
            "causal_all_orders_residual_observer_particle_quantum_claim": False,
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "schema_path": str(SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA),
            "inputs": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "result_id": records[name]["result_id"],
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
            "source_helper": {
                "path": "bridge/einstein_sector/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_source_explore.py",
                "sha256": "bfd38263ffddc95fa7d0320f086ace74340c2a426f5b9c83a800e2429b1df6db",
            },
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_all_m_moment_intersection --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_all_m_moment_intersection.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_all_m_moment_intersection -v",
        ],
        "next_gate": "extract the structural finite-harmonic theorem while keeping the unclassified opposite-direction resonance-only complex variety and larger multiple-|k| unions explicit",
        "claim_boundary": "This exact result classifies the physical common zero only on one locked |k| exceptional/generic pure-extra carrier, with both travel directions retained when distinct. The strict Hamiltonian Taub row makes uncomputed opposite-direction resonance coefficients redundant for that physical intersection, but their resonance-only complex variety remains open. No unrelated momentum fibre, global tangent, Einstein q-primary, infinite completion, causal/retarded, all-orders, residual, observer, particle, positivity or quantum claim is made.",
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    evidence = {
        "path": str(OUTPUT.relative_to(ROOT)),
        "result_id": certificate["result_id"],
        "sha256": hashlib.sha256(_render(certificate).encode()).hexdigest(),
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_boundary",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.ph.wm.interaction.exceptional_all_m_locked_moment_intersection",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {
                        "status": "CERTIFIED",
                        "statement": "The one-background k-by-2k locked dispersion and both travel directions are retained without circumference identification.",
                    },
                    "lee_wald": {
                        "status": "CERTIFIED",
                        "statement": "The transported exceptional and generic-extra current weights are positive and exact.",
                    },
                    "taub_maps": {
                        "status": "CERTIFIED",
                        "statement": "All five maps are explicit; mu_H is strictly negative away from the origin.",
                    },
                    "resonance": {
                        "status": "CERTIFIED",
                        "statement": "The co-propagating self and locked rows are exact; opposite-direction coefficients remain unnecessary for, and do not enlarge, the physical common zero.",
                    },
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {
                            "status": "OBSTRUCTED",
                            "statement": "Every nonzero physical tangent on this carrier fails mu_H; the zero tangent has v=0.",
                        },
                        "smooth_secular": {
                            "status": "OBSTRUCTED",
                            "statement": "Secular terms do not remove the stabilizer/Taub condition.",
                        },
                        "causal_retarded": {
                            "status": "NO_CERTIFIED_MAP",
                            "statement": "No causal/retarded compact-product correction complex is certified.",
                        },
                    },
                },
                "evidence": [evidence],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_all_m_moment_intersection --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-exceptional-all-m-moment-intersection-fragment.json",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_all_m_moment_intersection.py",
        ],
    }


def verify_output() -> None:
    certificate = build_certificate()
    atlas = build_atlas(certificate)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    _require(OUTPUT.read_text(encoding="utf-8") == _render(certificate), "certificate is stale")
    _require(ATLAS.read_text(encoding="utf-8") == _render(atlas), "atlas fragment is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        verify_output()
        print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1: PASS")
    else:
        certificate = build_certificate()
        OUTPUT.write_text(_render(certificate), encoding="utf-8")
        ATLAS.write_text(_render(build_atlas(certificate)), encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        print(f"wrote {ATLAS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

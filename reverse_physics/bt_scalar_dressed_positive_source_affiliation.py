#!/usr/bin/env python3
"""Affiliate the positive BT detector source to a dressed scalar projector."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-scalar-dressed-positive-source-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-scalar-dressed-positive-source-affiliation.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-scalar-dressed-positive-source-affiliation.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def sharp(matrix, metric):
    return metric * matrix.T * metric


def charge_components(matrix, charges):
    components = {}
    for row in range(matrix.rows):
        for column in range(matrix.cols):
            if matrix[row, column] != 0:
                charge = charges[row] - charges[column]
                components.setdefault(charge, sp.zeros(matrix.rows, matrix.cols))
                components[charge][row, column] = matrix[row, column]
    return components


def build():
    effect_cert = load(INPUTS[1])
    rigidity = load(INPUTS[2])
    charge_cert = load(INPUTS[3])
    unit_obstruction = load(INPUTS[4])
    zero_mode = load(INPUTS[5])

    dimension = 8
    charges = [2 * value.bit_count() - 3 for value in range(dimension)]
    eta = sp.zeros(dimension)
    for column in range(dimension):
        eta[7 - column, column] = 1
    kappa = eta.copy()
    charge_operator = sp.diag(*charges)

    u_plus = sp.zeros(dimension, 4)
    for column in range(4):
        u_plus[column, column] = 1 / sp.sqrt(2)
        u_plus[7 - column, column] = 1 / sp.sqrt(2)
    u0 = u_plus[:, 0]
    p_positive = sp.simplify(u_plus * u_plus.T * eta)
    p_u0 = sp.simplify(u0 * u0.T * eta)
    source_charge_components = charge_components(p_u0, charges)
    state_charge_support = sorted({charges[0], charges[7]})
    projector_charge_support = sorted(source_charge_components)

    charge_spaces = {
        charge: [index for index, value in enumerate(charges) if value == charge]
        for charge in sorted(set(charges))
    }
    fixed_charge_grams = {
        charge: eta.extract(indices, indices)
        for charge, indices in charge_spaces.items()
    }

    # This is only a nontrivial exact replay of the universal R-sharp R=1
    # algebra.  Affiliation in the theorem uses the certified public formal R_t.
    diagonal = [
        sp.Rational(2), sp.Rational(3), sp.Rational(5), sp.Rational(7),
        sp.Rational(1, 7), sp.Rational(1, 5), sp.Rational(1, 3), sp.Rational(1, 2),
    ]
    r_fixture = sp.diag(*diagonal)
    r_sharp = sharp(r_fixture, eta)
    scalar_state_fixture = sp.simplify(r_sharp * u0)
    scalar_projector_fixture = sp.simplify(r_sharp * p_u0 * r_fixture)
    scalar_positive_projector_fixture = sp.simplify(r_sharp * p_positive * r_fixture)
    scalar_kappa_fixture = sp.simplify(r_sharp * kappa * r_fixture)

    residue = sp.Matrix([
        [sp.Rational(entry) for entry in row]
        for row in effect_cert["fixed_shell_transition_effect"]["R_plus"]
    ])
    effect = sp.simplify(residue.T * residue)
    zeta = sp.symbols("zeta", nonnegative=True)
    click_bt = sp.simplify(u_plus * (zeta * effect) * u_plus.T * eta)
    no_click_bt = sp.simplify(p_positive - click_bt)
    click_scalar = sp.simplify(r_sharp * click_bt * r_fixture)
    no_click_scalar = sp.simplify(r_sharp * no_click_bt * r_fixture)
    target_click = sp.simplify(sp.trace(p_u0 * click_bt))
    target_no_click = sp.simplify(sp.trace(p_u0 * no_click_bt))
    scalar_click = sp.simplify(sp.trace(scalar_projector_fixture * click_scalar))
    scalar_no_click = sp.simplify(sp.trace(scalar_projector_fixture * no_click_scalar))

    identity8 = sp.eye(dimension)
    zero8 = sp.zeros(dimension)
    checks = {
        "predecessor_effect_passes": effect_cert["checks"]["ok"],
        "public_Rt_is_formally_two_sided": rigidity["formal_projection_rigidity"]["conclusion"] == "Pi(lambda)=identity as a formal power series",
        "formal_charge_pullback_is_equivariant": charge_cert["disposition"]["all_order_formal_pullback_equivariance"] == "PROVED",
        "regular_local_parity_automorphism_remains_obstructed": unit_obstruction["unit_obstruction"]["conclusion"] == "NO_SAME_CHART_REGULAR_LOCAL_SYMBOL_HIDDEN_PARITY_AUTOMORPHISM",
        "zero_mode_Laurent_carrier_is_available": zero_mode["zero_mode_orbit_algebra"]["algebra"] == "Q[Z,Z^-1] on finite Laurent supports",
        "three_particle_metric_is_cross_complement": eta == kappa and eta * eta == identity8,
        "positive_frame_is_ghost_even": kappa * u_plus == u_plus,
        "positive_frame_Gram_is_identity": sp.simplify(u_plus.T * eta * u_plus) == sp.eye(4),
        "declared_source_is_normalized": sp.simplify((u0.T * eta * u0)[0]) == 1,
        "declared_source_is_ghost_even": kappa * u0 == u0,
        "declared_source_projector_is_idempotent": p_u0 * p_u0 == p_u0,
        "declared_source_projector_is_Krein_self_adjoint": sharp(p_u0, eta) == p_u0,
        "declared_source_projector_has_rank_one": p_u0.rank() == 1,
        "positive_plane_projector_has_rank_four": p_positive.rank() == 4,
        "positive_plane_projector_is_idempotent": p_positive * p_positive == p_positive,
        "odd_particle_charge_spectrum_has_no_zero": 0 not in charges,
        "every_fixed_charge_space_is_totally_isotropic": all(gram == sp.zeros(gram.rows) for gram in fixed_charge_grams.values()),
        "positive_source_is_not_charge_invariant": charge_operator * p_u0 != p_u0 * charge_operator,
        "source_state_charge_support_is_plus_minus_three": state_charge_support == [-3, 3],
        "source_projector_charge_support_is_minus_six_zero_plus_six": projector_charge_support == [-6, 0, 6],
        "both_nonzero_projector_charge_branches_are_present": source_charge_components[-6].rank() == 1 and source_charge_components[6].rank() == 1,
        "fixture_R_is_nontrivial": r_fixture != identity8,
        "fixture_R_is_Krein_unitary": sp.simplify(r_fixture.T * eta * r_fixture) == eta and r_sharp * r_fixture == identity8,
        "pulled_scalar_state_is_normalized": sp.simplify((scalar_state_fixture.T * eta * scalar_state_fixture)[0]) == 1,
        "pulled_scalar_projector_is_idempotent": scalar_projector_fixture * scalar_projector_fixture == scalar_projector_fixture,
        "pulled_scalar_projector_is_Krein_self_adjoint": sharp(scalar_projector_fixture, eta) == scalar_projector_fixture,
        "projector_pushforward_returns_target": sp.simplify(r_fixture * scalar_projector_fixture * r_sharp) == p_u0,
        "positive_plane_pushforward_returns_target": sp.simplify(r_fixture * scalar_positive_projector_fixture * r_sharp) == p_positive,
        "pulled_fundamental_symmetry_is_involutive": scalar_kappa_fixture * scalar_kappa_fixture == identity8,
        "pulled_fundamental_symmetry_is_Krein_self_adjoint": sharp(scalar_kappa_fixture, eta) == scalar_kappa_fixture,
        "click_effect_is_pulled_by_similarity": sp.simplify(r_fixture * click_scalar * r_sharp) == click_bt,
        "no_click_effect_is_pulled_by_similarity": sp.simplify(r_fixture * no_click_scalar * r_sharp) == no_click_bt,
        "pulled_effects_are_complete_on_pulled_positive_plane": sp.simplify(click_scalar + no_click_scalar) == scalar_positive_projector_fixture,
        "target_declared_source_click_is_zeta_over_sixteen": target_click == zeta / 16,
        "target_declared_source_no_click_is_one_minus_zeta_over_sixteen": target_no_click == 1 - zeta / 16,
        "finite_trace_click_is_preserved": scalar_click == target_click,
        "finite_trace_no_click_is_preserved": scalar_no_click == target_no_click,
        "rate_is_imported_without_refitting": effect_cert["detector_probability_jet"]["declared_source_rate"] == "lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
    }

    failures = [name for name, ok in checks.items() if not bool(ok)]
    certificate = {
        "answer": (
            "Yes for an explicitly Rt-dressed, shift-breaking perfect-square scalar source on the finite covariant detector ideal. "
            "Let u0=(|Upsilon^3>+|Omega^3>)/sqrt(2), P_u=|u0><u0|_K, and use the certified formal two-sided public map Rt. "
            "Then psi_phi=Rt^dagger u0 and P_phi=Rt^dagger P_u Rt are normalized, positive-range, idempotent and Krein self-adjoint, while Rt P_phi Rt^dagger=P_u exactly. Pulling back the BT effects preserves the finite generalized-Born trace, so q_click=zeta/16, q_no=1-zeta/16 and the leading scalar click rate is lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]. "
            "The construction is not the standard shift-invariant characteristic projector: u0 has state charges -3 and +3, P_u has operator-charge support {-6,0,+6}, and its scalar pullback has Laurent orbit support {Z^-6,1,Z^6}. This charge breaking is forced for a positive odd-particle preparation because there is no zero-charge three-particle sector and every fixed-charge subspace is totally isotropic. The result therefore supplies a scoped physical-scalar dressed-source probability jet, not general Eq. (19)."
        ),
        "assumptions": [
            "the public Rt acts on the declared finite detector ideal on a common invariant domain and admits the certified formal lambda expansion",
            "the certified coefficientwise identities Rt^dagger Rt=Rt Rt^dagger=1 are used; no convergence or nonperturbative inverse is claimed",
            "the scalar source is the Rt-pullback of the positive BT source and is allowed to depend on the coupling, finite time, and vacuum-orbit coordinate",
            "the covariant scalar carrier contains finite Laurent powers of Z=exp(lambda phi0) with pairing <Z^m,Z^n>=delta_(m+n,0)",
            "the finite detector-ideal trace is cyclic under the displayed formal similarities",
            "the leading isolated-shell BT click effect and its finite-volume normalization are imported unchanged",
            "spatial boundary terms vanish on the declared periodic finite-volume cell when the public Hamiltonian intertwining is used"
        ],
        "certificate": "REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1",
        "checks": {"details": checks, "failures": failures, "ok": not failures, "passed": len(checks) - len(failures), "total": len(checks)},
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "does_not_establish": [
            "the standard shift-invariant characteristic projector P_chi^(phi)",
            "Eq. (19) for arbitrary scalar projectors",
            "ghost evenness of the public pushforward of P_chi^(phi)",
            "a regular same-chart local-symbol hidden-parity automorphism",
            "descent of the charge derivation through the fixed-vacuum quotient Z=1",
            "convergence or nonperturbative existence of the full Rt operator",
            "an explicit global dense domain for the pulled dressed projector",
            "an exact finite-time probability beyond the leading isolated-shell jet",
            "global gluing of the ten six-point shells",
            "an asymptotic Moller, LSZ, or S operator",
            "all-order transition-probability positivity",
            "loops or infrared resummation",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "formal_Rt_affiliation": {
            "public_identity": "Rt^dagger*Rt=Rt*Rt^dagger=1 coefficientwise in formal lambda",
            "scalar_state": "psi_phi=Rt^dagger*u0",
            "scalar_projector": "P_phi=Rt^dagger*P_u*Rt",
            "scalar_positive_plane": "P_phi_plus=Rt^dagger*P_plus*Rt",
            "scalar_fundamental_symmetry": "kappa_phi=Rt^dagger*kappa3*Rt",
            "projector_pushforward": "Rt*P_phi*Rt^dagger=P_u",
            "positive_plane_pushforward": "Rt*P_phi_plus*Rt^dagger=P_plus",
            "normalization": "<psi_phi,psi_phi>_K=1",
            "scalar_Laurent_orbit_support": ["Z^-6", "1", "Z^6"],
            "regularity": "finite Laurent-Fock detector ideal; no F^-1 or log(F) is adjoined",
            "fixture_role": "a nontrivial rational Krein-unitary replay checks the universal identities but is not identified with the public Rt",
            "status": "FORMAL_FINITE_DETECTOR_IDEAL_SOURCE_AFFILIATED"
        },
        "interpretation": {
            "dressed_shift_breaking_scalar_source": "CONSTRUCTED_AND_RT_AFFILIATED_FORMALLY",
            "leading_scalar_click_no_click_probability_jet": "TRANSFERRED_WITHOUT_REFITTING",
            "standard_shift_invariant_P_chi": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "regular_local_hidden_parity": "STILL_OBSTRUCTED",
            "all_time_scalar_probability": "NOT_CONSTRUCTED"
        },
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "next_gate": (
            "Construct a compact wave-packet realization and common invariant domain for psi_phi=Rt^dagger u0, including its vacuum-orbit and squeeze factors, then test whether its finite-time pulled effect converges independently of the point-cell regulator. General Eq. (19) remains a separate gate for the shift-invariant P_chi projector."
        ),
        "odd_particle_charge_positivity_obstruction": {
            "three_particle_charge_spectrum": charges,
            "charge_values": sorted(set(charges)),
            "zero_charge_dimension": charges.count(0),
            "fixed_charge_Gram": "eta restricted to every V_q is zero",
            "lemma": "a nonzero Q-invariant range contains a nonzero charge eigenvector; that vector is eta-null because q is nonzero",
            "conclusion": "NO_NONZERO_CHARGE_INVARIANT_POSITIVE_RANGE_IN_THE_THREE_PARTICLE_CARRIER",
            "forced_trade": "a positive three-particle source must break boost charge, hence its scalar preimage must carry nontrivial vacuum-orbit Laurent powers"
        },
        "positive_BT_source": {
            "basis": "u_x=(|x>+|7-x>)/sqrt(2), x=0,1,2,3",
            "declared_source": "u0=(|Upsilon^3>+|Omega^3>)/sqrt(2)",
            "metric": "eta=kappa3 with eta|x>=|7-x>",
            "positive_plane_Gram": "I4",
            "source_norm": "1",
            "source_state_charge_support": [-3, 3],
            "source_projector": "P_u=|u0><u0|_K",
            "source_projector_charge_support": [-6, 0, 6],
            "shift_invariant": False
        },
        "provenance": {
            "source_commit": "6c97a515",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact SymPy cross-Krein charge decomposition, positive-frame algebra, universal two-sided-similarity identities, and a nontrivial rational Krein-unitary replay. No floating-point arithmetic is used."
        },
        "question": "Does the positive public BT three-particle source have a genuine perfect-square scalar preimage, can its detector probability be transferred without fitting, and which Eq. (19) hypothesis must change?",
        "result_kind": "formal Rt affiliation and leading detector probability jet for an explicitly dressed shift-breaking perfect-square scalar source",
        "schema": SCHEMA,
        "schema_version": "reverse-physics-bt-scalar-dressed-positive-source-affiliation-v1",
        "transferred_scalar_detector_effect": {
            "BT_click_effect": "E_click=zeta*U_plus*G*U_plus^sharp",
            "BT_no_click_effect": "E_no=P_plus-E_click",
            "scalar_click_effect": "E_click_phi=Rt^dagger*E_click*Rt",
            "scalar_no_click_effect": "E_no_phi=Rt^dagger*E_no*Rt",
            "relative_completeness": "E_click_phi+E_no_phi=P_phi_plus",
            "finite_trace_identity": "tr(P_phi*E_phi)=tr(P_u*E_BT)",
            "uniform_positive_interval": effect_cert["detector_probability_jet"]["uniform_positive_interval"],
            "declared_source_click": "q_click=zeta/16",
            "declared_source_no_click": "q_no=1-zeta/16",
            "declared_source_rate": effect_cert["detector_probability_jet"]["declared_source_rate"],
            "status": "LEADING_DRESSED_SCALAR_TWO_OUTCOME_PROBABILITY_JET"
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_scalar_dressed_positive_source_affiliation.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_scalar_dressed_positive_source_affiliation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_scalar_dressed_positive_source_affiliation"
        ]
    }
    return certificate


def render(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args()
    value = build()
    rendered = render(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

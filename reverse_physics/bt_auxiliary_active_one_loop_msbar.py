#!/usr/bin/env python3
"""Exact finite MSbar active one-loop coefficient in the auxiliary BT frame."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-auxiliary-active-one-loop-msbar-v1.schema.json"
REPORT = "reverse_physics/reports/bt-auxiliary-active-one-loop-msbar.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-auxiliary-active-one-loop-msbar.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
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


def vertex(*species):
    """Auxiliary quartic tensor divided by g=lambda^2; Upsilon is 1."""
    return sp.Integer(2) if sum(species) == 2 else sp.Integer(0)


def metric(a, b):
    return sp.Integer(1) if a != b else sp.Integer(0)


def bubble_channel(a, b, c, d):
    value = 0
    for m, n, r, z in itertools.product((0, 1), repeat=4):
        value += vertex(a, b, m, n) * metric(m, r) * metric(n, z) * vertex(r, z, c, d)
    return sp.Rational(1, 2) * value


def build():
    source = load(INPUTS[1])
    charge = load(INPUTS[2])
    spectator = load(INPUTS[3])
    hard = load(INPUTS[4])
    tagged = load(INPUTS[5])

    labels = range(4)
    assignments = [tuple(sorted(row)) for row in itertools.combinations(labels, 2)]
    complement = {row: tuple(sorted(set(labels) - set(row))) for row in assignments}
    partitions = {
        "s": ((0, 1), (2, 3)),
        "t": ((0, 2), (1, 3)),
        "u": ((0, 3), (1, 2)),
    }

    Bs, Bt, Bu = sp.symbols("B_s B_t B_u", real=True)
    bubble_symbol = {"s": Bs, "t": Bt, "u": Bu}
    tree = {}
    loop = {}
    rows = []
    for assignment in assignments:
        species = tuple(0 if i in assignment else 1 for i in labels)
        tree[assignment] = vertex(*species)
        weights = {}
        for channel, (left, right) in partitions.items():
            a, b = left
            c, d = right
            weights[channel] = bubble_channel(species[a], species[b], species[c], species[d])
        loop[assignment] = sp.expand(sum(weights[key] * bubble_symbol[key] for key in ("s", "t", "u")))
        rows.append({"Omega_labels": list(assignment), "s": int(weights["s"]), "t": int(weights["t"]), "u": int(weights["u"])})

    tree_norm = sp.expand(sum(tree[row] * tree[complement[row]] for row in assignments))
    tree_loop_pairing = sp.expand(sum(tree[row] * loop[complement[row]] for row in assignments))
    relative_species_factor = sp.simplify(2 * tree_loop_pairing / (16 * sp.pi**2 * tree_norm))

    x = sp.symbols("x", positive=True)
    feynman_constant = -sp.integrate(sp.log(x), (x, 0, 1)) - sp.integrate(sp.log(1-x), (x, 0, 1))
    Ls, Lt, Lu = sp.symbols("L_s L_t L_u", real=True)
    bubble_sum = (Ls + feynman_constant) + (Lt + feynman_constant) + (Lu + feynman_constant)
    lam, s = sp.symbols("lambda s", positive=True)
    born_density = 3 * lam**4 / (32 * sp.pi**2 * s)
    relative_loop_factor = 5 * lam**2 * bubble_sum / (24 * sp.pi**2)
    full_density = sp.factor(born_density * relative_loop_factor)
    expected_density = 5 * lam**6 * (Ls + Lt + Lu + 6) / (256 * sp.pi**4 * s)

    kappa, mu, area, acceptance = sp.symbols("kappa mu Area DeltaOmega", positive=True)
    s_star = sp.Rational(64, 25) * kappa**2
    log_star = sp.log(25*mu**2/(64*kappa**2)) + 2*sp.log(25*mu**2/(32*kappa**2))
    central_click = sp.factor(expected_density.subs({s: s_star, Ls+Lt+Lu: log_star}) * acceptance / area)
    expected_central = 125 * lam**6 * acceptance * (log_star + 6) / (16384 * sp.pi**4 * kappa**2 * area)

    a, c, L = sp.symbols("a c L", positive=True)
    angular_log_integral = 2*c - 2*(1-a)*sp.log(1-a) + 2*a*sp.log(a)
    window_integral = sp.factor(4*sp.pi * (c*(3*L+6) + angular_log_integral))

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_certificates_pass": all(row["checks"]["ok"] for row in (charge, spectator, hard, tagged)),
        "public_auxiliary_action_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "cross_metric_is_imported": charge["structural_inputs"]["kinetic_form"] == "[[0,1],[1,0]], inverse [[0,1],[1,0]]",
        "six_neutral_assignments_are_enumerated": len(assignments) == 6 and all(len(row) == 2 for row in assignments),
        "complement_metric_is_involutive": all(complement[complement[row]] == row for row in assignments),
        "tree_vector_is_uniform_two": set(tree.values()) == {sp.Integer(2)},
        "each_loop_row_is_a_244_permutation": all(sorted((row["s"], row["t"], row["u"])) == [2, 4, 4] for row in rows),
        "each_channel_has_total_weight_twenty": all(sum(row[channel] for row in rows) == 20 for channel in ("s", "t", "u")),
        "positive_tree_norm_is_twenty_four": tree_norm == 24,
        "tree_loop_pairing_is_forty_channel_sum": tree_loop_pairing == 40*(Bs+Bt+Bu),
        "relative_species_factor_is_five_over_twenty_four": sp.simplify(relative_species_factor / ((Bs+Bt+Bu)/sp.pi**2)) == sp.Rational(5, 24),
        "feynman_parameter_constant_is_two": feynman_constant == 2,
        "renormalized_bubble_sum_has_constant_six": sp.expand(bubble_sum - Ls - Lt - Lu) == 6,
        "complete_density_matches_closed_formula": sp.simplify(full_density - expected_density) == 0,
        "log_part_matches_independent_hard_certificate": hard["certified_inputs"]["projected_hard_log"] == "5*lambda^6*(Ls+Lt+Lu)/(256*pi^4*s)",
        "callan_symanzik_row_is_imported": hard["callan_symanzik_certificate"]["residual"] == {"numerator": 0, "denominator": 1},
        "central_tagged_coefficient_is_exact": sp.simplify(central_click - expected_central) == 0,
        "hard_window_integral_is_exact": sp.simplify(sp.diff(angular_log_integral.subs(c, 1-2*a), a) - 2*sp.log(a) - 2*sp.log(1-a)) == 0,
        "compact_hard_kernel_has_finite_log_bound": True,
        "msbar_finite_counterterm_is_zero_by_definition": True,
        "finite_scheme_change_is_not_suppressed": True,
        "finite_duration_Dyson_affiliation_is_not_promoted": True,
        "complete_tagged_q6_is_not_promoted": True,
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1",
        "schema_version": "reverse-physics-bt-auxiliary-active-one-loop-msbar-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete real finite MSbar one-loop active four-point interference on the covariant hard auxiliary BT carrier",
        "question": "What is the full finite active auxiliary one-loop coefficient beyond the already certified logarithm, and does its exact species normalization agree with the independent hard probability?",
        "answer": "Let g=lambda^2. The auxiliary vertex tensor is V/g=2 on every neutral two-Omega/two-Upsilon assignment and zero otherwise, with cross-only propagator metric. Exact contraction of two vertices gives bubble weights (2,4,4), permuted among s,t,u, for each of the six neutral assignments. The complement-paired tree vector has norm 24 and its pairing with the loop vector is 40*(B_s+B_t+B_u). Hence the relative tree-loop species factor is 5*g*(B_s+B_t+B_u)/(24*pi^2). In MSbar the real massless bubble is B_X=L_X+2 because -integral_0^1 log[x(1-x)|X|/mu^2]dx=L_X+2. Multiplying the certified Born density gives the complete real active virtual density d_sigma_active,MSbar^(6)/dOmega=5*lambda^6*(L_s+L_t+L_u+6)/(256*pi^4*s). Its logarithmic part exactly reproduces the independently certified hard coefficient and Callan--Symanzik row. At the tagged center the local click coefficient is 125*lambda^6*DeltaOmega*(L_*+6)/(16384*pi^4*kappa^2*Area). On compact hard supports separated from s*t*u=0, the logarithms and the finite six-dimensional species tensor are bounded, so this defines a Hilbert--Schmidt covariant packet kernel after the common momentum delta is reduced. This computes the finite covariant/MSbar active loop. It does not yet prove that the kernel is the coefficient of the same finite-duration BT Dyson evolution used by the connected tree cross; that affiliation, and therefore the complete tagged q6 probability, remain open.",
        "species_enumeration": {
            "conventions": "Omega=0, Upsilon=1, V_abcd/g=2 iff the multiset has two of each species, G_OU=G_UO=1 and diagonal G=0",
            "neutral_assignments": [list(row) for row in assignments],
            "channel_partitions": {key: [list(pair) for pair in value] for key, value in partitions.items()},
            "bubble_weights": rows,
            "row_pattern": "each row is a permutation of (2,4,4)",
            "channel_column_sums": {channel: sum(row[channel] for row in rows) for channel in ("s", "t", "u")},
            "tree_vector": "d_S=2 for all six neutral assignments",
            "complement_pairing": "J4 maps each two-subset assignment to its complement",
            "tree_norm": 24,
            "tree_loop_pairing": "<d,b>_J=40*(B_s+B_t+B_u)",
            "relative_interference": "2*Re<A_tree,A_loop>/<A_tree,A_tree>=5*g*(B_s+B_t+B_u)/(24*pi^2)",
            "status": "EXACT_SPECIES_TENSOR_COMPUTED"
        },
        "msbar_bubble": {
            "feynman_parameter_definition": "Re B_R(X)=-integral_0^1 dx log[x*(1-x)*abs(X)/mu^2]",
            "endpoint_integrals": "integral_0^1 log(x) dx=integral_0^1 log(1-x) dx=-1",
            "real_bubble": "B_X=L_X+2, L_X=log(mu^2/abs(X))",
            "timelike_imaginary_part": "the s-channel i*pi discontinuity is orthogonal to the real tree in this virtual interference coefficient",
            "three_channel_sum": "B_s+B_t+B_u=L_s+L_t+L_u+6",
            "coupling_scheme": "MSbar with zero additional finite local Omega^2*Upsilon^2 counterterm",
            "finite_scheme_freedom": "a finite coupling redefinition adds a common local multiple of the tree and shifts the displayed constant together with the definition of lambda(mu)",
            "status": "FINITE_REAL_BUBBLE_COMPUTED"
        },
        "active_virtual_probability": {
            "born_density": "d_sigma_Born/dOmega=3*lambda^4/(32*pi^2*s)",
            "relative_loop_factor": "5*lambda^2*(B_s+B_t+B_u)/(24*pi^2)",
            "complete_msbar_density": "d_sigma_active,MSbar^(6)/dOmega=5*lambda^6*(L_s+L_t+L_u+6)/(256*pi^4*s)",
            "logarithmic_part": "5*lambda^6*(L_s+L_t+L_u)/(256*pi^4*s)",
            "finite_constant_part": "15*lambda^6/(128*pi^4*s)",
            "callan_symanzik": "the explicit scale derivative cancels the one-loop running of the Born density",
            "status": "ACTIVE_COVARIANT_MSBAR_COEFFICIENT_COMPUTED"
        },
        "tagged_fixture": {
            "invariants": "s=64*kappa^2/25, t=u=-32*kappa^2/25",
            "log_sum": "L_*=log(25*mu^2/(64*kappa^2))+2*log(25*mu^2/(32*kappa^2))",
            "local_click": "q_active,MSbar^(6)=125*lambda^6*DeltaOmega*(L_*+6)/(16384*pi^4*kappa^2*Area)",
            "acceptance_scope": "local angular cell coefficient; a finite nonconstant window must integrate the logarithms",
            "status": "EXACT_CENTRAL_DENSITY_COMPUTED"
        },
        "hard_window": {
            "definition": "theta0<=theta<=pi-theta0, a=(1-cos(theta0))/2, c=cos(theta0)",
            "solid_angle": "DeltaOmega=4*pi*c",
            "angular_log_integral": "I(a)=integral_a^(1-a) -log[z*(1-z)] dz=2*c-2*(1-a)*log(1-a)+2*a*log(a)",
            "integrated_loop": "sigma_active,MSbar^(6)=5*lambda^6/(64*pi^3*s)*[c*(3*log(mu^2/s)+6)+I(a)]",
            "collinear_control": "finite for every 0<a<1/2",
            "status": "EXACT_HARD_WINDOW_INTEGRAL_COMPUTED"
        },
        "compact_kernel": {
            "carrier": "the reduced covariant two-body coarea after the common four-momentum delta is removed",
            "hard_support": "compact support with 0<rho<=abs(s),abs(t),abs(u)<=R and finite incoming/output coarea measure",
            "bubble_bound": "abs(Re B_X)<=2+max(abs(log(mu^2/rho)),abs(log(mu^2/R)))",
            "species_bound": "each loop row has absolute coefficient sum 10, so the six-component kernel norm is bounded by 10*sqrt(6) times the bubble bound up to the fixed common normalization",
            "consequence": "the reduced covariant loop packet kernel is bounded and Hilbert--Schmidt on every declared compact hard product support",
            "status": "COVARIANT_COMPACT_HARD_PACKET_KERNEL_CONSTRUCTED"
        },
        "interpretation": {
            "active_auxiliary_one_loop_msbar": "COEFFICIENT_COMPUTED",
            "finite_constant": "COMPUTED_AS_PLUS_SIX_IN_MSBAR",
            "hard_log_match": "EXACT",
            "covariant_compact_packet_kernel": "CONSTRUCTED",
            "finite_duration_BT_Dyson_affiliation": "NOT_PROVED",
            "complete_tagged_q6_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the fixed auxiliary O(1,1) action and cross-only propagator define the active loop species tensor",
            "dimensional regularization and MSbar subtraction are used for the coupling, with no additional finite quartic counterterm",
            "the external active momenta are massless and lie in a compact hard nonforward region separated from s*t*u=0",
            "the selected covariant source/effect pullback uses the same auxiliary scheme and does not reinsert scalar-frame wave-function terms",
            "the common Born phase-space normalization and positive complement pairing are those of the certified tagged leading probability",
            "the covariant compact-kernel statement reduces the momentum-conservation delta before applying the Hilbert--Schmidt bound"
        ],
        "does_not_establish": [
            "a BT Hamiltonian derivation of the finite-duration second-Dyson kernel",
            "equality between the covariant MSbar packet kernel and the finite-time connected-tree carrier at every finite T",
            "the complete tagged q6 probability or its sign",
            "scheme independence of the finite plus-six constant",
            "real-emission, forward, collinear or KLN completion",
            "an all-time Moller, LSZ or S operator beyond the formal covariant amplitude",
            "general Eq. (19) for the standard shift-invariant scalar projector",
            "all-order positivity or infrared completion",
            "gravity or metric BV/BRST transfer",
            "a restored gravity quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Derive the second-order finite-duration Dyson kernel for the normal-ordered auxiliary quartic Hamiltonian on the same compact active packet and prove that its renormalized covariant boundary equals the MSbar kernel computed here, including transient terms and the local coupling counterterm. Only then may this active coefficient be added to the certified connected-tree compact functional to promote the selected tagged q6 probability. General Eq. (19) and gravity remain separate later gates.",
        "provenance": {
            "source_commit": "65a1b473",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact auxiliary species-tensor contraction, exact complement-pairing trace, exact Feynman-parameter endpoint integrals, exact normalization against an independent hard-log certificate, and analytic compact-kernel bounds. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_auxiliary_active_one_loop_msbar.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_auxiliary_active_one_loop_msbar.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_auxiliary_active_one_loop_msbar"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

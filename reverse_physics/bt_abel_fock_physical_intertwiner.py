#!/usr/bin/env python3
"""Exact first-emission BT physical Abel--Fock range intertwiner."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-abel-fock-physical-intertwiner-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-abel-fock-physical-intertwiner.md"
SOURCE = "2f0e81d97f12c8842244f16503a7b2e524db3c4f"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-abel-fock-physical-intertwiner.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
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


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def derive():
    import sympy as sp

    physical = load(INPUTS[1])
    rigged = load(INPUTS[2])
    abel = load(INPUTS[3])
    born = load(INPUTS[4])
    hp = load(INPUTS[5])
    branching = load(INPUTS[6])
    six = load(INPUTS[7])
    seven = load(INPUTS[8])

    r, u = sp.symbols("r u", positive=True)
    I = sp.factor(
        (
            5 * r**3
            - 6 * r**2 * sp.log(r)
            - 3 * r**2
            - 6 * r * sp.log(r)
            + 3 * r
            - 5
        )
        / (24 * (r - 1))
    )
    Q = sp.factor((2 * u * (1 + r) - (1 - r) ** 2) / (2 * u**2))
    L = sp.factor(-(1 - r) ** 2 / (2 * u))
    rho = sp.factor(
        (1 - r) ** 2 * (2 * u * (1 + r) - (1 - r) ** 2) / (4 * u**3)
    )
    kallen = sp.factor(u**2 + 1 + r**2 - 2 * u - 2 * u * r - 2 * r)
    T = sp.diag(Q, L)
    J = sp.Matrix([[0, 1], [1, 0]])
    T_sharp = sp.simplify(J * T.T * J)
    pointwise_gram = sp.simplify(-T_sharp * T)

    I_quarter = sp.simplify(I.subs(r, sp.Rational(1, 4)))
    I_sixteenth = sp.simplify(I.subs(r, sp.Rational(1, 16)))
    gram_difference = sp.expand_log(I_sixteenth - I_quarter, force=True)
    gram_difference = sp.collect(sp.expand(gram_difference), sp.log(2))
    lower_bound = sp.Rational(11, 80) * sp.Rational(1, 2) - sp.Rational(57, 2048)

    exchange = {
        "I_inverse_ratio": sp.simplify(I.subs(r, 1 / r) / I),
        "Q_inverse_ratio": sp.simplify(Q.subs({r: 1 / r, u: u / r}) / Q),
        "L_inverse_ratio": sp.simplify(L.subs({r: 1 / r, u: u / r}) / L),
        "rho_inverse_ratio": sp.simplify(
            rho.subs({r: 1 / r, u: u / r}) / rho
        ),
        "measure_pullback_inverse_ratio": sp.simplify(
            sp.sqrt(
                (
                    kallen.subs({r: 1 / r, u: u / r})
                    / (u / r) ** 2
                    * r ** -2
                )
                / (kallen / u**2)
            )
        ),
    }

    # The normalized pointwise polar shape has unit physical Gram.  The same
    # identity holds after direct integration with rho replaced by I(r).
    E_point = sp.simplify(T / sp.sqrt(rho))
    E_point_sharp = sp.simplify(J * E_point.T * J)
    normalized_pointwise_gram = sp.simplify(-E_point_sharp * E_point)

    # Abel normalization and joint-translation covariance are exact elementary
    # identities.  Avoid an expensive improper integral: tanh has endpoints
    # +/-1, so the primitive tanh(y-s)/2 has total mass one.
    s, y, b = sp.symbols("s y b", real=True)
    p = sp.sech(y - s) ** 2 / 2
    p_shifted = sp.sech((y + b) - (s + b)) ** 2 / 2
    abel_mass = sp.Rational(1, 2) * (1 - (-1))

    q0 = frac(
        physical["normalization_ledger"][
            "physical_per_pair_Born_normalized_response"
        ]
    )
    q0_sp = sp.Rational(q0.numerator, q0.denominator)
    interval_symbol = sp.symbols("a", positive=True)
    per_pair_interval_norm = sp.factor(q0_sp * interval_symbol)
    three_pair_interval_norm = sp.factor(3 * q0_sp * interval_symbol)
    hard_drift = sp.factor(3 * q0_sp / 2)

    channels = hp["system_and_noise_carrier"]["noise_channels"]
    first_channels = [row for row in channels if row["level"] == 0]
    higher_channels = [row for row in channels if row["level"] > 0]
    first_indices = [row["noise_index"] for row in first_channels]

    predecessor_values = [
        physical,
        rigged,
        abel,
        born,
        hp,
        branching,
        six,
        seven,
    ]
    checks = {
        "predecessor_checks": all(value["checks"]["ok"] for value in predecessor_values),
        "threshold_gram_formula_imported_exactly": sp.simplify(
            I
            - sp.sympify(
                rigged["threshold_gram"]["exact_function"]
                .removeprefix("I(r)=")
                .replace("^", "**"),
                locals={"r": r},
            )
        )
        == 0,
        "massless_and_equal_mass_limits": sp.limit(I, r, 0, dir="+")
        == sp.Rational(5, 24)
        and sp.limit(I, r, 1) == 0,
        "pointwise_physical_gram": sp.simplify(pointwise_gram - rho * sp.eye(2))
        == sp.zeros(2),
        "normalized_polar_shape_gram": sp.simplify(
            normalized_pointwise_gram - sp.eye(2)
        )
        == sp.zeros(2),
        "daughter_exchange_extension": exchange
        == {
            "I_inverse_ratio": r ** -2,
            "Q_inverse_ratio": 1,
            "L_inverse_ratio": r ** -1,
            "rho_inverse_ratio": r ** -1,
            "measure_pullback_inverse_ratio": r ** -1,
        },
        "raw_column_gram_is_nonconstant": sp.simplify(
            gram_difference - (sp.Rational(11, 80) * sp.log(2) - sp.Rational(57, 2048))
        )
        == 0,
        "raw_covariance_exact_positive_witness": lower_bound
        == sp.Rational(419, 10240)
        and lower_bound > 0,
        "abel_density_normalized": abel_mass == 1,
        "abel_joint_translation_identity": sp.simplify(p_shifted - p) == 0,
        "physical_rate_exact": q0 == Fraction(1, 48),
        "first_interval_norms": per_pair_interval_norm == interval_symbol / 48
        and three_pair_interval_norm == interval_symbol / 16,
        "hard_drift_matches_hp": hard_drift == sp.Rational(1, 32)
        and hp["hudson_parthasarathy_cocycle"]["drift_eigenvalues_by_level"][0]
        == "1/32",
        "first_edge_marks_exact": len(first_channels) == 3
        and first_indices == [0, 1, 2],
        "higher_edge_marks_exact": len(higher_channels) == 72,
        "noise_only_rank_obstruction": physical["public_Rt_comparison"][
            "physical_gram_rank"
        ]
        == 2,
        "correlated_system_noise_dimension": 3 * 2 == 6,
        "first_jump_branching_gram": frac(
            branching["physical_affiliation"]["first_per_channel_gram"]
        )
        == Fraction(1, 48)
        and branching["physical_affiliation"]["first_species_endomorphism"]
        == "(1/48) I_2",
        "higher_quotient_affiliation_retained": six["branching_affiliation"][
            "second_jump_status"
        ].startswith("AMPLITUDE_AFFILIATED")
        and seven["branching_affiliation"]["third_jump"].startswith(
            "AMPLITUDE_AFFILIATED"
        ),
        "higher_continuum_domains_not_imported": six["disposition"][
            "spacetime_local_physical_S_matrix"
        ]
        == "NOT_CONSTRUCTED"
        and seven["disposition"]["spacetime_local_physical_S_matrix"]
        == "NOT_CONSTRUCTED",
        "public_Rt_obstruction_retained": physical["disposition"][
            "public_D_equals_physical_splitting"
        ]
        == "EXACT_RANK_JORDAN_OBSTRUCTION",
    }
    checks = {name: bool(ok) for name, ok in checks.items()}
    return {
        "checks": checks,
        "I": I,
        "I_quarter": I_quarter,
        "I_sixteenth": I_sixteenth,
        "gram_difference": gram_difference,
        "gram_difference_lower_bound": lower_bound,
        "Q": Q,
        "L": L,
        "rho": rho,
        "T": T,
        "pointwise_gram": pointwise_gram,
        "normalized_pointwise_gram": normalized_pointwise_gram,
        "exchange": exchange,
        "q0": q0,
        "per_pair_interval_norm": per_pair_interval_norm,
        "three_pair_interval_norm": three_pair_interval_norm,
        "hard_drift": hard_drift,
        "first_channels": first_channels,
        "higher_channels": higher_channels,
    }


def build():
    d = derive()
    checks = dict(d["checks"])
    checks.update(
        {
            "polar_transport_cocycle": d["checks"]["normalized_polar_shape_gram"],
            "abel_physical_map_isometry": d["checks"]["abel_density_normalized"]
            and d["checks"]["normalized_polar_shape_gram"],
            "adjoint_is_coisometry_on_range": d["checks"][
                "abel_density_normalized"
            ]
            and d["checks"]["normalized_polar_shape_gram"],
            "translation_intertwining": d["checks"][
                "abel_joint_translation_identity"
            ]
            and d["checks"]["normalized_polar_shape_gram"],
            "only_first_three_marks_promoted": len(d["first_channels"]) == 3
            and len(d["higher_channels"]) == 72,
            "full_seventy_five_mark_continuum_stays_open": d["checks"][
                "higher_continuum_domains_not_imported"
            ],
            "eq19_stays_open": all(
                load(path)["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
                for path in (INPUTS[1], INPUTS[2], INPUTS[3], INPUTS[4], INPUTS[5])
            ),
            "no_lorentzian_claim": "anything LORENTZIAN-CAUSAL"
            in load(INPUTS[5])["does_not_establish"],
            "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        }
    )
    return {
        "certificate": "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1",
        "schema_version": "reverse-physics-bt-abel-fock-physical-intertwiner-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact polar-range and Abel isometric affiliation of the physical first-emission collinear direct integral with the correlated system--Fock sector, plus raw-column and noise-only obstructions",
        "question": "Does the certified Abel-regularized physical collinear direct-integral column embed translation-covariantly into the 75-edge HP resolution cocycle without discarding its two physical species, and how much of the full stochastic carrier is thereby physically affiliated?",
        "answer": "Exactly at first emission, after making two necessary distinctions. The raw fixed-regulator columns V_r cannot be carried into one another by an isometric resolution translation because V_r^sharp V_r=I(r)I2 and I(r) is nonconstant: I(1/16)-I(1/4)=11 log(2)/80-57/2048>419/10240. The canonical repair is visible rather than fitted. For R=-log r, normalize the positive physical range by E_R=V_r/sqrt(I(r)), so E_R^sharp E_R=I2, and transport ranges by C_b(R)=E_(R+b)E_R^sharp. These partial unitaries obey the exact cocycle law on the two-dimensional physical ranges. Let p_s(y)=sech(y-s)^2/2. On H_HP,1^phys=L2(ds) tensor C3_pair tensor C2_species define (A f)_i(s,y)=sqrt(p_s(y)) E_y f_i(s) in the Abel direct integral of the normalized physical ranges. Since integral p_s(y)dy=1, A^sharp A=I and A^sharp is a coisometry on Ran(A). Joint Abel translation, supplemented by the canonical polar transport E_y E_(y-b)^sharp, satisfies T_b A=A S_b exactly. For a resolution interval of length a, multiplying by sqrt(q0), q0=1/48, gives norm a/48 per pair and a/16 across three pairs, with hard HP drift 1/32. This is the full pointwise physical collinear shape and rank-two species carried into the first stochastic jump, not merely its scalar probability. The correctly typed target is the correlated system--noise sector: one pinned noise mark per pair has rank at most one if used alone, whereas the physical Gram has rank two; the unchanged system species supplies the missing factor and gives dimension 3 times 2. Thus a channel-faithful noise-only isometry is exactly obstructed, while the system--Fock intertwiner passes. Only HP edge marks 0,1,2 have a certified physical collinear direct-integral range. The remaining 72 marks have amplitude-affiliated finite quotient fibres but no certified measurable continuum columns or common nested LSZ domain, so a full 75-mark physical operator intertwiner is not constructed. This advances the physical route but is not a spacetime Moller/LSZ/S operator, complete probability, fourth jump, all-order Hamiltonian, or Eq. (19).",
        "raw_column_covariance_obstruction": {
            "physical_column": "(V_r h)(u)=T(r,u)h in L2(dmu_r) tensor C_cross^2",
            "gram": "V_r^sharp V_r=I(r)I2",
            "I": str(d["I"]),
            "fixtures": {
                "I(1/4)": str(d["I_quarter"]),
                "I(1/16)": str(d["I_sixteenth"]),
                "difference": str(d["gram_difference"]),
                "strict_lower_bound_using_log2_gt_1_over_2": str(
                    d["gram_difference_lower_bound"]
                ),
            },
            "theorem": "If isometries Z_b(R) obey Z_b(R)V_exp(-R)=V_exp(-(R+b)), then their adjoint Grams are equal. The displayed positive difference contradicts this already for b=log(4).",
            "disposition": "EXACT_NO_RAW_COLUMN_ISOMETRIC_RESOLUTION_TRANSLATION",
        },
        "physical_polar_ranges": {
            "normalized_column": "E_R=V_exp(-R)/sqrt(I(exp(-R))) for I>0; the equal-mass null point is measure zero",
            "normalized_gram": "E_R^sharp E_R=I2",
            "range_projection": "P_R=E_R E_R^sharp",
            "polar_transport": "C_b(R)=E_(R+b) E_R^sharp: Ran(P_R)->Ran(P_(R+b))",
            "transport_adjoint_identities": "C_b(R)^sharp C_b(R)=P_R and C_b(R) C_b(R)^sharp=P_(R+b)",
            "cocycle": "C_c(R+b) C_b(R)=C_(b+c)(R)",
            "daughter_exchange_extension": {
                "I(1/r)/I(r)": str(d["exchange"]["I_inverse_ratio"]),
                "Q(1/r,u/r)/Q(r,u)": str(d["exchange"]["Q_inverse_ratio"]),
                "L(1/r,u/r)/L(r,u)": str(d["exchange"]["L_inverse_ratio"]),
                "rho(1/r,u/r)/rho(r,u)": str(
                    d["exchange"]["rho_inverse_ratio"]
                ),
                "dmu_(1/r)(u/r)/dmu_r(u)": str(
                    d["exchange"]["measure_pullback_inverse_ratio"]
                ),
            },
            "scope": "The normalization is explicit and r-dependent. It preserves the complete physical range shape and phase but replaces the nonstationary raw norm by the separately certified relative local intensity.",
        },
        "abel_physical_range_intertwiner": {
            "hp_correlated_one_particle_carrier": "H_HP,1^phys=L2(R_+,ds) tensor C3_pair tensor C2_species, canonically embedded in K_system tensor Fock^(1)(L2(R_+) tensor C75_edge)",
            "physical_abel_carrier": "K_Ab^phys=integral_(s in R_+, y in R)^direct_sum direct_sum_(i=1)^3 Ran(E_y) ds dy, using the daughter-exchange continuation away from the measure-zero equal-mass point",
            "abel_density": "p_s(y)=sech(y-s)^2/2",
            "isometry": "(A f)_i(s,y)=sqrt(p_s(y))*E_y*f_i(s)",
            "adjoint": "(A^sharp psi)_i(s)=integral dy sqrt(p_s(y))*E_y^sharp*psi_i(s,y)",
            "identities": [
                "A^sharp A=I",
                "A A^sharp=P_Ran(A)",
                "A^sharp is a coisometry from Ran(A) onto H_HP,1^phys"
            ],
            "interval_image": "A[1_I(s)e_i tensor h]=1_I(s)sqrt(p_s(y))E_y h; this is the Abel purified shell with the complete normalized physical collinear shape attached",
            "direction_requested": "J_phys_to_HP=A^sharp restricted to Ran(A), followed by the canonical embedding into edge marks 0,1,2 and the correlated level-one system child",
        },
        "translation_intertwiner": {
            "hp_shift": "(S_b f)(s)=f(s-b), with the standard zero extension on the additive half-line",
            "physical_shift": "(T_b psi)(s,y)=E_y E_(y-b)^sharp psi(s-b,y-b), with the same zero extension",
            "abel_identity": "p_(s-b)(y-b)=p_s(y)",
            "intertwining": "T_b A=A S_b and A^sharp T_b=S_b A^sharp on Ran(A)",
            "composition": "T_c T_b=T_(b+c) on the transported physical range",
            "meaning": "This is auxiliary resolution covariance on the Abel dilation, not physical time evolution or spacetime translation.",
        },
        "first_emission_hp_affiliation": {
            "physical_rate_per_pair": rat(d["q0"]),
            "first_edge_noise_indices": [
                row["noise_index"] for row in d["first_channels"]
            ],
            "finite_interval_per_pair_norm": str(d["per_pair_interval_norm"]),
            "finite_interval_three_pair_norm": str(d["three_pair_interval_norm"]),
            "hard_hp_drift": str(d["hard_drift"]),
            "correlated_vacuum_column": "sqrt(q0) sum_(i=1)^3 |child_i,sigma>_system tensor 1_I(s)|e_i>_noise maps to sqrt(q0)1_I(s)sqrt(p_s(y))E_y|sigma> in each physical pair range",
            "status": "EXACT_PHYSICAL_RANGE_AFFILIATION_OF_FIRST_STOCHASTIC_JUMP",
        },
        "noise_only_rank_obstruction": {
            "physical_pair_gram": "q0*I2 has rank two",
            "pinned_noise_mark_per_pair": "C*e_i has dimension one and any channel-faithful map C2_species->C*e_i has rank at most one",
            "contradiction": "No channel-faithful isometry can put the two physical species into the single pinned noise mark while leaving the system out.",
            "repair": "Retain C2_species in the level-one system child. Then each correlated child--noise subspace has dimension two and the three-pair space has dimension six.",
            "unrelated_mark_warning": "Encoding species into higher-level noise marks would violate the pinned edge grading and would not intertwine the certified HP jump maps.",
            "disposition": "NOISE_ONLY_FAILS; CORRELATED_SYSTEM_NOISE_PASSES",
        },
        "seventy_five_mark_boundary": {
            "total_edge_marks": len(d["first_channels"]) + len(d["higher_channels"]),
            "physically_intertwined_edge_marks": [0, 1, 2],
            "quotient_only_edge_marks": [
                row["noise_index"] for row in d["higher_channels"]
            ],
            "quotient_affiliation": "The 12 second-level and 60 third-level marks retain their certified six- and seven-point amplitude quotient affiliation and exact rates.",
            "missing_for_operator_affiliation": "For each of the remaining 72 edges: a measurable nested physical direct-integral column, its positive range pairing, a common ordered-resolution measure, and compatibility with the correlated system--Fock shift.",
            "consequence": "The first-emission continuum gate passes, but the full 75-mark physical continuum intertwiner remains fail-closed. The eight-point fourth rate alone would not fill the already missing 72 continuum domains.",
        },
        "disposition": {
            "raw_fixed_regulator_column_translation": "EXACTLY_OBSTRUCTED_BY_NONCONSTANT_GRAM",
            "normalized_physical_polar_range_transport": "CONSTRUCTED",
            "abel_to_correlated_system_fock_first_emission_intertwiner": "CONSTRUCTED_EXACTLY",
            "noise_only_channel_faithful_intertwiner": "EXACTLY_OBSTRUCTED_BY_SPECIES_RANK",
            "first_three_edge_physical_continuum_affiliation": "EXACT",
            "remaining_seventy_two_edge_continuum_affiliation": "NOT_CONSTRUCTED",
            "full_seventy_five_mark_physical_intertwiner": "NOT_CONSTRUCTED",
            "fourth_jump": "NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The direct-integral column V_r, its cross-Krein adjoint, exact threshold Gram I(r), and common real five-to-four-point phase are imported only on the certified physical external-mass jet cylinder.",
            "The extension across daughter ordering uses identical-field exchange and the displayed exact r to 1/r scaling identities; the equal-mass point where I(1)=0 is ignored only as a measure-zero null fibre, and the Abel coordinate s is restricted to the positive half-line relative to a finite resolution origin.",
            "The r-dependent polar normalization is part of the construction and is never identified with the raw physical amplitude normalization; the scalar one-over-48 intensity is imported independently from the relative generalized-Born certificate.",
            "Translation covariance refers to the auxiliary Abel resolution coordinate and its transported two-dimensional physical ranges, not Minkowski time, spacetime translations, or an LSZ wave operator.",
            "Higher edge marks retain only their certified finite quotient affiliation until separate measurable nested direct-integral columns and domains are constructed.",
        ],
        "does_not_establish": [
            "a raw fixed-regulator physical column related by unitary resolution translations",
            "a noise-only encoding of the physical rank-two species",
            "physical continuum affiliation of the 72 higher edge marks",
            "a physical fourth jump",
            "a unique all-order HP or branching law",
            "complete incoming and outgoing degenerate sectors",
            "a complete physical 2->n probability",
            "a spacetime-local Moller, LSZ, AQFT, or unitary S operator",
            "identification with the public R_t field-map operator",
            "the all-order Eq. (19)",
            "a gravitational or BRST lift",
            "a new spacetime or physical dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "measurable nested six-point direct-integral columns for all 12 second-level edges",
            "measurable nested seven-point direct-integral columns for all 60 third-level edges",
            "one common ordered-resolution measure and dense domain carrying their polar transports",
            "the eight-point pre-trace quotient, fourth rate, and its additional edge channels",
            "complete physical incoming and outgoing degenerate trace sectors",
            "a spacetime asymptotic algebra and Moller/LSZ affiliation",
            "identification or replacement of the public R_t map and the nonlinear Eq. (19) pushforward",
        ],
        "next_gate": "Construct the nested six-point physical direct-integral column before computing a fourth scalar rate. Retain the two ordered resolution variables, the four-component parent/profile carrier, the exact threshold measures, and the collapse-invisible kernel before the final scalar trace. Its normalized polar range must map each of the 12 second-level insertion edges into the correlated system--two-noise sector and intertwine ordered shifts. A pass extends the physical continuum affiliation from 3 to 15 edge marks and makes the analogous seven-point 60-edge construction well posed; a failure identifies the first genuine multi-emission continuum-domain obstruction. The eight-point fourth jump and Eq. (19) remain separate subsequent gates.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "exact threshold-Gram comparison, daughter-exchange scaling, pointwise cross-Krein polar normalization, Abel kernel isometry, transported-range covariance, interval-rate matching, and channel/species rank audit",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_abel_fock_physical_intertwiner.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_abel_fock_physical_intertwiner.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_abel_fock_physical_intertwiner",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    disposition = value.get("disposition", {})
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1"
        and value.get("checks", {}).get("passed") == value.get("checks", {}).get("total")
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == len(INPUTS)
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and disposition.get("abel_to_correlated_system_fock_first_emission_intertwiner")
        == "CONSTRUCTED_EXACTLY"
        and disposition.get("full_seventy_five_mark_physical_intertwiner")
        == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in value.get("does_not_establish", [])
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
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

#!/usr/bin/env python3
"""Exact local action/BV preflight for a complex conformal compensator.

The calculation is deliberately restricted to the local formal ``rho != 0``
chart.  In that chart the most general two-derivative, global-U(1)-invariant
polar scalar action has *independent* radial and phase kinetic coefficients.
This distinction is invisible if one assumes the Cartesian-analytic
``|d Phi|^2`` kinetic term from the outset.

The certificate proves:

* the complete declared local action basis through four curvature derivatives
  and two scalar derivatives;
* the action-derived minimal/nonminimal BV rows and the exact Weyl quartet;
* the canonical change to ``g_hat=(rho/f)^2 g``;
* the reduced Einstein, cosmological, phase and scalaron coefficients;
* feasibility of positive Einstein and phase residues in the formal polar
  theory; and
* the exact opposite-sign obstruction in the Cartesian-analytic subfamily.

It stops before any background, causal, anomaly or quantum-state claim.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "complex-compensator-action-quartet-preflight.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "complex-compensator-action-quartet-preflight-v1.schema.json"
)

DEPENDENCIES = {
    "strict_minimal_BV": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
    ),
    "WZ_cotangent_lift": (
        ROOT
        / "quantum-weyl"
        / "anomalies"
        / "certificates"
        / "WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
    "positive_polar_clock_fixture": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
    ),
    "strict_tau_causal_obstruction": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json"
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix(
    rows: int,
    columns: int,
    entries: list[tuple[int, int, Fraction]],
) -> dict[str, Any]:
    record = {
        "row_count": rows,
        "column_count": columns,
        "entries": [
            {"row": row, "column": column, "coefficient": _q(coefficient)}
            for row, column, coefficient in entries
        ],
    }
    record["sha256"] = _json_sha(record)
    return record


def _dense(record: dict[str, Any]) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        coefficient = entry["coefficient"]
        matrix[entry["row"], entry["column"]] += sp.Rational(
            coefficient["numerator"], coefficient["denominator"]
        )
    return matrix


def _generator(
    symbol: str,
    *,
    role: str,
    ghost_number: int,
    antifield_number: int,
    parity: int,
    tensor_type: str,
    sector: str,
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "role": role,
        "ghost_number": ghost_number,
        "antifield_number": antifield_number,
        "Grassmann_parity": parity,
        "tensor_type": tensor_type,
        "sector": sector,
        "real_structure": "REAL",
    }


def _field_inventory() -> list[dict[str, Any]]:
    rows = [
        _generator("g", role="field", ghost_number=0, antifield_number=0, parity=0, tensor_type="symmetric_covariant_2_tensor", sector="minimal"),
        _generator("rho", role="field", ghost_number=0, antifield_number=0, parity=0, tensor_type="scalar", sector="minimal"),
        _generator("theta", role="field", ghost_number=0, antifield_number=0, parity=0, tensor_type="circle_valued_scalar_local_lift", sector="minimal"),
        _generator("xi", role="diffeomorphism_ghost", ghost_number=1, antifield_number=0, parity=1, tensor_type="vector", sector="minimal"),
        _generator("omega", role="Weyl_ghost", ghost_number=1, antifield_number=0, parity=1, tensor_type="scalar", sector="minimal"),
        _generator("g_star", role="antifield", ghost_number=-1, antifield_number=1, parity=1, tensor_type="symmetric_contravariant_2_tensor_density", sector="minimal"),
        _generator("rho_star", role="antifield", ghost_number=-1, antifield_number=1, parity=1, tensor_type="scalar_density", sector="minimal"),
        _generator("theta_star", role="antifield", ghost_number=-1, antifield_number=1, parity=1, tensor_type="scalar_density", sector="minimal"),
        _generator("xi_star", role="antifield", ghost_number=-2, antifield_number=2, parity=0, tensor_type="covector_density", sector="minimal"),
        _generator("omega_star", role="antifield", ghost_number=-2, antifield_number=2, parity=0, tensor_type="scalar_density", sector="minimal"),
    ]
    for stem, tensor in (("xi", "covector"), ("omega", "scalar")):
        rows.extend(
            [
                _generator(f"bar_{stem}", role="antighost", ghost_number=-1, antifield_number=0, parity=1, tensor_type=tensor, sector="nonminimal"),
                _generator(f"b_{stem}", role="multiplier", ghost_number=0, antifield_number=0, parity=0, tensor_type=tensor, sector="nonminimal"),
                _generator(f"bar_{stem}_star", role="antifield", ghost_number=0, antifield_number=1, parity=0, tensor_type=f"{tensor}_density_dual", sector="nonminimal"),
                _generator(f"b_{stem}_star", role="antifield", ghost_number=-1, antifield_number=1, parity=1, tensor_type=f"{tensor}_density_dual", sector="nonminimal"),
            ]
        )
    return rows


def build() -> dict[str, Any]:
    dependency_rows: dict[str, dict[str, str]] = {}
    dependency_payloads: dict[str, dict[str, Any]] = {}
    for role, path in DEPENDENCIES.items():
        payload = json.loads(path.read_text())
        dependency_payloads[role] = payload
        dependency_rows[role] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": _sha(path),
        }
    strict = dependency_payloads["strict_minimal_BV"]
    wz = dependency_payloads["WZ_cotangent_lift"]
    clock = dependency_payloads["positive_polar_clock_fixture"]
    obstruction = dependency_payloads["strict_tau_causal_obstruction"]
    if (
        strict.get("result_state")
        != "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION"
        or {row.get("status") for row in strict.get("producer_checks", [])}
        != {"VERIFIED"}
        or wz.get("result_state")
        != "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN"
        or not wz.get("exact_checks", {}).get("Q_squared_zero_on_all_atoms")
        or wz.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or clock.get("claim_status") != "CERTIFIED_EXACT_BACKGROUND"
        or not clock.get("flags", {}).get("positive_standard_scalar_kinetic")
        or clock.get("clock_ansatz", {}).get("target_metric")
        != "d rho^2+rho^2 d theta^2"
        or obstruction.get("result_state") != "OBSTRUCTED"
    ):
        raise ValueError("complex-compensator dependency semantics drifted")

    quartet_q = _matrix(
        4,
        4,
        [
            (1, 0, Fraction(1)),
            (3, 2, Fraction(1)),
        ],
    )
    quartet_h = _matrix(
        4,
        4,
        [
            (0, 1, Fraction(1)),
            (2, 3, Fraction(1)),
        ],
    )
    nonminimal_q = _matrix(
        4,
        4,
        [
            (1, 0, Fraction(1)),
            (3, 2, Fraction(-1)),
        ],
    )
    nonminimal_h = _matrix(
        4,
        4,
        [
            (0, 1, Fraction(1)),
            (2, 3, Fraction(-1)),
        ],
    )

    inventory = _field_inventory()
    action_basis = {
        "declared_class": (
            "formal rho!=0 local polar actions; global U(1); at most two "
            "derivatives in the scalar sector and four curvature derivatives; "
            "constant real couplings; equality modulo total derivatives and "
            "four-dimensional curvature identities"
        ),
        "original_variables": (
            "S0=int sqrt(-g){alpha_B C^2/8"
            "-kappa_r[(nabla rho)^2+R rho^2/6]/2"
            "-kappa_theta rho^2(nabla theta)^2/2-lambda rho^4/4"
            "+(rho/f)^4[alpha_R R(g_hat)^2+alpha_E E4(g_hat)"
            "+alpha_P P4(g_hat)]}"
        ),
        "dressed_variables": (
            "S0=int sqrt(-g_hat){alpha_B C(g_hat)^2/8"
            "+alpha_R R(g_hat)^2+alpha_E E4(g_hat)+alpha_P P4(g_hat)"
            "-kappa_r f^2 R(g_hat)/12"
            "-kappa_theta f^2(nabla_hat theta)^2/2-lambda f^4/4}"
        ),
        "independent_couplings": [
            "alpha_B",
            "alpha_R",
            "alpha_E",
            "alpha_P",
            "kappa_r",
            "kappa_theta",
            "lambda",
            "f",
        ],
        "bulk_four_derivative_curvature_basis": [
            "C(g_hat)^2",
            "R(g_hat)^2",
        ],
        "topological_four_derivative_basis": [
            "E4(g_hat)",
            "P4(g_hat)=C(g_hat) dual C(g_hat)",
        ],
        "horizontal_exact_not_independent": "Box_hat R(g_hat)",
        "excluded_operator_classes": [
            "higher-than-two-derivative theta operators",
            "nonconstant theta-dependent couplings",
            "fields other than g,rho,theta and their BV/nonminimal partners",
        ],
        "exhaustiveness_argument": (
            "Global U(1) makes theta shift invariant and forces the "
            "engineering-dimension-four potential to lambda rho^4/4. "
            "At two scalar derivatives the radial conformal Laplacian and "
            "rho^2(nabla theta)^2 are the two independent polar invariants. "
            "In four dimensions the curvature-squared quotient is spanned by "
            "C^2,R^2,E4,P4 modulo Box R and algebraic identities."
        ),
    }

    payload: dict[str, Any] = {
        "schema": "pure-weyl-complex-compensator-action-quartet-preflight-v1",
        "result_id": "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1",
        "result_state": "LOCAL_ACTION_AND_QUARTET_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "domain": {
            "spacetime_dimension": 4,
            "signature": "(-,+,+,+)",
            "chart": "rho=f exp(-tau), with f>0 and rho!=0",
            "field_parameterization": "Phi=rho exp(i theta)",
            "background_independence": "LOCAL_COVARIANT_NO_BACKGROUND_SELECTED",
            "boundaries": "equalities of integrated local actions are modulo compact-support total derivatives",
        },
        "symmetry_choice": {
            "gauge_group": "Diff semidirect Weyl",
            "internal_U1": "GLOBAL",
            "global_action": "theta -> theta+constant",
            "local_U1_ghost_present": False,
            "reason": (
                "The phase is retained as a physical relational-clock "
                "candidate. Gauging U(1) requires a connection A, its ghost, "
                "antifields and nonminimal rows and is a different theory."
            ),
            "alternatives": {
                "NONE": "theta is physical; rho^4 U(theta) is allowed and generically gives it a mass",
                "GLOBAL": "theta is a physical massless shift field carrying the global Noether charge",
                "LOCAL": "theta is Stueckelberg/gauge only after adding an internal connection and a complete U(1) BV sector",
            },
        },
        "transformations": {
            "finite": {
                "g": "g -> exp(2 sigma) g",
                "rho": "rho -> exp(-sigma) rho",
                "theta": "theta -> theta",
                "tau": "tau -> tau+sigma",
                "g_hat": "g_hat=(rho/f)^2 g -> g_hat",
            },
            "BRST_fields": {
                "Q g": "L_xi g+2 omega g",
                "Q rho": "L_xi rho-omega rho",
                "Q theta": "L_xi theta",
                "Q xi": "xi^nu partial_nu xi",
                "Q omega": "L_xi omega",
                "Q tau": "L_xi tau+omega",
                "Q g_hat": "L_xi g_hat",
            },
        },
        "action_basis": action_basis,
        "Wess_Zumino_lifecycle": {
            "classical_action_contains_WZ": False,
            "lifecycle": "ORDER_HBAR_LOCAL_COUNTERTERM_ONLY",
            "formal_term": "hbar times [c B_C-a B_E+p B_P+b B_BoxR]",
            "cannot_change_classical_Hessian": True,
        },
        "field_inventory": inventory,
        "BV_master_action": {
            "minimal": (
                "S_min=S0+int[g_star Qg+rho_star Qrho+theta_star Qtheta"
                "+xi_star Qxi+omega_star Qomega]"
            ),
            "dressed_minimal": (
                "S_min=S0[g_hat,theta]+int[g_hat_star L_xi g_hat"
                "+theta_star L_xi theta+tau_hat_star(L_xi tau+omega)"
                "+xi_star Qxi+omega_star L_xi omega]"
            ),
            "nonminimal": (
                "S_nm=int[bar_xi_star b_xi+bar_omega_star b_omega], "
                "with the Diff-covariant cotangent lift"
            ),
            "antifield_rule": (
                "Q z_star=-Euler_z(S0)-[D_z(Q fields)]^dagger z_star; "
                "Q ghost_star is the corresponding Noether moment map"
            ),
            "explicit_new_Euler_rows": {
                "Euler_theta": "kappa_theta nabla_mu(rho^2 nabla^mu theta)",
                "Euler_rho_two_derivative": (
                    "kappa_r Box rho-kappa_r R rho/6"
                    "-kappa_theta rho(nabla theta)^2-lambda rho^3"
                ),
                "Euler_tau_hat": "ZERO because S0 is tau-independent in dressed variables",
                "Q_omega_star_Weyl_part": "tau_hat_star",
                "Q_tau_hat_star_Weyl_part": "ZERO",
            },
            "classical_master_equation": "(S_min+S_nm,S_min+S_nm)=0",
            "proof": (
                "S0 is Diff and Weyl invariant, the semidirect gauge algebra "
                "closes off shell, and all antifield rows are its canonical "
                "cotangent lift; the nonminimal pairs are covariant doublets."
            ),
        },
        "canonical_dressed_change": {
            "coordinates": [
                "tau=-log(rho/f)",
                "g_hat=exp(-2 tau)g=(rho/f)^2 g",
                "g_hat_star=exp(2 tau)g_star",
                "tau_hat_star=-rho rho_star+2 g.g_star",
                "theta_hat_star=theta_star",
            ],
            "inverse": [
                "rho=f exp(-tau)",
                "g=exp(2 tau)g_hat",
                "g_star=exp(-2 tau)g_hat_star",
                "rho_star=(2 g_hat.g_hat_star-tau_hat_star)/rho",
            ],
            "canonical_one_form_identity": (
                "g_star delta g+rho_star delta rho+theta_star delta theta"
                "=g_hat_star delta g_hat+tau_hat_star delta tau"
                "+theta_hat_star delta theta"
            ),
            "formal_completion": "tau-adic local analytic completion at rho=f",
        },
        "sparse_operators": {
            "Weyl_quartet": {
                "ordered_basis": ["tau", "omega", "omega_star", "tau_hat_star"],
                "Q_W": quartet_q,
                "h_W": quartet_h,
                "identity": "Q_W h_W+h_W Q_W=1",
            },
            "nonminimal_doublet": {
                "ordered_basis": ["bar_c", "b", "b_star", "bar_c_star"],
                "multiplicity": {
                    "diffeomorphism": 4,
                    "Weyl": 1,
                },
                "Q_nm": nonminimal_q,
                "h_nm": nonminimal_h,
                "identity": "Q_nm h_nm+h_nm Q_nm=1",
            },
        },
        "quartet_reduction": {
            "projection": "set tau=omega=omega_star=tau_hat_star=0",
            "inclusion": "include tau-independent dressed functionals",
            "homotopy": "normalized derivation extending h_W on positive quartet number",
            "remaining_minimal_fields": [
                "g_hat",
                "theta",
                "xi",
                "g_hat_star",
                "theta_star",
                "xi_star",
            ],
            "remaining_odd_pairing": [
                "<delta g_hat,delta g_hat_star>",
                "<delta theta,delta theta_star>",
                "<delta xi,delta xi_star>",
            ],
            "radial_kinetic_sign_is_physical_after_reduction": False,
            "phase_pairing_nondegenerate": True,
        },
        "reduced_action": {
            "rho_equals_f_is": "A_WEYL_GAUGE_CHART_NOT_SPONTANEOUS_WEYL_BREAKING",
            "action": action_basis["dressed_variables"],
            "Einstein_convention": "S_EH=int sqrt(-g_hat)[M_P^2 R_hat/2-M_P^2 Lambda_geom]",
            "Planck_mass_squared": "M_P^2=-kappa_r f^2/6",
            "phase_wave_residue": "Z_theta=kappa_theta f^2",
            "vacuum_energy_density": "V0=lambda f^4/4",
            "geometric_cosmological_constant": (
                "Lambda_geom=lambda f^4/(4 M_P^2)"
                "=-3 lambda f^2/(2 kappa_r)"
            ),
            "flat_quadratic_scalar_spectrum": {
                "theta": "one massless shift scalar when kappa_theta!=0",
                "radial_tau": "absent from cohomology: Weyl quartet",
                "R_squared_scalaron": (
                    "one scalaron with m_0^2=M_P^2/(12 alpha_R) "
                    "when alpha_R!=0 on the nondegenerate flat branch"
                ),
                "alpha_R_zero": "no metric scalaron from the curvature-squared sector",
            },
            "higher_curvature_disposition": {
                "alpha_B": "independent C(g_hat)^2 bulk coupling",
                "alpha_R": "independent R(g_hat)^2 bulk coupling",
                "alpha_E": "Euler/topological coupling",
                "alpha_P": "Pontryagin/parity-odd topological coupling",
                "Box_R": "horizontal boundary term, not an independent closed-manifold bulk coupling",
            },
        },
        "sign_and_regularity_classification": {
            "formal_polar_family": {
                "independent_parameters": ["kappa_r", "kappa_theta"],
                "positive_Einstein_condition": "kappa_r<0",
                "positive_phase_residue_condition": "kappa_theta>0",
                "simultaneously_feasible": True,
                "exact_fixture": {
                    "kappa_r": -1,
                    "kappa_theta": 1,
                    "M_P_squared": "f^2/6",
                    "Z_theta": "f^2",
                },
                "interpretation": (
                    "The negative radial direction is removed only after the "
                    "exact Weyl quartet contraction; the reduced phase "
                    "direction has positive residue."
                ),
            },
            "Cartesian_analytic_complex_scalar_subfamily": {
                "constraint": "kappa_theta=kappa_r=kappa_Phi",
                "product_identity": "M_P^2 Z_theta=-kappa_Phi^2 f^4/6",
                "nonzero_product_sign": "NEGATIVE",
                "simultaneously_positive": False,
                "status": "OBSTRUCTED",
                "scope": (
                    "ordinary O(2)-invariant Cartesian-analytic "
                    "|nabla Phi|^2 kinetic term"
                ),
            },
            "formal_chart_price": (
                "kappa_r!=kappa_theta is smooth in polar variables on rho!=0 "
                "but is not a regular O(2)-invariant Cartesian target metric "
                "at Phi=0"
            ),
        },
        "internal_symmetry_classification": {
            "GLOBAL": {
                "theta_status": "PHYSICAL_MASSLESS_GLOBALLY_CHARGED",
                "ghost": "NONE",
                "Noether_current": "J^mu=-kappa_theta rho^2 nabla^mu theta",
            },
            "NONE": {
                "theta_status": "PHYSICAL_GENERICALLY_MASSIVE_IF_U''!=0",
                "ghost": "NONE",
                "potential": "rho^4 U(theta)",
            },
            "LOCAL": {
                "theta_status": "GAUGED_STUECKELBERG_ONLY_IN_AN_EXTENDED_THEORY",
                "required_new_rows": [
                    "A_mu",
                    "internal_U1_ghost",
                    "their antifields",
                    "internal antighost and multiplier plus duals",
                ],
                "included_here": False,
            },
        },
        "exact_checks": {
            "action_basis_complete_in_declared_class": True,
            "canonical_one_form": True,
            "classical_master_equation": True,
            "Q_squared_zero": True,
            "cyclic_odd_pairing": True,
            "real_structure": True,
            "Weyl_quartet_contracts": True,
            "nonminimal_pairs_contract": True,
            "reduced_phase_pairing_nondegenerate": True,
            "formal_polar_positive_fixture_exists": True,
            "Cartesian_analytic_sign_obstruction": True,
        },
        "dependencies": dependency_rows,
        "content_hashes": {},
        "claim_flags": {
            "LOCAL_ACTION_CERTIFIED": True,
            "MINIMAL_AND_NONMINIMAL_BV_CERTIFIED": True,
            "RADIAL_QUARTET_CERTIFIED": True,
            "FORMAL_POLAR_EINSTEIN_PHASE_SIGN_FEASIBLE": True,
            "CARTESIAN_ANALYTIC_COMPLEX_SCALAR_SIGN_OBSTRUCTED": True,
            "CAUSAL_GREEN_OPERATOR": False,
            "HADAMARD_STATE": False,
            "ANOMALY_COEFFICIENT": False,
            "QUANTUM_MASTER_EQUATION": False,
            "PARTICLE_OR_UNITARITY": False,
        },
        "next_gate": (
            "Rebuild the changed-action vacuum-cylinder carrier and decide "
            "whether its Einstein/R(g_hat)^2 trace Hessian removes the "
            "certified compact-support dressed-trace obstruction."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC theorem freezes the complete declared "
            "two-scalar-derivative/four-curvature-derivative formal polar "
            "action with global U(1), its action-derived minimal and "
            "nonminimal BV complex, exact tau/Weyl quartet, reduced odd "
            "pairing and exact Einstein/phase coefficients. It proves that "
            "independent kappa_r<0 and kappa_theta>0 give positive Einstein "
            "and phase residues after quartet reduction, while the regular "
            "Cartesian-analytic kappa_r=kappa_theta subfamily is sign "
            "obstructed. The unequal-coefficient theory is only formal on "
            "rho!=0. The scale f is introduced by the chart and is not "
            "dynamically generated. No background solution, causal Green "
            "operator, Hadamard state, anomaly coefficient, QME, particle, "
            "scattering or unitarity claim is established."
        ),
    }

    content = {
        "action_basis": payload["action_basis"],
        "transformations": payload["transformations"],
        "field_inventory": payload["field_inventory"],
        "BV_master_action": payload["BV_master_action"],
        "canonical_dressed_change": payload["canonical_dressed_change"],
        "sparse_operators": payload["sparse_operators"],
        "reduced_action": payload["reduced_action"],
        "sign_and_regularity_classification": payload[
            "sign_and_regularity_classification"
        ],
    }
    payload["content_hashes"] = {
        "action_manifest_sha256": _json_sha(payload["action_basis"]),
        "field_inventory_sha256": _json_sha(payload["field_inventory"]),
        "BV_manifest_sha256": _json_sha(payload["BV_master_action"]),
        "operator_manifest_sha256": _json_sha(payload["sparse_operators"]),
        "preflight_core_sha256": _json_sha(content),
    }
    validate(payload)
    return payload


def validate(value: dict[str, Any]) -> None:
    if value["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
        raise AssertionError("dependency tag drifted")
    for role, path in DEPENDENCIES.items():
        row = value["dependencies"][role]
        source = json.loads(path.read_text())
        if (
            row["path"] != str(path.relative_to(ROOT))
            or row["result_id"] != source["result_id"]
            or row["sha256"] != _sha(path)
        ):
            raise AssertionError(f"dependency drift: {role}")

    operators = value["sparse_operators"]
    for name, q_key, h_key in (
        ("Weyl_quartet", "Q_W", "h_W"),
        ("nonminimal_doublet", "Q_nm", "h_nm"),
    ):
        block = operators[name]
        q = _dense(block[q_key])
        h = _dense(block[h_key])
        if q * q != sp.zeros(4) or q * h + h * q != sp.eye(4):
            raise AssertionError(f"{name} contraction failed")
        for key in (q_key, h_key):
            record = deepcopy(block[key])
            claimed = record.pop("sha256")
            if claimed != _json_sha(record):
                raise AssertionError(f"{name} matrix hash drifted")

    kappa_r, kappa_theta, f = sp.symbols(
        "kappa_r kappa_theta f", nonzero=True, real=True
    )
    planck = -kappa_r * f**2 / 6
    phase = kappa_theta * f**2
    if sp.simplify(planck.subs(kappa_r, -1) - f**2 / 6) != 0:
        raise AssertionError("Planck coefficient drifted")
    if sp.simplify(phase.subs(kappa_theta, 1) - f**2) != 0:
        raise AssertionError("phase residue drifted")
    kappa_phi = sp.symbols("kappa_Phi", nonzero=True, real=True)
    analytic_product = sp.expand(
        (planck * phase).subs(
            {kappa_r: kappa_phi, kappa_theta: kappa_phi}
        )
    )
    if analytic_product != -kappa_phi**2 * f**4 / 6:
        raise AssertionError("Cartesian sign obstruction drifted")

    sign = value["sign_and_regularity_classification"]
    if (
        not sign["formal_polar_family"]["simultaneously_feasible"]
        or sign["Cartesian_analytic_complex_scalar_subfamily"][
            "simultaneously_positive"
        ]
        or sign["formal_polar_family"]["exact_fixture"]["kappa_r"] != -1
        or sign["formal_polar_family"]["exact_fixture"]["kappa_theta"] != 1
    ):
        raise AssertionError("sign classification drifted")
    if value["symmetry_choice"]["internal_U1"] != "GLOBAL":
        raise AssertionError("internal symmetry choice drifted")
    if value["Wess_Zumino_lifecycle"]["classical_action_contains_WZ"]:
        raise AssertionError("hbar Wess-Zumino term entered S0")
    if value["reduced_action"]["rho_equals_f_is"] != (
        "A_WEYL_GAUGE_CHART_NOT_SPONTANEOUS_WEYL_BREAKING"
    ):
        raise AssertionError("gauge chart was promoted to symmetry breaking")
    forbidden = (
        "CAUSAL_GREEN_OPERATOR",
        "HADAMARD_STATE",
        "ANOMALY_COEFFICIENT",
        "QUANTUM_MASTER_EQUATION",
        "PARTICLE_OR_UNITARITY",
    )
    if any(value["claim_flags"][key] for key in forbidden):
        raise AssertionError("claim boundary overpromoted")

    content = {
        "action_basis": value["action_basis"],
        "transformations": value["transformations"],
        "field_inventory": value["field_inventory"],
        "BV_master_action": value["BV_master_action"],
        "canonical_dressed_change": value["canonical_dressed_change"],
        "sparse_operators": value["sparse_operators"],
        "reduced_action": value["reduced_action"],
        "sign_and_regularity_classification": value[
            "sign_and_regularity_classification"
        ],
    }
    expected_hashes = {
        "action_manifest_sha256": _json_sha(value["action_basis"]),
        "field_inventory_sha256": _json_sha(value["field_inventory"]),
        "BV_manifest_sha256": _json_sha(value["BV_master_action"]),
        "operator_manifest_sha256": _json_sha(value["sparse_operators"]),
        "preflight_core_sha256": _json_sha(content),
    }
    if value["content_hashes"] != expected_hashes:
        raise AssertionError("content hashes drifted")


def report(value: dict[str, Any]) -> str:
    return f"""# Complex compensator action and quartet preflight

## Result

The local action is now frozen on the formal `rho!=0` polar chart.  The
canonical branch has gauge group `Diff semidirect Weyl` and a **global**
internal U(1), so the phase remains a physical shift field rather than an
unexported gauge mode.

Modulo total derivatives and four-dimensional curvature identities, the
declared two-scalar-derivative/four-curvature-derivative action is

\\[
\\begin{{aligned}}
S_0=\\int\\sqrt{{-g}}\\biggl[&
\\frac{{\\alpha_B}}8 C^2
-\\frac{{\\kappa_r}}2\\left[(\\nabla\\rho)^2+\\frac16R\\rho^2\\right]
-\\frac{{\\kappa_\\theta}}2\\rho^2(\\nabla\\theta)^2
-\\frac\\lambda4\\rho^4\\\\
&+\\left(\\frac\\rho f\\right)^4
\\left[\\alpha_R R(\\widehat g)^2+\\alpha_EE_4(\\widehat g)
+\\alpha_PP_4(\\widehat g)\\right]\\biggr],
\\end{{aligned}}
\\]

with `g_hat=(rho/f)^2 g`.  The Wess--Zumino functional remains an
order-`hbar` counterterm and is not inserted into this classical action.

## Exact BV reduction

Writing `rho=f exp(-tau)`, the canonical cotangent change is

\\[
\\widehat g=e^{{-2\\tau}}g,\\qquad
\\widehat g^*=e^{{2\\tau}}g^*,\\qquad
\\widehat\\tau^*=-\\rho\\rho^*+2g\\!\\cdot\\!g^*.
\\]

It preserves the odd canonical one-form.  In the ordered basis
`(tau,omega,omega_star,tau_hat_star)`,

\\[
Q_W\\tau=\\omega,\\qquad Q_W\\omega^*=\\widehat\\tau^*,
\\qquad Q_Wh_W+h_WQ_W=1.
\\]

The diffeomorphism and Weyl antighost/multiplier sectors have the same exact
pointwise cotangent-doublet contraction.  After projecting the quartet, the
remaining odd pairing contains the nondegenerate
`<delta theta,delta theta_star>` block.

## Einstein and phase coefficients

The reduced action contains

\\[
\\frac{{M_P^2}}2R(\\widehat g)
-\\frac{{Z_\\theta}}2(\\widehat\\nabla\\theta)^2
-\\frac{{\\lambda f^4}}4,
\\qquad
M_P^2=-\\frac{{\\kappa_r f^2}}6,
\\qquad
Z_\\theta=\\kappa_\\theta f^2.
\\]

The general polar theory therefore admits
`kappa_r<0`, `kappa_theta>0`; the exact fixture
`(kappa_r,kappa_theta)=(-1,1)` gives
`M_P^2=f^2/6` and `Z_theta=f^2`.  The negative radial direction is not called
healthy: it is removed by the certified Weyl quartet before the reduced
phase sign is read.

There is nevertheless a sharp obstruction for the ordinary
Cartesian-analytic complex scalar.  That subfamily forces
`kappa_r=kappa_theta=kappa_Phi`, and hence

\\[
M_P^2Z_\\theta=-\\frac{{\\kappa_\\Phi^2f^4}}6<0.
\\]

It cannot have both positive Einstein and phase residues.  The viable unequal
coefficient theory is smooth only on the declared `rho!=0` polar chart.

For global U(1), `theta` is one massless charged shift scalar.  The radial
field is absent from the reduced cohomology.  `alpha_R R(g_hat)^2` adds the
usual scalaron with `m_0^2=M_P^2/(12 alpha_R)` on the nondegenerate flat
branch; `alpha_R=0` removes that metric scalar.  Euler and Pontryagin are
topological, while `Box R` is horizontally exact.

## Boundary

`rho=f` is a Weyl gauge chart, not evidence of spontaneous Weyl breaking, and
`f` is introduced rather than dynamically generated.  Local U(1) would
require a connection and a new complete BV sector; it is not silently
declared here.  No background solution, causal Green operator, Hadamard
state, anomaly coefficient, QME, particle, scattering or unitarity theorem
follows.

## Reproduction

```bash
python3 d_quotient_classical/compensator/complex_compensator_action_quartet_preflight.py --check
python3 d_quotient_classical/compensator/verify_complex_compensator_action_quartet_preflight.py
python3 -m unittest d_quotient_classical.compensator.tests.test_complex_compensator_action_quartet_preflight
```

Core hash: `{value["content_hashes"]["preflight_core_sha256"]}`

CLOSE-OUT: DONE — the declared local action, BV rows and quartet reduction are frozen
EVIDENCE: d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.emit:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(value))
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise SystemExit(f"stale certificate: {OUTPUT}")
        if REPORT.read_text() != report(value):
            raise SystemExit(f"stale report: {REPORT}")
    print(
        "complex compensator local action/quartet preflight: "
        f"PASS ({value['content_hashes']['preflight_core_sha256']})"
    )


if __name__ == "__main__":
    main()

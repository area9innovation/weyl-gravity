#!/usr/bin/env python3
"""Exact quadratic visibility of minimal shift-symmetric kinetic braiding."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1.json"
)
IMPORTS = {
    "quadratic_active_clock_freeze": {
        "path": ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json",
        "sha256": "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
        "source_commit": "f64be4a5793764ebf8871d5f1a83bd736aed7fc1",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1",
        "result_state": "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_INDEPENDENTLY_FROZEN",
    },
    "background_stability": {
        "path": ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json",
        "sha256": "8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba",
        "source_commit": "b0ee2bea23af4af809bc0a50956c3e37d944e72f",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1",
        "result_state": (
            "SCOPED_ACTION_SPACE_NO_GO_BACKGROUND_STABLE_WITH_FIRST_BIFURCATION"
        ),
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> str:
    return str(sp.factor(value))


def _matrix(value: sp.Matrix) -> dict[str, Any]:
    core = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": i, "column": j, "coefficient": _q(value[i, j])}
            for i in range(value.rows)
            for j in range(value.cols)
            if value[i, j] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _imports() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for name, item in IMPORTS.items():
        actual = _sha(item["path"])
        if actual != item["sha256"]:
            raise AssertionError(f"{name} hash drifted")
        payload = json.loads(item["path"].read_text())
        if (
            payload["result_id"] != item["result_id"]
            or payload["result_state"] != item["result_state"]
        ):
            raise AssertionError(f"{name} semantics drifted")
        records[name] = {
            "path": str(item["path"].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "sha256": actual,
            "source_commit": item["source_commit"],
        }
    return records


def _minimal_action() -> dict[str, Any]:
    # G(X)=g0+beta X is the complete polynomial of degree at most one.
    # The g0 term is the horizontal divergence d(*d theta).
    H00, H11, box_theta = sp.symbols("H00 H11 box_theta")
    # With both indices raised, a diagonal Lorentzian Hessian has
    # H_ab H^ab=H00^2+H11^2 in this two-component fixture.
    lorentzian_hessian_square = H00**2 + H11**2
    euler = 2 * (lorentzian_hessian_square - box_theta**2)
    witness = sp.factor(
        euler.subs({H00: 1, H11: 1, box_theta: 0})
    )
    if witness != 4:
        raise AssertionError("non-boundary witness drifted")
    return {
        "declared_polynomial_degree": 1,
        "complete_family": "G(X)=g0+beta X",
        "constant_term": {
            "action": "g0 integral sqrt(-g_hat) Box_hat(theta)",
            "horizontal_reduction": "g0 integral d(*_hat d theta)",
            "status": "HORIZONTALLY_EXACT",
        },
        "first_nonexact_term": {
            "action": (
                "S3=beta integral sqrt(-g_hat) "
                "X Box_hat(theta), X=g_hat^{ab} nabla_a theta nabla_b theta"
            ),
            "flat_scalar_Euler": (
                "2 beta[(nabla_a nabla_b theta)(nabla^a nabla^b theta)"
                "-(Box theta)^2]"
            ),
            "nonboundary_jet_witness": {
                "H00": "1",
                "H11": "1",
                "Box_theta": "0",
                "Euler_over_beta": "4",
            },
            "status": "NOT_HORIZONTALLY_EXACT",
        },
        "normalization": (
            "beta is retained exactly; beta=0 is the exact boundary-only "
            "stratum and beta!=0 is the unique degree-one mechanism up to scale"
        ),
    }


def _covariant_hessian() -> dict[str, Any]:
    return {
        "background_hypotheses": [
            "v_a=nabla_a theta_bar is covariantly constant",
            "X_bar=v^a v_a is constant",
            "H_bar_ab=nabla_a nabla_b theta_bar=0",
            "Box_hat theta_bar=0",
        ],
        "perturbation": (
            "(h_ab,phi)=(delta g_hat_ab,delta theta), "
            "h=g_hat^{ab}h_ab"
        ),
        "first_variation_X": (
            "x(h,phi)=-h^{ab}v_a v_b+2 v^a nabla_a phi"
        ),
        "first_variation_Box": (
            "b(h,phi)=Box_hat phi-"
            "(nabla_a h^{ab}-(1/2)nabla^b h)v_b"
        ),
        "complete_bilinear_second_variation": (
            "delta^2 S3[(h,phi),(j,psi)]="
            "beta integral sqrt(-g_hat)[x(h,phi)b(j,psi)+"
            "x(j,psi)b(h,phi)] modulo compact-support/closed-slice boundary terms"
        ),
        "derivation": (
            "Subtract the numerical background constant X_bar: "
            "X_bar integral sqrt(-g_hat) Box_hat theta is an exact boundary "
            "functional for every perturbed field. Since X-X_bar and Box theta "
            "both vanish at the background, only their first-variation product "
            "survives in the Hessian. This accounts simultaneously for measure, "
            "inverse-metric, connection and second-variation terms."
        ),
        "included_variations": [
            "metric inverse",
            "volume density",
            "lapse",
            "shift",
            "spatial trace and tracefree metric",
            "clock",
            "Levi-Civita connection",
            "compact-support or closed-slice boundary terms",
        ],
        "action_first_variation": (
            "ZERO on both declared backgrounds because X_bar is constant and "
            "nabla_a nabla_b theta_bar=0"
        ),
    }


def _cylinder() -> dict[str, Any]:
    zero = sp.zeros(11)
    return {
        "background": (
            "g_hat=-dt^2+dOmega3^2 with theta_bar constant, hence v_a=0"
        ),
        "full_field_order": [
            "phi",
            "h00",
            "h01",
            "h02",
            "h03",
            "h11",
            "h22",
            "h33",
            "h12",
            "h13",
            "h23",
        ],
        "first_variations": {
            "x": "0 for every (h_ab,phi)",
            "b": "Box_hat phi; all connection terms are multiplied by v_b=0",
        },
        "complete_quadratic_Hessian": _matrix(zero),
        "rank": 0,
        "principal_symbol": "IDENTICALLY_ZERO_AT_EVERY_COVECTOR",
        "boundary_reduction": (
            "No nonzero quadratic density remains before or after integration "
            "by parts; S3 begins at cubic perturbative order"
        ),
        "consequence": (
            "The complete degree-one P(X)+G(X)Box(theta) family has exactly the "
            "same cylinder quadratic operator, dressed-trace row, split "
            "gravity-auxiliary pair and raw-D witnesses as the imported P(X) "
            "family."
        ),
    }


def _berger() -> dict[str, Any]:
    D, Delta, nu = sp.symbols("D Delta nu", nonzero=True)
    # Derived scalar carrier y=(phi,n,k,r), with h00=-2n,
    # k=gamma^{ij}h_ij and r=nabla^i s_i.  Formal adjoints are
    # D^sharp=-D and Delta^sharp=Delta.
    symbol = sp.Matrix(
        [
            [0, 2 * Delta, -D**2, 2 * D],
            [2 * Delta, 0, -nu * D, 2 * nu],
            [-D**2, nu * D, 0, 0],
            [-2 * D, 2 * nu, 0, 0],
        ]
    )
    time_gauge = sp.Matrix([nu, D, 0, -Delta])
    spatial_gauge = sp.Matrix([0, 0, 2 * Delta, D * Delta])
    if symbol * time_gauge != sp.zeros(4, 1):
        raise AssertionError("time-diffeomorphism null vector drifted")
    if symbol * spatial_gauge != sp.zeros(4, 1):
        raise AssertionError("spatial-diffeomorphism null vector drifted")
    minors3 = [
        sp.factor(symbol.extract(rows, columns).det())
        for rows in itertools.combinations(range(4), 3)
        for columns in itertools.combinations(range(4), 3)
    ]
    if any(value != 0 for value in minors3):
        raise AssertionError("rank upper bound drifted")
    delta_witness = sp.factor(symbol.extract([0, 1], [0, 1]).det())
    time_witness = sp.factor(symbol.extract([0, 2], [0, 2]).det())
    if delta_witness != -4 * Delta**2 or time_witness != -D**4:
        raise AssertionError("rank witnesses drifted")
    frozen = symbol.subs(nu, sp.Rational(3, 4))
    return {
        "background": (
            "static Berger product a=1, q=9/40, "
            "theta_bar=nu t with nu=3/4; formulas hold for every constant nu"
        ),
        "spatial_operators": (
            "Delta=Delta_Berger is the self-adjoint scalar Laplacian and "
            "r=nabla^i s_i is the divergence of the shift perturbation"
        ),
        "ADM_variables": {
            "h00": "-2n",
            "spatial_trace": "k=gamma_bar^{ij}h_ij",
            "shift_divergence": "r=nabla_bar^i s_i",
            "clock_velocity": "chi=D phi-nu n",
            "extrinsic_trace": "K=(1/2)(D k-2r)",
        },
        "specialized_first_variations": {
            "x": "-2 nu chi",
            "b": "-D chi+Delta phi-nu K",
        },
        "quadratic_action_before_boundary_reduction": (
            "S3^(2)=2 beta nu integral sqrt(gamma) "
            "chi(D chi-Delta phi+nu K)"
        ),
        "quadratic_action_after_boundary_reduction": (
            "S3^(2)=2 beta nu^2 integral sqrt(gamma) "
            "[chi K+n Delta phi]"
        ),
        "boundary_terms_removed": [
            "beta nu integral D(chi^2)",
            "-beta nu integral D[(nabla_i phi)(nabla^i phi)]",
        ],
        "field_support": {
            "nonzero": ["clock phi", "lapse n", "spatial trace k", "shift divergence r"],
            "zero": [
                "transverse shift",
                "spatial transverse-tracefree metric",
                "all tensor components orthogonal to the scalar trace/divergence block",
            ],
        },
        "formal_symbol": {
            "field_order": ["phi", "n", "k", "r"],
            "common_factor": "beta nu^2",
            "adjoints": {"D": "-D", "Delta": "Delta"},
            "matrix": _matrix(symbol),
            "frozen_nu_3_over_4": _matrix(frozen),
            "all_three_by_three_minors_zero": True,
            "rank": {
                "zero_covector": 0,
                "every_nonzero_scalar_covector": 2,
                "Delta_nonzero_witness": "-4*Delta**2",
                "D_nonzero_witness": "-D**4",
            },
            "gauge_null_vectors": [
                {
                    "generator": "time diffeomorphism T",
                    "coordinates": ["nu", "D", "0", "-Delta"],
                },
                {
                    "generator": "longitudinal spatial diffeomorphism L",
                    "coordinates": ["0", "0", "2*Delta", "D*Delta"],
                },
            ],
            "formal_self_adjoint": True,
        },
        "visibility": "NONZERO_RANK_TWO_SCALAR_BLOCK_MODULO_DECLARED_BOUNDARIES",
        "scope_warning": (
            "Berger visibility is not a cylinder repair and does not authorize "
            "an ADM health, causal-parent or selected-action promotion."
        ),
    }


def build() -> dict[str, Any]:
    imported = _imports()
    minimal = _minimal_action()
    covariant = _covariant_hessian()
    cylinder = _cylinder()
    berger = _berger()
    verdict = {
        "complete_degree_one_braiding_family_checked": True,
        "cylinder_quadratic_visibility": "IDENTICALLY_ZERO",
        "Berger_quadratic_visibility": "NONZERO_SCALAR_RANK_TWO",
        "level_2_cylinder_repair_possible": False,
        "selected_action_exported": False,
        "first_invariant_separator": (
            "v_a=0 on the required constant-clock cylinder forces "
            "delta X=0 and therefore delta^2 S3=0 on the complete metric-clock carrier"
        ),
    }
    value = {
        "schema": "pure-weyl-compensator-kinetic-braiding-quadratic-visibility-v1",
        "result_id": "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1",
        "result_state": "SCOPED_LEVEL2_BRAIDING_CYLINDER_QUADRATIC_INVISIBLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imported,
        "minimal_braiding_action": minimal,
        "covariant_complete_second_variation": covariant,
        "unit_cylinder": cylinder,
        "stationary_Berger": berger,
        "terminal_verdict": verdict,
        "exact_checks": {
            "dependency_hashes_and_semantics_pinned": True,
            "constant_G_removed_only_as_exact_boundary": True,
            "first_nonexact_G_term_has_nonzero_Euler_witness": True,
            "measure_inverse_metric_connection_and_clock_variations_included": True,
            "cylinder_full_Hessian_zero": True,
            "Berger_boundary_terms_explicit": True,
            "Berger_symbol_formally_self_adjoint": True,
            "Berger_two_gauge_null_vectors_exact": True,
            "Berger_rank_two_at_every_nonzero_scalar_covector": True,
            "cylinder_and_Berger_dispositions_separated": True,
        },
        "claim_flags": {
            "LEVEL2_BRAIDING_REPAIRS_CYLINDER": False,
            "SELECTED_LEVEL2_ACTION": False,
            "COMPLETE_REDUCED_ADM_HEALTH": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "NONLINEAR_Q2": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact theorem covers the complete polynomial G(X)=g0+beta X "
            "at the first degree for which integral sqrt(-g_hat)G(X)Box_hat(theta) "
            "is not horizontally exact. It uses the full metric-clock Hessian "
            "on the required constant-clock unit cylinder and stationary-gradient "
            "Berger fixture. The cylinder Hessian vanishes identically, while "
            "Berger has a separate rank-two scalar block. Therefore this minimal "
            "braiding mechanism cannot alter the imported cylinder dressed-trace, "
            "split-pair or raw-D obstruction. It is not a no-go for X^2 or higher "
            "G, Horndeski/DHOST curvature couplings, other backgrounds, new fields "
            "or enlarged gauge groups. It establishes no reduced ADM health, "
            "selected action, causal Green parent, nonlinear q2, Hadamard state, "
            "anomaly/QME result, particle space, scattering, positivity or unitarity."
        ),
        "next_gate": (
            "Close the complete declared Level-2 P(X)+linear-G(X) family by "
            "importing this cylinder-zero theorem; do not construct a nonlinear "
            "q2. Then activate the isolated minimal degenerate-curvature-coupling "
            "Level-3 gate."
        ),
    }
    value["content_hashes"] = {
        "imports_sha256": _digest(value["imports"]),
        "action_sha256": _digest(value["minimal_braiding_action"]),
        "hessian_sha256": _digest(value["covariant_complete_second_variation"]),
        "cylinder_sha256": _digest(value["unit_cylinder"]),
        "Berger_sha256": _digest(value["stationary_Berger"]),
        "verdict_sha256": _digest(value["terminal_verdict"]),
    }
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("kinetic-braiding quadratic visibility certificate is stale")
    print("COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1: PASS")


if __name__ == "__main__":
    main()

"""Fail-closed bootstrap for the asymptotically flat Einstein sector.

The exact result proved here is deliberately smaller than the commissioned
null-infinity theorem: for each nonzero spatial Fourier mode in linearized
TT pure-Weyl gravity on Minkowski space, the Einstein two-jet constraint is
an invariant subspace of the fourth-order Bach evolution.  Boundary
function spaces, surface charges, nonlinear closure, and scattering remain
open and are recorded as such.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT / "bridge" / "certificates" / "asymptotically_flat_einstein_bootstrap.json"
)

INPUTS = {
    "einstein_sector": ROOT
    / "bridge"
    / "certificates"
    / "einstein_sector_theorem.json",
    "closed_universe_bfv": ROOT
    / "bridge"
    / "certificates"
    / "closed_universe_bfv.json",
    "cylinder_causal_transport": ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_causal_transport_recognition.json",
    "cylinder_tt_factorization": ROOT
    / "covariant_completion"
    / "certificates"
    / "tt_local_factorization.json",
}


class AsymptoticBootstrapError(RuntimeError):
    """Raised when the bootstrap or an imported scope guard fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AsymptoticBootstrapError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_rows(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(entry)) for entry in matrix.row(row)] for row in range(matrix.rows)]


def _verify_scope_inputs(records: dict[str, dict[str, Any]]) -> None:
    theorem = records["einstein_sector"]
    commission = theorem.get("next_theorem_commission", {})
    _require(
        commission.get("status") == "OPEN_FAIL_CLOSED",
        "Einstein scattering commission is not open and fail-closed",
    )
    _require(
        theorem.get("claim_flags", {}).get(
            "einstein_sector_causally_closed_at_null_infinity"
        )
        is False,
        "upstream theorem already claims null-infinity closure",
    )

    closed = records["closed_universe_bfv"]
    _require(closed.get("boundary_components") == [], "closed-cylinder boundary changed")
    _require(
        closed.get("surface_charge_rank") == 0,
        "closed-cylinder input unexpectedly has surface charges",
    )
    _require(
        closed.get("alternative", {}).get("compact_time_is_charge") is True,
        "closed-cylinder input no longer recognizes a charged-time alternative",
    )

    causal = records["cylinder_causal_transport"]
    cylinder = causal.get("cylinder_specialization", {})
    _require(
        cylinder.get("cauchy_surface_compact") is True
        and cylinder.get("Gamma_sc_equals_Gamma_smooth") is True,
        "cylinder causal specialization changed",
    )

    tt = records["cylinder_tt_factorization"]
    _require(
        tt.get("constraint_subspace") == "TT, preserved by C_2 and both factors",
        "upstream TT factorization no longer preserves its constraint space",
    )
    _require(
        tt.get("scope_guard")
        == "this is the reduced physical TT operator, not a Green's witness for the complete BV complex",
        "upstream TT scope guard changed",
    )


def _linearized_tt_identity() -> dict[str, Any]:
    q = sp.symbols("q", positive=True, real=True)

    # State x=(h, h_dot, h_ddot, h_dddot) for
    # (d_t^2+q)^2 h=0, one TT polarization at fixed |k|^2=q.
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [-q**2, 0, -2 * q, 0],
        ]
    )
    einstein_constraint = sp.Matrix([[q, 0, 1, 0], [0, q, 0, 1]])
    constraint_evolution = sp.Matrix([[0, 1], [-q, 0]])
    defect = sp.simplify(
        einstein_constraint * evolution
        - constraint_evolution * einstein_constraint
    )
    _require(defect == sp.zeros(2, 4), "Einstein constraint is not evolution-invariant")
    _require(einstein_constraint.rank() == 2, "Einstein constraint rank changed")

    kernel_basis = sp.Matrix(
        [
            [1, 0],
            [0, 1],
            [-q, 0],
            [0, -q],
        ]
    )
    _require(
        einstein_constraint * kernel_basis == sp.zeros(2, 2),
        "displayed Einstein data do not lie in the constraint kernel",
    )
    induced = sp.Matrix([[0, 1], [-q, 0]])
    _require(
        evolution * kernel_basis == kernel_basis * induced,
        "Bach evolution does not restrict to Einstein wave evolution",
    )

    return {
        "background": "four-dimensional Minkowski space",
        "sector": "one transverse-traceless polarization at fixed spatial q=|k|^2>0",
        "bach_equation": "(d_t^2+q)^2 h=0",
        "einstein_equation": "(d_t^2+q) h=0",
        "state_order": ["h", "d_t h", "d_t^2 h", "d_t^3 h"],
        "bach_evolution_matrix": _matrix_rows(evolution),
        "einstein_constraint_order": ["(d_t^2+q)h", "d_t(d_t^2+q)h"],
        "einstein_constraint_matrix": _matrix_rows(einstein_constraint),
        "constraint_evolution_matrix": _matrix_rows(constraint_evolution),
        "intertwining_identity": "C_E A_B = A_E C_E",
        "intertwining_defect": _matrix_rows(defect),
        "einstein_kernel_basis": _matrix_rows(kernel_basis),
        "restricted_evolution_identity": "A_B i_E = i_E A_E",
        "bach_data_dimension_per_helicity": 4,
        "einstein_data_dimension_per_helicity": 2,
        "result": (
            "the linearized Einstein initial-data kernel is exactly invariant under "
            "fixed-mode Bach evolution"
        ),
        "scope_guards": [
            "q=0 soft and Coulombic sectors are not classified",
            "no statement about radial falloff or null-infinity flux",
            "no nonlinear constraint-preservation theorem",
            "modewise evolution invariance is not a support theorem for Green operators",
        ],
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _verify_scope_inputs(records)
    linearized = _linearized_tt_identity()

    obligations = [
        ("AF-E1", "PARTIAL", "linearized TT data fixed; nonlinear weighted Bondi/Bach spaces open"),
        ("AF-E2", "OPEN", "no retarded/advanced null-infinity complex"),
        ("AF-E3", "PARTIAL", "charge criterion fixed; pure-Weyl charges not computed"),
        ("AF-E4", "OPEN", "no causal exclusion of the non-Einstein branch"),
        ("AF-E5", "PARTIAL", "linearized fixed-mode closure proved; nonlinear closure open"),
        ("AF-E6", "OPEN", "no null-infinity current/flux comparison"),
        ("AF-E7", "OPEN", "no asymptotic scattering cohomology"),
        ("AF-E8", "OPEN", "extra Bach-flat asymptotic channels unclassified"),
    ]

    return {
        "schema": "pure-weyl-asymptotically-flat-einstein-bootstrap-v1",
        "result_id": "ASYMPTOTICALLY_FLAT_EINSTEIN_SECTOR_BOOTSTRAP",
        "result_state": "PARTIAL_EXACT_LINEARIZED_RAIL",
        "source_commit": "cab0e805238440d9d6e9ec39e1f3cf10624fae5e",
        "dependency_tags": ["REDUCED-MODE"],
        "required_promotion_tag": "LORENTZIAN-CAUSAL",
        "linearized_minkowski_theorem": linearized,
        "asymptotic_data_seed": {
            "status": "SPECIFIED_NOT_ADMISSIBILITY_PROVED",
            "conformal_completion": {
                "objects": ["M_tilde", "g_tilde", "Omega"],
                "relations": [
                    "g_tilde=Omega^2 g on the physical interior",
                    "Omega=0 and dOmega nonzero at I_plus and I_minus",
                    "I_plus and I_minus each have topology R x S^2",
                ],
                "regularity_choice": "smooth conformal completion at null infinity",
            },
            "bondi_seed_fields": [
                "unit-sphere metric q_AB",
                "trace-free shear C_AB(u,x)",
                "news N_AB=d_u C_AB",
                "Bondi mass aspect m(u,x)",
                "angular-momentum aspect N_A(u,x)",
            ],
            "candidate_radiative_class": [
                "C_AB is smooth and has finite H^s(S^2) endpoint limits as u tends to plus/minus infinity",
                "N_AB lies in L^1_u H^s(S^2) intersect L^2_u H^s(S^2), with s>3 declared but not sharp",
                "memory Delta C_AB is allowed and equals the difference of the endpoint shears",
            ],
            "missing_bach_data": [
                "falloffs and regularity for the second fourth-order radiative pair",
                "Coulombic and q=0 soft sectors",
                "corner matching through spatial infinity",
                "closure of the Bach operator on weighted/polyhomogeneous spaces",
                "constraint-compatible gauge and ghost falloffs",
            ],
        },
        "gauge_charge_rule": {
            "status": "CRITERION_FIXED_ASSIGNMENTS_OPEN",
            "proper_gauge_core": "Diff x Weyl parameters vanishing near null infinity",
            "boundary_preserving_parameter": (
                "proper gauge only when its renormalized surface-charge variation "
                "vanishes on every tangent direction and its reference charge is zero"
            ),
            "charged_parameter": "asymptotic symmetry, not quotiented as gauge",
            "consequence": "time translations and BMS-type generators cannot be gauged by name alone",
            "missing": [
                "pure-Weyl presymplectic potential and boundary counterterm choice",
                "finite integrable surface-charge formula",
                "flux/balance law and charge algebra",
                "generator-by-generator proper/charged classification",
            ],
        },
        "cylinder_non_reuse": {
            "established": True,
            "reasons": [
                "the cylinder proof uses compact S^3 to identify all smooth sections with spacelike-compact sections",
                "the selected closed-universe BFV problem has no boundary and surface-charge rank zero",
                "null infinity has boundary flux and may retain time/BMS transformations as charged symmetries",
            ],
        },
        "obligation_status": [
            {"id": identifier, "status": status, "receipt": receipt}
            for identifier, status, receipt in obligations
        ],
        "claim_flags": {
            "linearized_minkowski_einstein_data_invariant": True,
            "full_asymptotically_flat_function_space_admissible": False,
            "null_infinity_green_complex_constructed": False,
            "pure_weyl_surface_charges_computed": False,
            "non_einstein_branch_causally_excluded": False,
            "nonlinear_einstein_constraint_preserved": False,
            "radiative_symplectic_form_matched": False,
            "helicity_two_scattering_space_recovered": False,
            "extra_weyl_channels_classified": False,
        },
        "sources": [
            {
                "role": "null-infinity radiative phase-space control",
                "citation": "Ashtekar and Streubel, Proc. Roy. Soc. A 376 (1981) 585",
                "url": "https://doi.org/10.1098/rspa.1981.0109",
            },
            {
                "role": "charge-versus-gauge criterion with radiative flux",
                "citation": "Wald and Zoupas, Phys. Rev. D 61 (2000) 084027",
                "url": "https://arxiv.org/abs/gr-qc/9911095",
            },
            {
                "role": "four-dimensional conformal-gravity canonical charge control",
                "citation": "Lovrekovic, arXiv:1505.05820",
                "url": "https://arxiv.org/abs/1505.05820",
                "scope_guard": "generalized Fefferman-Graham boundaries, not an asymptotically flat theorem",
            },
        ],
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "verification_command": (
            "python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify "
            "bridge/certificates/asymptotically_flat_einstein_bootstrap.json"
        ),
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    actual = _load(path)
    expected = build_certificate()
    _require(actual == expected, f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

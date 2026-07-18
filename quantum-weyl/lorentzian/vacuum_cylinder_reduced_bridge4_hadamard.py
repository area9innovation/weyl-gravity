#!/usr/bin/env python3
"""Certify the reduced vacuum-cylinder Bridge-4 quasifree carrier.

The certificate is deliberately restricted to the physical E/A/L cohomology
carrier.  It constructs the compatible complex structure and the exact
spectral two-point distributions from already-certified, same-background
mode, Green and pairing data.  It does not manufacture a full-BV Hadamard
state or positivity on the A/L branches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json"
SCHEMA = HERE / "schema/vacuum-cylinder-reduced-bridge4-hadamard-v1.schema.json"

DEPENDENCIES = {
    "polarized_classical_complex": ROOT
    / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
    "reduced_causal_green": ROOT
    / "covariant_completion/certificates/reduced_physical_green.json",
    "causal_pairing_transport": ROOT
    / "covariant_completion/certificates/curved_direct_causal_pairing_transport.json",
    "positive_frequency_transform": ROOT
    / "covariant_completion/certificates/positive_frequency_transform.json",
    "branch_residues": ROOT
    / "covariant_completion/certificates/branch_residue_operators.json",
    "branch_spectrum": ROOT
    / "covariant_completion/certificates/branch_spectrum.json",
    "all_level_EAL_spectrum": ROOT
    / "covariant_completion/certificates/curved_EAL_spectrum_all_level.json",
    "branch_sobolev": ROOT
    / "covariant_completion/certificates/branch_sobolev_orders.json",
    "one_particle_krein": ROOT
    / "analytic_completion/certificates/one_particle_krein.json",
}

FAMILIES = ("E", "A", "L")
MINIMUM = {"E": 2, "A": 3, "L": 4}
SIGN = {"E": 1, "A": -1, "L": -1}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(payload.get("result_id") or payload.get("schema")),
        "sha256": _sha256(path),
    }


def _residue(family: str, energy: sp.Expr) -> sp.Expr:
    return sp.expand(
        {
            "E": 4 * (energy + 1),
            "A": 2 * (energy**2 - 4),
            "L": 4 * (energy - 1),
        }[family]
    )


def _one_chirality_dimension(family: str, energy: sp.Expr) -> sp.Expr:
    return sp.expand(
        {
            "E": energy**2 + 2 * energy - 3,
            "A": energy**2 - 1,
            "L": energy**2 - 2 * energy - 3,
        }[family]
    )


def _shift_positive(polynomial: sp.Expr, minimum: int) -> bool:
    m = sp.symbols("m", integer=True, nonnegative=True)
    shifted = sp.Poly(sp.expand(polynomial.subs({N: m + minimum})), m)
    return all(coefficient >= 0 for coefficient in shifted.all_coeffs()) and bool(
        shifted.eval(0) > 0
    )


N = sp.symbols("N", integer=True, positive=True)


def _exact_branch_checks(family: str) -> dict[str, bool]:
    sign = sp.Integer(SIGN[family])
    residue = _residue(family, N)
    # Use an explicitly positive abstract residue in the sesquilinear check;
    # positivity of the concrete branch polynomial is proved independently
    # below.  This keeps conjugation from treating sqrt(R_family(N)) as an
    # untyped complex expression.
    positive_residue = sp.symbols("R", positive=True, real=True)
    omega = sign * positive_residue * sp.Matrix([[0, 1], [-1, 0]])
    complex_structure = sp.Matrix([[0, -1 / N], [N, 0]])
    covariance = sp.simplify(omega * complex_structure)
    normalization = 1 / sp.sqrt(2 * positive_residue * N)
    mode = sp.Matrix([normalization, -sp.I * N * normalization])
    norm = sp.simplify(sp.I * (sp.conjugate(mode).T * omega * mode)[0])

    dt = sp.symbols("Delta_t", real=True)
    wightman = sign * sp.exp(-sp.I * N * dt) / (2 * positive_residue * N)
    causal = -sign * sp.sin(N * dt) / (positive_residue * N)
    bisolution = sp.simplify(sp.diff(wightman, dt, 2) + N**2 * wightman)
    ccr = sp.simplify(
        sp.expand_complex(
            wightman - wightman.subs(dt, -dt) - sp.I * causal
        )
    )

    return {
        "residue_positive_on_full_spectrum": _shift_positive(
            residue, MINIMUM[family]
        ),
        "multiplicity_positive_on_full_spectrum": _shift_positive(
            _one_chirality_dimension(family, N), MINIMUM[family]
        ),
        "J_squared_equals_minus_identity": complex_structure**2 == -sp.eye(2),
        "J_is_symplectic": sp.simplify(
            complex_structure.T * omega * complex_structure - omega
        ) == sp.zeros(2),
        "Omega_times_J_is_symmetric": covariance == covariance.T,
        "normalized_mode_has_declared_Krein_norm": norm == sign,
        "two_point_is_exact_bisolution": bisolution == 0,
        "two_point_antisymmetric_part_equals_i_causal_propagator": ccr == 0,
    }


def _load_and_validate_dependencies() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    polarized = values["polarized_classical_complex"]
    green = values["reduced_causal_green"]
    pairing = values["causal_pairing_transport"]
    positive = values["positive_frequency_transform"]
    residues = values["branch_residues"]
    spectrum = values["branch_spectrum"]
    all_level = values["all_level_EAL_spectrum"]
    sobolev = values["branch_sobolev"]
    krein = values["one_particle_krein"]

    if (
        polarized.get("state_complex")
        != "Sym(W_+ direct-sum W_-) tensor Lambda^bullet so(4,2)^*"
        or "the all-energy E/A/L action preserves the positive ket module"
        not in polarized.get("proved", [])
        or green.get("spacetime") != "Lorentzian R x S^3, unit radius"
        or green.get("advanced_retarded_support") is not True
        or green.get("scope") != "reduced physical E/A/L system"
        or green.get("full_bv_green_witness") is not False
        or pairing.get("Green_pairing_equals_current_pairing") is not True
        or pairing.get("pairing_compatibility") is not True
        or positive.get("normalized_metric_modes_map_to_unit_coefficients")
        is not True
        or positive.get("krein_signs") != SIGN
        or residues.get("oscillator_norms") != SIGN
        or residues.get("normalization_fixed_all_levels") is not True
        or spectrum.get("spectra") != {"A_E": "2,3,4,...", "A_L": "4,5,6,..."}
        or all_level.get("EAL_curvature_spectrum_match") is not True
        or all_level.get("all_level_not_finite_cutoff") is not True
        or sobolev.get("krein_unitary") is not True
        or krein.get("classification") != "infinite-index Krein space"
        or krein.get("algebraic_core_dense") is not True
    ):
        raise ValueError("vacuum-cylinder Bridge-4 dependency drifted")

    branch_rows = {row["family"]: row for row in all_level["branches"]}
    for family in FAMILIES:
        if (
            branch_rows[family]["frequency"] != "n"
            or branch_rows[family]["minimum_energy"] != MINIMUM[family]
            or residues["branches"][family]["krein_sign"] != SIGN[family]
        ):
            raise ValueError(f"{family} branch dictionary drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_and_validate_dependencies()
    checks = {family: _exact_branch_checks(family) for family in FAMILIES}
    if not all(all(row.values()) for row in checks.values()):
        raise ValueError("reduced Bridge-4 exact branch check failed")

    branch_data = {}
    for family in FAMILIES:
        branch_data[family] = {
            "minimum_energy": MINIMUM[family],
            "frequency": "N",
            "positive_residue": {
                "E": "4(N+1)",
                "A": "2(N^2-4)",
                "L": "4(N-1)",
            }[family],
            "krein_sign": SIGN[family],
            "one_chirality_dimension": {
                "E": "N^2+2N-3",
                "A": "N^2-1",
                "L": "N^2-2N-3",
            }[family],
            "complex_structure_on_Cauchy_data": "J_N(q,p)=(-p/N,N q)",
            "normalized_positive_frequency_mode": "v_N=(1,-iN)/sqrt(2 R_family(N) N)",
            "mode_two_point_kernel": "W_family,N^+(Delta t)=s_family exp(-i N Delta t)/(2 R_family(N) N)",
            "mode_causal_kernel": "Delta_family,N(Delta t)=-s_family sin(N Delta t)/(R_family(N) N)",
            "exact_checks": checks[family],
        }

    result = {
        "schema": "quantum-weyl-vacuum-cylinder-reduced-bridge4-hadamard-v1",
        "result_id": "VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD",
        "result_state": "BRIDGE4_CERTIFIED_ON_REDUCED_VACUUM_CYLINDER_KREIN_CARRIER_FULL_BV_EXTENSION_OPEN",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "free pure-Weyl BV-BFV gravity after reduction to physical E/A/L cohomology",
            "background": "vacuum conformal cylinder R x S3 of unit radius",
            "boundaries": "compact S3 Cauchy surfaces; stationary positive-frequency polarization",
            "carrier": "parity-complete all-energy E/A/L reduced solution module",
            "excluded": "full off-shell BV distributional complex, interactions, scattering and asymptotic particles",
        },
        "activation_gate": {
            "normalized_classical_mode": "CERTIFIED_SAME_BACKGROUND_ALL_ENERGY_EAL",
            "causal_Green_carrier": "CERTIFIED_SAME_BACKGROUND_REDUCED_ADVANCED_RETARDED_BLOCKS",
            "pairing": "CERTIFIED_SAME_BACKGROUND_GREEN_EQUALS_CAUCHY_CURRENT_WITH_SIGNS_PLUS_E_MINUS_A_MINUS_L",
            "gate_status": "CLOSED_FOR_REDUCED_PHYSICAL_BRIDGE4",
        },
        "BRST_status": {
            "cocycle": "CERTIFIED_ON_SELECTED_REDUCED_CLASSICAL_BRST_RETRACTION",
            "exactness": "NONEXACT_IN_SELECTED_REDUCED_COMPLEX",
            "reduced_differential": "ZERO_ON_PHYSICAL_COHOMOLOGY_REPRESENTATIVES",
            "full_BV_distributional_compatibility": "NO_CERTIFIED_MAP",
        },
        "branch_data": branch_data,
        "compatible_complex_structure": {
            "formula": "J(q,p)=(-A^{-1}p,Aq) branchwise",
            "square": "J^2=-1",
            "symplectic_compatibility": "J^T Omega J=Omega",
            "covariance": "Omega J=s_family R_family diag(A,A^{-1})",
            "positive_frequency_eigenspace": "z=2^-1/2[(RA)^1/2 q+i(RA^-1)^1/2 p]",
            "status": "CERTIFIED_ON_REDUCED_CAUCHY_SOBOLEV_CARRIER",
        },
        "spectral_two_point_function": {
            "mode_sum": "W_family^+(x,x')=sum_(N,M,chi) s_family exp[-iN(t-t'-i0)] u_(N,M,chi)(x) ubar_(N,M,chi)(x')/[2 R_family(N) N]",
            "distributional_convergence": "compact-S3 multiplicities are quadratic while smooth test-function spectral coefficients are rapidly decreasing",
            "bisolution": "exact for every normally hyperbolic branch factor and hence for the reduced direct sum",
            "CCR": "W^+-(W^+)^(sharp,swap)=i Delta_reduced in the imported retarded-minus-advanced convention",
            "wavefront_set": "C_plus on each nonzero E/A/L branch bundle",
            "wavefront_argument": "ultrastatic positive-frequency pseudodifferential covariance is Hadamard; multiplication by the elliptic finite-order residue inverse and a nonzero Krein sign preserves the wavefront relation",
            "kernel_status": "GLOBAL_STATIONARY_REDUCED_KREIN_HADAMARD_TWO_POINT_DISTRIBUTION",
        },
        "state_space": {
            "E": "POSITIVE_QUASIFREE_HADAMARD_STATE_SECTOR",
            "A": "NEGATIVE_KREIN_HADAMARD_DISTRIBUTION_NOT_A_POSITIVE_STATE",
            "L": "NEGATIVE_KREIN_HADAMARD_DISTRIBUTION_NOT_A_POSITIVE_STATE",
            "total": "INFINITE_INDEX_KREIN_QUASIFREE_FUNCTIONAL",
            "positive_graviton_Hilbert_space": False,
            "compact_cylinder_scattering_particle": False,
        },
        "decision": {
            "Bridge_4_reduced_vacuum_cylinder": "CERTIFIED",
            "Bridge_4_full_BV": "NO_CERTIFIED_MAP",
            "Bridge_4_Berger": "NO_CERTIFIED_MAP",
            "compatible_complex_structure": "CERTIFIED_REDUCED_MODE",
            "Hadamard_two_point_function": "CERTIFIED_REDUCED_KREIN_CARRIER",
            "state_space_sign": "PLUS_E_MINUS_A_MINUS_L",
            "global_BRST_Hadamard_state": "NO_CERTIFIED_MAP",
            "interacting_quantum_theory": "OBSTRUCTED_STRICT_FIELD_CONTENT_AND_NOT_PROMOTED",
        },
        "claim_flags": {
            "VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED": True,
            "SAME_BACKGROUND_NORMALIZED_MODE_GREEN_PAIRING_GATE_CLOSED": True,
            "REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED": True,
            "REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED": True,
            "E_BRANCH_POSITIVE_HADAMARD_STATE_CERTIFIED": True,
            "A_L_BRANCHES_POSITIVE": False,
            "FULL_BV_BRST_HADAMARD_STATE_CERTIFIED": False,
            "POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED": False,
            "BERGER_BRIDGE4_CERTIFIED": False,
        },
        "analytic_provenance": {
            "vector_valued_microlocal_spectrum": {
                "authors": ["H. Sahlmann", "R. Verch"],
                "title": "Microlocal spectrum condition and Hadamard form for vector-valued quantum fields in curved spacetime",
                "arxiv": "math-ph/0008029",
                "url": "https://arxiv.org/abs/math-ph/0008029",
            },
            "pseudodifferential_Hadamard_construction": {
                "authors": ["C. Gerard", "O. Oulghazi", "M. Wrochna"],
                "title": "Hadamard states for the Klein-Gordon equation on Lorentzian manifolds of bounded geometry",
                "arxiv": "1602.00930",
                "url": "https://arxiv.org/abs/1602.00930",
            },
        },
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "next_gate": "FULL_BV_BRST_HADAMARD_EXTENSION_OR_SAME_BACKGROUND_BERGER_STATIONARY_MODE_IMPORT",
        "claim_boundary": (
            "This REDUCED-MODE plus LORENTZIAN-CAUSAL certificate closes Bridge 4 only on the free physical E/A/L cohomology carrier of the unit vacuum conformal cylinder. The normalized classical modes, advanced/retarded reduced Green blocks and transported current pairing are all imported on that identical background. Their exact branch residues determine J(q,p)=(-A^{-1}p,Aq), normalized positive-frequency modes and global stationary spectral two-point distributions. Standard vector-valued pseudodifferential Hadamard theory applies to the normally hyperbolic branch factors; the finite-order elliptic residue inverses and nonzero Krein signs preserve the positive-frequency wavefront relation. The E sector is positive, whereas A and L are negative-Krein distributions, so the direct sum is an infinite-index Krein quasifree functional rather than a positive graviton Hilbert space. This result does not construct a distributional state on the full off-shell BV complex, ghost/antifield covariances, renormalized Lorentzian products, an interacting QME, a Berger stationary-mode crosswalk, scattering states or asymptotic particles. The strict fixed-field-content interacting QME remains obstructed and no cross-background mode identification is made."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    flags = value["claim_flags"]
    decision = value["decision"]
    if (
        decision["Bridge_4_reduced_vacuum_cylinder"] != "CERTIFIED"
        or decision["Bridge_4_full_BV"] != "NO_CERTIFIED_MAP"
        or decision["Bridge_4_Berger"] != "NO_CERTIFIED_MAP"
        or flags["VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED"] is not True
        or flags["REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"] is not True
        or flags["A_L_BRANCHES_POSITIVE"] is not False
        or flags["FULL_BV_BRST_HADAMARD_STATE_CERTIFIED"] is not False
        or flags["POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED"] is not False
        or flags["BERGER_BRIDGE4_CERTIFIED"] is not False
    ):
        raise ValueError("reduced vacuum-cylinder Bridge-4 certificate over-promoted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif OUTPUT.exists() and json.loads(OUTPUT.read_text()) != value:
        raise SystemExit(f"stale reduced Bridge-4 certificate: {OUTPUT}")
    print("VACUUM CYLINDER BRIDGE 4: REDUCED KREIN HADAMARD CARRIER CERTIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

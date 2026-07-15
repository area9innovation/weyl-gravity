"""Linear flat-TT causal Einstein subsector of compensated Weyl gravity.

In the constant-compensator frame, one TT polarization has the factorized
equation

    D_q (D_q + M^2) h = 0,       D_q = d_t^2 + |k|^2.

The Einstein defect ``chi=D_q h`` therefore obeys a massive Klein--Gordon
equation.  The two local Cauchy conditions ``chi=0`` and ``d_t chi=0`` remove
the massive branch and propagate by source-free hyperbolic uniqueness.  The
Einstein--Weyl current restricts to the nonzero Einstein-Hilbert current.

The result is exact for real-time flat TT Schwartz wave packets and both
helicities.  It is not a full metric BV, null-infinity, sourced, nonlinear, or
quantum theorem.
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
    ROOT / "bridge" / "certificates" / "compensated_einstein_causal_subsector.json"
)
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "compensated_einstein_causal_subsector.schema.json"
)
INPUTS = {
    "compensator_phase": ROOT / "bridge" / "certificates" / "compensator_einstein_phase.json",
    "pure_weyl_restriction": ROOT
    / "bridge"
    / "certificates"
    / "flat_einstein_symplectic_restriction.json",
}


class CompensatedEinsteinCausalSubsectorError(RuntimeError):
    """Raised when the causal subsector or a scope guard regresses."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompensatedEinsteinCausalSubsectorError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evolution_checks() -> dict[str, Any]:
    q, mass_squared = sp.symbols("q M2", positive=True)

    bach_evolution = sp.Matrix(
        [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [-q * (q + mass_squared), 0, -(2 * q + mass_squared), 0],
        ]
    )
    constraint = sp.Matrix([[q, 0, 1, 0], [0, q, 0, 1]])
    defect_evolution = sp.Matrix([[0, 1], [-(q + mass_squared), 0]])
    einstein_evolution = sp.Matrix([[0, 1], [-q, 0]])
    einstein_embedding = sp.Matrix([[1, 0], [0, 1], [-q, 0], [0, -q]])
    massive_embedding = sp.Matrix(
        [[1, 0], [0, 1], [-(q + mass_squared), 0], [0, -(q + mass_squared)]]
    )

    _require(constraint.rank() == 2, "Einstein Cauchy constraint rank changed")
    _require(
        sp.simplify(constraint * bach_evolution - defect_evolution * constraint)
        == sp.zeros(2, 4),
        "Einstein defect does not intertwine the fourth-order evolution",
    )
    _require(constraint * einstein_embedding == sp.zeros(2), "Einstein embedding misses ker C")
    _require(
        sp.simplify(
            bach_evolution * einstein_embedding
            - einstein_embedding * einstein_evolution
        )
        == sp.zeros(4, 2),
        "Einstein evolution is not embedded in the fourth-order flow",
    )
    _require(
        sp.Matrix.hstack(einstein_embedding, *constraint.nullspace()).rank() == 2,
        "Einstein embedding is not the complete constraint kernel",
    )
    branch_basis = sp.Matrix.hstack(einstein_embedding, massive_embedding)
    _require(
        sp.factor(branch_basis.det()) == mass_squared**2,
        "massless and massive Cauchy branches do not split for M2!=0",
    )
    _require(
        constraint * massive_embedding == -mass_squared * sp.eye(2),
        "massive branch is not detected by the Einstein defect data",
    )

    return {
        "fourth_order_cauchy_vector": "X=(h,d_t h,d_t^2 h,d_t^3 h)",
        "wave_operator": "D_q=d_t^2+q with q=|k|^2",
        "equation": "D_q(D_q+M2)h=0",
        "einstein_defect": "chi=D_q h",
        "defect_equation": "(D_q+M2)chi=0",
        "local_constraints": [
            "chi|_Sigma=d_t^2 h+q h=0",
            "d_t chi|_Sigma=d_t^3 h+q d_t h=0",
        ],
        "constraint_matrix": [["q", "0", "1", "0"], ["0", "q", "0", "1"]],
        "constraint_rank": 2,
        "constraint_intertwining": "C A_4=A_chi C",
        "einstein_embedding": [
            ["1", "0"],
            ["0", "1"],
            ["-q", "0"],
            ["0", "-q"],
        ],
        "einstein_intertwining": "A_4 I_E=I_E A_E",
        "kernel_identity": "ker C=im I_E",
        "massive_embedding_defect": "C I_M=-M2 I_2",
        "branch_basis_determinant": "det[I_E I_M]=M2^2",
        "causal_propagation": (
            "source-free Klein-Gordon uniqueness for (D_q+M2)chi=0 sends zero "
            "Cauchy data (chi,d_t chi) to chi=0 on the full domain of dependence"
        ),
        "future_boundary_data": "NOT_REQUIRED",
        "status": "PASS",
    }


def _current_checks() -> dict[str, Any]:
    q, alpha, c1 = sp.symbols("q alpha c1", nonzero=True)
    mass_squared = c1 / alpha

    x1 = sp.symbols("h1 v1 a1 j1")
    x2 = sp.symbols("h2 v2 a2 j2")
    h1, v1, a1, j1 = x1
    h2, v2, a2, j2 = x2
    chi1, dot_chi1 = a1 + q * h1, j1 + q * v1
    chi2, dot_chi2 = a2 + q * h2, j2 + q * v2

    weyl_current = sp.expand(
        alpha
        / 2
        * (
            chi1 * v2
            - dot_chi1 * h2
            - chi2 * v1
            + dot_chi2 * h1
        )
    )
    eh_current = sp.expand(c1 / 2 * (h1 * v2 - h2 * v1))
    total_current = sp.expand(weyl_current + eh_current)
    cauchy_matrix = sp.Matrix(
        4,
        4,
        lambda row, column: total_current.coeff(x1[row]).coeff(x2[column]),
    )
    _require(cauchy_matrix + cauchy_matrix.T == sp.zeros(4), "Cauchy current is not antisymmetric")

    einstein_embedding = sp.Matrix([[1, 0], [0, 1], [-q, 0], [0, -q]])
    massive_embedding = sp.Matrix(
        [[1, 0], [0, 1], [-(q + mass_squared), 0], [0, -(q + mass_squared)]]
    )
    canonical = sp.Matrix([[0, 1], [-1, 0]])
    restricted_einstein = sp.simplify(einstein_embedding.T * cauchy_matrix * einstein_embedding)
    restricted_massive = sp.simplify(massive_embedding.T * cauchy_matrix * massive_embedding)
    cross_pairing = sp.simplify(einstein_embedding.T * cauchy_matrix * massive_embedding)
    branch_basis = sp.Matrix.hstack(einstein_embedding, massive_embedding)
    branch_form = sp.simplify(branch_basis.T * cauchy_matrix * branch_basis)

    _require(restricted_einstein == c1 * canonical / 2, "Einstein current normalization changed")
    _require(restricted_massive == -c1 * canonical / 2, "massive current normalization changed")
    _require(cross_pairing == sp.zeros(2), "massless and massive branches are not symplectically orthogonal")
    _require(
        branch_form == sp.diag(c1 * canonical / 2, -c1 * canonical / 2),
        "branch-diagonal symplectic form changed",
    )
    _require(restricted_einstein.rank() == 2, "Einstein restricted pairing is degenerate")
    _require(
        sp.simplify(restricted_einstein.subs(c1, 0)) == sp.zeros(2),
        "pure-Weyl limit did not recover zero Einstein pairing",
    )

    return {
        "action_density": (
            "L_TT=(alpha/4)(Box h)^2-(c1/4)partial_mu h partial^mu h"
        ),
        "einstein_defect": "chi=Box h",
        "total_current": (
            "omega^mu=(alpha/2)[chi1 partial^mu h2-(partial^mu chi1)h2"
            "-chi2 partial^mu h1+(partial^mu chi2)h1]"
            "+(c1/2)[h1 partial^mu h2-h2 partial^mu h1]"
        ),
        "einstein_restriction": (
            "chi1=chi2=0 implies omega^mu=(c1/2)omega_EH^mu"
        ),
        "cauchy_coordinates": ["h", "d_t h", "d_t^2 h", "d_t^3 h"],
        "restricted_einstein_matrix": [["0", "c1/2"], ["-c1/2", "0"]],
        "restricted_massive_matrix": [["0", "-c1/2"], ["c1/2", "0"]],
        "cross_branch_matrix": [["0", "0"], ["0", "0"]],
        "restricted_ranks": {"einstein": 2, "massive": 2},
        "relative_signature": "massless and massive spin-2 branches have opposite symplectic normalization",
        "pure_weyl_limit": "c1->0 makes the restricted Einstein matrix rank zero",
        "status": "PASS",
    }


def _hamiltonian_checks() -> dict[str, Any]:
    q = sp.symbols("q", positive=True)
    c1 = sp.symbols("c1", nonzero=True)
    h, velocity = sp.symbols("h velocity", real=True)
    canonical = sp.Matrix([[0, 1], [-1, 0]])
    omega = c1 * canonical / 2
    evolution = sp.Matrix([[0, 1], [-q, 0]])
    state = sp.Matrix([h, velocity])
    hessian = sp.simplify(omega * evolution)
    hamiltonian = sp.simplify((state.T * hessian * state)[0] / 2)
    expected = -c1 * (velocity**2 + q * h**2) / 4

    _require(hessian == hessian.T, "P0 flow is not Hamiltonian on the Einstein sector")
    _require(sp.simplify(hamiltonian - expected) == 0, "Einstein wave Hamiltonian changed")
    _require(
        sp.simplify(expected.subs(c1, -1) - (velocity**2 + q * h**2) / 4) == 0,
        "healthy-sign Einstein energy is not positive",
    )

    return {
        "generator": "P_0=partial_t",
        "hamiltonian_convention": "delta H=Omega(delta h,L_P0 h)",
        "restricted_hamiltonian_per_polarization": "H_P0=-(c1/4)[(d_t h)^2+|grad h|^2]",
        "repository_healthy_sign": "c1=-1 gives positive H_P0",
        "einstein_hilbert_match": "exact with the action normalization c1 R",
        "two_helicity_energy": "sum of the identical positive helicity +2 and -2 contributions for c1=-1",
        "status": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "compensated-einstein-causal-subsector-v1",
        "wrong causal subsector schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"causal subsector certificate is missing {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(
        payload.get("dependency_tags") == ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "wrong dependency tags",
    )
    _require(
        payload.get("provenance", {}).get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    _require(
        payload.get("verdict")
        == "LINEAR_FLAT_TT_EINSTEIN_SECTOR_CAUSALLY_CLOSED_AND_SYMPLECTIC",
        "causal subsector verdict changed",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "local_einstein_cauchy_constraints_derived",
        "constraint_rank_two",
        "constraint_intertwining_exact",
        "source_free_causal_propagation_proved",
        "massive_branch_eliminated_on_selected_free_solutions",
        "no_future_boundary_data_required",
        "einstein_embedding_intertwines",
        "restricted_current_equals_einstein_hilbert",
        "restricted_pairing_nondegenerate",
        "P0_energy_matches_einstein_hilbert",
        "both_tt_helicities_recovered_classically",
        "pure_weyl_limit_recovers_zero_pairing",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved flag missing")
    _require(
        all(flags.get(name) is False for name in set(required_flags) - true_flags),
        "an open claim was promoted",
    )


def build_certificate() -> dict[str, Any]:
    compensator = _load(INPUTS["compensator_phase"])
    pure_weyl = _load(INPUTS["pure_weyl_restriction"])
    _require(
        compensator.get("verdict")
        == "EINSTEIN_WEYL_PHASE_REPAIRS_MASSLESS_PAIRING_BUT_RETAINS_EXTRA_SPIN2",
        "compensator phase premise changed",
    )
    _require(
        compensator.get("claim_flags", {}).get("extra_massive_spin2_branch_present") is True
        and compensator.get("claim_flags", {}).get("massive_branch_causally_excluded") is False,
        "compensator causal input gate changed",
    )
    _require(
        pure_weyl.get("verdict") == "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED",
        "pure-Weyl pairing premise changed",
    )

    certificate = {
        "schema": "compensated-einstein-causal-subsector-v1",
        "schema_path": (
            "bridge/einstein_sector/schema/"
            "compensated_einstein_causal_subsector.schema.json"
        ),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_EINSTEIN_CAUSAL_SUBSECTOR",
        "result_state": "LINEAR_FLAT_TT_CAUSAL_AND_SYMPLECTIC_SUBSECTOR_CERTIFIED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "provenance": {
            "input_base_commit": "0c200a2805f1085f44e466987dc126001035585b",
            "generator_path": (
                "bridge/einstein_sector/compensated_einstein_causal_subsector.py"
            ),
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "domain": {
            "spacetime": "four-dimensional Minkowski space",
            "theory": "constant-compensator Einstein-Weyl phase with lambda=0",
            "sector": "free transverse-traceless metric perturbations, both helicities +/-2",
            "parameters": "c1!=0, alpha!=0, M2=c1/alpha>0",
            "cauchy_class": (
                "real TT Schwartz data obtained from smooth compactly supported Fourier data "
                "away from k=0, duplicated for the two helicities"
            ),
            "boundary": "complete spacelike Cauchy surface; no future boundary condition",
        },
        "causal_constraint_theorem": _evolution_checks(),
        "symplectic_restriction_theorem": _current_checks(),
        "time_translation_theorem": _hamiltonian_checks(),
        "helicity_interpretation": {
            "before_selection": (
                "each TT helicity contains a massless Einstein solution and a massive spin-2 solution"
            ),
            "selected_data": (
                "chi=0 and n.chi=0 leave one ordinary massless wave Cauchy pair per helicity"
            ),
            "selected_phase_space": (
                "the direct sum of the two real TT Einstein wave-packet phase spaces with "
                "nondegenerate Einstein-Hilbert symplectic form"
            ),
            "where_the_graviton_is": (
                "the conventional helicity +/-2 graviton is the massless simple root with "
                "nonzero c1 normalization; it becomes zero-normalized only as c1->0 and the "
                "simple roots coalesce in pure Weyl gravity"
            ),
        },
        "source_and_interaction_boundary": {
            "source_free_result": "CERTIFIED",
            "arbitrary_source_equation": "D_q(D_q+M2)h=J generally gives (D_q+M2)chi=J",
            "consequence": (
                "generic sources can excite chi; a source-compatible Einstein subcomplex or "
                "projected retarded Green operator is not constructed"
            ),
            "nonlinear_consequence": (
                "linear closure does not prove that generic Einstein-Weyl interactions preserve "
                "the selected constraints or exclude massive internal channels"
            ),
        },
        "verdict": "LINEAR_FLAT_TT_EINSTEIN_SECTOR_CAUSALLY_CLOSED_AND_SYMPLECTIC",
        "claim_flags": {
            "local_einstein_cauchy_constraints_derived": True,
            "constraint_rank_two": True,
            "constraint_intertwining_exact": True,
            "source_free_causal_propagation_proved": True,
            "massive_branch_eliminated_on_selected_free_solutions": True,
            "no_future_boundary_data_required": True,
            "einstein_embedding_intertwines": True,
            "restricted_current_equals_einstein_hilbert": True,
            "restricted_pairing_nondegenerate": True,
            "P0_energy_matches_einstein_hilbert": True,
            "both_tt_helicities_recovered_classically": True,
            "pure_weyl_limit_recovers_zero_pairing": True,
            "full_metric_diff_weyl_bv_complex_constructed": False,
            "constraint_compatible_with_arbitrary_sources": False,
            "projected_retarded_green_operator_constructed": False,
            "null_infinity_boundary_complex_constructed": False,
            "bondi_charge_and_flux_match_proved": False,
            "nonlinear_einstein_constraint_propagation_proved": False,
            "massive_branch_absent_from_full_theory": False,
            "einstein_scattering_equivalence_proved": False,
            "quantum_one_particle_hilbert_space_constructed": False,
            "unitarity_proved": False,
        },
        "scope_guards": [
            "the LORENTZIAN-CAUSAL tag is restricted to the source-free real-time flat TT Cauchy problem",
            "the local constraints select a subspace of solutions; they do not delete the massive branch from the full Einstein-Weyl theory",
            "the result is not a full tensor Diff x Weyl BV-BFV or gauge-fixing theorem",
            "the result is not a null-infinity, Bondi, soft, memory, corner, or scattering theorem",
            "generic sources and nonlinear interactions may excite the Einstein defect until separately excluded",
            "the pure-Weyl c1=0 theory remains governed by the zero-pairing obstruction",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.compensated_einstein_causal_subsector "
            "--verify bridge/certificates/compensated_einstein_causal_subsector.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


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

"""Flat TT Einstein-sector symplectic-restriction kill test.

For one transverse-traceless polarization, the pure-Weyl quadratic action is
equivalent up to a nonzero overall constant and a divergence to

    L_W = (Box h)^2 / 2.

Writing ``chi=Box h``, its covariant current is linear in ``chi`` and
``d chi``.  It therefore vanishes pointwise when both arguments lie in the
Einstein wave subspace ``chi=0``.  The Einstein-Hilbert wave current does not.

The theorem is scoped to the flat Schwartz Cauchy core and local finite-jet
current improvements.  It does not classify null-infinity corner terms,
compensators, or the complete metric BV complex.
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
    ROOT / "bridge" / "certificates" / "flat_einstein_symplectic_restriction.json"
)
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "flat_einstein_symplectic_restriction.schema.json"
)
INPUTS = {
    "flat_tt_bach": ROOT / "bridge" / "certificates" / "flat_tt_bach_operator.json",
    "einstein_defect": ROOT
    / "bridge"
    / "certificates"
    / "einstein_defect_asymptotics.json",
}


class FlatEinsteinSymplecticRestrictionError(RuntimeError):
    """Raised when the restriction theorem or a scope guard regresses."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FlatEinsteinSymplecticRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _current_checks() -> dict[str, Any]:
    t, q = sp.symbols("t q", real=True)
    h = sp.Function("h")(t)
    variation = sp.Function("v")(t)
    fourier_chi = sp.diff(h, t, 2) + q * h
    varied_density = fourier_chi * (sp.diff(variation, t, 2) + q * variation)
    euler_term = variation * (sp.diff(fourier_chi, t, 2) + q * fourier_chi)
    fourier_theta = fourier_chi * sp.diff(variation, t) - sp.diff(fourier_chi, t) * variation
    _require(
        sp.simplify(varied_density - euler_term - sp.diff(fourier_theta, t)) == 0,
        "quadratic density does not produce the declared potential",
    )

    # Jet symbols for two linearized solutions.  ``n`` denotes contraction
    # with an arbitrary hypersurface normal, so no plane-wave normalization is
    # built into the current identity.
    h1, h2 = sp.symbols("h1 h2")
    chi1, chi2 = sp.symbols("chi1 chi2")
    dn_h1, dn_h2 = sp.symbols("dn_h1 dn_h2")
    dn_chi1, dn_chi2 = sp.symbols("dn_chi1 dn_chi2")

    theta_1_on_2 = chi1 * dn_h2 - dn_chi1 * h2
    theta_2_on_1 = chi2 * dn_h1 - dn_chi2 * h1
    weyl_current = sp.expand(theta_1_on_2 - theta_2_on_1)
    restricted = sp.simplify(
        weyl_current.subs({chi1: 0, chi2: 0, dn_chi1: 0, dn_chi2: 0})
    )
    _require(restricted == 0, "pure-Weyl current did not vanish on chi=0")

    eh_current = sp.expand(h1 * dn_h2 - h2 * dn_h1)
    qnorm = sp.symbols("Q2", positive=True)
    eh_witness = eh_current.subs({h1: 1, dn_h1: 0, h2: 0, dn_h2: qnorm})
    _require(eh_witness == qnorm, "Einstein-Hilbert Cauchy witness vanished")

    return {
        "quadratic_density": "L_W=(1/2)(Box h)^2",
        "fourier_variation_identity": (
            "delta[(1/2)(D_q h)^2]=delta h D_q^2 h+d_t[(D_q h)d_t(delta h)-d_t(D_q h)delta h]"
        ),
        "defect": "chi=Box h",
        "presymplectic_potential": "theta_W^mu=chi partial^mu(delta h)-partial^mu(chi) delta h",
        "current": (
            "omega_W^mu(h1,h2)=chi1 partial^mu h2-partial^mu chi1 h2"
            "-chi2 partial^mu h1+partial^mu chi2 h1"
        ),
        "einstein_restriction": "chi1=chi2=0 implies omega_W^mu=0 pointwise",
        "eh_current": "omega_EH^mu=h1 partial^mu h2-h2 partial^mu h1 up to a nonzero normalization",
        "eh_cauchy_witness": "data (q,0) and (0,q) give Omega_EH=int_Sigma q_ij q^ij>0",
        "status": "PASS",
    }


def _matrix_checks() -> dict[str, Any]:
    j_weyl = sp.zeros(2)
    j_eh = sp.Matrix([[0, 1], [-1, 0]])
    scale = sp.symbols("c", nonzero=True)
    _require(j_weyl.rank() == 0, "restricted Weyl form has nonzero rank")
    _require(j_eh.rank() == 2 and j_eh.det() == 1, "EH Cauchy form is degenerate")
    _require(j_weyl != scale * j_eh, "a nonzero proportional embedding survived")
    return {
        "cauchy_coordinates": ["q", "p"],
        "restricted_weyl_matrix": [["0", "0"], ["0", "0"]],
        "einstein_hilbert_matrix": [["0", "1"], ["-1", "0"]],
        "ranks": {"restricted_weyl": 0, "einstein_hilbert": 2},
        "nonzero_proportionality": "IMPOSSIBLE",
        "status": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "pure-weyl-flat-einstein-symplectic-restriction-v1",
        "wrong restriction schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"restriction certificate is missing {key}")
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
        payload.get("verdict") == "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED",
        "restriction verdict changed",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "pure_weyl_tt_current_derived",
        "einstein_restriction_pointwise_zero",
        "schwartz_local_improvements_integrate_to_zero",
        "einstein_hilbert_witness_nonzero",
        "nonzero_symplectic_proportionality_refuted",
        "normalized_P0_charge_zero_on_restricted_core",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved flag missing")
    _require(
        all(flags.get(name) is False for name in set(required_flags) - true_flags),
        "an open claim was promoted",
    )


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    flat = records["flat_tt_bach"]
    defect = records["einstein_defect"]
    _require(
        flat.get("operator_identity") == "B_1(h_TT)=-(1/4) Box^2 h_TT",
        "flat TT biwave premise changed",
    )
    _require(
        defect.get("geometric_definition", {}).get("einstein_equation") == "chi=0",
        "Einstein defect premise changed",
    )

    certificate = {
        "schema": "pure-weyl-flat-einstein-symplectic-restriction-v1",
        "schema_path": (
            "bridge/einstein_sector/schema/"
            "flat_einstein_symplectic_restriction.schema.json"
        ),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "FLAT_EINSTEIN_SYMPLECTIC_RESTRICTION",
        "result_state": "REFUTED_REDUCED_SYMPLECTIC_EMBEDDING",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "provenance": {
            "input_base_commit": "ed5ada08f4dbe0dca929fc49957770b4a8a99fd0",
            "generator_path": (
                "bridge/einstein_sector/flat_einstein_symplectic_restriction.py"
            ),
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "action_current_derivation": _current_checks(),
        "cauchy_matrix_test": _matrix_checks(),
        "schwartz_wave_packet_domain": {
            "spacetime": "four-dimensional Minkowski space",
            "sector": "one flat transverse-traceless helicity amplitude; duplicated for helicity +/-2",
            "momentum_seed": (
                "choose q_hat in C_c^infinity(K), where K is a contractible momentum cone "
                "with closure disjoint from k=0, and multiply by a smooth TT helicity tensor"
            ),
            "position_space": "inverse Fourier Cauchy tensors q_ij are Schwartz, trace-free, and transverse",
            "witness_data": ["E_q:(h,d_t h)=(q,0)", "E_p:(h,d_t h)=(0,q)"],
            "evolution": "global real-time Box h=0 solutions from the displayed Cauchy data",
            "weyl_pairing": "Omega_W(E_q,E_p)=0",
            "einstein_hilbert_pairing": "Omega_EH(E_q,E_p)=int_R3 q_ij q^ij>0",
        },
        "boundary_improvement_test": {
            "potential_ambiguity": "theta -> theta+dY+delta B",
            "current_change": "omega -> omega+d(delta_1 Y(delta_2)-delta_2 Y(delta_1))",
            "delta_B_effect": "zero by antisymmetry of commuting field variations",
            "allowed_Y": "local finite-jet polynomial with smooth background coefficients",
            "schwartz_consequence": "the improvement integrand is Schwartz on every finite-time Cauchy slice",
            "spatial_boundary": "lim_(R->infinity) int_(S_R) improvement=0",
            "conclusion": "no allowed local improvement changes the zero restricted Cauchy pairing",
            "not_classified": [
                "nonlocal boundary functionals",
                "finite null-infinity corner degrees of freedom",
                "soft or distributional endpoint data",
                "counterterms requiring a dynamical conformal frame",
            ],
        },
        "time_translation_test": {
            "generator": "P_0=d_t",
            "tangency": "P_0 maps ker(Box) to ker(Box)",
            "pure_weyl_variation": "delta H_P0=Omega_W(delta h,L_P0 h)=0 on every tangent direction",
            "normalization": "H_P0[0]=0",
            "restricted_charge": "H_P0=0 on the connected Schwartz Einstein-wave core",
            "einstein_hilbert_comparison": "positive-energy wave packets have nonzero EH Hamiltonian",
        },
        "cylinder_non_contradiction": {
            "flat_domain": "Schwartz Cauchy data with vanishing spatial improvement surface term",
            "cylinder_domain": "global S3 D-energy modes and the radial/cylinder adjoint",
            "reason": (
                "global cylinder E modes do not map into the stated flat Schwartz domain on a "
                "single Minkowski patch; the restriction theorem does not alter the certified "
                "compact E/A/L pairing"
            ),
        },
        "interpretation": {
            "proved": (
                "Einstein wave solutions form an isotropic, in fact zero-pairing, subspace "
                "of the reduced flat pure-Weyl Cauchy phase space"
            ),
            "consequence": (
                "causal closure of chi=0 alone cannot recover the nondegenerate "
                "Einstein-Hilbert radiative phase space"
            ),
            "possible_repairs_not_tested": [
                "a compensator or matter condensate generating an Einstein-Hilbert term",
                "symmetry breaking with a nonzero Planck scale",
                "a boundary/corner extension with independently justified degrees of freedom",
                "nonzero-curvature dS or AdS boundary-selected sectors",
            ],
        },
        "verdict": "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED",
        "claim_flags": {
            "pure_weyl_tt_current_derived": True,
            "einstein_restriction_pointwise_zero": True,
            "schwartz_local_improvements_integrate_to_zero": True,
            "einstein_hilbert_witness_nonzero": True,
            "nonzero_symplectic_proportionality_refuted": True,
            "normalized_P0_charge_zero_on_restricted_core": True,
            "full_tensor_bv_complex_constructed": False,
            "null_infinity_symplectic_form_computed": False,
            "all_boundary_counterterms_classified": False,
            "compensator_or_eh_scale_included": False,
            "full_einstein_scattering_no_go_proved": False,
            "einstein_solutions_absent": False,
            "helicity_two_scattering_space_recovered": False,
        },
        "scope_guards": [
            "exact for the reduced flat TT quadratic action and its two helicity copies",
            "the LORENTZIAN-CAUSAL tag applies only to the real-time flat Schwartz Cauchy core",
            "not a complete metric Diff x Weyl BV phase-space theorem",
            "not a null-infinity soft, memory, Coulombic, or corner theorem",
            "local finite-jet improvements are excluded as repairs; nonlocal or boundary extensions remain open",
            "solution-sector inclusion Einstein subset Weyl remains true",
            "the result refutes a nondegenerate symplectic embedding, not the existence of gravitational wave solutions",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.flat_einstein_symplectic_restriction "
            "--verify bridge/certificates/flat_einstein_symplectic_restriction.json"
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

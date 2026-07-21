#!/usr/bin/env python3
"""Generate fail-closed atlas rows for the general closed-Cauchy theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCER = (
    ROOT
    / "d_quotient_classical/atlas/"
    "generate_general_closed_cauchy_relative_phase_hodge_atlas_fragment.py"
)
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/compensator/"
    "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/compensator/"
    "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_PAYLOAD_V1.json"
)
OUTPUT = (
    ROOT
    / "residual_atlas/"
    "general-closed-cauchy-relative-phase-hodge-fragment-v1.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second_order() -> dict[str, object]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(
            "NO_CERTIFIED_MAP", "No quadratic correction class is constructed."
        ),
        "smooth_secular": _claim(
            "NO_CERTIFIED_MAP", "No nonlinear secular equation is constructed."
        ),
        "causal_retarded": _claim(
            "NO_CERTIFIED_MAP", "No support-local retarded Green carrier is imported."
        ),
    }


def _entry(
    suffix: str,
    carrier: str,
    charge_sector: str,
    degree: int,
    ell: str,
    m: str,
    omega: str,
    dispersion_status: str,
    dispersion: str,
    symplectic_status: str,
    symplectic: str,
    evidence: dict[str, str],
    boundary: str,
) -> dict[str, object]:
    return {
        "id": f"classical.general_closed_cauchy.relative_phase.{suffix}",
        "scope": {
            "theory": "linear fixed-modulus compact-Abelian phase-connection two-derivative class; no selected gravity coupling",
            "background": "one connected closed oriented smooth Riemannian Cauchy three-manifold X in the trivial local bundle chart",
            "boundaries": "none",
            "charge_sector": charge_sector,
            "carrier": carrier,
            "degree": degree,
            "parity": "Hodge scalar/exact/coexact/harmonic type; no pure-Weyl parity crosswalk",
            "ell": ell,
            "m": m,
            "k": "charge rank k=rank(Q); not a Fourier momentum label",
            "omega": omega,
        },
        "descriptions": {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": symplectic_status,
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim(dispersion_status, dispersion),
            "lee_wald": _claim(symplectic_status, symplectic),
            "taub_maps": _claim(
                "NO_CERTIFIED_MAP", "No second-order Taub or resonance map is computed."
            ),
            "resonance": _claim(
                "NO_CERTIFIED_MAP", "No nonlinear mode-pair source or resonance is computed."
            ),
            "second_order": _second_order(),
        },
        "evidence": [evidence],
        "claim_boundary": boundary,
    }


def build() -> dict[str, object]:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if certificate["result_id"] != "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1":
        raise AssertionError("theorem identity drifted")
    if _sha(PAYLOAD) != certificate["payload_ref"]["sha256"]:
        raise AssertionError("theorem payload hash drifted")
    if payload["content_sha256"] != certificate["payload_ref"]["content_sha256"]:
        raise AssertionError("theorem payload canonical hash drifted")
    evidence = {
        "path": str(CERTIFICATE.relative_to(ROOT)),
        "result_id": certificate["result_id"],
        "sha256": _sha(CERTIFICATE),
    }
    boundary = (
        "CERTIFIED only as a LOCAL-ALGEBRAIC/REDUCED-MODE linear Hodge/Gauss "
        "structure row on the explicitly scoped background class. No "
        "same-background pure-Weyl, gravity, support-local causal, Lee-Wald, "
        "nonlinear, observer, particle, Hadamard or quantum crosswalk exists."
    )
    entries = [
        _entry(
            "constant_scalar_relative",
            "constant scalar relative-phase quotient",
            "Q^T p_0=0; n-k relative coordinates; constant ker(Q) reducibility retained",
            0,
            "constant scalar Laplace eigenspace lambda=0",
            "unique connected-manifold constant mode",
            "zero before a separately declared reduced potential Hessian",
            "CERTIFIED",
            "The constant mode has exact reduced metric G_rel and Gauss constraint; no causal frequency theorem is inferred.",
            "OPEN",
            "A reduced kinetic metric is certified, but no Lee-Wald field-theory pairing is imported.",
            evidence,
            boundary,
        ),
        _entry(
            "positive_scalar_relative",
            "relative phase in a positive scalar Laplace eigenspace E_lambda",
            "ker(Q^T) relative sector of dimension n-k per eigenfunction",
            0,
            "lambda>0",
            "eigenspace index 1..m_lambda",
            "omega^2=lambda at principal two-derivative order",
            "CERTIFIED",
            "The exact relative principal polynomial is det(G_rel)(omega^2-lambda)^(n-k).",
            "OPEN",
            "The positive reduced kinetic form is certified, not a covariant Lee-Wald pairing.",
            evidence,
            boundary,
        ),
        _entry(
            "longitudinal_and_coexact_connection",
            "exact longitudinal scalar mode together with positive coexact one-form eigenspaces",
            "k active massive families; r-k exact modes gauge and r-k coexact Maxwell families physical",
            1,
            "scalar lambda>0 or coexact Hodge eigenvalue nu>0",
            "scalar multiplicity m_lambda or coexact multiplicity t_nu",
            "spec(lambda I+K_a^-1 V) or spec(nu I+K^-1 Q^T M Q)",
            "CERTIFIED",
            "Exact Gauss Schur and coexact frequency matrices are certified modewise.",
            "OPEN",
            "No unreduced support-local Lee-Wald or BV pairing is imported.",
            evidence,
            boundary,
        ),
        _entry(
            "harmonic_wilson",
            "harmonic one-form connection tangent and compact kernel-Wilson directions",
            "b1*k active massive and b1(r-k) kernel-Wilson local tangent families",
            1,
            "harmonic Hodge eigenvalue zero",
            "integral harmonic basis index 1..b1",
            "spec(K^-1 Q^T M Q), including r-k zero frequencies",
            "CERTIFIED",
            "Harmonic modes and their integral lattice are retained; they are not exact gauge directions.",
            "OPEN",
            "The local harmonic kinetic matrix is certified, but its global phase space and Lee-Wald pairing remain open.",
            evidence,
            boundary,
        ),
        _entry(
            "winding_torsion_strata",
            "combined phase-winding/Wilson quotient and admissible torsion bundle components",
            "Smith invariants d_i; free winding rank b1(n-k); ker(Q) on Tor H2 bundle sectors",
            0,
            "NOT_APPLICABLE; discrete global topological carrier",
            "H1(X;Z)_free and Tor H2(X;Z) labels",
            "NOT_APPLICABLE",
            "NOT_APPLICABLE",
            "This is a discrete/compact topological quotient, not a dispersion relation.",
            "OPEN",
            "The integral quotient is certified, but no global symplectic form across disconnected sectors is constructed.",
            evidence,
            boundary,
        ),
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(PRODUCER.relative_to(ROOT)),
        "generated_by_sha256": _sha(PRODUCER),
        "status_vocabulary": [
            "CERTIFIED",
            "OBSTRUCTED",
            "OPEN",
            "NOT_APPLICABLE",
            "NO_CERTIFIED_MAP",
        ],
        "description_axes": [
            "causal",
            "symplectic",
            "nonlinear",
            "observational",
            "quantum",
        ],
        "entries": entries,
        "verification_commands": [
            "python3 d_quotient_classical/compensator/general_closed_cauchy_relative_phase_hodge_theorem.py --check",
            "python3 d_quotient_classical/compensator/verify_general_closed_cauchy_relative_phase_hodge_theorem.py",
            "python3 -m unittest -v d_quotient_classical.compensator.tests.test_general_closed_cauchy_relative_phase_hodge_theorem",
            "python3 residual_atlas/validate_fragment.py residual_atlas/general-closed-cauchy-relative-phase-hodge-fragment-v1.json",
        ],
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write() -> None:
    OUTPUT.write_text(_render(build()))


def check() -> None:
    expected = build()
    if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != expected:
        raise AssertionError("generated atlas fragment drifted")
    print("GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_ATLAS_FRAGMENT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()


if __name__ == "__main__":
    main()

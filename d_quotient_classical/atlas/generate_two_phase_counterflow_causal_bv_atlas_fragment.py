#!/usr/bin/env python3
"""Generate fail-closed atlas rows for the 70-component causal BV parent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_causal_bv_atlas_fragment.py"
CERTIFICATE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-causal-bv-parent-fragment-v1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _entry(suffix: str, charge: str, carrier: str, omega: str, causal_status: str, statement: str, evidence: dict[str, str]) -> dict[str, object]:
    return {
        "id": f"classical.two_phase_counterflow_causal.{suffix}",
        "scope": {
            "theory": "selected two-phase counterflow action with auxiliary diagonal U1 and separate Weyl scale quartet",
            "background": "stationary Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": charge,
            "carrier": carrier,
            "degree": 0,
            "parity": "full BV carrier; mode parity not identified with pure-Weyl residual parity",
            "ell": "all S3 Hodge sectors including scalar constants",
            "m": "all allowed degeneracy labels",
            "k": "NOT_APPLICABLE",
            "omega": omega,
        },
        "descriptions": {"causal": causal_status, "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
        "mode_data": {
            "dispersion": _claim(causal_status, statement),
            "lee_wald": _claim("CERTIFIED", "The real cyclic BV pairing and transported relative-clock current are certified on the same carrier."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No selected-action q2 tangent-cone map is imported."),
            "resonance": _claim("NO_CERTIFIED_MAP", "No nonlinear resonance computation is imported."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "No second-order correction is constructed."),
                "smooth_secular": _claim("NO_CERTIFIED_MAP", "No secular correction is constructed."),
                "causal_retarded": _claim("OPEN", "The unary retarded carrier is certified; the nonlinear source and q2 are not."),
            },
        },
        "evidence": [evidence],
        "claim_boundary": "Same-background classical LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL q1 carrier only. No observer, q2, Einstein-source, Hadamard, particle or quantum map is certified.",
    }


def build() -> dict[str, object]:
    result = json.loads(CERTIFICATE.read_text())
    if result["result_state"] != "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT":
        raise AssertionError("causal parent not certified")
    evidence = {"path": str(CERTIFICATE.relative_to(ROOT)), "result_id": result["result_id"], "sha256": _sha(CERTIFICATE)}
    entries = [
        _entry("gravity_clock_parent", "fixed Q_rel leaf; Q_diag=0", "complete real cyclic 70-component gauge-fixed BV carrier", "operator-valued all-mode spectrum", "CERTIFIED", "Advanced and retarded chain homotopies exist on every row without a spatial inverse.", evidence),
        _entry("relative_phase", "fixed Q_rel leaf, with scalar constant mode retained", "physical relative phase psi in the imported Berger clock block", "Hodge scalar wave spectrum on Berger S3", "CERTIFIED", "The positive relative clock and its conserved current are transported with normalization mu_squared=1.", evidence),
        _entry("diagonal_u1_quartet", "Q_diag=0 by local Gauss", "16-component algebraic diagonal-U1 minimal/nonminimal quartet", "NOT_APPLICABLE", "CERTIFIED", "The diagonal sector is support-locally contractible by B=A-dchi; no Coulomb inverse or propagating particle is introduced.", evidence),
        _entry("unrestricted_d_charge", "unrestricted union of Q_rel leaves", "D=K+Omega R_rel orbit", "NOT_APPLICABLE", "OBSTRUCTED", "The causal Cartan identity exists, but unrestricted D remains globally charged and is not a gauge quotient direction.", evidence),
    ]
    return {"schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "classical", "generated_by": str(PRODUCER.relative_to(ROOT)), "generated_by_sha256": _sha(PRODUCER), "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"], "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"], "entries": entries, "verification_commands": ["python3 d_quotient_classical/compensator/two_phase_counterflow_causal_bv_parent.py --check", "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_causal_bv_parent.py", "python3 -m unittest -v d_quotient_classical.compensator.tests.test_two_phase_counterflow_causal_bv_parent", "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-causal-bv-parent-fragment-v1.json"]}


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write() -> None:
    OUTPUT.write_text(_render(build()))


def check() -> None:
    if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != build():
        raise AssertionError("atlas fragment drifted")
    print("TWO_PHASE_COUNTERFLOW_CAUSAL_BV_ATLAS_FRAGMENT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()

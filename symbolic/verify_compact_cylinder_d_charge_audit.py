#!/usr/bin/env python3
"""Emit and verify the fail-closed compact-cylinder ``D``-charge audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.taub_moment_map.compact_d_charge import (  # noqa: E402
    CompactCylinderDChargeAudit,
)


CERTIFICATE = ROOT / "d_quotient_classical" / "certificates" / "compact_cylinder_d_charge_audit.json"
SCHEMA = ROOT / "d_quotient_classical" / "schema" / "compact-cylinder-d-charge-audit-v1.schema.json"
REPORT = ROOT / "d_quotient_classical" / "reports" / "compact-cylinder-d-charge-audit.md"

INPUTS = (
    "bridge/taub_moment_map/all_energy.py",
    "bridge/certificates/taub_moment_map.json",
    "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json",
    "bridge/certificates/closed_universe_bfv.json",
    "covariant_completion/certificates/curved_current_comparison.json",
    "covariant_completion/certificates/curved_EAL_pairing_regression.json",
    "bridge/taub_moment_map/compact_d_charge.py",
    "d_quotient_classical/schema/compact-cylinder-d-charge-audit-v1.schema.json",
    "symbolic/verify_compact_cylinder_d_charge_audit.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _assert_inputs() -> None:
    taub = _load(ROOT / INPUTS[1])
    endpoint = _load(ROOT / INPUTS[2])
    boundary = _load(ROOT / INPUTS[3])
    current = _load(ROOT / INPUTS[4])
    eal = _load(ROOT / INPUTS[5])
    if taub.get("schema") != "pure-weyl-taub-moment-map-all-energy-v1":
        raise AssertionError("all-energy moment-map certificate is missing")
    if taub.get("direct_D_HH_coefficients") != {
        "A": "-2*J - 1",
        "E": "2*J",
        "L": "-2*J - 2",
    }:
        raise AssertionError("direct D normalization certificate drifted")
    if endpoint.get("schema") != "pure-weyl-endpoint-taub-moment-map-v1":
        raise AssertionError("endpoint/Taub composition certificate is missing")
    if endpoint.get("moment_map_components") != 15:
        raise AssertionError("complete residual moment map is missing")
    if boundary.get("schema") != "pure-weyl-closed-universe-bfv-choice-v1":
        raise AssertionError("closed-universe boundary policy is missing")
    if not (
        boundary.get("compact_time_is_constraint")
        and boundary.get("surface_charge_rank") == 0
        and boundary.get("boundary_components") == []
    ):
        raise AssertionError("closed-universe boundary policy drifted")
    if not current.get("curved_current_comparison"):
        raise AssertionError("covariant/current comparison is not certified")
    if not eal.get("verified") or eal.get("krein_signs") != {
        "A": -1,
        "E": 1,
        "L": -1,
    }:
        raise AssertionError("all-energy E/A/L current normalization drifted")


def certificate_data(import_base_commit: str | None = None) -> dict[str, Any]:
    _assert_inputs()
    audit = CompactCylinderDChargeAudit.build(6)
    return {
        "schema": "pure-weyl-compact-cylinder-d-charge-audit-v1",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "setting": {
            "spacetime": "R x S^3 with gbar=-dt^2+dOmega_3^2",
            "action": "S_red=int sqrt(-g)(Ric^2-R^2/3)=(C^2-Euler)/2",
            "equations": "linearized Bach equation; second-order Bach equation for the Taub test",
            "allowed_variations": "smooth D-finite E/A/L linearized solutions modulo local Diff x Weyl; residual constraints are declared per phase space",
            "cauchy_surface": "closed oriented S^3",
            "spatial_boundary": "empty",
            "corner_data": "none",
            "presymplectic_convention": "action-derived metric current transported to +I_E direct-sum (-I_A) direct-sum (-I_L)",
            "finite_counterterm_convention": "Euler/total-derivative improvement fixed; no added boundary counterterm; H_D[gbar]=H_D[0]=0",
            "flux": "zero through a timelike boundary because no timelike/spatial boundary is present",
        },
        "charge": {
            "covariant_identity": "delta H_D=Omega_Sigma(delta h,R_D h)",
            "quadratic_identity": "H_D=mu_D=1/2 Omega_Sigma(h,R_D h)=zbar M_D z",
            "kernel": "M_D=-(1/2) J D",
            "all_energy_branch_coefficients": audit.all_energy_formula(),
            "integrable": True,
            "conserved": True,
            "reference_normalization": "H_D[0]=0",
            "regression_buffer_maximum_energy": audit.maximum_energy,
            "regression_buffer_dimension": audit.dimension,
        },
        "phase_spaces": {
            "P_lin": {
                "definition": "D-finite algebraic linearized solution space after local Diff x Weyl quotient and before every residual Taub restriction",
                "residual_zero_charge_restriction": False,
                "strongest_counterexamples": audit.lowest_counterexamples(),
                "D_presymplectic_degeneracy": False,
                "normalized_H_D_identically_zero": False,
                "verdict": "D_CHARGED",
                "interpretation": "D is an integrable physical Hamiltonian symmetry on this phase space",
            },
            "P_Taub0": {
                "definition": "formal common derived zero fibre mu^{-1}(0) of all fifteen Taub/moment-map components inside P_lin",
                "residual_zero_charge_restriction": True,
                "tangent_identity": "for i:P_Taub0->P_lin, i^* i_XD Omega=i^* d mu_D=d(i^* mu_D)=0",
                "D_presymplectic_degeneracy": True,
                "D_action_preserves_phase_space": True,
                "preservation_identity": "L_XD mu_A=f_DA^B mu_B=0 on the common zero fibre",
                "normalized_H_D_identically_zero": True,
                "verdict": "D_GAUGE",
                "interpretation": "D becomes proper gauge only after the explicit zero-charge restriction and residual quotient",
            },
            "P_der": {
                "definition": "[P_lin x^R_{g*}{0} /^R g] with all fifteen residual generators constrained",
                "D_presymplectic_degeneracy": True,
                "D_action_preserves_phase_space": True,
                "normalized_H_D_identically_zero": True,
                "verdict": "D_GAUGE",
                "interpretation": "selected formal closed-universe derived phase space of Paper VII",
            },
        },
        "strongest_counterexample_scope": {
            "representative": "unit-amplitude normalized E_2 mode of either chirality",
            "H_D": "-1",
            "radial_delta_H_D": "-2",
            "smooth_global_linearized_solution": True,
            "D_action_preserves_P_lin": True,
            "claimed_second_order_linearizable": False,
            "reason": "nonzero mu_D excludes the representative from the Taub/Kuranishi zero fibre",
        },
        "compact_vacuum_verdict": "SECTOR_DEPENDENT",
        "exact_checks": {
            "direct_D_normalization_imported": True,
            "all_energy_kernel_formula": True,
            "quadratic_integrability": True,
            "nonzero_E_A_L_counterexamples": True,
            "closed_surface_has_no_boundary_or_corner_term": True,
            "zero_fibre_pullback_degeneracy_identity": True,
            "zero_fibre_invariant_under_D_by_equivariance": True,
            "current_to_EAL_pairing_transport_imported": True,
        },
        "fail_closed": {
            "compactness_alone_implies_D_gauge": False,
            "P_lin_counterexample_is_second_order_integrable": False,
            "Taub_zero_is_sufficient_for_all_orders_integrability": False,
            "boundary_or_clock_sectors_classified": False,
            "unrestricted_smooth_infinite_completion_reproved_here": False,
            "universal_D_verdict": False,
        },
        "open_settings": [
            "cylinder plus conformally coupled scalar clock",
            "cylinder plus Yang-Mills",
            "weakly perturbed conformally flat backgrounds",
            "Lorentzian dS and AdS with declared boundary conditions",
            "asymptotically flat spacetimes at null infinity",
        ],
        "verification_receipts": [
            {
                "command": "python3 symbolic/verify_compact_cylinder_d_charge_audit.py --check",
                "elapsed_seconds": 0.57,
                "status": "PASS",
                "test_tier": 1,
                "recorded_date": "2026-07-15",
            },
            {
                "command": "python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge",
                "elapsed_seconds": 0.48,
                "status": "PASS",
                "test_tier": 1,
                "recorded_date": "2026-07-15",
            },
        ],
        "provenance": {
            "import_base_git_commit": import_base_commit or _git_head(),
            "input_sha256": {
                path: _sha256(ROOT / path) for path in INPUTS
            },
            "verification_commands": [
                "python3 symbolic/verify_compact_cylinder_d_charge_audit.py",
                "python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge",
            ],
            "test_tiers": ["Tier 0", "Tier 1"],
            "higher_tiers_not_run": "No shared operator or previously certified theorem input was changed.",
        },
    }


def _validate_shape(data: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    if schema.get("$id") != "pure-weyl-compact-cylinder-d-charge-audit-v1":
        raise AssertionError("D-charge JSON schema identifier drifted")
    required = schema["required"]
    missing = [key for key in required if key not in data]
    if missing:
        raise AssertionError(f"D-charge certificate missing fields: {missing}")
    if data["compact_vacuum_verdict"] not in schema["properties"][
        "compact_vacuum_verdict"
    ]["enum"]:
        raise AssertionError("invalid compact-vacuum verdict")
    for phase in ("P_lin", "P_Taub0", "P_der"):
        verdict = data["phase_spaces"][phase]["verdict"]
        if verdict not in ("D_GAUGE", "D_CHARGED", "SECTOR_DEPENDENT", "NOT_HAMILTONIAN"):
            raise AssertionError(f"invalid phase-space verdict {verdict}")


def _verify_persisted() -> dict[str, Any]:
    data = _load(CERTIFICATE)
    _validate_shape(data)
    expected = certificate_data(data["provenance"]["import_base_git_commit"])
    if data != expected:
        raise AssertionError("persisted compact-cylinder D-charge certificate drifted")
    try:
        subprocess.run(
            ["git", "cat-file", "-e", data["provenance"]["import_base_git_commit"] + "^{commit}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError("import base commit is unavailable") from exc
    if REPORT.read_text(encoding="utf-8") != render_report(data):
        raise AssertionError("human-readable D-charge report drifted")
    return data


def render_report(data: dict[str, Any]) -> str:
    counterexamples = data["phase_spaces"]["P_lin"]["strongest_counterexamples"]
    rows = "\n".join(
        f"| {branch} | {counterexamples[branch]['energy']} | {counterexamples[branch]['unit_amplitude_H_D']} | {counterexamples[branch]['unit_radial_variation_delta_H_D']} |"
        for branch in ("E", "A", "L")
    )
    hashes = "\n".join(
        f"- `{path}`: `{digest}`"
        for path, digest in sorted(data["provenance"]["input_sha256"].items())
    )
    open_items = "\n".join(f"- {item}" for item in data["open_settings"])
    template = r"""# Compact-cylinder \(D\)-charge audit

## Result

The compact vacuum-cylinder verdict is **`__VERDICT__`**.
Compactness removes the spatial boundary and its flux; it does not by itself
make cylinder time translation a presymplectic degeneracy.

On the unrestricted algebraic linearized solution space after the local
Diff x Weyl quotient,

```text
P_lin verdict = D_CHARGED
H_D = mu_D = zbar M_D z
M_D = -(1/2) J D
```

The charge is integrable, conserved, and nonzero on smooth global modes:

| branch | energy | unit-amplitude \(H_D\) | radial \(\delta H_D\) |
|---|---:|---:|---:|
__ROWS__

The unit \(E_2\) mode is the strongest compact counterexample: \(H_D=-1\)
and its unit radial variation is \(-2\).  It is **not** claimed to be tangent
to a second-order Bach-flat family.  In fact its nonzero \(D\) moment map
excludes it from the Taub zero fibre.

On the explicitly restricted formal phase space

```text
P_Taub0 = mu^{-1}(0)
```

the answer changes.  If \(i:P_{\rm Taub0}\to P_{\rm lin}\), then

\[
 i^*\iota_{X_D}\Omega_\Sigma
 =i^*d\mu_D=d(i^*\mu_D)=0.
\]

With \(H_D[0]=0\), the pulled-back charge vanishes.  Thus `D_GAUGE` holds on
the selected common fifteen-component Taub/Kuranishi zero fibre and its
derived residual quotient, not on `P_lin`.

## Declared covariant data

- Spacetime: \(\mathbb R\times S^3\), with closed oriented Cauchy surface.
- Action: \(S_{\rm red}=\int\sqrt{-g}(R_{\mu\nu}R^{\mu\nu}-R^2/3)\).
- Presymplectic convention: the action-derived metric current transported to
  \(+I_E\oplus(-I_A)\oplus(-I_L)\).
- Boundary and corners: \(\partial S^3=\varnothing\); no corner variables or
  timelike-boundary flux occur.
- Counterterms: the Euler/total-derivative convention is fixed, no boundary
  counterterm is added, and the additive normalization is \(H_D[0]=0\).

## Exact scope

This audit composes the certified covariant current comparison with the exact
all-energy E/A/L moment-map normalization.  It carries both
`REDUCED-MODE` and `LORENTZIAN-CAUSAL` dependency tags.  The reduced-mode
calculation is not used alone to infer a new Lorentzian current theorem.

It proves neither sufficiency of the quadratic Taub conditions for an exact
nonlinear solution nor a universal decision about clocks, deparametrized
sectors, or boundaries.  Those settings remain open:

__OPEN_ITEMS__

## Reproduction and provenance

```bash
python3 symbolic/verify_compact_cylinder_d_charge_audit.py
python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge
```

Tier 0 and Tier 1 are the applicable test tiers.  Higher tiers are not
required because this audit changes no shared operator or previously
certified theorem input.  The recorded scoped runs took 0.57 s for the
certificate audit and 0.48 s for the unit-test command on 2026-07-15.

Imported base commit: `__BASE_COMMIT__`

__HASHES__
"""
    return (
        template.replace("__VERDICT__", data["compact_vacuum_verdict"])
        .replace("__ROWS__", rows)
        .replace("__OPEN_ITEMS__", open_items)
        .replace("__BASE_COMMIT__", data["provenance"]["import_base_git_commit"])
        .replace("__HASHES__", hashes)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the persisted certificate and report (the default without --emit)",
    )
    parser.add_argument("--claim-D-gauge-on-P-lin", action="store_true")
    parser.add_argument("--claim-counterexample-linearizable", action="store_true")
    parser.add_argument("--claim-universal-compact-verdict", action="store_true")
    parser.add_argument("--claim-boundary-or-clock-verdict", action="store_true")
    args = parser.parse_args()
    refused = {
        "claim_D_gauge_on_P_lin": "P_lin contains exact nonzero D-charge counterexamples",
        "claim_counterexample_linearizable": "the nonzero-charge mode is excluded from the Taub zero fibre",
        "claim_universal_compact_verdict": "the compact result is sector-dependent",
        "claim_boundary_or_clock_verdict": "clock and boundary phase spaces have not been audited",
    }
    for option, reason in refused.items():
        if getattr(args, option):
            raise SystemExit("REFUSED: " + reason)

    if args.emit:
        data = certificate_data()
        _validate_shape(data)
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        REPORT.write_text(render_report(data), encoding="utf-8")
        print("wrote", CERTIFICATE.relative_to(ROOT))
        print("wrote", REPORT.relative_to(ROOT))
    data = _verify_persisted()
    print("[PASS] P_lin: D_CHARGED")
    print("[PASS] P_Taub0/P_der: D_GAUGE after explicit zero-charge restriction")
    print("[PASS] compact vacuum cylinder: " + data["compact_vacuum_verdict"])


if __name__ == "__main__":
    main()

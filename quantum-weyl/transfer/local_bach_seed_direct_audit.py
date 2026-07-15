"""Direct Tier-2 curvature reevaluation for the two HT1b local seeds.

Unlike the fast HT1b certificate, this audit calls the exact three-wave
curvature engine.  Six forward probes reconstruct the two local Taub
densities and two reverse slice probes establish the density-level adjoint
relation.  Reverse gauge probes are not exported, so no reverse local Taub
density is claimed.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
for search_root in (ROOT, TRANSFER_ROOT):
    if str(search_root) not in sys.path:
        sys.path.insert(0, str(search_root))

from symbolic.verify_conformal_quartic_currents import calculate_probe
from local_bach_seed_lift import (
    OUTPUT_PATH as SEED_CERTIFICATE_PATH,
    _canonical_hash,
    _exact,
    _parse_exact_scalar,
)


OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "HT1B_DIRECT_CURVATURE_AUDIT.json"
SCHEMA_PATH = TRANSFER_ROOT / "schema" / "local-bach-seed-direct-audit-v1.schema.json"

UPSTREAM_PATHS = (
    "symbolic/verify_conformal_quartic_contact.py",
    "symbolic/verify_conformal_quartic_currents.py",
    "symbolic/verify_conformal_quartic_exchange.py",
    "symbolic/verify_conformal_quartic_hessian.py",
    "symbolic/verify_conformal_taub_charge.py",
    "quantum-weyl/transfer/local_bach_seed_lift.py",
    "quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json",
)

PROBE_SPECS = (
    ("negative", "slice", False, False),
    ("negative", "gauge-0", False, False),
    ("negative", "gauge-1", False, False),
    ("positive", "slice", False, False),
    ("positive", "gauge-0", False, False),
    ("positive", "gauge-1", False, False),
    ("negative", "slice", True, False),
    ("positive", "slice", True, False),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_radial(expression: sp.Expr) -> sp.Expr:
    tangent = sp.symbols("t", positive=True, real=True)
    radial = [
        symbol
        for symbol in expression.free_symbols
        if symbol.name in {"radial_tangent", "t"}
    ]
    if len(radial) > 1:
        raise ValueError("direct curvature result has multiple radial coordinates")
    if radial:
        expression = expression.subs(radial[0], tangent)
    return sp.factor(expression)


def _run_probe(spec: tuple[str, str, bool, bool]) -> dict[str, object]:
    side, probe, reverse, parity = spec
    density, measured, coefficient, amplitude = calculate_probe(
        "t", side, probe, reverse=reverse, parity=parity
    )
    return {
        "side": side,
        "probe": probe,
        "reverse": reverse,
        "parity": parity,
        "local_radial_density": _exact(_canonical_radial(density)),
        "measured_stereographic_integrand": _exact(_canonical_radial(measured)),
        "integrated_action_coefficient": _exact(coefficient),
        "reduced_amplitude": None if probe != "slice" else _exact(amplitude),
        "execution_kind": "DIRECT_EXACT_CURVATURE_ENGINE",
    }


def _probe_index(results: list[dict[str, object]]) -> dict[tuple[str, str, bool], dict[str, object]]:
    return {
        (str(result["side"]), str(result["probe"]), bool(result["reverse"])): result
        for result in results
    }


def _parse_probe_scalar(result: dict[str, object], key: str) -> sp.Expr:
    return _parse_exact_scalar(result.get(key), f"direct audit {key}")


def _reconstructed_seed(
    index: dict[tuple[str, str, bool], dict[str, object]], side: str
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    signed_frequency = -1 if side == "negative" else 1
    slice_result = index[(side, "slice", False)]
    gauge0_result = index[(side, "gauge-0", False)]
    gauge1_result = index[(side, "gauge-1", False)]
    local_density = sp.factor(
        (
            -2 * sp.I * signed_frequency
            * _parse_probe_scalar(slice_result, "local_radial_density")
            - 2 * _parse_probe_scalar(gauge0_result, "local_radial_density")
            - sp.I * signed_frequency
            * _parse_probe_scalar(gauge1_result, "local_radial_density")
        )
        / 2
    )
    tangent = next(iter(local_density.free_symbols))
    measured = sp.factor(2 * local_density / (1 + tangent**2))
    charge = sp.simplify(
        8 * sp.pi**2 * sp.integrate(measured, (tangent, 0, sp.oo))
    )
    return local_density, measured, charge


def validate_direct_audit(certificate: object, seed_certificate: object) -> None:
    """Verify direct outputs, reconstruction, adjointness, and provenance."""

    if not isinstance(certificate, dict) or not isinstance(seed_certificate, dict):
        raise ValueError("HT1b direct curvature audit is malformed")
    if certificate.get("result_state") != "DIRECT_CURVATURE_REEVALUATED_SELECTED_HT1B_SEEDS":
        raise ValueError("HT1b direct curvature audit lifecycle changed")
    if certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise ValueError("HT1b direct curvature audit dependency boundary changed")
    if certificate.get("direct_curvature_reevaluated_in_this_certificate") is not True:
        raise ValueError("HT1b direct curvature audit lacks a direct-execution claim")
    results = certificate.get("direct_probe_results")
    if not isinstance(results, list) or len(results) != len(PROBE_SPECS):
        raise ValueError("HT1b direct curvature audit probe ledger is incomplete")
    actual_specs = [
        (result.get("side"), result.get("probe"), result.get("reverse"), result.get("parity"))
        for result in results
        if isinstance(result, dict)
    ]
    if actual_specs != list(PROBE_SPECS):
        raise ValueError("HT1b direct curvature audit probe ordering changed")
    tangent = sp.symbols("t", positive=True, real=True)
    for result in results:
        if not isinstance(result, dict) or result.get("execution_kind") != "DIRECT_EXACT_CURVATURE_ENGINE":
            raise ValueError("HT1b audit contains a non-direct probe")
        density = _parse_probe_scalar(result, "local_radial_density")
        measured = _parse_probe_scalar(result, "measured_stereographic_integrand")
        coefficient = _parse_probe_scalar(result, "integrated_action_coefficient")
        if sp.cancel(measured - 2 * density / (1 + tangent**2)) != 0:
            raise ValueError("HT1b direct probe measure identity failed")
        integrated = sp.simplify(
            8 * sp.pi**2 * sp.integrate(measured, (tangent, 0, sp.oo))
        )
        if integrated != coefficient:
            raise ValueError("HT1b direct probe density does not reproduce its coefficient")

    seed_payload = seed_certificate.get("seed_payload")
    if not isinstance(seed_payload, dict):
        raise ValueError("HT1b direct curvature audit lacks its seed input")
    if certificate.get("input_seed_payload_sha256") != _canonical_hash(seed_payload):
        raise ValueError("HT1b direct curvature audit seed payload hash mismatch")
    seed_channels = {
        str(channel["channel_id"]).split("_", 1)[0]: channel
        for channel in seed_payload["direct_local_channels"]
    }
    index = _probe_index(results)
    for side in ("negative", "positive"):
        density, measured, charge = _reconstructed_seed(index, side)
        seed = seed_channels[side]
        if density != _parse_exact_scalar(seed["local_radial_density"], "seed density"):
            raise ValueError("HT1b direct curvature density disagrees with the fast seed")
        if measured != _parse_exact_scalar(seed["measured_stereographic_integrand"], "seed measure"):
            raise ValueError("HT1b direct curvature measure disagrees with the fast seed")
        if charge != _parse_exact_scalar(seed["integrated_taub_charge"], "seed charge"):
            raise ValueError("HT1b direct curvature charge disagrees with the fast seed")

    for side, opposite in (("negative", "positive"), ("positive", "negative")):
        reverse_density = _parse_probe_scalar(
            index[(side, "slice", True)], "local_radial_density"
        )
        forward_density = _parse_probe_scalar(
            index[(opposite, "slice", False)], "local_radial_density"
        )
        if sp.simplify(reverse_density - sp.conjugate(forward_density)) != 0:
            raise ValueError("HT1b reverse slice lost its density-level adjoint relation")
    if certificate.get("checks", {}).get("reverse_slice_density_adjoint") != "VERIFIED_EXACT":
        raise ValueError("HT1b reverse slice adjoint was not certified")
    if certificate.get("checks", {}).get("reverse_local_taub_density") != "NOT_COMPUTED_MISSING_REVERSE_GAUGE_PROBES":
        raise ValueError("HT1b reverse local Taub density was over-promoted")

    provenance = certificate.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("HT1b direct curvature audit provenance is missing")
    for manifest_key, root in (
        ("upstream_sha256", ROOT),
        ("implementation_sha256", TRANSFER_ROOT),
    ):
        manifest = provenance.get(manifest_key)
        if not isinstance(manifest, dict) or any(
            _sha256(root / path) != digest for path, digest in manifest.items()
        ):
            raise ValueError(f"HT1b direct audit {manifest_key} content hash mismatch")
        expected_manifest_hash = provenance.get(
            manifest_key.replace("sha256", "manifest_sha256")
        )
        if _canonical_hash(manifest) != expected_manifest_hash:
            raise ValueError(f"HT1b direct audit {manifest_key} manifest hash mismatch")


def build_direct_audit(jobs: int = 1) -> dict[str, Any]:
    if jobs < 1:
        raise ValueError("HT1b direct audit requires at least one worker")
    seed_certificate = json.loads(SEED_CERTIFICATE_PATH.read_text(encoding="utf-8"))
    if jobs == 1:
        results = [_run_probe(spec) for spec in PROBE_SPECS]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_run_probe, PROBE_SPECS))
    upstream_hashes = {path: _sha256(ROOT / path) for path in UPSTREAM_PATHS}
    implementation_paths = (
        "local_bach_seed_direct_audit.py",
        "schema/local-bach-seed-direct-audit-v1.schema.json",
        "tests/test_local_bach_seed_direct_audit.py",
    )
    implementation_hashes = {
        path: _sha256(TRANSFER_ROOT / path) for path in implementation_paths
    }
    certificate = {
        "result_id": "HT1B_DIRECT_CURVATURE_AUDIT",
        "result_state": "DIRECT_CURVATURE_REEVALUATED_SELECTED_HT1B_SEEDS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "direct_curvature_reevaluated_in_this_certificate": True,
        "input_seed_payload_sha256": seed_certificate["seed_payload_sha256"],
        "direct_probe_results": results,
        "checks": {
            "forward_direct_probe_count": 6,
            "reverse_direct_slice_probe_count": 2,
            "forward_local_taub_density_reconstruction": "VERIFIED_EXACT_TWO_CHANNELS",
            "reverse_slice_density_adjoint": "VERIFIED_EXACT",
            "reverse_local_taub_density": "NOT_COMPUTED_MISSING_REVERSE_GAUGE_PROBES",
            "arbitrary_input_bilinear_bach_tensor": "NOT_COMPUTED",
        },
        "claim_guards": [
            "direct reevaluation covers two mode-specialized forward Taub densities, not arbitrary inputs",
            "the reverse density-level adjoint is certified only for slice currents because reverse gauge probes are absent",
            "no ghost, antifield, quantum, or LORENTZIAN-CAUSAL claim is made",
        ],
        "provenance": {
            "upstream_sha256": upstream_hashes,
            "upstream_manifest_sha256": _canonical_hash(upstream_hashes),
            "implementation_sha256": implementation_hashes,
            "implementation_manifest_sha256": _canonical_hash(implementation_hashes),
            "schema": "quantum-weyl/transfer/schema/local-bach-seed-direct-audit-v1.schema.json",
        },
    }
    validate_direct_audit(certificate, seed_certificate)
    return certificate


def render_certificate(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    content = render_certificate(build_direct_audit(args.jobs))
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"HT1b direct curvature audit is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("HT1B DIRECT CURVATURE AUDIT: EIGHT EXACT PROBES PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

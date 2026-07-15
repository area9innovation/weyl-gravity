"""Certify the first support-local metric-sector seeds for HT1b.

The repository does not yet export the general tensor
``B^(2)_{mu nu}[h_1,h_2]``.  It does contain two independent mixed curvature
runs in the proper-conformal channel.  Each run retains the exact local
stereographic radial density before integration.  This module binds those
densities to their integrated Taub charges and then, entry by entry, to the
raw-normalized kernels underlying the selected residual cubic bracket.

This is a genuine local-lift seed, not the complete support-local ``q2``.
The missing arbitrary-input tensor and its ghost/antifield completions keep
the quadratic classical-master identity fail-closed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.taub_moment_map import (
    AllEnergyTaubMomentMap,
    RAW_CK_TO_CANONICAL_SCALE,
)
from symbolic.verify_conformal_quartic_currents import CurrentPair, channel_pairs
from symbolic.verify_conformal_taub_charge import (
    charge_from_slice,
    forward_taub_result,
    low_energy_charge_matrices,
)


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "HT1B_LOCAL_BACH_SEED_LIFT.json"
SCHEMA_PATH = TRANSFER_ROOT / "schema" / "local-bach-seed-lift-v1.schema.json"
HT1_PATH = TRANSFER_ROOT / "certificates" / "HT1_RESIDUAL_CUBIC_BLOCK.json"

UPSTREAM_PATHS = (
    "bridge/taub_moment_map/all_energy.py",
    "bridge/certificates/taub_moment_map.json",
    "symbolic/verify_conformal_quartic_contact.py",
    "symbolic/verify_conformal_quartic_currents.py",
    "symbolic/verify_conformal_quartic_exchange.py",
    "symbolic/verify_conformal_quartic_hessian.py",
    "symbolic/verify_conformal_taub_charge.py",
    "symbolic/verify_conformal_taub_moment_map_all_levels.py",
    "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json",
    "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json",
    "quantum-weyl/transfer/certificates/HT1_RESIDUAL_CUBIC_BLOCK.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _exact(value: sp.Expr) -> str:
    if value.atoms(sp.Float):
        raise ValueError("HT1b local Bach seed contains floating-point data")
    return sp.srepr(sp.factor(value))


def _matrix_payload(matrix: sp.MatrixBase) -> dict[str, object]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "scalar_format": "sympy-srepr-exact-v1",
        "entries": [
            [int(row), int(column), _exact(value)]
            for (row, column), value in sorted(matrix.todok().items())
            if value != 0
        ],
    }


def _mode_payload(pair: CurrentPair) -> list[dict[str, object]]:
    return [
        {
            "family": oriented.mode.family,
            "energy": oriented.mode.frequency,
            "chirality": _exact(oriented.mode.chirality),
            "magnetic_left": _exact(oriented.mode.magnetic_left),
            "magnetic_right": _exact(oriented.mode.magnetic_right),
            "polarization": "bra" if oriented.bra else "ket",
            "signed_frequency": oriented.signed_frequency,
        }
        for oriented in pair.modes
    ]


def _state_index(
    taub: AllEnergyTaubMomentMap,
    family: str,
    energy: int,
    chirality: sp.Expr,
    magnetic: tuple[sp.Expr, sp.Expr],
) -> int:
    space = taub.plus if chirality > 0 else taub.minus
    offset = 0 if chirality > 0 else taub.plus.dimension
    label = f"{family}{energy}"
    mode = next(item for item in space.irreps if item.label == label)
    return offset + space.offsets[label] + mode.basis.index(magnetic)


def _payload_matrix_entry(
    payload: dict[str, Any], label: str, row: int, column: int
) -> sp.Expr:
    matrix = payload["q2"]["matter_matter_to_ghost_momentum"]["matrices"][label]
    matches = [
        scalar
        for entry_row, entry_column, scalar in matrix["entries"]
        if entry_row == row and entry_column == column
    ]
    if len(matches) != 1 or "Float" in matches[0]:
        raise AssertionError(f"HT1 payload lacks one exact {label}[{row},{column}] entry")
    value = sp.sympify(matches[0])
    if value.atoms(sp.Float):
        raise AssertionError("HT1 payload matrix entry is not exact")
    return value


def _seed_channel(
    taub: AllEnergyTaubMomentMap,
    ht1_payload: dict[str, Any],
    side: str,
    pair: CurrentPair,
) -> dict[str, object]:
    signed_frequency = pair.signed_frequency
    if signed_frequency not in (-1, 1):
        raise AssertionError("proper-conformal seed has the wrong frequency")
    result = forward_taub_result(signed_frequency)
    bra, ket = pair.modes
    if not bra.bra or ket.bra:
        raise AssertionError("direct seed is not in the declared mixed polarization")
    row = _state_index(
        taub,
        bra.mode.family,
        bra.mode.frequency,
        bra.mode.chirality,
        (bra.mode.magnetic_left, bra.mode.magnetic_right),
    )
    column = _state_index(
        taub,
        ket.mode.family,
        ket.mode.frequency,
        ket.mode.chirality,
        (ket.mode.magnetic_left, ket.mode.magnetic_right),
    )

    # The scalar CK harmonic labels the dual component.  The charge kernel
    # therefore carries the opposite magnetic pair in the repository's
    # Condon--Shortley convention.
    component = (
        -pair.scalar_magnetic_left,
        -pair.scalar_magnetic_right,
    )
    family = "K-" if signed_frequency == -1 else "K+"
    kernels = taub.lowering_kernels if family == "K-" else taub.raising_kernels
    canonical_entry = sp.simplify(kernels[component][row, column])
    raw_entry = sp.simplify(RAW_CK_TO_CANONICAL_SCALE * canonical_entry)
    payload_label = f"{family}_{component[0]}_{component[1]}"
    serialized_entry = _payload_matrix_entry(
        ht1_payload, payload_label, row, column
    )
    if canonical_entry != serialized_entry:
        raise AssertionError("HT1 portable kernel disagrees with the Taub implementation")
    if raw_entry != result.charge:
        raise AssertionError("direct local Bach seed does not equal the residual kernel entry")

    return {
        "channel_id": f"{side}_{ket.mode.family}{ket.mode.frequency}_to_{bra.mode.family}{bra.mode.frequency}",
        "support_scope": "mode-specialized local stereographic radial density before S3 integration",
        "bilinear_taylor_convention": "coefficient of a*b in E(gbar+a*h1+b*h2)",
        "external_modes": _mode_payload(pair),
        "ck_scalar_magnetic": [
            _exact(pair.scalar_magnetic_left),
            _exact(pair.scalar_magnetic_right),
        ],
        "kernel_magnetic_component": [_exact(component[0]), _exact(component[1])],
        "residual_kernel_label": payload_label,
        "residual_matrix_coordinate": [row, column],
        "local_radial_density": _exact(result.local_density),
        "measured_stereographic_integrand": _exact(result.measured_integrand),
        "slice_coefficient": _exact(result.slice_coefficient),
        "integrated_taub_charge": _exact(result.charge),
        "canonical_residual_kernel_entry": _exact(canonical_entry),
        "raw_ck_to_canonical_scale": _exact(RAW_CK_TO_CANONICAL_SCALE),
        "raw_residual_kernel_entry": _exact(raw_entry),
        "checks": {
            "local_density_integrates_to_taub_charge": "VERIFIED_EXACT",
            "raw_residual_kernel_entry_equals_taub_charge": "VERIFIED_EXACT",
            "checked_in_ht1_payload_entry_equals_regenerated_kernel": "VERIFIED_EXACT",
        },
    }


def build_certificate(maximum_energy: int = 4) -> dict[str, Any]:
    if maximum_energy != 4:
        raise ValueError("HT1b seed lift is pinned to the certified energy-four buffer")
    ht1 = json.loads(HT1_PATH.read_text(encoding="utf-8"))
    if ht1["checks"]["cubic_master_equation"]["status"] != "VERIFIED_EXACT_CUBIC_MASTER_EQUATION":
        raise AssertionError("HT1 residual cubic master equation is not certified")
    taub = AllEnergyTaubMomentMap.build(maximum_energy)
    pairs = channel_pairs()["t"]
    channels = [
        _seed_channel(taub, ht1["transfer_payload"], "negative", pairs.negative),
        _seed_channel(taub, ht1["transfer_payload"], "positive", pairs.positive),
    ]
    if len({item["integrated_taub_charge"] for item in channels}) != 2:
        raise AssertionError("the two direct local Bach seeds are not independent")

    q_minus, q_plus = low_energy_charge_matrices()
    if q_plus != q_minus.conjugate().T:
        raise AssertionError("reverse integrated curvature channels lost the dagger relation")
    parity_equal = all(
        charge_from_slice(signed_frequency, reverse=reverse, parity=True)
        == charge_from_slice(signed_frequency, reverse=reverse, parity=False)
        for signed_frequency in (-1, 1)
        for reverse in (False, True)
    )
    if not parity_equal:
        raise AssertionError("parity-related integrated curvature seeds disagree")

    seed_payload = {
        "schema_version": 1,
        "scalar_format": "sympy-srepr-exact-v1",
        "radial_coordinate": "t=tan(beta/2), t in (0,infinity)",
        "s3_integration_formula": "8*pi^2*integral_0^infinity measured_stereographic_integrand dt",
        "direct_local_channels": channels,
        "integrated_reverse_completion": {
            "ordered_basis": ["E_+", "A_+", "A_-", "L_-"],
            "K_minus_raw_matrix": _matrix_payload(q_minus),
            "K_plus_raw_matrix": _matrix_payload(q_plus),
            "dagger_relation": "VERIFIED_EXACT",
            "parity_seed_equality": "VERIFIED_EXACT",
            "support_local_density_available_for_reverse_channels": False,
        },
    }
    upstream_hashes = {path: _sha256(ROOT / path) for path in UPSTREAM_PATHS}
    implementation_paths = (
        "local_bach_seed_lift.py",
        "local_bach_seed_certificate.py",
        "schema/local-bach-seed-lift-v1.schema.json",
        "tests/test_local_bach_seed_lift.py",
    )
    implementation_hashes = {
        path: _sha256(TRANSFER_ROOT / path) for path in implementation_paths
    }
    certificate = {
        "result_id": "HT1B_LOCAL_BACH_SEED_LIFT",
        "result_state": "LOCAL_METRIC_SEEDS_COMPUTED_FULL_BV_LIFT_BLOCKED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "category": "mode-specialized local metric-sector quadratic Bach seeds",
        "seed_payload": seed_payload,
        "seed_payload_sha256": _canonical_hash(seed_payload),
        "checks": {
            "direct_local_density_channel_count": len(channels),
            "integrated_raw_kernel_entry_count": sum(
                len(matrix.todok()) for matrix in (q_minus, q_plus)
            ),
            "selected_projection_to_residual_q2": "VERIFIED_2_DIRECT_LOCAL_CHANNELS",
            "selected_residual_cubic_master_equation": "VERIFIED_UPSTREAM",
            "local_q1_q2_chain_identity": "NOT_COMPUTED_MISSING_ARBITRARY_INPUT_Q2_AND_COMPLETIONS",
            "full_support_local_q2": "NOT_COMPUTED",
            "ghost_completion": "NOT_COMPUTED",
            "antifield_completion": "NOT_COMPUTED",
        },
        "established": [
            "two independent mixed B^(2) curvature channels retain exact local radial densities before integration",
            "each local density integrates exactly to its action-normalized Taub charge",
            "both direct charges equal the corresponding raw-normalized entries of the checked-in HT1 residual q2 payload",
            "the four integrated forward/reverse entries obey the exact dagger relation and parity-seed equality",
        ],
        "claim_guards": [
            "mode-specialized radial densities are not the arbitrary-support tensor B^(2)_{mu nu}[h1,h2]",
            "equivariant reconstruction of fifteen residual kernels is not direct local evaluation of fifteen Bach-source components",
            "the quadratic classical-master identity is not claimed without the full q1, q2 ghost rows, and antifield rows",
            "HT1b is not complete and HT2 transfer is not unblocked by this seed certificate alone",
            "this is not a quantum correction or a LORENTZIAN-CAUSAL result",
        ],
        "next_required_exports": [
            "arbitrary-input bilinear Bach tensor B^(2)_{mu nu}[h1,h2] in a portable local basis",
            "Diff and Weyl ghost-metric q2 rows",
            "antifield q2 rows fixed by the classical master equation",
            "portable local q1 and contraction maps pi_cl, iota_cl, s_cl",
            "exact arity-two chain identity and full projection comparison",
        ],
        "provenance": {
            "upstream_sha256": upstream_hashes,
            "upstream_manifest_sha256": _canonical_hash(upstream_hashes),
            "implementation_sha256": implementation_hashes,
            "implementation_manifest_sha256": _canonical_hash(implementation_hashes),
            "schema": "quantum-weyl/transfer/schema/local-bach-seed-lift-v1.schema.json",
        },
    }
    validate_certificate(certificate)
    return certificate


def validate_certificate(certificate: object) -> None:
    """Fail closed on payload, provenance, or claim-boundary changes."""

    if not isinstance(certificate, dict):
        raise ValueError("HT1b local Bach seed certificate is not an object")
    if certificate.get("result_state") != "LOCAL_METRIC_SEEDS_COMPUTED_FULL_BV_LIFT_BLOCKED":
        raise ValueError("HT1b local Bach seed lifecycle was over-promoted")
    if certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise ValueError("HT1b local Bach seed dependency boundary changed")
    payload = certificate.get("seed_payload")
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("HT1b local Bach seed payload is missing")
    if _canonical_hash(payload) != certificate.get("seed_payload_sha256"):
        raise ValueError("HT1b local Bach seed payload hash mismatch")
    channels = payload.get("direct_local_channels")
    if not isinstance(channels, list) or len(channels) != 2:
        raise ValueError("HT1b requires exactly two direct local seed channels")
    for channel in channels:
        if not isinstance(channel, dict):
            raise ValueError("HT1b local seed channel is malformed")
        for key in (
            "local_radial_density",
            "measured_stereographic_integrand",
            "integrated_taub_charge",
            "canonical_residual_kernel_entry",
            "raw_residual_kernel_entry",
        ):
            scalar = channel.get(key)
            if not isinstance(scalar, str) or "Float" in scalar or sp.sympify(scalar).atoms(sp.Float):
                raise ValueError("HT1b local seed contains non-exact scalar data")
        if channel.get("integrated_taub_charge") != channel.get("raw_residual_kernel_entry"):
            raise ValueError("HT1b direct local integral no longer equals its residual entry")
    checks = certificate.get("checks")
    if not isinstance(checks, dict) or any(
        checks.get(key) != "NOT_COMPUTED"
        for key in ("full_support_local_q2", "ghost_completion", "antifield_completion")
    ):
        raise ValueError("HT1b missing local BV sectors were over-promoted")
    if checks.get("local_q1_q2_chain_identity") != "NOT_COMPUTED_MISSING_ARBITRARY_INPUT_Q2_AND_COMPLETIONS":
        raise ValueError("HT1b local classical-master identity was over-promoted")
    provenance = certificate.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("HT1b provenance is missing")
    for manifest_key, root in (
        ("upstream_sha256", ROOT),
        ("implementation_sha256", TRANSFER_ROOT),
    ):
        manifest = provenance.get(manifest_key)
        if not isinstance(manifest, dict) or any(
            _sha256(root / path) != digest for path, digest in manifest.items()
        ):
            raise ValueError(f"HT1b {manifest_key} content hash mismatch")
        if _canonical_hash(manifest) != provenance.get(manifest_key.replace("sha256", "manifest_sha256")):
            raise ValueError(f"HT1b {manifest_key} manifest hash mismatch")


def render_certificate(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"

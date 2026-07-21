"""Independent verifier for the cylinder derived BFV/Koszul assembly."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/CYLINDER_DERIVED_BFV_KOSZUL_TIME_SLICE_CARRIER_V1.json"
ATLAS = ROOT / "residual_atlas/cylinder-derived-bfv-koszul-time-slice-carrier-fragment-v1.json"
SCHEMA = ROOT / "bridge/anomaly_restriction/schema/cylinder-derived-bfv-koszul-time-slice-carrier-v1.schema.json"

EXPECTED_HASHES = {
    "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json": "4863e00186e719e933e20fe58f2bc0429b1cb0a13db8481b6f8152680b3255fb",
    "bridge/certificates/residual_bfv.json": "f7c73355ec9712283e30693ca6f4b53a67ed0638ae366bee76c0c10e632a81ac",
    "bridge/certificates/closed_universe_bfv.json": "37eda8319d7fbe69e6b0838677b3d7fd4aecddd8b6274c281fefc2cf3f612ceb",
    "bridge/certificates/full_hpl_transfer.json": "18acc197a45ba9256e0979e7b04c0cd5e7ca36de94b7540aa2038fc1f9e3511a",
    "bridge/certificates/metric_to_residual.json": "25bd2b6c3ac31139bda9bcee6ad18f2df69a73cea3ec102b66ff310b1644f8c3",
    "bridge/certificates/taub_moment_map.json": "84fb8d94043f89fcd70e8fdd2940b266ea6f9006c3ff94cb55884b1b4ceb46e1",
    "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json": "72ac747c0b15c85c75f7a86d983960f305e486c96ab594c056f9b3377cfbf540",
    "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json": "dfe70f8bf6ad6820178e67247a06b1c27fefba3c5b7396ba42fd14e96db82b53",
    "quantum-weyl/transfer/certificates/HT1_RESIDUAL_CUBIC_BLOCK.json": "802ea86e1bb807476c7e1bbbe25f33435fa1a79ba433c1b0943b19c4986eefc4",
    "quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json": "f08976200d4e07dc4fb349fa785c960ab4aa8a0d685fc82fe1a2cb30c5ff26c5",
    "quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json": "2c03b184f27d6f0054ed12029b052834ef08aa8bf4f2c42663f84617f0e63063",
    "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json": "a7730a34b21d2068cc73e46c563ce929195a3d9a7c7626d3843788b54e0592b3",
    "d_quotient_classical/certificates/compact_cylinder_d_charge_audit.json": "6e609dd850049fb7b85867033dbdce0b2b214f2d5196665015f8e2b552d493e4",
}


class IndependentCylinderCarrierError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentCylinderCarrierError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


NAMES = (
    "D",
    *(f"R{a}{b}" for a, b in combinations(range(4), 2)),
    *(f"K+_{a}" for a in range(4)),
    *(f"K-_{a}" for a in range(4)),
)


def _add(output: dict[str, Fraction], name: str | None, value: Fraction | int) -> None:
    if name is None or value == 0:
        return
    output[name] = output.get(name, Fraction()) + Fraction(value)
    if output[name] == 0:
        del output[name]


def _rotation(a: int, b: int) -> tuple[str | None, int]:
    if a == b:
        return None, 0
    return (f"R{a}{b}", 1) if a < b else (f"R{b}{a}", -1)


def _positive_bracket(first: str, second: str, mutate: bool) -> dict[str, Fraction]:
    if first == "D" and second.startswith("K"):
        return {second: Fraction(1 if second.startswith("K+") else -1)}
    if first.startswith("R") and second.startswith("R"):
        a, b, c, d = int(first[1]), int(first[2]), int(second[1]), int(second[2])
        out: dict[str, Fraction] = {}
        for coefficient, left, right in ((b == c, a, d), (-(a == c), b, d), (-(b == d), a, c), (a == d, b, c)):
            name, sign = _rotation(left, right)
            _add(out, name, int(coefficient) * sign)
        return out
    if first.startswith("R") and second.startswith("K"):
        a, b, index = int(first[1]), int(first[2]), int(second[-1])
        sign = "+" if second.startswith("K+") else "-"
        out: dict[str, Fraction] = {}
        _add(out, f"K{sign}_{a}", int(b == index))
        _add(out, f"K{sign}_{b}", -int(a == index))
        return out
    if first.startswith("K+") and second.startswith("K-"):
        a, b = int(first[-1]), int(second[-1])
        out: dict[str, Fraction] = {}
        name, sign = _rotation(a, b)
        _add(out, name, 2 * sign)
        _add(out, "D", (1 if mutate else 2) * int(a == b))
        return out
    return {}


def _bracket(first: str, second: str, mutate: bool = False) -> dict[str, Fraction]:
    if first == second:
        return {}
    ordered = _positive_bracket(first, second, mutate)
    if ordered:
        return ordered
    reverse = _positive_bracket(second, first, mutate)
    return {name: -value for name, value in reverse.items()}


def _bracket_linear(first: dict[str, Fraction], second: str, mutate: bool) -> dict[str, Fraction]:
    out: dict[str, Fraction] = {}
    for name, coefficient in first.items():
        for target, value in _bracket(name, second, mutate).items():
            _add(out, target, coefficient * value)
    return out


def _jacobi_defects(mutate: bool = False) -> int:
    defects = 0
    for a in NAMES:
        for b in NAMES:
            for c in NAMES:
                out: dict[str, Fraction] = {}
                for left, right in ((_bracket(a, b, mutate), c), (_bracket(b, c, mutate), a), (_bracket(c, a, mutate), b)):
                    for name, value in _bracket_linear(left, right, mutate).items():
                        _add(out, name, value)
                defects += int(bool(out))
    return defects


def _independent_geometry_and_algebra() -> None:
    _require(len(NAMES) == 15 and len(set(NAMES)) == 15, "real conformal basis changed")
    _require(_jacobi_defects(False) == 0, "independent so(4,2) Jacobi check failed")
    _require(_jacobi_defects(True) > 0, "decisive conformal coefficient mutation survived")
    # R x unit-S3: only the spatial constant-curvature block contributes.
    riemann_squared = 12
    ricci_squared = 12
    scalar = 6
    c_squared = riemann_squared - 2 * ricci_squared + scalar**2 // 3
    euler = riemann_squared - 4 * ricci_squared + scalar**2
    _require(c_squared == 0 and euler == 0, "cylinder background invariants changed")


def verify_certificate(certificate_path: Path = CERTIFICATE, atlas_path: Path = ATLAS) -> None:
    payload = _load(certificate_path)
    jsonschema.Draft202012Validator(_load(SCHEMA)).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")
    imported = {row["path"]: row["sha256"] for row in payload["provenance"]["imported_artifacts"]}
    _require(imported == EXPECTED_HASHES, "input ledger changed")
    for relative, expected in EXPECTED_HASHES.items():
        _require(_sha256(ROOT / relative) == expected, f"input hash drift: {relative}")
    _independent_geometry_and_algebra()

    carrier = payload["derived_carrier"]
    _require(carrier["constraint_count"] == 15, "constraint count changed")
    _require(carrier["generators"]["eta_A_equals_b_A"]["ghost_free_differential"] == "d_K eta_A=mu_A", "Koszul differential changed")
    _require(carrier["nilpotency"]["jacobi_defects"] == 0, "upstream Jacobi defects")
    _require(carrier["nilpotency"]["representation_defects"] == 0, "upstream representation defects")
    _require(carrier["nilpotency"]["moment_map_equivariance_defects"] == 0, "upstream moment-map defects")

    ledger = payload["chain_map_ledger"]
    _require(ledger["endpoint_to_BFV_ghost_momentum"]["normalization"] == "1", "transgression normalization changed")
    _require(ledger["support_local_full_BV_bulk_to_slice"]["status"] == "OBSTRUCTED", "support-local obstruction promoted")
    _require(ledger["support_local_full_BV_bulk_to_slice"]["witnesses"]["full_support_local_q2"] == "NOT_COMPUTED", "support-local q2 appeared without a new input")
    orders = {row["class_id"]: row["first_metric_order"] for row in payload["anomaly_perturbative_orders"]}
    _require(orders == {"ANOM_OMEGA_C2": 2, "ANOM_OMEGA_E4": 1, "ANOM_OMEGA_C_DUAL_C": 2}, "anomaly metric orders changed")

    classification = payload["classification"]
    _require(classification["fifteen_generator_intrinsic_derived_carrier_certified"] is True, "carrier not certified")
    for key in (
        "support_local_full_BV_time_slice_chain_map_certified",
        "local_anomaly_representatives_mapped_to_carrier",
        "local_anomaly_receiver_cohomology_verdict_assigned",
        "full_higher_syzygy_resolution_certified",
        "lorentzian_causal_claim",
        "quantum_claim",
    ):
        _require(classification[key] is False, f"forbidden promotion: {key}")

    atlas = _load(atlas_path)
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(certificate_path), "atlas evidence hash drift")
    _require(entry["descriptions"]["nonlinear"] == "OBSTRUCTED", "atlas nonlinear status changed")
    _require(entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP", "atlas quantum status changed")


def main() -> int:
    verify_certificate()
    print("independent cylinder derived BFV/Koszul carrier verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

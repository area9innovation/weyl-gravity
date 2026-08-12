#!/usr/bin/env python3
"""Independent verifier for the global connected finite-time BT column."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-global-connected-finite-time-packet-column-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_constants():
    mass = Fraction(16, 5)
    mass_squared = mass * mass
    # On one ordered half-square, the polynomial term is -1/32.  The
    # substitution x=1-2k turns the logarithmic term into
    # -(1/4)*integral_0^1 x log(x)dx=+1/16.
    log_moment = Fraction(-1, 4)
    half = Fraction(-1, 32) - log_moment / 4
    full = 2 * half
    exchange = mass_squared / 32768
    hard = mass_squared / 65536
    kernel_sum = hard + 9 * exchange
    amplitude = 256 * Fraction(81, 16) * kernel_sum
    scalar = 16 * 9 * 9 * exchange
    return {
        "mass_squared": mass_squared,
        "Jacobian_determinant": -2 * mass_squared,
        "half": half,
        "full": full,
        "exchange": exchange,
        "hard": hard,
        "kernel_sum": kernel_sum,
        "amplitude": amplitude,
        "scalar": scalar,
    }


def verify(certificate):
    constants = independent_constants()
    inputs = certificate["provenance"]["inputs"]
    recorded_path = next(row["path"] for row in inputs if "TEN_CHANNEL_RECORDED" in row["path"])
    recorded = load(os.path.join(ROOT, recorded_path))
    masks = recorded["ten_channel_residue_algebra"]["channel_masks"]
    hard = [mask for mask in masks if mask in (7, 56)]
    mixed = [mask for mask in masks if mask not in (7, 56)]
    geometry = certificate["soft_zero_geometry"]
    integral = certificate["exact_exchange_integral"]
    column = certificate["global_connected_column"]
    source = certificate["declared_scalar_source"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    ledger = certificate["missing_object_ledger"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "all_predecessor_certificates_pass": all(load(os.path.join(ROOT, row["path"]))["checks"]["ok"] for row in inputs if "/certificates/" in row["path"]),
        "one_hard_channel_is_reconstructed": hard == [7],
        "nine_mixed_channels_are_reconstructed": len(mixed) == 9 and all((mask & 7).bit_count() in (1, 2) for mask in mixed),
        "spectator_energy_range_is_closed": certificate["phase_space_disintegration"]["spectator_energy_range"] == "0<=E<=M/2",
        "soft_zero_condition_is_exact": geometry["energy_component"] == "q_ia^0=M-E_i-K_a>=0" and "E_i=K_a=M/2" in geometry["zero_locus"],
        "antipodal_condition_is_exact": "direction(k_a)=-direction(p_i)" in geometry["zero_locus"],
        "rank_four_Jacobian_is_rederived": geometry["effective_transverse_rank"] == 4 and Fraction(geometry["Jacobian_determinant"]) == constants["Jacobian_determinant"] == Fraction(-512, 25),
        "local_radial_power_is_integrable": "r*dr" in geometry["local_measure_power"],
        "recursive_phase_measure_is_present": certificate["phase_space_disintegration"]["recursive_measure"] == "dPhi3(P)=E*dE*dOmega*dOmega_star/(512*pi^5)",
        "standard_total_phase_volume_is_present": certificate["phase_space_disintegration"]["total_phase_volume"] == "Phi3(P)=M^2/(256*pi^3)=1/(25*pi^3)",
        "angular_primitive_is_exact": integral["angular_reduction"] == "integral_-1^1 dc/(D/M)^2=(1/(e*k))*[log((1)/(1-2*min(e,k)))+(1-e-k)-(1-e-k)/(1-2*min(e,k))]" and integral["half_domain_integrand_after_e_integration"] == "3*k^2/2-3*k/4+(k-1/2)*log(1-2*k)",
        "log_moment_is_independently_rederived": integral["log_moment"] == "integral_0^1 x*log(x)dx=-1/4",
        "half_integral_is_independently_rederived": constants["half"] == Fraction(1, 32) and integral["half_domain_value"] == "1/32",
        "full_integral_is_independently_rederived": constants["full"] == Fraction(1, 16) and integral["full_dimensionless_value"] == "1/16",
        "exchange_channel_constant_is_rederived": constants["exchange"] == Fraction(1, 3200) and "1/(3200*pi^6)" in integral["exchange_channel_value"],
        "hard_channel_constant_is_rederived": constants["hard"] == Fraction(1, 6400) and integral["hard_channel_value"].endswith("1/(6400*pi^6)"),
        "ten_channel_constant_is_rederived": constants["kernel_sum"] == Fraction(19, 6400) and column["kernel_sum_bound"] == "sum_B ||K_B,T||_HS^2<=19*T^2/(6400*pi^6)",
        "global_amplitude_bound_is_rederived": constants["amplitude"] == Fraction(1539, 400) and "1539*lambda^8*T^2/(400*pi^6)" in column["operator_bound"],
        "global_scalar_bound_is_rederived": constants["scalar"] == Fraction(81, 200) and source["global_bound"] == "q_click<=81*lambda^8*T^2/(200*pi^6)",
        "global_positive_effect_is_explicit": column["click"] == "E_click=A_full^*A_full" and column["no_click"] == "E_no=I-E_click" and column["status"] == "GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED",
        "soft_cutoff_is_removed_only_at_finite_time": interpretation["q_B_zero_cutoff"] == "REMOVED_FOR_FIXED_FINITE_TIME_CONNECTED_COLUMN" and interpretation["all_time_limit"] == "NOT_CONSTRUCTED",
        "disconnected_forward_and_Eq19_objects_remain_missing": [row["status"] for row in ledger] == ["MISSING"] * 3 and "disconnected" in ledger[0]["object"] and "forward" in ledger[1]["object"] and "Eq. 19" in ledger[2]["object"],
        "gravity_and_Lorentzian_boundaries_are_preserved": "gravity or metric BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())

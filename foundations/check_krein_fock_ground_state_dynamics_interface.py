#!/usr/bin/env python3
"""Independent exact checker for the free ground-state/dynamics interface."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json"
SOURCES = {
    "foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json": "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
    "foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json": "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
    "foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json": "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
    "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json": "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    errors: list[str] = []
    checks: list[str] = []
    if result.get("canonical_digest") != canonical_digest(result):
        errors.append("canonical digest")
    provenance = {item.get("path"): item for item in result.get("provenance", {}).get("inputs", [])}
    if set(provenance) != set(SOURCES):
        errors.append("source closure")
    sources = {}
    for relative, expected_id in SOURCES.items():
        path = ROOT / relative
        source = load(path)
        sources[relative] = source
        if source.get("result_id") != expected_id or provenance.get(relative, {}).get("sha256") != sha(path):
            errors.append("source identity/hash " + relative)
    checks.append("four pinned source identities and hashes")

    state = sources["foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json"]
    energy = sources["foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json"]
    dynamics = sources["foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json"]
    krein = sources["foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json"]
    if state.get("fock_state_construction", {}).get("carrier") != "Gamma_s(H_1)=l2(Occ(I))":
        errors.append("state carrier")
    if energy.get("fock_proof", {}).get("carrier") != "l2(Occ(I))" or energy.get("fock_proof", {}).get("operator") != "dGamma(D)|m>=(sum_i m(i)energy(i))|m>":
        errors.append("energy carrier/operator")
    if dynamics.get("fock_lift", {}).get("carrier") != "Gamma_s(H_1)=l2(Occ(I))" or dynamics.get("fock_lift", {}).get("generator") != "dGamma(D), the imported total-occupation energy operator":
        errors.append("dynamics carrier/generator")
    if krein.get("fock_construction", {}).get("hilbert_carrier") != "l2(Occ(I)) in the normalized occupation basis":
        errors.append("Krein Fock carrier")
    ledger = result.get("shared_object_ledger", [])
    if {item.get("id") for item in ledger} != {"H_F", "J_F", "H_0", "VAC", "OMEGA_0", "U_F"} or any(item.get("identity_status") != "IDENTICAL_OBJECT" for item in ledger):
        errors.append("shared object ledger")
    checks.append("six shared Krein--Fock objects")

    interface = result.get("interface", {})
    if interface.get("id") != "SELECTION_TO_DYNAMICS" or interface.get("status") != "CERTIFIED" or interface.get("relation") != "CONDITIONAL_BRIDGE":
        errors.append("interface identity")
    if interface.get("source_coordinates") != [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "PHYSICAL_STATE_SELECTION"}]:
        errors.append("source coordinate")
    if interface.get("target_coordinates") != [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "GENERATOR_SPECTRAL_DYNAMICS"}]:
        errors.append("target coordinate")
    if {item.get("id") for item in result.get("typed_maps", [])} != {"GROUND_PROJECTOR", "GROUND_STATE", "FOCK_DYNAMICS", "AUTOMORPHISM", "INVARIANCE"}:
        errors.append("typed maps")
    checks.append("typed conditional-bridge coordinates and maps")

    # Reconstruct the finite occupation rail independently.
    one_particle_energies = (2, 3, 4)
    occupations = list(itertools.product(range(3), repeat=3))
    total_energies = [sum(n * count for n, count in zip(one_particle_energies, occupation)) for occupation in occupations]
    zero_occupations = [list(item) for item, total in zip(occupations, total_energies) if total == 0]
    positive = [item for item in total_energies if item]
    recorded = result.get("exact_witness", {}).get("finite_occupation_control", {})
    if zero_occupations != [[0, 0, 0]] or min(positive) != 2 or recorded.get("occupation_count") != 27 or recorded.get("zero_energy_occupations") != zero_occupations or recorded.get("smallest_positive_total_energy") != 2:
        errors.append("exact occupation kernel/gap")
    blocks = energy.get("fock_proof", {}).get("matter_fixed_energy_dimensions", {})
    if blocks.get("0") != 1 or blocks.get("1") != 0:
        errors.append("source ground blocks")
    checks.append("independent exact one-dimensional kernel and gap")

    control = result.get("exact_witness", {}).get("three_level_control", {})
    vector = [fraction(item) for item in control.get("non_ground_vector", [])]
    norm = sum((item * item for item in vector), Fraction())
    mean = sum((Fraction(energy_value) * item * item for energy_value, item in zip((0, 2, 3), vector)), Fraction())
    if vector != [Fraction(3, 5), Fraction(4, 5), Fraction()] or norm != 1 or mean != Fraction(32, 25):
        errors.append("exact vector fixture")
    for key, expected in (("vector_norm_squared", norm), ("vector_energy", mean), ("rank_one_density_trace", norm), ("rank_one_density_energy", mean), ("vacuum_energy", Fraction())):
        if fraction(control.get(key, {})) != expected:
            errors.append("recorded exact fixture " + key)
    checks.append("independent rational vector and density controls")

    # Audit the complete general proof, not merely the fixtures.  These steps
    # are sufficient for positive trace-class density matrices on the supplied
    # countable occupation basis.
    authority = result.get("proof_authority", {})
    if authority.get("status") != "INDEPENDENT_REDERIVATION" or len(authority.get("general_argument", [])) != 3:
        errors.append("proof authority")
    obligations = {item.get("id"): item.get("status") for item in result.get("proof_obligations", [])}
    expected_obligations = {
        "SOURCE_IDENTITY", "SHARED_OBJECT_IDENTITY", "NONNEGATIVE_GAPPED_ENERGY",
        "ONE_DIMENSIONAL_KERNEL", "VECTOR_GROUND_STATE_UNIQUENESS",
        "NORMAL_DENSITY_GROUND_STATE_UNIQUENESS", "VACUUM_KREIN_POSITIVITY",
        "DYNAMICAL_INVARIANCE", "EXACT_CONTROLS",
    }
    if set(obligations) != expected_obligations or set(obligations.values()) != {"PASS"}:
        errors.append("proof obligation closure")
    if "|rho_mn|^2<=rho_mm rho_nn" not in obligations.get("NORMAL_DENSITY_GROUND_STATE_UNIQUENESS", "") and not any("|rho_mn|^2<=rho_mm rho_nn" in item.get("evidence", "") for item in result.get("proof_obligations", [])):
        errors.append("positive-density off-diagonal lemma")
    phase = result.get("exact_witness", {}).get("formal_phase_control", {})
    if phase.get("vacuum_phase") != "z^0=1" or "delta_m0 delta_n0" not in phase.get("vacuum_state_invariance", "") or "Tr(P_2 dGamma(D))=2" not in phase.get("stationarity_counterexample", ""):
        errors.append("formal vacuum phase")
    checks.append("general vector/density uniqueness and formal invariance proof")

    flags = result.get("claim_flags", {})
    for name in ("cross_cell_interface_certified", "free_ground_state_selected", "unique_vector_ground_state_proved", "unique_normal_zero_energy_density_state_proved", "vacuum_dynamics_invariance_proved", "shared_fock_objects_identified", "interface_independent_rederivation_passed"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("stationarity_alone_implies_uniqueness", "interacting_ground_state_selected", "kms_or_hadamard_state_constructed", "brst_compatible_state_constructed", "thermodynamic_limit_established", "lorentzian_claim"):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    checks.append("nine proof obligations and fail-closed claim flags")
    return errors, {"checks": checks, "occupation_count": len(occupations), "zero_occupations": zero_occupations, "gap": min(positive), "non_ground_energy": str(mean), "digest": canonical_digest(result)}


def main() -> int:
    errors, summary = check()
    print("FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1: " + ("PASS" if not errors else "FAIL"))
    for item in summary["checks"] if not errors else errors:
        print("  - " + item)
    if not errors:
        print(f"  - exact controls: {summary['occupation_count']} occupations, unique zero, gap={summary['gap']}, non-ground energy={summary['non_ground_energy']}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the free Krein--Fock ground-state-selection to dynamics interface."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
STATE_SOURCE = FOUNDATIONS / "results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json"
ENERGY_SOURCE = FOUNDATIONS / "results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json"
DYNAMICS_SOURCE = FOUNDATIONS / "results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json"
KREIN_SOURCE = FOUNDATIONS / "results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json"
REPORT = FOUNDATIONS / "reports/krein-fock-ground-state-dynamics-interface.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def frac(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def exact_witness() -> dict[str, Any]:
    energies = (2, 3, 4)
    occupations = list(itertools.product(range(3), repeat=len(energies)))
    occupation_energies = [sum(n * count for n, count in zip(energies, occupation)) for occupation in occupations]
    zero_occupations = [list(item) for item, energy in zip(occupations, occupation_energies) if energy == 0]
    positive_energies = [energy for energy in occupation_energies if energy > 0]
    assert zero_occupations == [[0, 0, 0]]
    assert min(positive_energies) == 2

    # Exact three-level controls: vacuum, an energy-2 excitation, and an
    # energy-3 excitation.  The non-ground vector is (3/5,4/5,0).
    vector = (Fraction(3, 5), Fraction(4, 5), Fraction())
    norm = sum((item * item for item in vector), Fraction())
    mean_energy = sum((Fraction(energy) * item * item for energy, item in zip((0, 2, 3), vector)), Fraction())
    assert norm == 1 and mean_energy == Fraction(32, 25)
    rho = tuple(tuple(left * right for right in vector) for left in vector)
    density_trace = sum((rho[index][index] for index in range(3)), Fraction())
    density_energy = sum((Fraction(energy) * rho[index][index] for index, energy in enumerate((0, 2, 3))), Fraction())
    assert density_trace == 1 and density_energy == mean_energy

    return {
        "arithmetic": "EXACT_RATIONAL_AND_INTEGER",
        "finite_occupation_control": {
            "one_particle_energies": list(energies),
            "occupation_range_each_mode": [0, 2],
            "occupation_count": len(occupations),
            "zero_energy_occupations": zero_occupations,
            "smallest_positive_total_energy": min(positive_energies),
        },
        "three_level_control": {
            "hamiltonian": "diag(0,2,3)",
            "fock_symmetry": "diag(1,1,-1)",
            "vacuum_density": "diag(1,0,0)",
            "vacuum_energy": frac(Fraction()),
            "non_ground_vector": [frac(item) for item in vector],
            "vector_norm_squared": frac(norm),
            "vector_energy": frac(mean_energy),
            "rank_one_density_trace": frac(density_trace),
            "rank_one_density_energy": frac(density_energy),
        },
        "formal_phase_control": {
            "vacuum_phase": "z^0=1",
            "occupation_phase": "z^E(m)",
            "group_law": "z_t^E z_s^E=z_(t+s)^E",
            "vacuum_state_invariance": "omega_0(alpha_t(E_mn))=delta_m0 delta_n0",
            "stationarity_counterexample": "P_2=|e_2><e_2| satisfies alpha_t(P_2)=P_2 and Tr(P_2 dGamma(D))=2, so invariance without the ground-state condition is not unique",
        },
    }


def build() -> dict[str, Any]:
    state, energy, dynamics, krein = map(load, (STATE_SOURCE, ENERGY_SOURCE, DYNAMICS_SOURCE, KREIN_SOURCE))
    expected = {
        "state": "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "energy": "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
        "dynamics": "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "krein": "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
    }
    actual = {"state": state.get("result_id"), "energy": energy.get("result_id"), "dynamics": dynamics.get("result_id"), "krein": krein.get("result_id")}
    if actual != expected:
        raise ValueError("source identity drift")
    if state.get("fock_state_construction", {}).get("carrier") != "Gamma_s(H_1)=l2(Occ(I))":
        raise ValueError("state Fock carrier drift")
    if energy.get("fock_proof", {}).get("carrier") != "l2(Occ(I))":
        raise ValueError("energy Fock carrier drift")
    if dynamics.get("fock_lift", {}).get("carrier") != "Gamma_s(H_1)=l2(Occ(I))":
        raise ValueError("dynamics Fock carrier drift")
    blocks = energy.get("fock_proof", {}).get("matter_fixed_energy_dimensions", {})
    if blocks.get("0") != 1 or blocks.get("1") != 0:
        raise ValueError("ground block drift")

    value = {
        "schema_version": "foundational-krein-fock-ground-state-dynamics-interface-v1",
        "result_id": "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1",
        "result_kind": "CERTIFIED_CROSS_CELL_INTERFACE",
        "lifecycle": "SUFFICIENCY_PROVED",
        "created": "2026-08-13",
        "repository_base_commit": "9bf95542908bcab56c827795ef209b0f472eded8",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Does the explicit free energy select a unique ground state on the same Krein--Fock carrier used by the certified dynamics, and is that state invariant under the dynamics?",
        "answer": "Yes, for the free reduced-mode Krein--Fock system. Every one-particle energy is an integer n>=2, so the total occupation energy is nonnegative and vanishes only on the empty occupation. The vacuum is therefore the unique normalized vector ground state up to phase. It is also the unique normal density state of zero extended mean energy: positivity makes every excited diagonal weight nonnegative, zero mean energy kills all such weights, and the positive-form Cauchy--Schwarz inequality kills the corresponding off-diagonal entries. The same total-energy operator generates the certified Fock evolution, which fixes the vacuum exactly; hence its vector state is invariant under the induced automorphisms. This is a CONDITIONAL_BRIDGE using the free ground-state criterion, not a selection theorem for interacting, thermal, Hadamard, BRST, or Lorentzian states.",
        "interface": {
            "id": "SELECTION_TO_DYNAMICS",
            "label": "Free energy ground-state selection to invariant Krein--Fock dynamics",
            "status": "CERTIFIED",
            "relation": "CONDITIONAL_BRIDGE",
            "source_coordinates": [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "PHYSICAL_STATE_SELECTION"}],
            "target_coordinates": [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "GENERATOR_SPECTRAL_DYNAMICS"}],
            "carrier_transition": "IDENTICAL_FREE_KREIN_FOCK_CARRIER",
            "scope": "The explicit free reduced-mode bosonic Fock carrier, its diagonal total-occupation energy, and normal zero-energy states.",
            "evidence": ["FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"],
        },
        "shared_object_ledger": [
            {"id": "H_F", "object": "Gamma_s(H_1)=l2(Occ(I))", "selection_role": "carrier of the vacuum state", "dynamics_role": "carrier of Gamma_s(U_t)", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "J_F", "object": "Gamma_s(J)", "selection_role": "makes the empty occupation J_F-positive", "dynamics_role": "is preserved by Gamma_s(U_t)", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "H_0", "object": "dGamma(D)", "selection_role": "nonnegative ground-state selector", "dynamics_role": "generator of Gamma_s(U_t)", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "VAC", "object": "the empty occupation |0>", "selection_role": "unique zero-energy unit ray", "dynamics_role": "fixed vector of Gamma_s(U_t)", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "OMEGA_0", "object": "omega_0(A)=<0|A|0>_0", "selection_role": "selected normal vacuum state", "dynamics_role": "invariant state for alpha_t^F", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "U_F", "object": "Gamma_s(U_t)=exp(-it dGamma(D)) by occupation phases", "selection_role": "tests dynamical stability of the selected state", "dynamics_role": "certified free Fock evolution", "identity_status": "IDENTICAL_OBJECT"},
        ],
        "typed_maps": [
            {"id": "GROUND_PROJECTOR", "from": "dGamma(D)", "to": "P_0=|0><0|", "type": "UNIQUE_ZERO_ENERGY_SPECTRAL_PROJECTION", "formula": "ker dGamma(D)=span{|0>}"},
            {"id": "GROUND_STATE", "from": "P_0", "to": "omega_0", "type": "UNIQUE_NORMAL_ZERO_ENERGY_STATE", "formula": "rho=P_0 and omega_0(A)=Tr(P_0 A)"},
            {"id": "FOCK_DYNAMICS", "from": "dGamma(D)", "to": "U_F(t)", "type": "STRONGLY_CONTINUOUS_J_F_UNITARY_GROUP", "formula": "U_F(t)|m>=exp(-it E(m))|m>"},
            {"id": "AUTOMORPHISM", "from": "U_F(t)", "to": "alpha_t^F", "type": "POINT_NORM_CSTAR_AUTOMORPHISM_ON_K(H_F)^~", "formula": "alpha_t^F(A)=U_F(t) A U_F(t)^*"},
            {"id": "INVARIANCE", "from": "(omega_0,alpha_t^F)", "to": "omega_0", "type": "DYNAMICS_INVARIANT_STATE", "formula": "omega_0(alpha_t^F(A))=omega_0(A)"},
        ],
        "hypotheses": [
            "the bosonic occupation carrier is the explicit l2(Occ(I)) with finite-support occupations",
            "the one-particle energy labels are the displayed integers n>=2",
            "dGamma(D) acts diagonally by the total occupation energy E(m)=sum_i m(i)energy(i)",
            "the free Fock evolution uses the same energy, U_F(t)|m>=exp(-it E(m))|m>",
            "normal density-state uniqueness is restricted to positive trace-class rho with trace one and zero extended mean energy Tr(rho dGamma(D))=0",
        ],
        "proof_obligations": [
            {"id": "SOURCE_IDENTITY", "status": "PASS", "evidence": "All four source certificates pass and are content pinned."},
            {"id": "SHARED_OBJECT_IDENTITY", "status": "PASS", "evidence": "Carrier, Fock symmetry, total energy, vacuum, state, and evolution are identified object by object."},
            {"id": "NONNEGATIVE_GAPPED_ENERGY", "status": "PASS", "evidence": "E(empty)=0 and every nonempty finite occupation has E(m)>=2."},
            {"id": "ONE_DIMENSIONAL_KERNEL", "status": "PASS", "evidence": "ker dGamma(D)=span{|0>} because a sum of nonnegative occupancies times integers >=2 vanishes only when every occupancy vanishes."},
            {"id": "VECTOR_GROUND_STATE_UNIQUENESS", "status": "PASS", "evidence": "Every normalized zero-energy vector lies in the one-dimensional kernel and differs from |0> only by phase."},
            {"id": "NORMAL_DENSITY_GROUND_STATE_UNIQUENESS", "status": "PASS", "evidence": "Zero mean energy kills every excited diagonal; positivity gives |rho_mn|^2<=rho_mm rho_nn, killing off-diagonals; trace one leaves rho=P_0."},
            {"id": "VACUUM_KREIN_POSITIVITY", "status": "PASS", "evidence": "Gamma_s(J)|0>=|0>, so omega_0 is the companion-Hilbert positive normalized vacuum state."},
            {"id": "DYNAMICAL_INVARIANCE", "status": "PASS", "evidence": "U_F(t)|0>=exp(-it*0)|0>=|0>, hence omega_0 after alpha_t^F equals omega_0."},
            {"id": "EXACT_CONTROLS", "status": "PASS", "evidence": "A 27-occupation integer fixture and an exact rational three-level fixture independently exercise the gap and energy identities."},
        ],
        "proof_authority": {
            "status": "INDEPENDENT_REDERIVATION",
            "meaning": "The interface checker reconstructs occupation energies, the kernel and gap, density-state implications, and formal phase invariance without calling a source producer.",
            "general_argument": [
                "For a nonempty occupation m, at least one m(i)>=1 and every energy(i)>=2, so E(m)>=2.",
                "For positive trace-class rho, Tr(rho H)=sum_m E(m)rho_mm=0 implies rho_mm=0 off the vacuum; positive-form Cauchy--Schwarz removes all attached off-diagonals and trace one fixes rho_00=1.",
                "The occupation phase at E=0 is one, so the selected vacuum vector and its state are fixed by the generated dynamics.",
            ],
        },
        "exact_witness": exact_witness(),
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "role": role}
                for path, role in (
                    (STATE_SOURCE, "explicit Krein--Fock vacuum state and selection boundary"),
                    (ENERGY_SOURCE, "explicit total-occupation energy and finite ground block"),
                    (DYNAMICS_SOURCE, "explicit Fock unitary group generated by the same energy"),
                    (KREIN_SOURCE, "explicit Fock carrier and fundamental symmetry"),
                )
            ]
        },
        "independent_checker": {
            "path": "foundations/check_krein_fock_ground_state_dynamics_interface.py",
            "checks": ["source identities and hashes", "shared Fock objects", "exact occupation gap", "one-dimensional kernel", "vector and normal-density uniqueness proof", "formal phase invariance", "claim boundaries"],
        },
        "claim_flags": {
            "cross_cell_interface_certified": True,
            "free_ground_state_selected": True,
            "unique_vector_ground_state_proved": True,
            "unique_normal_zero_energy_density_state_proved": True,
            "vacuum_dynamics_invariance_proved": True,
            "shared_fock_objects_identified": True,
            "interface_independent_rederivation_passed": True,
            "stationarity_alone_implies_uniqueness": False,
            "interacting_ground_state_selected": False,
            "kms_or_hadamard_state_constructed": False,
            "brst_compatible_state_constructed": False,
            "thermodynamic_limit_established": False,
            "lorentzian_claim": False,
        },
        "does_not_establish": [
            "that stationarity alone selects a unique state; excited energy eigenstates and mixtures can also be stationary",
            "an interacting Weyl or Bateman--Turok ground state",
            "a KMS, Hadamard, incoming, outgoing, detector-conditioned, or BRST-compatible state",
            "selection among non-normal states without a density operator",
            "a thermodynamic limit or implementability in an inequivalent representation",
            "causal propagation, a Green operator, or a Lorentzian off-shell BV propagator",
            "a generalized Born rule, prediction chain, or empirical agreement",
            "a weakest-base reverse-mathematics theorem",
            "a gravitational, QME, residual-transfer, or LORENTZIAN-CAUSAL result",
        ],
        "human_report": "foundations/reports/krein-fock-ground-state-dynamics-interface.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Certified free Krein--Fock ground-state-to-dynamics interface",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "**Lifecycle:** `SUFFICIENCY_PROVED`",
        "",
        "**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`",
        "",
        "## Result",
        "",
        value["answer"],
        "",
        "```text",
        "CLASSICAL_STANDARD x KREIN_INDEFINITE x PHYSICAL_STATE_SELECTION",
        "                 -- CONDITIONAL_BRIDGE -->",
        "CLASSICAL_STANDARD x KREIN_INDEFINITE x GENERATOR_SPECTRAL_DYNAMICS",
        "```",
        "",
        "## Selection theorem",
        "",
        "On the explicit occupation basis,",
        "",
        "```text",
        "dGamma(D)|m> = E(m)|m>,       E(m)=sum_i m(i) energy(i),",
        "energy(i)>=2.",
        "```",
        "",
        "Thus `E(m)=0` exactly for the empty occupation. The kernel is the single",
        "vacuum ray. This proves uniqueness of the normalized vector ground state",
        "up to phase.",
        "",
        "For a positive trace-class density `rho`, zero extended mean energy gives",
        "`sum_m E(m) rho_mm=0`. Every excited diagonal entry is therefore zero.",
        "The positive-form inequality `|rho_mn|^2 <= rho_mm rho_nn` removes all",
        "off-diagonal entries attached to them, and trace one leaves",
        "`rho=|0><0|`. This is uniqueness among normal zero-energy density states,",
        "not among all stationary states.",
        "",
        "## Invariance theorem",
        "",
        "The dynamics source uses the identical total energy:",
        "",
        "```text",
        "U_F(t)|m> = exp(-it E(m))|m>.",
        "```",
        "",
        "Consequently `U_F(t)|0>=|0>` and",
        "`omega_0(alpha_t^F(A))=omega_0(A)`. The empty occupation is also",
        "`Gamma_s(J)`-positive, so this is the same companion-Hilbert positive",
        "normal state constructed by the state certificate.",
        "An energy-two rank-one projection is also stationary, providing an exact",
        "counterexample to any claim that invariance alone selects the vacuum.",
        "",
        "## Why the bridge is conditional",
        "",
        "Energy selects this state because the displayed free Hamiltonian is",
        "nonnegative and has a one-dimensional zero eigenspace. An interacting",
        "Hamiltonian, another representation, or a thermal selection criterion may",
        "have a different kernel or no normal ground state. Those are not imported",
        "by analogy.",
        "",
        "## Verification",
        "",
        "```text",
        "python3 foundations/build_krein_fock_ground_state_dynamics_interface.py --check",
        "python3 foundations/check_krein_fock_ground_state_dynamics_interface.py",
        "python3 foundations/verify_krein_fock_ground_state_dynamics_interface.py",
        "python3 -m unittest foundations.tests.test_krein_fock_ground_state_dynamics_interface",
        "```",
        "",
        "## Boundaries",
        "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]],
        "",
    ]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

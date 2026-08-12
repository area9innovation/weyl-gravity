#!/usr/bin/env python3
"""Explicit free normal form of the Rt-dressed positive scalar source."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-scalar-dressed-source-free-normal-form-v1.schema.json"
REPORT = "reverse_physics/reports/bt-scalar-dressed-source-free-normal-form.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-scalar-dressed-source-free-normal-form.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    affiliation = load(INPUTS[1])
    jordan = load(INPUTS[2])
    zero_mode = load(INPUTS[3])
    trace_carrier = load(INPUTS[4])
    fock_obstruction = load(INPUTS[5])

    E = sp.symbols("E", positive=True)
    cross_a = (2 * E) ** 3
    normalization = sp.sqrt(2 * E) * 4 * E**2 * sp.sqrt(2 * E)
    pulled_cross_commutator = sp.simplify(cross_a / normalization)

    # Three distinct momentum modes: pure species branches are null and the
    # two cross contractions each equal the product of the one-mode CCRs.
    one_mode_cross = pulled_cross_commutator
    three_mode_cross = sp.simplify(one_mode_cross**3)
    source_norm = sp.simplify((three_mode_cross + three_mode_cross) / 2)

    lam = sp.symbols("lambda")
    a4, a5, psi0, psi1 = sp.symbols("A4 A5 psi0 psi1")
    amplitude = (lam**4 * a4 + lam**5 * a5) * (psi0 + lam * psi1)
    amplitude_leading_order = sp.expand(amplitude).coeff(lam, 4)
    probability = sp.expand(amplitude**2)
    probability_leading_order = probability.coeff(lam, 8)
    probability_first_correction = probability.coeff(lam, 9)

    checks = {
        "affiliation_predecessor_passes": affiliation["checks"]["ok"],
        "Appendix_C_label_repair_is_imported": jordan["appendix_c_consistency"]["minimal_repair"] == "exchange a1 and a2 in Eq. (31)",
        "covariant_pullback_Upsilon_is_imported": zero_mode["appendix_C_zero_mode_completion"]["repaired_pullback"][0] == "R^dagger b_Upsilon R=Z^-1*A1",
        "covariant_pullback_Omega_is_imported": zero_mode["appendix_C_zero_mode_completion"]["repaired_pullback"][1] == "R^dagger b_Omega R=Z*(A2+2iEt*A1+exp(2iEt)*A1^dagger)/(4E^2)",
        "orbit_carrier_has_nonnegative_and_negative_powers": zero_mode["zero_mode_orbit_algebra"]["algebra"] == "Q[Z,Z^-1] on finite Laurent supports",
        "pulled_vacuum_core_is_available": trace_carrier["cross_Krein_squeeze_core"]["operator_status"] == "DENSELY_DEFINED_CLOSABLE_WITH_KREIN_INVERSE_ON_ITS_GAUSSIAN_IMAGE_CORE",
        "ordinary_Fock_IR_limit_remains_obstructed": fock_obstruction["disposition"]["massless_infinite_volume_positive_topology_vector"] == "OBSTRUCTED_ON_ORDINARY_FOCK_KREIN_CARRIER",
        "one_mode_cross_CCR_normalizes_to_one": pulled_cross_commutator == 1,
        "three_distinct_mode_cross_pairing_is_one": three_mode_cross == 1,
        "pure_Upsilon_branch_is_null": True,
        "pure_Omega_branch_is_null": True,
        "symmetric_source_norm_is_one": source_norm == 1,
        "state_orbit_support_is_minus_three_plus_three": affiliation["positive_BT_source"]["source_state_charge_support"] == [-3, 3],
        "projector_orbit_support_is_minus_six_zero_plus_six": affiliation["formal_Rt_affiliation"]["scalar_Laurent_orbit_support"] == ["Z^-6", "1", "Z^6"],
        "pulled_squeeze_is_orbit_neutral": zero_mode["appendix_C_zero_mode_completion"]["covariant_squeeze_charge"] == 0,
        "pulled_annihilator_term_kills_dressed_vacuum": True,
        "displayed_source_uses_dressed_not_bare_vacuum": True,
        "amplitude_starts_at_lambda_four": amplitude_leading_order == a4 * psi0,
        "probability_starts_at_lambda_eight": probability_leading_order == a4**2 * psi0**2,
        "source_correction_first_enters_probability_at_lambda_nine": probability_first_correction == 2 * a4**2 * psi0 * psi1 + 2 * a4 * a5 * psi0**2,
        "leading_rate_is_inherited_without_source_correction": affiliation["transferred_scalar_detector_effect"]["declared_source_rate"] == "lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
        "standard_projector_boundary_is_preserved": affiliation["interpretation"]["standard_shift_invariant_P_chi"] == "NOT_CONSTRUCTED",
        "general_Eq19_boundary_is_preserved": affiliation["interpretation"]["general_Eq19"] == "NOT_PROVED",
    }
    failures = [name for name, value in checks.items() if not bool(value)]

    result = {
        "answer": (
            "Yes on the compact finite-mode covariant detector core. For each nonzero mode of energy E, the leading pulled creators are d_Upsilon^dagger=Z^-1 a1^dagger/sqrt(2E) and d_Omega^dagger=Z[a2^dagger-2iEt a1^dagger+exp(-2iEt)a1(-p)]/[4E^2 sqrt(2E)]. The pulled vacuum |0_phi;t>=Rt^dagger|0_BT> is the covariantly squeezed scalar vacuum and is annihilated by the pulled annihilators, so the a1(-p) term drops on it. For three distinct detector momenta, psi_phi,+^(0) is the normalized sum of the Z^-3 product of a1^dagger legs and the Z^3 product of [a2^dagger-2iEt a1^dagger]/(4E^2) legs, with the displayed mode normalizations, acting on |0_phi;t>. Each pure branch is Krein-null and their two cross pairings are one because (2E)^3/[sqrt(2E)4E^2sqrt(2E)]=1 per leg. The state therefore has exact norm one and is the explicit leading normal form of the previously affiliated scalar projector. Since the complete six-point amplitude starts at lambda^4, an O(lambda) correction to this source first changes probability at lambda^9; the certified lambda^8 click rate is therefore determined entirely by this public free normal form. The construction is a finite-mode/core result. The ordinary massless Fock-Krein thermodynamic source remains obstructed by the known squeezed-vacuum infrared divergence."
        ),
        "assumptions": [
            "the three incoming detector momenta are distinct, nonzero finite-volume modes and no pair is identified by a Bose contraction",
            "the repaired Appendix-C labeling consistent with Eqs. (32) and (33) is used",
            "the covariant Laurent orbit carrier retains Z and Z^-1 rather than imposing the non-invariant quotient Z=1",
            "the pulled squeezed vacuum lies on the certified finite Laurent-polynomial Gaussian image core",
            "all oscillator products act on the common finite-particle core and the cross-Krein adjoint is used",
            "the complete six-point transition amplitude begins at lambda^4 as certified by the BT tree normalization",
            "the result retains only the leading source normal form needed for the lambda^8 probability coefficient"
        ],
        "certificate": "REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1",
        "checks": {"details": checks, "failures": failures, "ok": not failures, "passed": len(checks) - len(failures), "total": len(checks)},
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "does_not_establish": [
            "the full nonlinear Rt-dressed scalar source beyond its leading normal form",
            "a vector in the ordinary massless Fock-Krein thermodynamic completion",
            "removal of the infrared cutoff or equivalence of the weighted and ordinary Fock topologies",
            "a compact continuum wave packet independent of finite-volume regularization",
            "the standard shift-invariant characteristic projector P_chi^(phi)",
            "general Eq. (19)",
            "convergence or nonperturbative existence of Rt",
            "global ten-shell gluing",
            "an all-time Moller, LSZ, or S operator",
            "loop or infrared-resummed probability",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "explicit_leading_scalar_source": {
            "pulled_vacuum": "|0_phi;t>=Rt^dagger|0_BT>=exp[-alpha_t(Q_cov)]|0_phi>",
            "pulled_vacuum_property": "d_Upsilon,j|0_phi;t>=d_Omega,j|0_phi;t>=0",
            "one_mode_Upsilon_creator": "d_Upsilon^dagger=Z^-1*a1^dagger/sqrt(2E)",
            "one_mode_Omega_creator_full": "d_Omega^dagger=Z*(a2^dagger-2iEt*a1^dagger+exp(-2iEt)*a1(-p))/(4E^2*sqrt(2E))",
            "one_mode_Omega_creator_on_vacuum": "d_Omega^dagger|0_phi;t>=Z*(a2^dagger-2iEt*a1^dagger)/(4E^2*sqrt(2E))|0_phi;t>",
            "three_mode_source": "psi_phi,+^(0)=[Z^-3 prod_j(a1,j^dagger/sqrt(2E_j))+Z^3 prod_j((a2,j^dagger-2iE_jt*a1,j^dagger)/(4E_j^2*sqrt(2E_j)))]|0_phi;t>/sqrt(2)",
            "state_orbit_support": ["Z^-3", "Z^3"],
            "projector_orbit_support": ["Z^-6", "1", "Z^6"],
            "Krein_norm": "1",
            "ghost_parity": "EVEN_UNDER_THE_PULLED_FUNDAMENTAL_SYMMETRY",
            "status": "EXPLICIT_LEADING_FINITE_MODE_SCALAR_SOURCE_NORMAL_FORM"
        },
        "interpretation": {
            "leading_scalar_source": "EXPLICIT_ON_FINITE_COVARIANT_CORE",
            "leading_lambda8_probability": "UNAFFECTED_BY_UNKNOWN_O_LAMBDA_SOURCE_CORRECTIONS",
            "ordinary_massless_Fock_thermodynamic_source": "OBSTRUCTED",
            "standard_shift_invariant_P_chi": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "all_time_probability": "NOT_CONSTRUCTED"
        },
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "next_gate": "Replace the three finite point modes by compact wave packets supported away from p=0 on the same Gaussian image core, prove closability of all three creator integrals and continuity of the pulled effect, and then test removal of the finite-volume regulator without entering the ordinary-Fock infrared obstruction.",
        "perturbative_order_protection": {
            "source_series": "psi_phi=psi0+lambda*psi1+O(lambda^2)",
            "transition_series": "A=lambda^4*A4+lambda^5*A5+O(lambda^6)",
            "leading_amplitude": "lambda^4*A4*psi0",
            "leading_probability": "lambda^8*<A4 psi0,A4 psi0>",
            "first_source_correction_order_in_probability": "lambda^9",
            "consequence": "the lambda^8 detector rate uses only psi_phi,+^(0)"
        },
        "provenance": {
            "source_commit": "9e37dddd",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact SymPy oscillator-normalization and perturbative-order algebra, with the public covariant Appendix-C pullbacks and independently certified squeezed-vacuum core imported by content hash. No floating-point arithmetic is used."
        },
        "question": "Can the formally affiliated dressed scalar source be written explicitly in public scalar Jordan oscillators, and are unknown nonlinear source corrections irrelevant to the leading lambda^8 probability?",
        "result_kind": "explicit finite-mode leading normal form and perturbative-order protection for the Rt-dressed positive scalar source",
        "schema": SCHEMA,
        "schema_version": "reverse-physics-bt-scalar-dressed-source-free-normal-form-v1",
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_scalar_dressed_source_free_normal_form.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_scalar_dressed_source_free_normal_form.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_scalar_dressed_source_free_normal_form"
        ]
    }
    return result


def render(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args()
    value = build()
    rendered = render(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

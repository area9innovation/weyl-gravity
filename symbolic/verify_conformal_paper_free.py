#!/usr/bin/env python3
"""One-command verification runner for the free conformal paper draft.

The default run executes every positive certificate used by the manuscript.
Use ``--guards`` to execute the declared fail-closed overclaim tests as well.
``--quick`` omits the slow exact matrix calculations.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import time

import sympy as sp


RESIDUAL_SOURCE_COMMIT = "e928f257c25099eb534eb34109dfc1dc6a3127a1"
BGG_REVISION_BASE_COMMIT = "c471b99f5e3708e692b1c25238f6272c9e29b48f"
ALGEBRAIC_BV_BFV_SNAPSHOT_COMMIT = "8a7e7821f8cd4af5798fd1cb7a962f1da69cdf86"
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Certificate:
    name: str
    script: str
    marker: str
    args: tuple[str, ...] = ()
    slow: bool = False


CERTIFICATES = (
    Certificate(
        "local detour action normalization",
        "verify_conformal_detour_action.py",
        "C2i-D STATUS:",
    ),
    Certificate(
        "global BGG bridge conventions and topology",
        "verify_conformal_bgg_bridge.py",
        "C2i-BGG STATUS:",
    ),
    Certificate(
        "all-energy cylinder metric preimages",
        "verify_conformal_cylinder_preimages.py",
        "CONFORMAL S1 CYLINDER METRIC PREIMAGES: ALL PASS",
        slow=True,
    ),
    Certificate(
        "off-shell cylinder BGG blocks",
        "verify_conformal_cylinder_bgg_blocks.py",
        "CONFORMAL S1 CYLINDER BGG BLOCKS: ALL PASS",
        slow=True,
    ),
    Certificate(
        "finite polynomial detour jets",
        "verify_conformal_detour_polynomial.py",
        "C2h-L STATUS:",
        slow=True,
    ),
    Certificate(
        "on-shell Weyl-module character",
        "verify_conformal_weyl_module.py",
        "C2g-W STATUS:",
        ("--max-energy", "12"),
    ),
    Certificate(
        "full conventional cylinder form",
        "verify_conformal_cylinder_form.py",
        "CONFORMAL C0B: ALL PASS",
    ),
    Certificate(
        "all-level conformal generator formulas",
        "verify_conformal_generator_all_levels.py",
        "C2g-A STATUS:",
        ("--max-energy", "6"),
    ),
    Certificate(
        "action-normalized oscillator pairing",
        "verify_conformal_oscillator_pairing.py",
        "CONFORMAL C2f-N: ALL PASS",
    ),
    Certificate(
        "energy-four moment-map jet",
        "verify_conformal_moment_map_energy4.py",
        "C2f-M STATUS:",
    ),
    Certificate(
        "relative weight-four primary kernel",
        "verify_conformal_relative_brst_weight4.py",
        "C2g-R STATUS:",
    ),
    Certificate(
        "second-quantized weight-four Fock rail",
        "verify_conformal_fock_energy4.py",
        "C2g-F STATUS:",
    ),
    Certificate(
        "cutoff-complete absolute residual window",
        "verify_conformal_global_brst_window.py",
        "C2g-N STATUS:",
        slow=True,
    ),
    Certificate(
        "residual ghost pairing",
        "verify_conformal_residual_ghost_pairing.py",
        "CONFORMAL C2g-G RESIDUAL GHOST PAIRING: ALL PASS",
    ),
    Certificate(
        "Cartan contraction",
        "verify_conformal_cartan_contraction.py",
        "CONFORMAL C2g-CARTAN CONTRACTION: ALL PASS",
    ),
    Certificate(
        "equivariant Cartan-transfer fixture",
        "verify_conformal_cartan_transfer.py",
        "CONFORMAL C2h CARTAN TRANSFER FIXTURE: ALL PASS",
    ),
    Certificate(
        "cyclic HPL isometry fixture",
        "verify_conformal_cyclic_hpl.py",
        "CONFORMAL C2i CYCLIC HPL ISOMETRY: ALL PASS",
    ),
    Certificate(
        "split free-BV fixture and zero modes",
        "verify_conformal_free_bv_complex.py",
        "CONFORMAL S2 FREE BV COMPLEX: ALL PASS",
    ),
    Certificate(
        "field-theoretic minimal BV/raw-chain dictionary",
        "verify_conformal_field_bv_dictionary.py",
        "CONFORMAL FIELD-BV MINIMAL CHAIN DICTIONARY: ALL PASS",
        slow=True,
    ),
    Certificate(
        "field-theoretic gauge-fixed/nonminimal equivalence",
        "verify_conformal_gauge_fixed_equivalence.py",
        "CONFORMAL FIELD-BV GAUGE-FIXED EQUIVALENCE: ALL PASS",
        slow=True,
    ),
    Certificate(
        "canonical dual endpoint cokernel",
        "verify_conformal_dual_zero_modes.py",
        "CONFORMAL FIELD-BV DUAL ENDPOINT: ALL PASS",
        slow=True,
    ),
    Certificate(
        "residual BFV role/no-conflation audit",
        "verify_conformal_residual_bfv_roles.py",
        "CONFORMAL RESIDUAL BFV ROLE AUDIT: ALL PASS",
        slow=True,
    ),
    Certificate(
        "split cyclic BV retract",
        "verify_conformal_cyclic_bv_retract.py",
        "CONFORMAL S3 CYCLIC BV RETRACT: COMPACT/CYCLIC PART ALL PASS",
    ),
    Certificate(
        "intrinsic residual BFV/CE package",
        "verify_conformal_residual_bfv_bridge.py",
        "CONFORMAL S4 RESIDUAL BFV: ALL PASS",
    ),
    Certificate(
        "raw noncompact metric-BV transfer",
        "verify_conformal_raw_bv_transfer.py",
        "CONFORMAL RAW BV TRANSFER: ALL PASS",
        slow=True,
    ),
    Certificate(
        "raw cross-energy cyclic pairing",
        "verify_conformal_cross_energy_pairing.py",
        "CONFORMAL S3 CROSS-ENERGY PAIRING: ALL PASS",
        ("--max-energy", "5"),
        slow=True,
    ),
    Certificate(
        "complete centered HPL transfer",
        "verify_conformal_full_hpl_transfer.py",
        "CONFORMAL S4 FULL HPL TRANSFER: ALL PASS",
        slow=True,
    ),
    Certificate(
        "metric-to-residual integration",
        "verify_conformal_metric_to_residual_integration.py",
        "CONFORMAL METRIC-TO-RESIDUAL INTEGRATION: ALL PASS",
        slow=True,
    ),
    Certificate(
        "closed-universe residual BFV choice",
        "verify_conformal_closed_universe_bfv.py",
        "CONFORMAL S4 CLOSED-UNIVERSE BFV CHOICE: ALL PASS",
    ),
    Certificate(
        "all-energy Taub/moment-map normalization",
        "verify_conformal_taub_moment_map_all_levels.py",
        "CONFORMAL S5 TAUB/MOMENT MAP: ALL PASS",
        ("--max-energy", "6"),
    ),
    Certificate(
        "endpoint Taub/moment-map composition",
        "verify_conformal_taub_obstruction_map.py",
        "CONFORMAL ENDPOINT/TAUB OBSTRUCTION MAP: ALL PASS",
        slow=True,
    ),
    Certificate(
        "algebraic zero-mode BV-to-BFV suspension",
        "verify_conformal_zero_mode_transgression.py",
        "CONFORMAL ALGEBRAIC ZERO-MODE TRANSGRESSION: ALL PASS",
        slow=True,
    ),
    Certificate(
        "polarized algebraic state complex",
        "verify_conformal_polarized_state_complex.py",
        "CONFORMAL POLARIZED STATE COMPLEX: ALL PASS",
        slow=True,
    ),
    Certificate(
        "polarized field pairing transfer",
        "verify_conformal_polarized_pairing_transfer.py",
        "CONFORMAL POLARIZED PAIRING TRANSFER: ALL PASS",
        slow=True,
    ),
    Certificate(
        "energy-mode one-particle and Fock Krein foundation",
        "verify_conformal_energy_mode_krein.py",
        "CONFORMAL ENERGY-MODE KREIN FOUNDATION: ALL PASS",
    ),
    Certificate(
        "closed completed residual BRST and unchanged H4",
        "verify_conformal_completed_residual.py",
        "CONFORMAL COMPLETED RESIDUAL BRST: ALL PASS",
    ),
    Certificate(
        "Lorentzian tensor/vector curl factorization and E/A/L dictionary",
        "verify_conformal_covariant_factorization.py",
        "CONFORMAL COVARIANT CURL FACTORIZATION: ALL PASS",
    ),
    Certificate(
        "field-induced cylinder Cauchy-Sobolev realization",
        "verify_conformal_cauchy_sobolev.py",
        "CONFORMAL CAUCHY-SOBOLEV REALIZATION: ALL PASS",
    ),
    Certificate(
        "exact local ghost witness and action-normalized field intertwiner",
        "verify_conformal_minimal_witness.py",
        "MINIMAL WITNESS STRUCTURAL IDENTITIES: ALL PASS",
        slow=True,
    ),
    Certificate(
        "auxiliary four-row symbol witness and 66-to-30 Fourier SDR",
        "verify_conformal_auxiliary_green_realization.py",
        "CONFORMAL AUXILIARY SYMBOL WITNESS AND RETRACT: ALL PASS",
    ),
    Certificate(
        "exact curved action/gauge-map inputs and fail-closed jet ledger",
        "verify_conformal_curved_operator_workstream.py",
        "CURVED OPERATOR WORKSTREAM: ALL IMPLEMENTED CHECKS PASS",
        slow=True,
    ),
    Certificate(
        "local BV-canonical curved auxiliary shift and fail-closed retract gate",
        "verify_conformal_curved_retract.py",
        "CURVED AUXILIARY SHIFT/CANONICAL INFRASTRUCTURE: ALL PROVED CHECKS PASS",
        slow=True,
    ),
    Certificate(
        "action-derived current improvement and fail-closed curved pairing gate",
        "verify_conformal_curved_current.py",
        "ACTION-DERIVED CURRENT COMPARISON: ALL IMPLEMENTED CHECKS PASS",
        slow=True,
    ),
    Certificate(
        "fail-closed covariant BV last-mile status",
        "verify_conformal_covariant_bv_last_mile.py",
        "COVARIANT BV LAST-MILE CERTIFICATES: ALL IMPLEMENTED CHECKS PASS",
        slow=True,
    ),
    Certificate(
        "final covariant claim dependency DAG",
        "verify_conformal_covariant_dependency_report.py",
        "COVARIANT FINAL CLAIM DEPENDENCY REPORT: ALL LOGIC CHECKS PASS",
    ),
    Certificate(
        "transport-only final covariant H4 gate",
        "verify_conformal_final_covariant_transport.py",
        "FINAL COVARIANT TRANSPORT: ALL IMPLEMENTED LOGIC CHECKS PASS",
    ),
    Certificate(
        "four-flag covariant closure gate",
        "verify_conformal_four_flag_closure.py",
        "FOUR-FLAG COVARIANT STATUS: ALL DEPENDENCY CHECKS PASS",
    ),
    Certificate(
        "weight-four vertex descent",
        "verify_conformal_vertex_descent.py",
        "CONFORMAL PAPER VERTEX DESCENT: ALL PASS",
    ),
    Certificate(
        "dynamical/topological quotient",
        "verify_conformal_dynamical_topological.py",
        "CONFORMAL C2l-P DYNAMICAL/TOPOLOGICAL SPLIT: ALL PASS",
    ),
)


# Each guard is expected to exit nonzero.  They are kept separate from the
# positive battery so a routine paper build remains concise.
GUARDS = (
    ("detour is not an explicit cylinder C1 map", "verify_conformal_detour_action.py", ("--require-explicit-cylinder-c1",)),
    ("BGG fine resolution is a literature theorem", "verify_conformal_bgg_bridge.py", ("--claim-machine-proof-of-bgg",)),
    ("smooth BGG exactness is not an analytic completion theorem", "verify_conformal_bgg_bridge.py", ("--claim-completed-domain",)),
    ("physical E/A/L preimages are not the complete off-shell harmonic complex", "verify_conformal_cylinder_preimages.py", ("--claim-complete-harmonic-complex",)),
    ("BGG split blocks are not raw magnetic-state matrices", "verify_conformal_cylinder_bgg_blocks.py", ("--claim-raw-coordinate-basis",)),
    ("degree-three BGG is not yet geometrically identified with the normalized Taub sector", "verify_conformal_bgg_bridge.py", ("--claim-taub-identification",)),
    ("BGG exactness is not the complete field-theory BV-domain transfer", "verify_conformal_bgg_bridge.py", ("--claim-completed-bv-transfer",)),
    ("residual CE saturation is not the complete field-theory pure-Weyl BFV pairing", "verify_conformal_bgg_bridge.py", ("--claim-pure-weyl-bfv-pairing",)),
    ("finite jets do not prove all levels", "verify_conformal_detour_polynomial.py", ("--claim-all-levels",)),
    ("finite jets do not prove Lorentzian E/A/L equivalence", "verify_conformal_detour_polynomial.py", ("--claim-lorentzian-eal",)),
    ("character equality is not local exactness", "verify_conformal_weyl_module.py", ("--claim-exact-sequence",)),
    ("a finite generator buffer is not the infinite domain", "verify_conformal_generator_all_levels.py", ("--require-infinite-module",)),
    ("moment-map jet is not physical cohomology", "verify_conformal_moment_map_energy4.py", ("--require-physical-cohomology",)),
    ("relative kernel is not full local BV cohomology", "verify_conformal_relative_brst_weight4.py", ("--claim-absolute-cohomology",)),
    ("Fock rail omits local/global BRST transfer", "verify_conformal_fock_energy4.py", ("--require-local-global-brst",)),
    ("absolute residual window omits local BRST", "verify_conformal_global_brst_window.py", ("--require-local-brst",)),
    ("absolute residual window is not full physical cohomology", "verify_conformal_global_brst_window.py", ("--require-physical-cohomology",)),
    ("Cartan rail does not derive local BV", "verify_conformal_cartan_contraction.py", ("--claim-local-bv",)),
    ("Cartan contraction requires D to be gauged", "verify_conformal_cartan_contraction.py", ("--treat-d-as-physical-hamiltonian",)),
    ("transfer fixture is not pure-Weyl BV", "verify_conformal_cartan_transfer.py", ("--claim-pure-weyl-bv",)),
    ("cyclic fixture is not pure-Weyl BV", "verify_conformal_cyclic_hpl.py", ("--claim-pure-weyl-bv",)),
    ("split free-BV contraction is not yet the full cyclic transfer", "verify_conformal_free_bv_complex.py", ("--claim-full-conformal-cyclic-transfer",)),
    ("minimal master-action chain is not the complete gauge-fixed field-BV domain", "verify_conformal_field_bv_dictionary.py", ("--claim-complete-field-bv-domain",)),
    ("gauge fixing alone does not perform the bulk-to-BFV zero-mode transfer", "verify_conformal_gauge_fixed_equivalence.py", ("--claim-dual-zero-mode-replacement",)),
    ("gauge-fixed dictionary is not the complete centered row ledger", "verify_conformal_gauge_fixed_equivalence.py", ("--claim-complete-row-inventory",)),
    ("canonical gauge fixing does not transfer the field BV/BFV pairing", "verify_conformal_gauge_fixed_equivalence.py", ("--claim-pairing-transfer",)),
    ("endpoint duality is not the time-slice BFV transgression", "verify_conformal_dual_zero_modes.py", ("--claim-bfv-transgression",)),
    ("bulk endpoint degree is not BFV ghost-momentum degree", "verify_conformal_dual_zero_modes.py", ("--claim-endpoint-is-bfv-momentum",)),
    ("role counting is not the no-duplication transfer theorem", "verify_conformal_residual_bfv_roles.py", ("--claim-no-duplication-transfer",)),
    ("compact split cyclicity is not full conformal equivariance", "verify_conformal_cyclic_bv_retract.py", ("--claim-full-so42-equivariance",)),
    ("intrinsic residual CE pairing is not the transferred BV pairing", "verify_conformal_residual_bfv_bridge.py", ("--claim-transferred-pure-weyl-pairing",)),
    ("raw SDR is homotopy-equivariant rather than strict", "verify_conformal_raw_bv_transfer.py", ("--claim-strict-sdr",)),
    ("algebraic cross-energy pairing is not the complete field-theory BV pairing", "verify_conformal_cross_energy_pairing.py", ("--claim-full-bv-pairing",)),
    ("integrated algebraic cohomology does not identify the complete field-theory BV/BFV domain", "verify_conformal_metric_to_residual_integration.py", ("--claim-complete-bv-bfv-pairing",)),
    ("the closed-universe choice does not make D universally gauge", "verify_conformal_closed_universe_bfv.py", ("--claim-universal-D-gauging",)),
    ("equivariance does not replace direct curvature integration in every magnetic block", "verify_conformal_taub_moment_map_all_levels.py", ("--claim-all-block-direct-curvature",)),
    ("Taub endpoint normalization does not compute the BFV transgression", "verify_conformal_taub_obstruction_map.py", ("--claim-bfv-transgression",)),
    ("the normalized endpoint/Taub/BFV data leave no arbitrary suspension magnitude", "verify_conformal_zero_mode_transgression.py", ("--claim-arbitrary-lambda",)),
    ("the algebraic zero-mode suspension is not an analytic boundary theorem", "verify_conformal_zero_mode_transgression.py", ("--claim-analytic-boundary-theorem",)),
    ("row concentration is a polarized-state result, not an unpolarized bulk-BV claim", "verify_conformal_polarized_state_complex.py", ("--claim-unpolarized-single-row",)),
    ("the algebraic polarized state complex is not a Hilbert/Krein completion", "verify_conformal_polarized_state_complex.py", ("--claim-hilbert-completion",)),
    ("the polarized I2 is not a positive particle Hilbert metric", "verify_conformal_polarized_pairing_transfer.py", ("--claim-particle-hilbert",)),
    ("the exact algebraic pairing is not an analytic completion theorem", "verify_conformal_polarized_pairing_transfer.py", ("--claim-analytic-pairing",)),
    ("the energy-mode Krein space has infinite positive and negative index", "verify_conformal_energy_mode_krein.py", ("--claim-pontryagin",)),
    ("the completed E/A/L space is not a positive graviton Hilbert space", "verify_conformal_energy_mode_krein.py", ("--claim-positive-graviton-hilbert",)),
    ("closed unbounded conformal generators are not bounded group operators", "verify_conformal_energy_mode_krein.py", ("--claim-bounded-generators",)),
    ("formal matrix adjointness alone does not prove maximal adjoint domains", "verify_conformal_energy_mode_krein.py", ("--claim-formal-adjoint-domains",)),
    ("common-core Lie brackets do not prove group exponentiation", "verify_conformal_energy_mode_krein.py", ("--claim-group-representation",)),
    ("the energy Sobolev scale is not a covariant metric Sobolev theorem", "verify_conformal_energy_mode_krein.py", ("--claim-covariant-sobolev",)),
    ("the completed residual BRST operator is closed but unbounded", "verify_conformal_completed_residual.py", ("--claim-bounded-q",)),
    ("the centered ghost insertion is not a global ghost Krein metric", "verify_conformal_completed_residual.py", ("--claim-global-ghost-krein",)),
    ("completed Cartan localization still requires D to be gauged", "verify_conformal_completed_residual.py", ("--treat-d-as-physical-hamiltonian",)),
    ("the energy-mode theorem is not Green-hyperbolic", "verify_conformal_completed_residual.py", ("--claim-green-hyperbolic",)),
    ("the energy-mode theorem is not a Hadamard-state theorem", "verify_conformal_completed_residual.py", ("--claim-hadamard",)),
    ("the energy-mode theorem is not a quantum unitarity result", "verify_conformal_completed_residual.py", ("--claim-quantum-unitarity",)),
    ("the reduced cylinder theorem is not an arbitrary-background theorem", "verify_conformal_covariant_factorization.py", ("--claim-arbitrary-background",)),
    ("the TT projector is not local", "verify_conformal_covariant_factorization.py", ("--claim-local-tt-projector",)),
    ("the spectral E/L split is not local", "verify_conformal_covariant_factorization.py", ("--claim-local-branch-split",)),
    ("the spectral E/L split is not certified support-preserving", "verify_conformal_covariant_factorization.py", ("--claim-causal-branch-split",)),
    ("the vector Killing band is not a metric A_2 block", "verify_conformal_covariant_factorization.py", ("--include-vector-killing-as-a2",)),
    ("reduced Green factors are not a full BV Green witness", "verify_conformal_covariant_factorization.py", ("--claim-full-bv-green",)),
    ("the exact ghost biwave does not imply a direct metric factorization", "verify_conformal_minimal_witness.py", ("--claim-exact-factorization",)),
    ("the auxiliary symbol witness is not a direct same-bundle factorization", "verify_conformal_auxiliary_green_realization.py", ("--claim-direct-factorization",)),
    ("the auxiliary symbol witness is not a direct causal homotopy on H", "verify_conformal_auxiliary_green_realization.py", ("--claim-direct-original-causal-homotopy",)),
    ("the symbol witness is not the curved global witness", "verify_conformal_auxiliary_green_realization.py", ("--claim-curved-globalization",)),
    ("the recognition identity is not a constructed causal homotopy", "verify_conformal_auxiliary_green_realization.py", ("--claim-causal-homotopy",)),
    ("the action-derived curved gauge map is not the full curved witness identity", "verify_conformal_curved_operator_workstream.py", ("--claim-curved-operator-identity",)),
    ("the canonical auxiliary shift is not yet the actual curved-Q deformation retract", "verify_conformal_curved_retract.py", ("--claim-curved-deformation-retract",)),
    ("the exact action-level current improvement is not the complete curved current theorem", "verify_conformal_curved_current.py", ("--claim-curved-current",)),
    ("the current algorithm has not emitted both complete curved presymplectic potentials", "verify_conformal_curved_current.py", ("--claim-curved-potentials",)),
    ("formal witness consequences do not replace the curved Green/current equality", "verify_conformal_curved_current.py", ("--claim-green-current-equality",)),
    ("the covariant theorem waits for curved coefficients and the Green current", "verify_conformal_covariant_bv_last_mile.py", ("--claim-complete-covariant-theorem",)),
    ("the curved lower-order coefficient table is not emitted", "verify_conformal_covariant_bv_last_mile.py", ("--claim-curved-coefficient-table",)),
    ("the Fourier SDR is not yet the curved support-category retract", "verify_conformal_covariant_bv_last_mile.py", ("--claim-curved-retract",)),
    ("the covariant/Cauchy pairing is not inferred from I2", "verify_conformal_covariant_bv_last_mile.py", ("--claim-covariant-cauchy-pairing",)),
    ("the exact Fourier witness is not the curved operator identity", "verify_conformal_covariant_dependency_report.py", ("--claim-curved-operator",)),
    ("the support-local Fourier SDR is not the curved deformation retract", "verify_conformal_covariant_dependency_report.py", ("--claim-curved-retract",)),
    ("the reduced EAL current is not the curved current comparison", "verify_conformal_covariant_dependency_report.py", ("--claim-curved-current",)),
    ("wave symbols do not by themselves prove complete BV Green hyperbolicity", "verify_conformal_covariant_dependency_report.py", ("--claim-complete-green-hyperbolicity",)),
    ("the final covariant H4 transport remains dependency-blocked", "verify_conformal_covariant_dependency_report.py", ("--claim-final-covariant-h4",)),
    ("the transport theorem cannot promote while curved inputs are false", "verify_conformal_final_covariant_transport.py", ("--claim-final-covariant-h4",)),
    ("the final theorem transports rather than recomputes auxiliary H4", "verify_conformal_final_covariant_transport.py", ("--recompute-auxiliary-h4",)),
    ("the four covariant flags cannot be promoted while curved lemmas are open", "verify_conformal_four_flag_closure.py", ("--claim-complete",)),
    ("the vector field residue has elliptic order two", "verify_conformal_cauchy_sobolev.py", ("--claim-vector-residue-order-zero",)),
    ("the vector Cauchy space is not H half plus H minus half", "verify_conformal_cauchy_sobolev.py", ("--claim-vector-h-half",)),
    ("the raw Bach data carry a mixed graph norm", "verify_conformal_cauchy_sobolev.py", ("--claim-product-sobolev",)),
    ("equation factorization alone does not fix the pairing", "verify_conformal_cauchy_sobolev.py", ("--claim-factorization-fixes-pairing",)),
    ("the Cauchy theorem is not distributional or Hadamard", "verify_conformal_cauchy_sobolev.py", ("--claim-hadamard",)),
    ("vertex descent is not a particle Hilbert theorem", "verify_conformal_vertex_descent.py", ("--claim-particle-hilbert",)),
    ("Pontryagin is not globally trivial", "verify_conformal_dynamical_topological.py", ("--claim-pontryagin-globally-trivial",)),
    ("theta can retain boundary observables", "verify_conformal_dynamical_topological.py", ("--claim-theta-has-no-observables",)),
    ("only one local dynamical direction", "verify_conformal_dynamical_topological.py", ("--claim-two-local-dynamics",)),
)


def run_command(script: str, args: tuple[str, ...], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "symbolic" / script), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def run_positive(quick: bool, verbose: bool, timeout: int) -> None:
    selected = tuple(c for c in CERTIFICATES if not (quick and c.slow))
    print(f"positive certificates: {len(selected)}/{len(CERTIFICATES)}")
    for index, certificate in enumerate(selected, start=1):
        started = time.monotonic()
        print(f"[{index:02d}/{len(selected):02d}] {certificate.name} ...", flush=True)
        result = run_command(certificate.script, certificate.args, timeout)
        elapsed = time.monotonic() - started
        if result.returncode != 0 or certificate.marker not in result.stdout:
            print(result.stdout)
            raise SystemExit(
                f"certificate failed: {certificate.name} "
                f"(exit={result.returncode}, marker={certificate.marker!r})"
            )
        if verbose:
            print(result.stdout.rstrip())
        print(f"    PASS ({elapsed:.2f}s): {certificate.marker}")


def run_guards(timeout: int, verbose: bool) -> None:
    print(f"expected-failure guards: {len(GUARDS)}")
    for index, (name, script, args) in enumerate(GUARDS, start=1):
        print(f"[G{index:02d}/{len(GUARDS):02d}] {name} ...", flush=True)
        result = run_command(script, args, timeout)
        if result.returncode == 0:
            print(result.stdout)
            raise SystemExit(f"guard unexpectedly passed: {name}")
        if verbose:
            print(result.stdout.rstrip())
        else:
            final_line = next(
                (line for line in reversed(result.stdout.splitlines()) if line.strip()),
                "nonzero exit",
            )
            print(f"    EXPECTED FAIL: {final_line}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="omit the slow exact matrix, rank, cross-energy, and HPL jobs",
    )
    parser.add_argument(
        "--guards",
        action="store_true",
        help="also run every declared expected-failure overclaim guard",
    )
    parser.add_argument(
        "--guards-only",
        action="store_true",
        help="run only the declared expected-failure overclaim guards",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800, help="per-process seconds")
    parser.add_argument("--list", action="store_true", help="list jobs without running them")
    args = parser.parse_args()

    if args.list:
        for certificate in CERTIFICATES:
            suffix = " [slow]" if certificate.slow else ""
            print(f"CERT {certificate.name}: {certificate.script}{suffix}")
        for name, script, guard_args in GUARDS:
            print(f"GUARD {name}: {script} {' '.join(guard_args)}")
        return

    print("=== Free conformal paper verification ===")
    print("residual scientific input commit:", RESIDUAL_SOURCE_COMMIT)
    print("BGG bridge revision base:", BGG_REVISION_BASE_COMMIT)
    print("algebraic BV-BFV snapshot:", ALGEBRAIC_BV_BFV_SNAPSHOT_COMMIT)
    print("python:", sys.version.split()[0])
    print("sympy:", sp.__version__)
    if not args.guards_only:
        run_positive(args.quick, args.verbose, args.timeout)
    if args.guards or args.guards_only:
        run_guards(args.timeout, args.verbose)
    print(
        "CONFORMAL FREE PAPER BATTERY: ALL PASS. The exact result is the "
        "minimal residual vertex cohomology plus the smooth Bach-curvature "
        "bridge, all-energy E/A/L metric preimages, and an end-to-end "
        "algebraic polynomial metric-to-residual calculation with a "
        "field-derived minimal master-action/raw-chain dictionary and "
        "gauge-fixed/nonminimal contraction, "
        "canonical dual endpoint and Taub obstruction map, "
        "normalized algebraic BV-to-BFV zero-mode suspension, selected "
        "positive-frequency state polarization, and field pairing transfer, "
        "cross-energy cyclic form, complete centered HPL transfer, explicit "
        "closed-universe BFV choice, and all-energy Taub normalization. The "
        "algebraic result has a certified infinite-index energy-mode "
        "Krein--Fock completion with closed residual BRST operator, bounded "
        "off-center Cartan contraction, closed range, and unchanged centered "
        "H4 and I2. The reduced Lorentzian metric fields now have an exact "
        "tensor-curl Green factorization and a field-induced branch "
        "Cauchy--Sobolev realization Krein-unitarily equivalent to the "
        "energy-mode module. The exact ghost biwave, auxiliary four-row "
        "symbol witness, and 66-to-30 Fourier SDR with support-local formulas "
        "are proved. The curved workstreams additionally certify the exact "
        "covariant action/gauge map, parallel-curvature normal form, local "
        "BV-canonical auxiliary shift with universal SDR, and action-level "
        "auxiliary/metric current improvement. A machine-readable four-flag "
        "claim DAG keeps the curved operator, "
        "deformation-retract, and current-comparison lemmas false and blocks "
        "every dependent theorem. The expanded curved Hessian/companion and "
        "adjoint table, actual curved-Q retract, full curved presymplectic and "
        "Green-current comparison, a direct same-bundle metric factorization, complete "
        "covariant/Cauchy pairing comparison, "
        "distributional/Hadamard completion, uniqueness among alternative "
        "boundary polarizations, nonlinear stability, and quantum theory "
        "remain explicitly out of scope."
    )


if __name__ == "__main__":
    main()

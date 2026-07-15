#!/usr/bin/env python3
"""Verify and emit the Weyl electric/magnetic principal evolution block."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_evolution import (
    CurvatureEvolutionPrincipalSymbol,
)
from covariant_completion.curved_operator.curvature_eb_bundle import (
    WeylElectricMagneticBundle,
)
from covariant_completion.curved_operator.curvature_eb_jets import (
    CurvedWeylCottonJetComparison,
)
from covariant_completion.curved_operator.curvature_eal_spectrum import (
    AllLevelCurvatureEALSpectrum,
)
from covariant_completion.curved_operator.curvature_prolongation_status import (
    OPEN_OBLIGATION_FIELDS,
    CurvatureProlongationStatus,
)
from covariant_completion.curved_operator.weyl_3plus1 import (
    WeylCottonBachFirstOrder,
    WeylCottonThreePlusOne,
)
from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (
    ConstraintAdjustedWeylCottonEvolution,
)
from covariant_completion.curved_operator.weyl_cotton_differential_ideal import (
    WeylCottonDifferentialIdealAudit,
)
from covariant_completion.curved_operator.weyl_cotton_formal_integrability import (
    WeylCottonFormalIntegrability,
)
from covariant_completion.curved_operator.weyl_cotton_causal_pde import (
    CausalWeylCottonPDE,
)
from covariant_completion.curved_operator.weyl_cotton_row_audit import (
    WeylCottonRowReductionAudit,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_evolution_principal_symbol.json"
)
STATUS_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_prolongation_status.json"
)
EB_BUNDLE_CERTIFICATE = (
    ROOT / "covariant_completion" / "certificates" / "curved_curvature_eb_bundle.json"
)
WEYL_COTTON_CERTIFICATE = (
    ROOT / "covariant_completion" / "certificates" / "curved_weyl_cotton_3plus1.json"
)
BACH_FIRST_ORDER_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_bach_first_order.json"
)
JET_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_jet_comparison.json"
)
HYPERBOLIC_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_hyperbolic.json"
)
ROW_AUDIT_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_row_audit.json"
)
DIFFERENTIAL_IDEAL_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_differential_ideal.json"
)
FORMAL_INTEGRABILITY_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_formal_integrability.json"
)
CAUSAL_PDE_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_causal_pde.json"
)
EAL_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_EAL_spectrum_all_level.json"
)
MAPPING_CYLINDER_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_mapping_cylinder_substitution.json"
)
CURVED_CORE_CHAIN_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_core_curvature_chain_map.json"
)
PREIMAGE_CERTIFICATE = ROOT / "bridge" / "certificates" / "cylinder_metric_preimages.json"
BGG_CERTIFICATE = ROOT / "bridge" / "certificates" / "cylinder_bgg_blocks.json"


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("wrote", path.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    status = CurvatureEvolutionPrincipalSymbol.build()
    certificate = status.certificate()
    eb_bundle_certificate = WeylElectricMagneticBundle.build().certificate()
    weyl_cotton_certificate = WeylCottonThreePlusOne.build().certificate()
    bach_first_order_certificate = WeylCottonBachFirstOrder.build().certificate()
    jet_certificate = CurvedWeylCottonJetComparison.build().certificate()
    hyperbolic_certificate = ConstraintAdjustedWeylCottonEvolution.build().certificate()
    row_audit_certificate = WeylCottonRowReductionAudit.build().certificate()
    differential_ideal_certificate = WeylCottonDifferentialIdealAudit.build().certificate()
    formal_integrability_certificate = WeylCottonFormalIntegrability.build().certificate()
    causal_pde_certificate = CausalWeylCottonPDE.build().certificate()
    eal_certificate = AllLevelCurvatureEALSpectrum.build(
        jet_certificate=jet_certificate,
        preimage_certificate=json.loads(PREIMAGE_CERTIFICATE.read_text(encoding="utf-8")),
        bgg_certificate=json.loads(BGG_CERTIFICATE.read_text(encoding="utf-8")),
    ).certificate()
    prolongation = CurvatureProlongationStatus.build(
        phase1_certificate=jet_certificate,
        eal_certificate=eal_certificate,
        hyperbolic_certificate=hyperbolic_certificate,
        differential_ideal_certificate=differential_ideal_certificate,
        formal_integrability_certificate=formal_integrability_certificate,
        mapping_cylinder_certificate=json.loads(
            MAPPING_CYLINDER_CERTIFICATE.read_text(encoding="utf-8")
        ),
        curved_core_chain_certificate=json.loads(
            CURVED_CORE_CHAIN_CERTIFICATE.read_text(encoding="utf-8")
        ),
    )
    prolongation_certificate = prolongation.certificate()
    if args.emit:
        _write(CERTIFICATE, certificate)
        _write(EB_BUNDLE_CERTIFICATE, eb_bundle_certificate)
        _write(WEYL_COTTON_CERTIFICATE, weyl_cotton_certificate)
        _write(BACH_FIRST_ORDER_CERTIFICATE, bach_first_order_certificate)
        _write(JET_CERTIFICATE, jet_certificate)
        _write(HYPERBOLIC_CERTIFICATE, hyperbolic_certificate)
        _write(ROW_AUDIT_CERTIFICATE, row_audit_certificate)
        _write(DIFFERENTIAL_IDEAL_CERTIFICATE, differential_ideal_certificate)
        _write(FORMAL_INTEGRABILITY_CERTIFICATE, formal_integrability_certificate)
        _write(CAUSAL_PDE_CERTIFICATE, causal_pde_certificate)
        _write(EAL_CERTIFICATE, eal_certificate)
        _write(STATUS_CERTIFICATE, prolongation_certificate)
    if args.guards:
        if not certificate[
            "candidate_curvature_principal_symmetric_hyperbolicity"
        ]:
            raise AssertionError("principal curvature hyperbolicity regressed")
        if not certificate["candidate_curvature_principal_constraints_propagate"]:
            raise AssertionError("principal curvature constraint closure regressed")
        evolution_false_obligations = (
            "principal_system_derived_from_curved_Bianchi_Bach",
            "curved_Bianchi_Bach_lower_terms_derived",
            "curved_EB_equations",
            "curved_EB_first_order_closure",
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
            "curvature_constraints_propagate",
            "curved_constraint_propagation",
            "EAL_curvature_spectrum_match",
            "local_prolongation_retract_verified",
            "support_local_prolongation_retract",
            "prolonged_BV_operator_identity",
            "prolonged_green_witness",
            "curvature_causal_green_operators",
            "causal_green_homotopy",
            "complete_curvature_green_realization",
        )
        for false_obligation in evolution_false_obligations:
            if certificate[false_obligation]:
                raise AssertionError(f"open obligation was inferred: {false_obligation}")
        if not prolongation_certificate["weyl_symbol_helicity_isomorphism"]:
            raise AssertionError("exact reduced Weyl-symbol theorem regressed")
        if set(prolongation_certificate["atomic_open_obligations"]) != set(
            OPEN_OBLIGATION_FIELDS
        ):
            raise AssertionError("expanded curvature obligation ledger is incomplete")
        promoted = {
            "curved_EB_equations",
            "curved_EB_first_order_closure",
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
            "curved_constraint_propagation",
            "EAL_curvature_spectrum_match",
            "support_local_prolongation_retract",
            "prolonged_BV_operator_identity",
        }
        for open_obligation in OPEN_OBLIGATION_FIELDS:
            expected = open_obligation in promoted
            if prolongation_certificate[open_obligation] is not expected:
                raise AssertionError(
                    "curvature obligation promotion mismatch: "
                    f"{open_obligation}={prolongation_certificate[open_obligation]}"
                )
        if not prolongation_certificate["curvature_prolonged_complex_exact"]:
            raise AssertionError("the exact local prolonged complex regressed")
        if prolongation_certificate["curvature_green_realization"]:
            raise AssertionError("curvature Green realization was inferred")
        if any(prolongation_certificate["proof_boundary"].values()):
            raise AssertionError("a fail-closed proof boundary was crossed")
        if jet_certificate["tested_two_jets"] != 150:
            raise AssertionError("curved Weyl two-jet coverage regressed")
        if not jet_certificate["coverage_complete"]:
            raise AssertionError("curved Weyl two-jet coverage is incomplete")
        if bach_first_order_certificate["temporal_matrix_rank"] != 26:
            raise AssertionError("Weyl--Cotton temporal closure rank regressed")
        if row_audit_certificate["row_equivalent_modulo_original_eight_constraints"]:
            raise AssertionError("rank-six hyperbolic row defect was hidden")
        if row_audit_certificate["exact_defect_rank"] != 6:
            raise AssertionError("hyperbolic row-equivalence defect rank drifted")
        if not differential_ideal_certificate[
            "covariant_and_adjusted_differential_ideals_equal"
        ]:
            raise AssertionError("formal-integrability repair regressed")
        if not differential_ideal_certificate["source_compatibility_map_available"]:
            raise AssertionError("compatible-source map regressed")
        if not formal_integrability_certificate[
            "compatible_sources_preserve_all_fourteen_constraints"
        ]:
            raise AssertionError("fourteen-constraint source propagation regressed")
        if not causal_pde_certificate["curvature_block_causal_solution_operators"]:
            raise AssertionError("curvature-block causal solution theorem regressed")
        if causal_pde_certificate["curvature_causal_green_operators"]:
            raise AssertionError("curvature-block theorem crossed the BV Green boundary")
        if not eal_certificate["all_level_not_finite_cutoff"]:
            raise AssertionError("E/A/L theorem regressed to a finite cutoff")
        dependent_obligations = tuple(
            name for name in OPEN_OBLIGATION_FIELDS if name not in promoted
        )
        fail_closed_base = CurvatureProlongationStatus.build()
        for premature_flag in dependent_obligations:
            premature = replace(fail_closed_base, **{premature_flag: True})
            try:
                premature.verify()
            except AssertionError:
                pass
            else:
                raise AssertionError(
                    f"dependency guard accepted premature flag: {premature_flag}"
                )
        guard_count = (
            2
            + len(evolution_false_obligations)
            + 1
            + len(OPEN_OBLIGATION_FIELDS)
            + 14
            + len(dependent_obligations)
        )
        print(f"CURVATURE EVOLUTION GUARDS: {guard_count}/{guard_count} PASS")
    print(
        "CURVATURE EVOLUTION: EXACT PHASE-1 EQUATIONS AND FIRST-ORDER "
        "CLOSURE CERTIFIED"
    )


if __name__ == "__main__":
    main()

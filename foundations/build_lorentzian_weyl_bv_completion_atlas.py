#!/usr/bin/env python3
"""Build the branch-by-stage Lorentzian Weyl BV completion atlas."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v1.md"

INPUTS = [
    ("quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_CERTIFICATE.json", "historical all-check import gate"),
    ("quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json", "successor minimal-BV import repair"),
    ("quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json", "cross-commit classical snapshot bridge"),
    ("quantum-weyl/transfer/certificates/BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json", "independent Berger q2 replay"),
    ("covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json", "strict 386-row causal BV homotopy"),
    ("d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json", "Bach-flat rank-310 causal branch"),
    ("d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json", "Einstein metric biwave branch"),
    ("d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json", "Nariai/KS rank-310 transfer"),
    ("d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json", "Berger retained causal homotopy"),
    ("d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json", "Berger complete gauge-fixed causal homotopy"),
    ("d_quotient_classical/certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json", "Berger nonlinear cyclic compatibility"),
    ("quantum-weyl/lorentzian/certificates/BERGER_RETAINED26_HADAMARD_WARD_REDUCTION.json", "Berger Hadamard/CCR candidate and Ward defect"),
    ("quantum-weyl/lorentzian/certificates/BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION.json", "Berger Ward-correction nondefinition"),
    ("quantum-weyl/lorentzian/certificates/BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION.json", "scoped stationary normalization obstruction"),
    ("quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json", "reduced physical-mode Hadamard control"),
    ("quantum-weyl/anomalies/certificates/REGULATED_SLAVNOV_QME_DISPOSITION.json", "strict local Euclidean one-loop obstruction"),
    ("quantum-weyl/anomalies/certificates/TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json", "conditional changed-theory local QME theorem"),
    ("d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json", "tau-adic causal extension obstruction"),
    ("d_quotient_classical/certificates/COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json", "changed-action causal parent"),
    ("quantum-weyl/cartan/certificates/QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION.json", "quantum D-Cartan coefficient disposition"),
]

STAGES = [
    ("S0_CLASSICAL_AUTHORITY", "Classical authority", "A content-pinned classical BV snapshot passes the receiver's nilpotency, contraction, chain-map, cyclicity, residual-cohomology and pairing checks."),
    ("S1_OFF_SHELL_BV", "Off-shell BV carrier", "The complete declared fields, ghosts, antifields and nonminimal rows carry exact differentials and pairings."),
    ("S2_CAUSAL_GREEN", "Causal Green homotopy", "Advanced and retarded homotopies exist on every required row with declared support and two-sided chain identities."),
    ("S3_NONLINEAR_CARTAN", "Nonlinear cyclic compatibility", "The causal contraction is compatible with support-local interactions and the cyclic D-Cartan recurrence to the declared arity."),
    ("S4_HADAMARD_CCR", "Hadamard/CCR carrier", "A normalized global two-point distribution has the required singularity and commutator on the same carrier and background."),
    ("S5_BRST_WARD", "BRST Ward identity", "The two-point distribution is compatible with the BV differential, or a valid smooth correction is constructed in a declared bikernel support class."),
    ("S6_PHYSICAL_POSITIVITY", "Physical positivity", "Positivity is proved on the physical BRST quotient; an indefinite Krein covariance is kept distinct from a Hilbert state."),
    ("S7_RENORMALIZED_PRODUCTS", "Renormalized products", "Lorentzian time-ordered products satisfying the required causal, microlocal and symmetry axioms are constructed."),
    ("S8_QME", "Quantum master equation", "The anomaly class is classified, coefficients are computed in the same theory, and the local Lorentzian QME is restored."),
    ("S9_RESIDUAL_TRANSFER", "Residual transfer", "Only after QME restoration is the quantum correction transferred through pi_cl to the certified residual complex."),
    ("S10_LORENTZIAN_CERTIFIED", "Lorentzian completion", "The full declared theory, rather than a reduced mode or changed action, has passed the causal quantum lifecycle."),
]

STATUS = {
    "CERTIFIED": "The complete requirement is certified for the branch exactly as declared.",
    "SCOPED_CERTIFIED": "The requirement is certified only on the named background, carrier, arity or theory variant.",
    "PARTIAL_CERTIFIED": "Several required pieces are certified, but the complete stage is not.",
    "CONDITIONAL": "A theorem exists only under an explicit unconstructed hypothesis.",
    "OPEN_SEEDED": "Concrete inputs or a candidate exist, but the stage theorem is absent.",
    "OBSTRUCTED_SCOPED": "An exact obstruction rules out the declared subclass, not all neighboring routes.",
    "FAIL_CLOSED": "The acceptance conditions are not all met; no positive promotion is allowed.",
    "FORBIDDEN_TRANSFER": "Earlier evidence is of the wrong type or lifecycle to justify this stage.",
    "NOT_APPLICABLE": "The branch intentionally does not target this full-theory stage.",
}


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def cell(stage: str, status: str, statement: str, evidence: list[str], boundary: str) -> dict[str, Any]:
    return {"stage": stage, "status": status, "statement": statement, "evidence": evidence, "boundary": boundary}


def branch(branch_id: str, name: str, relation: str, scope: str, cells: list[dict[str, Any]], first_gate: str, next_object: str) -> dict[str, Any]:
    return {
        "id": branch_id,
        "name": name,
        "relation_to_target": relation,
        "scope": scope,
        "stages": cells,
        "first_unclosed_gate": first_gate,
        "next_decisive_object": next_object,
    }


def build() -> dict[str, Any]:
    docs = {path: json.loads((ROOT / path).read_text()) for path, _ in INPUTS}
    old_gate = docs[INPUTS[0][0]]
    import_v2 = docs[INPUTS[1][0]]
    strict_green = docs[INPUTS[4][0]]
    berger26 = docs[INPUTS[8][0]]
    berger54 = docs[INPUTS[9][0]]
    berger_had = docs[INPUTS[11][0]]
    reduced = docs[INPUTS[14][0]]
    tau_qme = docs[INPUTS[16][0]]
    tau_causal = docs[INPUTS[17][0]]
    changed = docs[INPUTS[18][0]]

    if old_gate.get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("historical import gate unexpectedly changed")
    if not import_v2["claim_flags"]["CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT"]:
        raise ValueError("minimal-BV repair missing")
    if strict_green.get("causal_green_homotopy") is not True:
        raise ValueError("strict causal homotopy missing")
    if berger26.get("result_state") != "GREEN_CERTIFIED_HADAMARD_OPEN":
        raise ValueError("Berger 26-row causal state drift")
    if berger54.get("next_gate") != "BERGER_CAUSAL_D_CARTAN_V2":
        raise ValueError("Berger 54-row causal state drift")
    if not berger_had["claim_flags"]["BERGER_26_ROW_HADAMARD_EXACT_CCR_CANDIDATE"]:
        raise ValueError("Berger Hadamard candidate missing")
    if not reduced["claim_flags"]["REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"]:
        raise ValueError("reduced Hadamard control missing")
    if tau_qme["claim_flags"]["UNCONDITIONAL_ALL_LOOP_QME"]:
        raise ValueError("tau-adic QME boundary promoted")
    if not tau_causal["claim_flags"]["COMPLETE_DECLARED_FINITE_DIFFERENTIAL_CLASS_OBSTRUCTED"]:
        raise ValueError("tau-adic causal obstruction missing")
    if not changed["claim_flags"]["CHANGED_CLASSICAL_ACTION"]:
        raise ValueError("changed-action boundary missing")

    branches = [
        branch(
            "STRICT_PURE_WEYL_386",
            "Strict pure-Weyl full BV",
            "TARGET_THEORY",
            "The fixed-field-content pure-Weyl action, including the certified 386-row prolonged vacuum-cylinder causal complex.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "FAIL_CLOSED", "The historical all-check receiver gate remains red, although later minimal-BV and snapshot-compatibility repairs are certified.", ["CLASSICAL_IMPORT_CERTIFICATE", "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY"], "Separate successor receipts do not silently constitute a replacement full freeze certificate."),
                cell("S1_OFF_SHELL_BV", "SCOPED_CERTIFIED", "A complete prolonged 386-row classical BV carrier is certified on the vacuum-cylinder architecture.", ["pure-weyl-full-prolonged-green-homotopy-assembly-v1"], "This does not by itself pass the independent quantum import/freeze gate."),
                cell("S2_CAUSAL_GREEN", "SCOPED_CERTIFIED", "The prolonged carrier has an all-row causal Green homotopy assembled from 356 algebraic and 30 causal endpoint rows.", ["pure-weyl-full-prolonged-green-homotopy-assembly-v1"], "The theorem is architecture/background scoped and is not a Hadamard construction."),
                cell("S3_NONLINEAR_CARTAN", "OPEN_SEEDED", "Local BV interaction and Cartan ingredients exist, but no coefficient-bearing closed strict Lorentzian D-Cartan defect is classified.", ["QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION"], "A local source ledger is not a causal nonlinear contraction."),
                cell("S4_HADAMARD_CCR", "OPEN_SEEDED", "Reduced physical-mode Hadamard evidence exists on the same vacuum cylinder, but no full 386-row BRST covariance is constructed.", ["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"], "Reduced-mode kernels cannot be promoted to the off-shell BV carrier."),
                cell("S5_BRST_WARD", "FAIL_CLOSED", "No full-carrier BRST-compatible Hadamard covariance is certified.", [], "A causal Green homotopy supplies the commutator, not a BRST Hadamard state."),
                cell("S6_PHYSICAL_POSITIVITY", "OPEN_SEEDED", "The reduced E branch is positive, while A and L remain negative-Krein; no positive full physical quotient is certified.", ["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"], "Krein covariance is not Hilbert-space positivity."),
                cell("S7_RENORMALIZED_PRODUCTS", "FAIL_CLOSED", "No renormalized Lorentzian time-ordered products exist for the full theory.", [], "Euclidean determinants and local counterterm classifications are different objects."),
                cell("S8_QME", "OBSTRUCTED_SCOPED", "The strict fixed-field-content local Euclidean BV QME is obstructed at one loop.", ["REGULATED_SLAVNOV_QME_DISPOSITION"], "This does not rule out anomaly-cancelling matter or a genuinely different compensator theory, and it is not a Lorentzian QME theorem."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "Residual quantum transfer is not authorized before QME restoration.", [], "The centered [W_+^2] and [W_-^2] classes remain deformation/vertex classes, not particle states."),
                cell("S10_LORENTZIAN_CERTIFIED", "FAIL_CLOSED", "The strict target theory has not completed the Lorentzian quantum lifecycle.", [], "Classical causal completion is necessary but not sufficient."),
            ],
            "S0_CLASSICAL_AUTHORITY",
            "A replacement full classical-import certificate that folds the later exact repairs into every original freeze check without weakening the acceptance contract.",
        ),
        branch(
            "PURE_WEYL_BACH_FLAT_RANK310",
            "Pure-Weyl Bach-flat rank-310",
            "TARGET_THEORY_SCOPED_BACKGROUND",
            "A relative-open Bach-flat ADM class and its natural curvature-corrected rank-310 mapping-cone carrier.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "SCOPED_CERTIFIED", "The classical construction and cyclic transfer inputs are content-pinned inside the branch certificate.", ["BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1"], "This is not the quantum programme's full repository freeze gate."),
                cell("S1_OFF_SHELL_BV", "SCOPED_CERTIFIED", "The natural rank-310 all-row mapping-cone carrier is exact on the declared class.", ["BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1"], "No pure normal-tractor-parent-to-metric SDR is claimed."),
                cell("S2_CAUSAL_GREEN", "SCOPED_CERTIFIED", "Advanced and retarded all-row homotopies transfer from the metric Bach complex.", ["BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1"], "The class is relative-open, not all smooth Lorentzian metrics."),
                cell("S3_NONLINEAR_CARTAN", "OPEN_SEEDED", "Cyclic transfer machinery exists, but no branch-specific nonlinear D-Cartan closure is certified.", ["BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1"], "Unary cyclic Green transfer is not interacting closure."),
                cell("S4_HADAMARD_CCR", "FAIL_CLOSED", "No rank-310 Hadamard covariance is constructed.", [], "Causal support does not establish wavefront-set control."),
                cell("S5_BRST_WARD", "FAIL_CLOSED", "No rank-310 BRST Ward covariance is constructed.", [], "No state exists here on which to impose the identity."),
                cell("S6_PHYSICAL_POSITIVITY", "FAIL_CLOSED", "No physical quotient positivity theorem is present.", [], "No particle interpretation follows from the residual deformation complex."),
                cell("S7_RENORMALIZED_PRODUCTS", "FAIL_CLOSED", "Lorentzian products are absent.", [], "Classical transfer is not renormalization."),
                cell("S8_QME", "FAIL_CLOSED", "No Lorentzian QME is defined on this branch.", [], "Local or Euclidean coefficients cannot be transferred without common-theory typing."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "Quantum residual transfer is not authorized.", [], "QME restoration must precede transfer."),
                cell("S10_LORENTZIAN_CERTIFIED", "FAIL_CLOSED", "The branch is classically causal, not quantum-complete.", [], "The positive result ends at the classical causal stage."),
            ],
            "S3_NONLINEAR_CARTAN",
            "A support-local q2/q3 import and cyclic D-Cartan recurrence on the same rank-310 Bach-flat carrier, or a proof that the transfer preserves the required nonlinear brackets.",
        ),
        branch(
            "EINSTEIN_NARIAI_KS",
            "Einstein/Nariai metric and rank-310 controls",
            "TARGET_THEORY_CONTROL_CLASS",
            "Globally hyperbolic Einstein backgrounds with Ric=g, including certified common Kantowski--Sachs slabs and unit Nariai.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "SCOPED_CERTIFIED", "Exact metric and transferred complexes are pinned by their branch certificates.", ["EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1", "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1"], "This does not replace the repository-wide quantum import gate."),
                cell("S1_OFF_SHELL_BV", "SCOPED_CERTIFIED", "The complete gauge-fixed four-row metric Bach complex and a natural rank-310 common-slab transfer are certified.", ["EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1", "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1"], "The rank-310 theorem is limited to certified common slabs."),
                cell("S2_CAUSAL_GREEN", "SCOPED_CERTIFIED", "Exact advanced and retarded homotopies exist on the four-row metric complex and transfer to the rank-310 common-slab carrier.", ["EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1", "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1"], "No whole-cylinder nonzero KS family is claimed."),
                cell("S3_NONLINEAR_CARTAN", "OPEN_SEEDED", "The branch supplies a curved causal control but no certified nonlinear D-Cartan recurrence.", [], "A free metric complex is not an interacting BV theory."),
                cell("S4_HADAMARD_CCR", "OPEN_SEEDED", "Normally-hyperbolic factorization makes Hadamard construction plausible, but no branch covariance is serialized.", ["EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1"], "Applicability of a theorem is not an explicit normalized state."),
                cell("S5_BRST_WARD", "FAIL_CLOSED", "No BRST Ward covariance is constructed.", [], "Metric-sector Hadamard data would still require ghost and antifield compatibility."),
                cell("S6_PHYSICAL_POSITIVITY", "FAIL_CLOSED", "No physical positivity theorem is present.", [], "Fourth-order factorization can carry indefinite sectors."),
                cell("S7_RENORMALIZED_PRODUCTS", "FAIL_CLOSED", "Lorentzian products are absent.", [], "Free causal control is not pAQFT."),
                cell("S8_QME", "FAIL_CLOSED", "No branch-specific Lorentzian QME is defined.", [], "Background trace anomalies are not BV master-equation breakings."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "Quantum transfer is not authorized.", [], "The lifecycle has not reached QME restoration."),
                cell("S10_LORENTZIAN_CERTIFIED", "FAIL_CLOSED", "The branch is a strong curved control, not a completed theory.", [], "Its value is analytic generality through the causal stage."),
            ],
            "S3_NONLINEAR_CARTAN",
            "A nonlinear support-local BV interaction and cyclic causal transfer theorem on the same Einstein/Nariai carrier; independently, serialize one normalized factorwise Hadamard covariance as the analytic control.",
        ),
        branch(
            "BERGER_POSITIVE_CLOCK_54",
            "Berger positive-clock 54-row BV",
            "NEIGHBORING_CLOCK_ARCHITECTURE",
            "The frozen rational Berger fixture with a positive clock, 26 retained rows and the complete 54-row gauge-fixed classical complex.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "SCOPED_CERTIFIED", "The complete support-local q2 tensor is imported and independently replayed with exact Q(sqrt(10)) arithmetic.", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"], "This is Berger-specific and not the strict pure-Weyl freeze."),
                cell("S1_OFF_SHELL_BV", "CERTIFIED", "The declared 54-row gauge-fixed classical Berger BV carrier and pairing/Koszul structure are complete at the fixture.", ["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "BERGER_ARITY_THREE_D_CARTAN_FULL_4D"], "Certification is fixture-specific."),
                cell("S2_CAUSAL_GREEN", "CERTIFIED", "Advanced and retarded chain homotopies exist on all 26 retained and all 54 gauge-fixed rows.", ["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"], "This remains classical causal data."),
                cell("S3_NONLINEAR_CARTAN", "SCOPED_CERTIFIED", "The cyclic two-sided-causal D-Cartan recurrence closes through arity three on the complete 54-row four-dimensional complex.", ["BERGER_ARITY_THREE_D_CARTAN_FULL_4D"], "Arity four and separately retarded higher primitives are not claimed."),
                cell("S4_HADAMARD_CCR", "PARTIAL_CERTIFIED", "All 26 endpoint rows have global exact Hadamard carriers and an exact-CCR candidate; a real stationary compatible-complex-structure normalization is obstructed on the full homogeneous retained carrier.", ["BERGER_RETAINED26_HADAMARD_WARD_REDUCTION", "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION"], "The obstruction leaves nonstationary Krein representatives open."),
                cell("S5_BRST_WARD", "OPEN_SEEDED", "The exact Ward defect C26=[H26_plus,q26] is smooth, but no normalized H26 representative or admissible global bikernel correction is defined.", ["BERGER_RETAINED26_HADAMARD_WARD_REDUCTION", "BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION"], "Compact-source homotopies cannot silently act on an arbitrary smooth two-variable defect."),
                cell("S6_PHYSICAL_POSITIVITY", "FAIL_CLOSED", "No positive physical BRST quotient is certified.", [], "A Krein covariance is not positivity."),
                cell("S7_RENORMALIZED_PRODUCTS", "FAIL_CLOSED", "Renormalized Lorentzian products are absent.", [], "A free covariance is only the input to renormalization."),
                cell("S8_QME", "FAIL_CLOSED", "The coefficient-bearing Berger Cartan defect is analytically undefined and no Lorentzian QME is restored.", ["QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION"], "Classical D-Cartan closure does not cancel the quantum anomaly."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "Quantum residual transfer is not authorized.", [], "QME restoration must come first."),
                cell("S10_LORENTZIAN_CERTIFIED", "FAIL_CLOSED", "The branch is the analytically most advanced full classical route, but not a Lorentzian quantum theory.", [], "The first quantum obstruction is explicit rather than absent."),
            ],
            "S5_BRST_WARD",
            "A content-addressed nonstationary Krein H26_plus with declared Cauchy-time normalization, followed by exact C26 support/pairing classification and either a continuous bikernel homotopy correction or direct q26-equivariant Feynman selection.",
        ),
        branch(
            "VACUUM_CYLINDER_REDUCED",
            "Vacuum-cylinder reduced physical modes",
            "REDUCED_MODE_CONTROL",
            "The free E/A/L physical cohomology carrier on the unit vacuum conformal cylinder.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "SCOPED_CERTIFIED", "Normalized classical modes, reduced Green blocks and current pairing are imported on one background.", ["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"], "This is reduced cohomology, not the off-shell BV snapshot."),
                cell("S1_OFF_SHELL_BV", "NOT_APPLICABLE", "The branch intentionally omits ghosts, antifields and contractible rows.", [], "It cannot certify a full-BV claim."),
                cell("S2_CAUSAL_GREEN", "SCOPED_CERTIFIED", "Advanced and retarded reduced Green blocks are certified on the same background.", ["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"], "Reduced propagation cannot be used as a full-complex homotopy."),
                cell("S3_NONLINEAR_CARTAN", "NOT_APPLICABLE", "The result is free and reduced.", [], "No interacting D-Cartan claim is targeted."),
                cell("S4_HADAMARD_CCR", "SCOPED_CERTIFIED", "Global stationary spectral Krein two-point distributions are certified on the E/A/L carrier.", ["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"], "This is a REDUCED-MODE plus LORENTZIAN-CAUSAL result."),
                cell("S5_BRST_WARD", "NOT_APPLICABLE", "The off-shell BRST differential is absent from the carrier.", [], "Physical-cohomology construction does not prove the off-shell Ward identity."),
                cell("S6_PHYSICAL_POSITIVITY", "PARTIAL_CERTIFIED", "The E sector is positive; A and L have negative Krein sign, so the direct sum is indefinite.", ["VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD"], "No positive graviton Hilbert space is certified."),
                cell("S7_RENORMALIZED_PRODUCTS", "NOT_APPLICABLE", "No interacting product construction is attempted.", [], "A free reduced quasifree functional is not pAQFT."),
                cell("S8_QME", "NOT_APPLICABLE", "No off-shell BV Laplacian or interacting master equation exists on this reduced carrier.", [], "Reduced data cannot repair the strict QME."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "This is already a classical/free reduced carrier, not a post-QME quantum transfer.", [], "The lifecycle order cannot be reversed."),
                cell("S10_LORENTZIAN_CERTIFIED", "NOT_APPLICABLE", "The branch is a control for states, not a full theory completion.", [], "Its strength is the genuine Hadamard/Krein result at reduced scope."),
            ],
            "S1_OFF_SHELL_BV",
            "A same-background lift from the reduced E/A/L covariance to a complete off-shell BV covariance with ghost/antifield rows and a verified BRST Ward identity.",
        ),
        branch(
            "TAU_ADIC_COMPENSATOR",
            "Tau-adic compensator extension",
            "CHANGED_THEORY_FORMAL_EXTENSION",
            "A formal compensator theory used to study local anomaly cancellation; it is not strict pure Weyl gravity.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "SCOPED_CERTIFIED", "The strict 386-row input and formal Wess--Zumino cotangent/Cartan data are pinned.", ["TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1"], "The combined tau-adic carrier does not pass the causal contraction gate."),
                cell("S1_OFF_SHELL_BV", "PARTIAL_CERTIFIED", "A canonical scalar extension is assembled, but the dressed trace remains nontrivial unary homology in the declared finite differential class.", ["TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1"], "Formal local algebra does not supply a causal BV carrier."),
                cell("S2_CAUSAL_GREEN", "OBSTRUCTED_SCOPED", "No all-row causal homotopy can exist in the declared tau-adic finite differential class because the compactly supported dressed trace survives.", ["TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1"], "Adding the missing conformal gauge generator or changing the action remains open."),
                cell("S3_NONLINEAR_CARTAN", "OPEN_SEEDED", "Formal D-Cartan and compensator ingredients exist, but no common causal nonlinear contraction is certified.", ["QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION"], "The raw generators and theories are not identified."),
                cell("S4_HADAMARD_CCR", "FAIL_CLOSED", "No full tau-adic BRST Hadamard kernel exists.", [], "The causal carrier is already obstructed in the declared class."),
                cell("S5_BRST_WARD", "FAIL_CLOSED", "No state exists on which to close the Ward identity.", [], "Local cohomology does not create a covariance."),
                cell("S6_PHYSICAL_POSITIVITY", "FAIL_CLOSED", "No physical positivity theorem exists.", [], "The extension is formal and changed-theory."),
                cell("S7_RENORMALIZED_PRODUCTS", "CONDITIONAL", "An all-order local induction assumes a suitable quantum action principle/regulator, which is not constructed.", ["TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY"], "This is not a Lorentzian product construction."),
                cell("S8_QME", "CONDITIONAL", "Formal local all-loop QME restoration is proved only under the declared quantum action principle and regular coupling-chart assumptions.", ["TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY"], "It neither repairs strict pure Weyl nor establishes a Lorentzian QME."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "No residual transfer is authorized.", [], "The conditional local theorem and causal obstruction prevent promotion."),
                cell("S10_LORENTZIAN_CERTIFIED", "FAIL_CLOSED", "The formal extension is not Lorentzian-complete.", [], "Its local-QME strength and causal weakness must remain visibly separate."),
            ],
            "S2_CAUSAL_GREEN",
            "A new, explicitly chosen theory with either the missing conformal gauge generator or a dressed-trace kinetic term, followed by a fresh all-row causal BV certificate.",
        ),
        branch(
            "COMPLEX_COMPENSATOR_CHANGED_ACTION",
            "Complex compensator changed-action parent",
            "CHANGED_CLASSICAL_ACTION",
            "One exact unequal-kinetic polar compensator action on the unit vacuum cylinder, with 390 classical BV rows.",
            [
                cell("S0_CLASSICAL_AUTHORITY", "SCOPED_CERTIFIED", "The changed action, carrier and strict complement are content-pinned at one fixture.", ["COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"], "This is not strict pure Weyl gravity or the Berger theory."),
                cell("S1_OFF_SHELL_BV", "CERTIFIED", "A complete 390-row classical BV parent is constructed; the dressed trace and phase have causal kinetic blocks.", ["COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"], "The negative R^2 coefficient is not claimed stable or positive."),
                cell("S2_CAUSAL_GREEN", "CERTIFIED", "The changed carrier has complete classical causal Green data at the fixture.", ["COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"], "The result is action- and background-specific."),
                cell("S3_NONLINEAR_CARTAN", "OPEN_SEEDED", "The exact action supplies a concrete nonlinear target, but raw D-Cartan closure is unproved.", ["COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"], "The classical causal parent is not yet a cyclic interacting contraction."),
                cell("S4_HADAMARD_CCR", "OPEN_SEEDED", "The first analytic quantum gate is an all-row BRST-compatible Hadamard/Feynman selection.", ["COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"], "No state is constructed by the classical certificate."),
                cell("S5_BRST_WARD", "FAIL_CLOSED", "No BRST covariance or smooth Ward correction is certified.", [], "It must be built on the exact 390-row carrier."),
                cell("S6_PHYSICAL_POSITIVITY", "FAIL_CLOSED", "No positivity theorem exists and the scalar sector has an explicit stability concern.", [], "Causal propagation does not decide energy sign."),
                cell("S7_RENORMALIZED_PRODUCTS", "FAIL_CLOSED", "No Lorentzian products are defined.", [], "Same-action quantum consumers must first be reissued."),
                cell("S8_QME", "FAIL_CLOSED", "No anomaly classification or QME restoration exists for this exact changed action.", [], "The tau-adic formal theorem cannot be silently identified with this action."),
                cell("S9_RESIDUAL_TRANSFER", "FORBIDDEN_TRANSFER", "No residual transfer is authorized.", [], "Changed residual cohomology has not been constructed and the QME is open."),
                cell("S10_LORENTZIAN_CERTIFIED", "FAIL_CLOSED", "The branch is a viable classical causal parent, not a quantum completion.", [], "It is a neighboring theory rather than evidence that strict pure Weyl is complete."),
            ],
            "S3_NONLINEAR_CARTAN",
            "Reissue the nonlinear and quantum consumers against the exact 390-row action/carrier hash, then construct a BRST-compatible Hadamard/Feynman selection on that same carrier.",
        ),
    ]

    value: dict[str, Any] = {
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v1",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1",
        "result_kind": "BRANCH_BY_STAGE_COMPLETION_ATLAS",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "03b850e81ace1414419cbc6b0263e72d5603114d",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Which current Weyl-gravity architecture is closest to a complete Lorentzian BV quantum theory, and what is the first missing theorem on each route?",
        "answer": "There is no single winning ladder. Strict pure Weyl is the identity-preserving target and already has a scoped complete 386-row classical causal homotopy, but its repository-wide classical import remains fail-closed and its fixed-field-content local Euclidean QME is obstructed. The Berger positive-clock route is the analytic-maturity leader: 54-row causal control and cyclic D-Cartan closure through arity three are certified, and a 26-row exact-CCR Hadamard candidate has only a smooth Ward defect. Its next decisive theorem is a content-addressed nonstationary Krein normalization plus an admissible BRST Ward correction. Bach-flat and Einstein/Nariai branches are strong curved causal controls; reduced vacuum-cylinder modes are the genuine Hadamard control; compensator routes show that local-QME and causal completion can move in opposite directions.",
        "status_vocabulary": [{"id": key, "meaning": meaning} for key, meaning in STATUS.items()],
        "stages": [{"id": stage, "name": name, "completion_test": test} for stage, name, test in STAGES],
        "branches": branches,
        "frontier_summary": {
            "identity_preserving_front": {
                "branch": "STRICT_PURE_WEYL_386",
                "strength": "complete scoped classical causal BV homotopy on the target action",
                "first_gate": "replacement full classical-import freeze certificate",
                "independent_quantum_obstruction": "strict fixed-field-content local Euclidean one-loop QME obstruction",
            },
            "analytic_maturity_front": {
                "branch": "BERGER_POSITIVE_CLOCK_54",
                "strength": "complete 54-row causal complex, D-Cartan through arity three, and a 26-row exact-CCR Hadamard candidate with smooth Ward defect",
                "first_gate": "normalized nonstationary Krein H26_plus and admissible C26 Ward correction",
                "theory_boundary": "positive-clock Berger architecture, not strict pure Weyl",
            },
            "curved_generality_front": {
                "branch": "PURE_WEYL_BACH_FLAT_RANK310",
                "strength": "rank-310 all-row causal transfer on a relative-open Bach-flat ADM class",
                "first_gate": "same-carrier nonlinear cyclic compatibility, followed by Hadamard data",
            },
            "state_control_front": {
                "branch": "VACUUM_CYLINDER_REDUCED",
                "strength": "genuine reduced-mode Lorentzian Hadamard/Krein construction with E positivity and explicit A/L negative signs",
                "first_gate": "same-background full off-shell BRST lift",
            },
        },
        "classical_import_reconciliation": {
            "historical_gate": "FAIL_CLOSED",
            "later_certified_repairs": ["CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY", "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"],
            "current_disposition": "PARTIALLY_REPAIRED_REPLACEMENT_FREEZE_CERTIFICATE_ABSENT",
            "rule": "The old gate remains historical evidence, while later repairs are positive evidence. Neither may be erased; only a new all-check receiver certificate may supersede the old gate for publication authority.",
        },
        "research_queue": [
            {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "replacement full classical-import freeze certificate", "why": "It removes evidence drift and determines which quantum claims may use the authoritative classical snapshot."},
            {"priority": 2, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "normalized nonstationary Krein H26_plus and C26 support/pairing ledger", "why": "It is the shortest known path from a complete causal BV complex to a genuine full-carrier BRST Hadamard covariance."},
            {"priority": 3, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "continuous smooth-bikernel homotopy or direct q26-equivariant Feynman selection", "why": "It decides whether the smooth Ward defect can be removed without violating support and pairing constraints."},
            {"priority": 4, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear D-Cartan transfer", "why": "It tests whether the broadest curved causal target branch survives interaction compatibility."},
            {"priority": 5, "branch": "COMPLEX_COMPENSATOR_CHANGED_ACTION", "object": "same-action nonlinear and Hadamard consumers", "why": "It supplies an independently viable changed-theory control after the tau-adic causal obstruction."},
        ],
        "provenance": {"inputs": [{"path": path, "sha256": sha(path), "role": role} for path, role in INPUTS]},
        "claim_flags": {
            "architectures_classified": True,
            "historical_import_gate_reconciled": True,
            "strict_pure_weyl_scoped_full_causal_homotopy_recorded": True,
            "berger_54_row_causal_homotopy_recorded": True,
            "berger_arity_three_d_cartan_recorded": True,
            "berger_brst_hadamard_state_constructed": False,
            "strict_pure_weyl_qme_restored": False,
            "renormalized_lorentzian_products_constructed": False,
            "residual_quantum_transfer_authorized": False,
            "lorentzian_full_theory_certified": False,
        },
        "does_not_establish": [
            "a passed repository-wide classical freeze gate",
            "a BRST-compatible Hadamard state on any complete off-shell Weyl BV carrier",
            "physical Hilbert-space positivity for the full theory",
            "renormalized Lorentzian time-ordered products",
            "a causal perturbative AQFT construction",
            "a Lorentzian quantum-master-equation theorem",
            "residual quantum transfer",
            "equivalence of strict pure Weyl, Berger, tau-adic and changed-action compensator theories",
            "that reduced-mode or Euclidean evidence proves a Lorentzian full-complex claim",
            "that [W_+^2] or [W_-^2] is a one-particle graviton state",
            "a complete observationally validated theory",
        ],
        "independent_checker": {
            "path": "foundations/check_lorentzian_weyl_bv_completion_atlas.py",
            "checks": ["stage and branch closure", "first-gate consistency", "evidence-id closure", "status firewall", "provenance hashes", "claim-flag firewall", "canonical atlas digest"],
            "expected_digest": "",
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v1.md",
    }
    value["independent_checker"]["expected_digest"] = atlas_digest(value)
    return value


def atlas_digest(value: dict[str, Any]) -> str:
    payload = {key: value[key] for key in ("status_vocabulary", "stages", "branches", "frontier_summary", "classical_import_reconciliation", "research_queue")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def render(value: dict[str, Any]) -> str:
    stages = {stage["id"]: stage["name"] for stage in value["stages"]}
    symbols = {
        "CERTIFIED": "C",
        "SCOPED_CERTIFIED": "S",
        "PARTIAL_CERTIFIED": "P",
        "CONDITIONAL": "?",
        "OPEN_SEEDED": "o",
        "OBSTRUCTED_SCOPED": "X",
        "FAIL_CLOSED": "-",
        "FORBIDDEN_TRANSFER": "!",
        "NOT_APPLICABLE": "n/a",
    }
    lines = [
        "# Lorentzian Weyl BV completion atlas",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "## Outcome",
        "",
        value["answer"],
        "",
        "## How to read the atlas",
        "",
        "A row is a physically distinct architecture, not merely a different proof of the same theory. Columns are lifecycle gates. `C` means complete in the row's declared scope; `S` means a genuine but narrower result; `P` means certified pieces; `o` means a concrete open route; `X` is a scoped obstruction; `?` is conditional; `-` is fail-closed; `!` is a forbidden lifecycle transfer; and `n/a` means the reduced branch intentionally does not target that gate.",
        "",
        "| architecture | authority | off-shell BV | causal Green | nonlinear/cyclic | Hadamard/CCR | BRST Ward | positivity | Lorentzian products | QME | residual transfer | complete |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for route in value["branches"]:
        marks = [symbols[cell_["status"]] for cell_ in route["stages"]]
        lines.append("| " + route["name"] + " | " + " | ".join(marks) + " |")
    lines += ["", "## The four useful fronts", ""]
    for name, front in value["frontier_summary"].items():
        label = name.replace("_", " ").title()
        lines.append(f"- **{label}:** `{front['branch']}` — {front['strength']}. First gate: {front['first_gate']}.")
    lines += ["", "## First missing theorem by route", ""]
    for route in value["branches"]:
        lines += [f"### {route['name']}", "", f"**Relation to target:** `{route['relation_to_target']}`", "", f"**Scope:** {route['scope']}", "", f"**First unclosed gate:** `{route['first_unclosed_gate']}` — {stages[route['first_unclosed_gate']]}", "", f"**Next decisive object:** {route['next_decisive_object']}", ""]
    lines += ["## Why the old import gate and new causal results can coexist", "", value["classical_import_reconciliation"]["rule"], "", "The historical bootstrap certificate still fails closed. Later receipts independently repair the minimal-BV filtration, cross-commit snapshot identity and the Berger support-local q2 import. Separately, classical certificates establish full causal complexes. These results answer different acceptance questions; the atlas records all of them and asks for a new all-check receiver certificate instead of rewriting history.", "", "## Ranked research queue", ""]
    for item in value["research_queue"]:
        lines.append(f"{item['priority']}. **{item['object']}** (`{item['branch']}`): {item['why']}")
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas.py", "python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas", "```", "", "## Boundaries", ""]
    lines += [f"- This does not establish {item}." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

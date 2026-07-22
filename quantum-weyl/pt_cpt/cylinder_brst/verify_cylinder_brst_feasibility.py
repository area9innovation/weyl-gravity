#!/usr/bin/env python3
"""Independent exact verifier for the cylinder CPT/BRST feasibility result.

This rail does not import the producer.  It reconstructs the energy-five
matrices from the pinned representation implementation and separately checks
the analytic tower-link argument.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from symbolic.verify_conformal_generator_all_levels import (
    lowering_blocks,
    representation_space,
)

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1.json"
SCHEMA = HERE / "schema/cylinder-brst-structured-cpt-feasibility-v1.schema.json"
RECEIPT = HERE / "receipts/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1_TIER_RECEIPT.json"
REPORT = ROOT / "reports/phase2-cpt-cylinder-brst-feasibility-2026-07-22.md"
ATLAS = ROOT / "residual_atlas/phase2-cpt-cylinder-brst-feasibility-fragment-v1.json"

EXPECTED_INPUTS = {
    "one_particle_krein": ("analytic_completion/certificates/one_particle_krein.json", "c52f8b2fcee6573e55e72402008779fd706311b77e2463a774b9eb16ce12b374"),
    "krein_implementation": ("analytic_completion/one_particle/krein.py", "1924e6cd323df39dc280e9b39e0c890a63673db4e1a5c249382bbe3b7e19c295"),
    "closed_generators": ("analytic_completion/one_particle/generators.py", "9165404959b1f581a710a233fb7a076290f559e3bb9d0790a0c896cf9798332f"),
    "all_level_generators": ("symbolic/verify_conformal_generator_all_levels.py", "9b7f90e8377d794cd2fa4cde8b34a88baf2cba90c41074cb1a4a0fde4c77a6a0"),
    "polarized_state_complex": ("field_bv_identification/polarized_state/certificates/polarized_state_complex.json", "efe492946333578e91d880fde0008166ba8960bc366840413883e5c0e39d0ec1"),
    "polarized_state_implementation": ("field_bv_identification/polarized_state/polarized_complex.py", "245452186edd42cba7d4eeb2feb2bca0b5db2c39eba846903c4b3d39e854511d"),
    "reduced_bridge4": ("quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json", "f49edce04b39d1e600d0072bfabc784b8ef6edf0d5a1fc39c8ad89f7fe031d48"),
    "p2a_contract": ("quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json", "377f699d854724f743188b854e4f5be3f29540ba1f5bc2beee3ec9204e7dbf6a"),
}

OUTPUTS = {
    "producer": HERE / "cylinder_brst_feasibility.py",
    "verifier": Path(__file__),
    "schema": SCHEMA,
    "certificate": CERTIFICATE,
    "tests": HERE / "tests/test_cylinder_brst_feasibility.py",
    "report": REPORT,
    "atlas": ATLAS,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_pins(certificate: dict[str, Any]) -> None:
    for role, (relative, expected_hash) in EXPECTED_INPUTS.items():
        path = ROOT / relative
        if _sha(path) != expected_hash:
            raise AssertionError(f"source drift: {role}")
        if certificate["source_refs"][role] != {"path": relative, "sha256": expected_hash}:
            raise AssertionError(f"certificate pin drift: {role}")


def _proper_defects(space: Any) -> tuple[dict[str, int], list[sp.MatrixBase]]:
    c0 = space.form
    ranks = {"D": int((c0 * space.energy - space.energy * c0).rank())}
    for side, generators in (("left", space.left), ("right", space.right)):
        for axis, matrix in sorted(generators.items()):
            ranks[f"SO4_{side}_{axis}"] = int((c0 * matrix - matrix * c0).rank())
    defects = []
    for kind, generators in (("Kminus", space.lowering), ("Kplus", space.raising)):
        for component, matrix in sorted(generators.items()):
            defect = c0 * matrix - matrix * c0
            defects.append(defect)
            ranks[f"{kind}_({component[0]},{component[1]})"] = int(defect.rank())
    return ranks, defects


def _verify_finite_buffer(certificate: dict[str, Any]) -> None:
    finite = certificate["finite_buffer_regression"]
    if finite["maximum_energy"] != 5 or finite["generator_count"] != 15:
        raise AssertionError("buffer scope mutation")
    if "do not prove" not in finite["buffer_warning"]:
        raise AssertionError("finite buffer was promoted")
    for chirality in (-1, 1):
        space = representation_space(5, chirality)
        row = finite["chiralities"][str(chirality)]
        c0 = space.form
        if c0**2 != sp.eye(space.dimension) or space.form * c0 != sp.eye(space.dimension):
            raise AssertionError("independent C0/eta0 identity failed")
        ranks, defects = _proper_defects(space)
        if row["commutator_ranks"] != ranks:
            raise AssertionError("commutator rank table mismatch")
        compact_names = ["D"] + [f"SO4_{side}_{axis}" for side in ("left", "right") for axis in ("x", "y", "z")]
        proper_names = [name for name in ranks if name.startswith("K")]
        if any(ranks[name] != 0 for name in compact_names):
            raise AssertionError("C0 compact commutator mutation")
        if len(proper_names) != 8 or any(ranks[name] != 32 for name in proper_names):
            raise AssertionError("rank-32 proper-conformal regression failed")
        stacked_rank = int(sp.Matrix.vstack(*defects).rank())
        if stacked_rank != 102 or row["degree_zero_to_one_BRST_defect_rank"] != stacked_rank:
            raise AssertionError("BRST defect rank mismatch")
        plus = sum(value == 1 for value in space.form.diagonal())
        minus = sum(value == -1 for value in space.form.diagonal())
        if row["krein_inertia"] != {"positive": plus, "negative": minus, "zero": 0}:
            raise AssertionError("Krein inertia mismatch")
        if row["eta0_inertia"] != {"positive": space.dimension, "negative": 0, "zero": 0}:
            raise AssertionError("eta0 positivity mismatch")


def _verify_all_energy_commutant(certificate: dict[str, Any]) -> None:
    search = certificate["invariant_commutant_search"]
    graph = search["finite_buffer_branch_scalar_graph"]
    blocks = lowering_blocks(5)
    expected_edges = {(b.family, b.source, b.target, str(b.coefficient)) for b in blocks}
    stored_edges = {(b["family"], b["source"], b["target"], b["coefficient"]) for b in graph["edges"]}
    if stored_edges != expected_edges:
        raise AssertionError("finite tower graph mismatch")
    nodes = {b.source for b in blocks} | {b.target for b in blocks}
    adjacency = {node: set() for node in nodes}
    for block in blocks:
        adjacency[block.source].add(block.target)
        adjacency[block.target].add(block.source)
    seen = set()
    stack = [next(iter(nodes))]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(adjacency[node] - seen)
    if seen != nodes or graph["commutant_dimension_per_chirality"] != 1:
        raise AssertionError("finite branch-scalar graph disconnected")

    # Separate positivity proof for every analytic coefficient tail.  The
    # factored formulas in the certificate are parsed afresh, and positivity
    # follows directly from the signed integer factors on n>=minimum.
    n = sp.symbols("n", integer=True, positive=True)
    expected_minima = {"EE": 3, "AE": 3, "AA": 4, "LE": 4, "LA": 4, "LL": 5}
    expected_squares = {
        "EE": 2 * (n - 1) * (n + 1) * (n + 3) / (n + 2),
        "AE": 8 * (n - 1) / ((n - 2) * (n + 2)),
        "AA": 2 * (n - 3) * (n - 1) * (n + 2) / (n - 2),
        "LE": 2 * (n - 3) / (n - 2),
        "LA": 8 / (n - 2),
        "LL": 2 * (n - 2) * (n + 1),
    }
    for family, row in search["all_energy_nonzero_coefficients"].items():
        minimum = expected_minima[family]
        if row["minimum_source_energy"] != minimum or row["strictly_positive_on_declared_tail"] is not True:
            raise AssertionError("coefficient tail scope mutation")
        expression = sp.sympify(row["coefficient_squared"], locals={"n": n})
        if sp.simplify(expression - expected_squares[family]) != 0:
            raise AssertionError(f"analytic coefficient formula mismatch: {family}")
        numerator, denominator = sp.fraction(sp.cancel(expression))
        m = sp.symbols("m", nonnegative=True)
        npoly = sp.Poly(sp.expand(numerator.subs(n, m + minimum)), m)
        dpoly = sp.Poly(sp.expand(denominator.subs(n, m + minimum)), m)
        if not (
            all(value >= 0 for value in npoly.all_coeffs())
            and all(value >= 0 for value in dpoly.all_coeffs())
            and npoly.eval(0) > 0
            and dpoly.eval(0) > 0
        ):
            raise AssertionError(f"nonzero analytic link failed: {family}")

    if search["full_connected_conformal_commutant"] != "C=c_minus*I on chirality -1 direct-sum c_plus*I on chirality +1":
        raise AssertionError("full commutant mutation")
    if search["all_energy_result"] != "NO_POSITIVE_GC_METRIC_FROM_A_RESIDUAL_INVARIANT_HERMITIAN_INVOLUTION":
        raise AssertionError("positive invariant GC mutation")


def verify_certificate(certificate: dict[str, Any], *, verify_pins: bool = True) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    if verify_pins:
        _verify_pins(certificate)
    _verify_finite_buffer(certificate)
    _verify_all_energy_commutant(certificate)
    chain = certificate["BRST_chain_decision"]
    if chain["C0_chain_map"] is not False or chain["corrected_residual_invariant_C_exists"] is not False:
        raise AssertionError("chain obstruction mutation")
    if chain["positive_cohomology_test_reached"] is not False:
        raise AssertionError("cohomology positivity overpromotion")
    if chain["nontrivial_ghost_normalizers"] != "NOT_CLASSIFIED_OUTSIDE_THE_DECLARED_INVARIANT_COMMUTANT":
        raise AssertionError("ghost-action scope widened")
    if certificate["decision"]["full_BV_state_or_unitarity"] != "NOT_ESTABLISHED":
        raise AssertionError("full BV/unitarity promotion")


def verify_receipt(receipt: dict[str, Any], certificate: dict[str, Any]) -> None:
    if receipt["subject_result_id"] != certificate["result_id"]:
        raise AssertionError("receipt subject mismatch")
    for role, (_, expected_hash) in EXPECTED_INPUTS.items():
        if receipt["source_pins"][role] != expected_hash:
            raise AssertionError(f"receipt source pin mismatch: {role}")
    if set(receipt["output_hashes"]) != set(OUTPUTS):
        raise AssertionError("receipt output manifest mismatch")
    for role, path in OUTPUTS.items():
        if receipt["output_hashes"][role] != _sha(path):
            raise AssertionError(f"receipt output hash mismatch: {role}")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    verify_certificate(certificate)
    mutations = [
        lambda value: value["BRST_chain_decision"].update(C0_chain_map=True),
        lambda value: value["finite_buffer_regression"]["chiralities"]["1"]["commutator_ranks"].update({"Kplus_(1/2,1/2)": 0}),
        lambda value: value["finite_buffer_regression"].update(buffer_warning="finite exact representation"),
        lambda value: value["invariant_commutant_search"].update(all_energy_result="POSITIVE_C_EXISTS"),
        lambda value: value["BRST_chain_decision"].update(nontrivial_ghost_normalizers="EXCLUDED"),
        lambda value: value["decision"].update(full_BV_state_or_unitarity="CERTIFIED"),
    ]
    for mutate in mutations:
        mutant = copy.deepcopy(certificate)
        mutate(mutant)
        try:
            verify_certificate(mutant, verify_pins=False)
        except (AssertionError, KeyError, TypeError, ValidationError):
            continue
        raise AssertionError("decisive mutation accepted")
    verify_receipt(json.loads(RECEIPT.read_text()), certificate)
    print(
        "CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1 independent verification: "
        f"PASS ({len(mutations)} decisive mutations rejected)"
    )


if __name__ == "__main__":
    main()

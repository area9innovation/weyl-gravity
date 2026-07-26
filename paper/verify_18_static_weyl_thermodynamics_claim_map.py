#!/usr/bin/env python3
"""Fail-closed verifier for the Paper 18 theorem/evidence boundary."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GENERATOR = HERE / "generate_18_static_weyl_thermodynamics_claim_map.py"
CLAIM_MAP = HERE / "18-static-bach-flat-black-hole-thermodynamics-claim-map.json"
PAPER = HERE / "18-static-bach-flat-black-hole-thermodynamics.tex"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def load_generator():
    spec = importlib.util.spec_from_file_location("paper18_claim_generator", GENERATOR)
    require(spec is not None and spec.loader is not None, "cannot load generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    require(CLAIM_MAP.exists(), "claim map missing")
    generator = load_generator()
    actual = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    expected = generator.build()
    require(actual == expected, "claim map is stale or mutated")

    evidence = {
        key: json.loads((ROOT / row["path"]).read_text(encoding="utf-8"))
        for key, row in actual["evidence"].items()
    }
    require(
        evidence["BH0"]["claim_flags"]["laurent_class_completeness_certified"],
        "BH0 Laurent completeness flag is false",
    )
    require(
        not evidence["BH0"]["claim_flags"]["general_completeness_certified"],
        "BH0 unexpectedly claims general completeness",
    )
    require(
        evidence["BH1"]["claim_flags"]["bare_form_nonintegrable_certified"],
        "BH1 bare nonintegrability flag is false",
    )
    for flag in (
        "normalized_form_basic_certified",
        "normalized_form_closed_certified",
        "hamiltonian_potential_certified",
        "wald_entropy_certified",
        "static_first_law_certified",
    ):
        require(evidence["BH1A"]["claim_flags"][flag], f"BH1A flag is false: {flag}")
    for flag in (
        "conformal_charge_annihilation_certified",
        "conformal_entropy_invariance_certified",
        "conformal_null_direction_certified",
        "diffeo_charge_annihilation_certified",
        "unique_linear_generator_extension_certified",
    ):
        require(evidence["BH1B"]["claim_flags"][flag], f"BH1B flag is false: {flag}")
    require(
        not evidence["BH1B"]["claim_flags"]["second_order_physical_process_certified"],
        "BH1B unexpectedly claims a physical-process theorem",
    )
    require(
        not evidence["BH1B"]["claim_flags"]["radiative_bilinear_flux_matrix_certified"],
        "BH1B unexpectedly claims radiative bilinear flux",
    )
    for flag in (
        "laurent_classification_certified",
        "residual_basic_normalization_certified",
        "simultaneous_static_first_law_certified",
        "linear_spherical_gauge_audit_certified",
    ):
        require(evidence["P18"]["claim_flags"][flag], f"P18 promotion flag is false: {flag}")
    require(
        evidence["P18"]["declaration"]["historical_certificates_unchanged"],
        "P18 promotion is not append-only",
    )

    paper = PAPER.read_text(encoding="utf-8")
    required_fragments = (
        r"\title{Residual-Basic Charges and Simultaneous Horizon First Laws",
        r"\large on the Mannheim--Kazanas Family",
        r"\gamma=0,\qquad w=1",
        r"\dd J\neq0",
        r"\mathcal F\neq0",
        r"N=u f(J)",
        r"u\mathcal F=\dd H",
        r"\boxed{\dd H=T_h\,\dd S_h}",
        r"\mathcal E_\beta",
        r"Q_{\delta\chi}",
        "Jacobson--Kang--Myers",
        "no preferred physical mass",
        "does not compute the bilinear radiative flux",
        "stability, quasinormal ringing, Hawking radiation, or any quantum",
    )
    for fragment in required_fragments:
        require(fragment in paper, f"required manuscript boundary missing: {fragment}")

    require(
        actual["release_boundary"]["paper_status"] == "WORKING_DRAFT",
        "paper improperly promoted beyond working draft",
    )
    require(
        not actual["release_boundary"]["immutable_archive"],
        "claim map incorrectly asserts an immutable archive",
    )
    print("PASS Paper 18 claim map, evidence hashes, exact flags, and manuscript boundary")


if __name__ == "__main__":
    main()

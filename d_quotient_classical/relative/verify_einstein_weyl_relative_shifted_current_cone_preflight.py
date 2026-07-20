#!/usr/bin/env python3
"""Independent replay of the shifted current-cone typing and rank census."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-shifted-current-cone-preflight-v1.schema.json"
CURRENT_LAYOUT = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _degree_vector(ranks: dict[int, int], lower: int, upper: int) -> list[int]:
    return [ranks.get(degree, 0) for degree in range(lower, upper + 1)]


def _cotangent_complete(base: dict[int, int]) -> dict[int, int]:
    """Return ranks of B direct-sum B^vee[1], paired in degrees n and 1-n."""
    result = Counter(base)
    for degree, rank in base.items():
        result[1 - degree] += rank
    return dict(result)


def verify() -> dict[str, object]:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source manifest drift: {relative}")

    dependencies: dict[str, dict] = {}
    for name, artifact in value["dependencies"].items():
        path = ROOT / artifact["path"]
        if _sha(path) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {name}")
        dependencies[name] = json.loads(path.read_text())

    cone = dependencies["relative_cone"]["mapping_cofiber"]
    if cone["convention"] != "Cone(iota)^n=W^n direct_sum E^(n+1), with the source ghost row placed in the initial degree":
        raise AssertionError("mapping-cone shift convention drifted")
    cone_ranks = {degree: rank for degree, rank in zip(range(-2, 3), cone["degree_dimensions"], strict=True)}

    current_layout = json.loads(CURRENT_LAYOUT.read_text())
    primal_rows = [row for row in current_layout["rows"] if row["chain"] == "primal"]
    primal_ranks = Counter(row["degree"] for row in primal_rows)
    if _degree_vector(dict(primal_ranks), -2, 2) != [5, 20, 30, 20, 5]:
        raise AssertionError("primal five-current ranks drifted")

    # The repository convention is K[1]^n=K^(n+1), as used in Cone(iota).
    shifted_primal = {degree - 1: rank for degree, rank in primal_ranks.items()}
    base = Counter(cone_ranks)
    base.update(shifted_primal)
    base_vector = _degree_vector(dict(base), -3, 2)
    if base_vector != value["shifted_cyclic_carrier"]["base_degree_ranks"]:
        raise AssertionError("shifted mapping-cone base census failed")

    completed = _cotangent_complete(dict(base))
    completed_vector = _degree_vector(completed, -3, 4)
    if completed_vector != value["shifted_cyclic_carrier"]["completed_degree_ranks"]:
        raise AssertionError("shifted cotangent completion census failed")
    if sum(base_vector) != 158 or sum(completed_vector) != 316:
        raise AssertionError("shifted carrier total rank failed")

    target_rows = dependencies["target_layout"]["content"]["rows"]
    target_ranks = Counter(row["degree"] for row in target_rows)
    components = value["required_chain_map"]["components"]
    if [item["source_rank"] for item in components] != [5, 20, 30, 20, 5]:
        raise AssertionError("chain-map source ranks drifted")
    if [item["target_rank"] for item in components] != [0, 6, 14, 14, 6]:
        raise AssertionError("chain-map target ranks drifted")
    if _degree_vector(dict(target_ranks), -1, 2) != [6, 14, 14, 6]:
        raise AssertionError("target degree census drifted")

    old_ranks = dependencies["cotangent_316"]["bundle_classification"]["completed_degree_ranks"]
    if old_ranks != value["comparison_with_existing_316"]["existing_degree_ranks"]:
        raise AssertionError("existing 316-row profile drifted")
    if old_ranks == completed_vector:
        raise AssertionError("distinct 316-row gradings were conflated")

    flags = value["classification"]
    if any(flags[key] for key in (
        "existing_316_direct_sum_grading_sufficient",
        "support_local_chain_map_A_constructed",
        "top_descent_solved",
        "relative_q2_repaired",
        "causal_observable_particle_or_quantum_claim",
    )):
        raise AssertionError("preflight overpromoted")

    return {
        "status": "PASS",
        "primal_ranks": _degree_vector(dict(primal_ranks), -2, 2),
        "shifted_base_ranks": base_vector,
        "shifted_completed_ranks": completed_vector,
        "old_completed_ranks": old_ranks,
        "support_local_chain_map_open": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
